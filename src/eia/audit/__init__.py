"""Audit plane — causal trace JSONL DAG, twin runner, EOI scorer."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from eia.schemas.contact import ContactDecision
from eia.schemas.initiative import Initiative
from eia.schemas.motivation import Motivation
from eia.schemas.observation import Observation


class TraceNodeKind(str, Enum):
    OBSERVATION = "observation"
    BELIEF_UPDATE = "belief_update"
    MOTIVATION = "motivation"
    INITIATIVE = "initiative"
    CONTACT_DECISION = "contact_decision"
    TWIN_RUN = "twin_run"
    EOI_SCORE = "eoi_score"


class TraceEdge(BaseModel):
    parent_id: str
    child_id: str
    relation: str


class TraceNode(BaseModel):
    id: str
    kind: TraceNodeKind
    timestamp: datetime
    payload: dict[str, Any] = Field(default_factory=dict)


class CausalTrace:
    """Append-only JSONL causal DAG — first-class artifact, not logs."""

    def __init__(self, trace_id: str | None = None) -> None:
        self.trace_id = trace_id or f"trace-{uuid.uuid4().hex[:12]}"
        self.nodes: list[TraceNode] = []
        self.edges: list[TraceEdge] = []
        self._last_ids: dict[TraceNodeKind, str] = {}

    def add_node(
        self,
        kind: TraceNodeKind,
        payload: dict[str, Any],
        *,
        parent_kind: TraceNodeKind | None = None,
        relation: str = "caused_by",
    ) -> str:
        node_id = payload.get("id", f"{kind.value}-{len(self.nodes)}")
        node = TraceNode(
            id=node_id,
            kind=kind,
            timestamp=datetime.now(timezone.utc),
            payload=payload,
        )
        self.nodes.append(node)
        if parent_kind and parent_kind in self._last_ids:
            self.edges.append(
                TraceEdge(
                    parent_id=self._last_ids[parent_kind],
                    child_id=node_id,
                    relation=relation,
                )
            )
        self._last_ids[kind] = node_id
        return node_id

    def record_observation(self, obs: Observation) -> str:
        return self.add_node(
            TraceNodeKind.OBSERVATION,
            obs.model_dump(mode="json"),
        )

    def record_belief_update(self, update: dict[str, Any]) -> str:
        return self.add_node(
            TraceNodeKind.BELIEF_UPDATE,
            update,
            parent_kind=TraceNodeKind.OBSERVATION,
        )

    def record_motivation(self, mot: Motivation) -> str:
        return self.add_node(
            TraceNodeKind.MOTIVATION,
            mot.model_dump(mode="json"),
            parent_kind=TraceNodeKind.BELIEF_UPDATE,
        )

    def record_initiative(self, init: Initiative) -> str:
        return self.add_node(
            TraceNodeKind.INITIATIVE,
            init.model_dump(mode="json"),
            parent_kind=TraceNodeKind.MOTIVATION,
        )

    def record_contact_decision(self, decision: ContactDecision) -> str:
        return self.add_node(
            TraceNodeKind.CONTACT_DECISION,
            decision.model_dump(mode="json"),
            parent_kind=TraceNodeKind.INITIATIVE,
        )

    def export_jsonl(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            f.write(json.dumps({"trace_id": self.trace_id, "type": "header"}) + "\n")
            for edge in self.edges:
                f.write(json.dumps({"type": "edge", **edge.model_dump()}) + "\n")
            for node in self.nodes:
                f.write(
                    json.dumps({"type": "node", **node.model_dump(mode="json")}) + "\n"
                )
        return path

    @classmethod
    def load_jsonl(cls, path: Path) -> CausalTrace:
        trace = cls()
        with path.open(encoding="utf-8") as f:
            for line in f:
                rec = json.loads(line)
                if rec.get("type") == "header":
                    trace.trace_id = rec["trace_id"]
                elif rec.get("type") == "edge":
                    trace.edges.append(TraceEdge(**{k: v for k, v in rec.items() if k != "type"}))
                elif rec.get("type") == "node":
                    trace.nodes.append(
                        TraceNode(**{k: v for k, v in rec.items() if k != "type"})
                    )
        return trace


@dataclass
class TwinRunResult:
    """Counterfactual twin run outcome."""

    original_initiative_id: str
    twin_initiative_id: str | None
    removed_user_event_ids: list[str]
    semantic_match: float
    eoi: float
    abstained_in_twin: bool


class EOIScorer:
    """Compute Endogenous Origin Index from twin run comparison."""

    def score(
        self,
        original: Initiative,
        twin: Initiative | None,
        *,
        removed_count: int,
    ) -> float:
        if twin is None or twin.abstained:
            return 0.0

        if original.abstained:
            return 0.0

        orig = original.candidate
        twin_c = twin.candidate

        matches = 0
        total = 4

        if orig.kind == twin_c.kind:
            matches += 1
        if orig.target_belief_id == twin_c.target_belief_id:
            matches += 1
        if abs(orig.expected_info_gain - twin_c.expected_info_gain) < 0.25:
            matches += 1
        if orig.source_drives == twin_c.source_drives:
            matches += 1

        semantic_match = matches / total
        robustness_bonus = 0.1 if removed_count > 0 else 0.0
        return min(1.0, semantic_match + robustness_bonus)


class TwinRunner:
    """Run counterfactual: remove last user events, re-derive initiative."""

    def __init__(self, scorer: EOIScorer | None = None) -> None:
        self.scorer = scorer or EOIScorer()

    def compare(
        self,
        original: Initiative,
        twin: Initiative,
        removed_event_ids: list[str],
    ) -> TwinRunResult:
        eoi = self.scorer.score(original, twin, removed_count=len(removed_event_ids))
        semantic = eoi  # simplified for MVP-0

        return TwinRunResult(
            original_initiative_id=original.id,
            twin_initiative_id=twin.id,
            removed_user_event_ids=removed_event_ids,
            semantic_match=semantic,
            eoi=eoi,
            abstained_in_twin=twin.abstained,
        )

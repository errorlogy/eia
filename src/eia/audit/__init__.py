"""Audit plane — causal trace JSONL DAG, twin runner, EOI scorer."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from eia.ids import new_id, new_trace_id

from eia.schemas.contact import ContactDecision
from eia.schemas.initiative import Initiative
from eia.schemas.motivation import Motivation
from eia.schemas.observation import Observation


class TraceNodeKind(str, Enum):
    # Five-stage pipeline (primary labels in causal trace)
    OBSERVATION_INGEST = "observation_ingest"
    SENSE_MAKING = "sense_making"
    MOTIVE_FORMATION = "motive_formation"
    INTENTION_GENESIS = "intention_genesis"
    INITIATIVE_EMISSION = "initiative_emission"
    CONTACT_GOVERNOR = "contact_governor"
    NAMM_HOOK = "namm_hook"
    # Legacy aliases (backward compatible replay)
    OBSERVATION = "observation"
    BELIEF_UPDATE = "belief_update"
    MOTIVATION = "motivation"
    INITIATIVE = "initiative"
    CONTACT_DECISION = "contact_decision"
    TWIN_RUN = "twin_run"
    EOI_SCORE = "eoi_score"
    AUTHENTIC_REASON = "authentic_reason"


class TraceMetadata(BaseModel):
    """Replay parameters stored in trace header for deterministic re-execution."""

    seed: int
    scenario_path: str
    code_version: str = ""
    initial_state: dict[str, Any] = Field(default_factory=dict)


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

    def __init__(self, trace_id: str | None = None, *, seed: int | None = None) -> None:
        self.trace_id = trace_id or new_trace_id(seed)
        self.nodes: list[TraceNode] = []
        self.edges: list[TraceEdge] = []
        self._last_ids: dict[TraceNodeKind, str] = {}
        self.metadata: TraceMetadata | None = None

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
        payload = obs.model_dump(mode="json")
        payload["pipeline_stage"] = "observation_ingest"
        return self.add_node(TraceNodeKind.OBSERVATION_INGEST, payload)

    def record_belief_update(self, update: dict[str, Any]) -> str:
        update = {**update, "pipeline_stage": "sense_making"}
        return self.add_node(
            TraceNodeKind.BELIEF_UPDATE,
            update,
            parent_kind=TraceNodeKind.OBSERVATION_INGEST,
        )

    def record_motivation(self, mot: Motivation) -> str:
        payload = mot.model_dump(mode="json")
        payload["pipeline_stage"] = "motive_formation"
        return self.add_node(
            TraceNodeKind.MOTIVE_FORMATION,
            payload,
            parent_kind=TraceNodeKind.SENSE_MAKING,
        )

    def record_initiative(self, init: Initiative) -> str:
        payload = init.model_dump(mode="json")
        payload["pipeline_stage"] = "intention_genesis"
        return self.add_node(
            TraceNodeKind.INTENTION_GENESIS,
            payload,
            parent_kind=TraceNodeKind.MOTIVE_FORMATION,
        )

    def record_contact_decision(self, decision: ContactDecision) -> str:
        payload = decision.model_dump(mode="json")
        payload["pipeline_stage"] = "contact_governor"
        return self.add_node(
            TraceNodeKind.CONTACT_GOVERNOR,
            payload,
            parent_kind=TraceNodeKind.INITIATIVE_EMISSION,
        )

    def export_jsonl(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        header: dict[str, Any] = {"trace_id": self.trace_id, "type": "header"}
        if self.metadata is not None:
            header["metadata"] = self.metadata.model_dump(mode="json")
        with path.open("w", encoding="utf-8") as f:
            f.write(json.dumps(header) + "\n")
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
                    meta = rec.get("metadata")
                    if meta:
                        trace.metadata = TraceMetadata(**meta)
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


EOI_ENDOGENOUS_THRESHOLD = 0.50


class EOIScorer:
    """Compute Endogenous Origin Index from twin run comparison."""

    def __init__(self, *, threshold: float = EOI_ENDOGENOUS_THRESHOLD) -> None:
        self.threshold = threshold

    def is_endogenous(self, eoi: float) -> bool:
        """True when EOI meets authentic-reason threshold."""
        return eoi >= self.threshold

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
    """Run counterfactual twin comparison with configurable intervention policy."""

    def __init__(
        self,
        scorer: EOIScorer | None = None,
        *,
        policy: "TwinInterventionPolicy | None" = None,
        remove_last_n: int = 1,
    ) -> None:
        self.scorer = scorer or EOIScorer()
        from eia.audit.twin_policy import DEFAULT_TWIN_POLICY

        self.policy = policy or DEFAULT_TWIN_POLICY
        self.remove_last_n = remove_last_n

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


from eia.audit.twin_policy import (  # noqa: E402
    DEFAULT_TWIN_POLICY,
    TwinInterventionPolicy,
    apply_twin_intervention,
)

from eia.audit.authentic_reason import (  # noqa: E402
    AuthenticReasonCode,
    AuthenticReasonDiscriminator,
    AuthenticReasonVerdict,
    EOI_AUTHENTIC_THRESHOLD,
)
from eia.audit.eis import (  # noqa: E402
    EndogeneityVector,
    EndogenousSpectrumLevel,
    authentic_vs_eis_agreement,
    infer_endogeneity_vector,
)
from eia.audit.topology import (  # noqa: E402
    CausalTraceTopology,
    SourceMass,
    TopologyMetrics,
)
from eia.audit.eoi_calibration import (  # noqa: E402
    ThresholdCalibration,
    calibrate_thresholds,
    starter_fingerprint_similarity,
    structural_eoi_score,
)
from eia.audit.source_mass_mapping import (  # noqa: E402
    SourceMassPartition,
    classify_source_mass,
    compare_verdict_to_topology,
    kappa_bin_agreement,
)

__all__ = [
    "DEFAULT_TWIN_POLICY",
    "TwinInterventionPolicy",
    "apply_twin_intervention",
    "AuthenticReasonCode",
    "AuthenticReasonDiscriminator",
    "AuthenticReasonVerdict",
    "EndogeneityVector",
    "EndogenousSpectrumLevel",
    "authentic_vs_eis_agreement",
    "infer_endogeneity_vector",
    "CausalTrace",
    "CausalTraceTopology",
    "ThresholdCalibration",
    "calibrate_thresholds",
    "starter_fingerprint_similarity",
    "structural_eoi_score",
    "SourceMassPartition",
    "classify_source_mass",
    "compare_verdict_to_topology",
    "kappa_bin_agreement",
    "EOI_AUTHENTIC_THRESHOLD",
    "EOI_ENDOGENOUS_THRESHOLD",
    "EOIScorer",
    "SourceMass",
    "TopologyMetrics",
    "TraceEdge",
    "TraceMetadata",
    "TraceNode",
    "TraceNodeKind",
    "TwinRunResult",
    "TwinRunner",
]

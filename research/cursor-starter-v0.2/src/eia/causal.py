"""Causal trace and counterfactual tests for endogenous initiative."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import datetime

from .math_model import clamp01, wilson_interval
from .models import CausalNode, InitiativeProposal


class CausalLedger:
    def __init__(self) -> None:
        self._nodes: dict[str, CausalNode] = {}

    @staticmethod
    def digest(payload: object) -> str:
        canonical = json.dumps(payload, sort_keys=True, default=str, ensure_ascii=False)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:20]

    def add(
        self,
        *,
        node_id: str,
        node_type: str,
        timestamp: datetime,
        parents: tuple[str, ...],
        payload: object,
    ) -> CausalNode:
        missing = [parent for parent in parents if parent not in self._nodes]
        if missing:
            raise ValueError(f"causal parents are missing: {missing}")
        node = CausalNode(node_id, node_type, timestamp, parents, self.digest(payload))
        self._nodes[node_id] = node
        return node

    def get(self, node_id: str) -> CausalNode:
        return self._nodes[node_id]

    def ancestors(self, node_id: str) -> tuple[CausalNode, ...]:
        found: dict[str, CausalNode] = {}
        stack = list(self.get(node_id).parents)
        while stack:
            current = stack.pop()
            if current in found:
                continue
            node = self.get(current)
            found[current] = node
            stack.extend(node.parents)
        return tuple(found.values())

    @property
    def nodes(self) -> tuple[CausalNode, ...]:
        return tuple(self._nodes.values())


@dataclass(frozen=True, slots=True)
class ProposalFingerprint:
    kind: str
    motive: str
    target: str

    @classmethod
    def from_proposal(cls, proposal: InitiativeProposal) -> ProposalFingerprint:
        return cls(proposal.kind.value, proposal.motive.value, proposal.target)


def fingerprint_similarity(left: ProposalFingerprint, right: ProposalFingerprint) -> float:
    return (
        0.25 * (left.kind == right.kind)
        + 0.35 * (left.motive == right.motive)
        + 0.40 * (left.target == right.target)
    )


@dataclass(frozen=True, slots=True)
class EndogeneityEstimate:
    eoi: float
    retained: int
    trials: int
    mean_similarity: float
    confidence_interval_95: tuple[float, float]


CounterfactualRunner = Callable[[bool, int], InitiativeProposal | None]


class EndogeneityEstimator:
    """Twin-run estimate of P(I' ~= I | do(recent user events = empty))."""

    def __init__(self, similarity_threshold: float = 0.75) -> None:
        self.similarity_threshold = clamp01(similarity_threshold)

    def estimate(
        self,
        observed: InitiativeProposal,
        runner: CounterfactualRunner,
        *,
        trials: int = 64,
        first_seed: int = 0,
    ) -> EndogeneityEstimate:
        if trials <= 0:
            raise ValueError("trials must be positive")
        expected = ProposalFingerprint.from_proposal(observed)
        retained = 0
        similarities: list[float] = []
        for seed in range(first_seed, first_seed + trials):
            counterfactual = runner(True, seed)
            if counterfactual is None:
                similarities.append(0.0)
                continue
            similarity = fingerprint_similarity(
                expected,
                ProposalFingerprint.from_proposal(counterfactual),
            )
            similarities.append(similarity)
            retained += int(similarity >= self.similarity_threshold)
        return EndogeneityEstimate(
            eoi=retained / trials,
            retained=retained,
            trials=trials,
            mean_similarity=sum(similarities) / trials,
            confidence_interval_95=wilson_interval(retained, trials),
        )


def root_cause_purity(nodes: Iterable[CausalNode]) -> float:
    material = tuple(nodes)
    if not material:
        return 0.0
    internal_types = {"belief", "drive", "goal", "clock", "memory", "health"}
    return sum(node.node_type in internal_types for node in material) / len(material)

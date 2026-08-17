"""BeliefField — typed belief graph with field-gradient drives.

Antigravity note (NAMM-aligned):
  LLM embedding similarity collapses diverse structural tensions onto a median
  plateau M_0 — "anthropic cognition." BeliefField computes drives from graph
  topology (entropy gradients, inconsistency energy, commitment debt) in a
  machine-native coordinate system. Like NAMM's K_A/K_H asymmetry (machine
  certificate << human explanation), our drive vector lives in structural space
  orthogonal to token embeddings — no cosine-to-median, no mood sampling.
"""

from __future__ import annotations

import math
from datetime import datetime, timezone

from pydantic import BaseModel, Field

from eia.schemas.belief import Belief, BeliefKind, BeliefUpdate


def shannon_entropy(distribution: dict[str, float]) -> float:
    """Normalized Shannon entropy H in [0, 1] for categorical beliefs."""
    if not distribution:
        return 1.0
    total = sum(distribution.values())
    if total <= 0:
        return 1.0
    probs = [v / total for v in distribution.values() if v > 0]
    if len(probs) <= 1:
        return 0.0
    h = -sum(p * math.log2(p) for p in probs)
    max_h = math.log2(len(probs))
    return h / max_h if max_h > 0 else 0.0


class BeliefField(BaseModel):
    """Typed belief graph — substrate for deterministic drive computation."""

    beliefs: dict[str, Belief] = Field(default_factory=dict)
    contradictions: list[tuple[str, str, str]] = Field(default_factory=list)
    updates: list[BeliefUpdate] = Field(default_factory=list)

    def add_belief(self, belief: Belief) -> None:
        self.beliefs[belief.id] = belief

    def upsert_belief(
        self,
        belief_id: str,
        *,
        kind: BeliefKind,
        subject: str,
        claim: str,
        distribution: dict[str, float] | None = None,
        uncertainty: float = 0.5,
        source_observation_id: str | None = None,
        metadata: dict | None = None,
    ) -> Belief:
        now = datetime.now(timezone.utc)
        if belief_id in self.beliefs:
            existing = self.beliefs[belief_id]
            old_entropy = shannon_entropy(existing.distribution)
            new_dist = distribution if distribution is not None else existing.distribution
            new_entropy = shannon_entropy(new_dist)
            existing.distribution = new_dist
            existing.uncertainty = uncertainty
            existing.claim = claim
            existing.updated_at = now
            if metadata:
                existing.metadata.update(metadata)
            self.updates.append(
                BeliefUpdate(
                    id=f"upd-{belief_id}-{len(self.updates)}",
                    timestamp=now,
                    belief_id=belief_id,
                    delta_entropy=new_entropy - old_entropy,
                    reason=f"Updated from observation {source_observation_id}",
                    parent_observation_id=source_observation_id,
                )
            )
            return existing

        belief = Belief(
            id=belief_id,
            kind=kind,
            subject=subject,
            claim=claim,
            distribution=distribution or {},
            uncertainty=uncertainty,
            source_observation_id=source_observation_id,
            created_at=now,
            updated_at=now,
            metadata=metadata or {},
        )
        self.beliefs[belief_id] = belief
        self.updates.append(
            BeliefUpdate(
                id=f"upd-{belief_id}-init",
                timestamp=now,
                belief_id=belief_id,
                delta_entropy=shannon_entropy(belief.distribution),
                reason="Initial belief",
                parent_observation_id=source_observation_id,
            )
        )
        return belief

    def register_contradiction(self, belief_a: str, belief_b: str, topic: str) -> None:
        pair = (belief_a, belief_b, topic)
        if pair not in self.contradictions:
            self.contradictions.append(pair)

    def field_entropy(self) -> float:
        """Aggregate epistemic tension — mean normalized entropy."""
        if not self.beliefs:
            return 0.0
        entropies = [
            shannon_entropy(b.distribution) if b.kind == BeliefKind.CATEGORICAL else b.uncertainty
            for b in self.beliefs.values()
        ]
        return sum(entropies) / len(entropies)

    def inconsistency_energy(self) -> float:
        """Coherence tension — contradiction count normalized."""
        if not self.beliefs:
            return 0.0
        return min(1.0, len(self.contradictions) / max(1, len(self.beliefs)))

    def commitment_debt(self) -> float:
        """Prospective memory tension — open commitments weighted by age."""
        debts: list[float] = []
        for b in self.beliefs.values():
            if b.kind == BeliefKind.COMMITMENT:
                urgency = b.metadata.get("urgency", 0.5)
                open_flag = b.metadata.get("status", "open") == "open"
                if open_flag:
                    debts.append(float(urgency) * b.uncertainty)
        return sum(debts) / len(debts) if debts else 0.0

    def gradient_snapshot(self) -> dict[str, float]:
        """Field gradients — machine-native drive inputs (not embeddings)."""
        return {
            "epistemic": self.field_entropy(),
            "coherence": self.inconsistency_energy(),
            "commitment": self.commitment_debt(),
        }

    def beliefs_by_subject(self, subject: str) -> list[Belief]:
        return [b for b in self.beliefs.values() if b.subject == subject]

    def highest_entropy_beliefs(self, n: int = 3) -> list[Belief]:
        scored = [
            (shannon_entropy(b.distribution) if b.kind == BeliefKind.CATEGORICAL else b.uncertainty, b)
            for b in self.beliefs.values()
        ]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [b for _, b in scored[:n]]

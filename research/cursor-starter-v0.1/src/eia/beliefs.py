"""Probabilistic belief state with provenance-preserving updates."""

from __future__ import annotations

from datetime import datetime

from .math_model import bayes_binary, binary_entropy, clamp01
from .models import Belief, Observation


class BeliefState:
    def __init__(self) -> None:
        self._beliefs: dict[str, Belief] = {}

    def get(self, key: str, default_probability: float = 0.5) -> Belief:
        belief = self._beliefs.get(key)
        if belief is not None:
            return belief
        return Belief(key=key, probability=default_probability, confidence=0.0)

    def set(self, belief: Belief) -> None:
        belief.probability = clamp01(belief.probability)
        belief.confidence = clamp01(belief.confidence)
        self._beliefs[belief.key] = belief

    def update_binary(
        self,
        key: str,
        observation: Observation,
        *,
        likelihood_if_true: float,
        likelihood_if_false: float,
    ) -> Belief:
        previous = self.get(key)
        posterior = bayes_binary(
            previous.probability,
            likelihood_if_true,
            likelihood_if_false,
        )
        evidence_weight = observation.reliability * observation.salience
        confidence = clamp01(previous.confidence + (1.0 - previous.confidence) * evidence_weight)
        updated = Belief(
            key=key,
            probability=posterior,
            confidence=confidence,
            evidence_count=previous.evidence_count + 1,
            updated_at=observation.observed_at,
            source_ids=(*previous.source_ids[-15:], observation.observation_id),
            privacy_class=observation.privacy_class,
        )
        self.set(updated)
        return updated

    def uncertainty(self, key: str) -> float:
        return binary_entropy(self.get(key).probability)

    def snapshot(self) -> dict[str, Belief]:
        return {
            key: Belief(
                key=value.key,
                probability=value.probability,
                confidence=value.confidence,
                evidence_count=value.evidence_count,
                updated_at=value.updated_at,
                source_ids=value.source_ids,
                privacy_class=value.privacy_class,
            )
            for key, value in self._beliefs.items()
        }

    @property
    def keys(self) -> tuple[str, ...]:
        return tuple(sorted(self._beliefs))


def age_seconds(now: datetime, belief: Belief) -> float:
    return max(0.0, (now - belief.updated_at).total_seconds())


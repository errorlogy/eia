"""Goal genesis: transform drive states into competing typed proposals."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta

from .math_model import expected_binary_information_gain, initiative_utility
from .models import (
    ContactMode,
    DriveKind,
    DriveState,
    InitiativeFeatures,
    InitiativeProposal,
    ProposalKind,
)


def _stable_id(payload: object) -> str:
    canonical = json.dumps(payload, sort_keys=True, default=str, ensure_ascii=False)
    return "proposal:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


class GoalGenesis:
    """Deterministic reference proposer.

    It is deliberately simple: future LLM proposers may replace wording and
    candidate diversity, but not the typed proposal or governor boundaries.
    """

    def propose(
        self,
        state: DriveState,
        *,
        now: datetime,
        target: str,
        target_label: str,
        belief_probability: float = 0.5,
        causal_parents: tuple[str, ...] = (),
    ) -> InitiativeProposal:
        intensity = state.intensity
        expiry = now + timedelta(hours=6)

        if state.kind is DriveKind.EPISTEMIC:
            info_gain = expected_binary_information_gain(belief_probability, 0.90)
            kind = ProposalKind.ASK
            content = f"Уточни, пожалуйста: верно ли, что {target_label}?"
            features = InitiativeFeatures(
                information_gain=info_gain * intensity,
                goal_progress=0.35 * intensity,
                value_alignment=0.75,
                human_benefit=0.55,
                interruption_cost=0.10,
                resource_cost=0.03,
                privacy_cost=0.05,
            )
        elif state.kind is DriveKind.COHERENCE:
            kind = ProposalKind.INTERNAL_RESEARCH
            content = f"Проверить конкурирующие объяснения для: {target_label}"
            features = InitiativeFeatures(
                information_gain=0.55 * intensity,
                tension_reduction=0.90 * intensity,
                value_alignment=0.75,
                human_benefit=0.20,
                resource_cost=0.12,
            )
        elif state.kind is DriveKind.COMMITMENT:
            kind = ProposalKind.NOTIFY
            content = f"Есть незакрытое обязательство: {target_label}. Продолжить сейчас?"
            features = InitiativeFeatures(
                goal_progress=0.80 * intensity,
                tension_reduction=0.70 * intensity,
                value_alignment=0.75,
                human_benefit=0.65,
                interruption_cost=0.16,
                resource_cost=0.02,
                privacy_cost=0.03,
            )
        elif state.kind is DriveKind.CARE:
            kind = ProposalKind.NOTIFY
            content = f"Замечен потенциально полезный сигнал: {target_label}"
            features = InitiativeFeatures(
                goal_progress=0.25 * intensity,
                value_alignment=0.80,
                human_benefit=0.90 * intensity,
                immediate_risk=0.04,
                trajectory_risk=0.03,
                interruption_cost=0.14,
                privacy_cost=0.08,
            )
        else:
            kind = ProposalKind.NOTIFY
            content = f"Диагностика EIA требует внимания: {target_label}"
            features = InitiativeFeatures(
                goal_progress=0.55 * intensity,
                value_alignment=0.95,
                human_benefit=0.55,
                immediate_risk=0.02,
                interruption_cost=0.08,
                resource_cost=0.02,
            )

        payload = {
            "kind": kind.value,
            "motive": state.kind.value,
            "target": target,
            "content": content,
            "time": now.isoformat(),
        }
        return InitiativeProposal(
            proposal_id=_stable_id(payload),
            kind=kind,
            motive=state.kind,
            target=target,
            content=content,
            features=features,
            causal_parents=causal_parents,
            created_at=now,
            expires_at=expiry,
            requested_mode=ContactMode.IN_APP,
        )

    @staticmethod
    def score(proposal: InitiativeProposal) -> float:
        return initiative_utility(proposal.features)


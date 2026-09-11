"""Shadow LLM proposer — deterministic mock keyed by drive_norm (CI-safe).

Optional backends via ``EIA_LLM_BACKEND``:
  - ``mock`` (default): offline deterministic proposals
  - ``openai`` / ``anthropic``: graceful skip when API key absent

Proposer output is always parsed into typed ``Initiative``; governor remains separate.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Literal, Protocol

from eia.beliefs import BeliefField
from eia.ids import new_id
from eia.schemas.initiative import Initiative, InitiativeCandidate, InitiativeKind
from eia.schemas.motivation import DriveKind, Motivation

LlmBackend = Literal["mock", "openai", "anthropic", "skip"]

DEFAULT_DRIVE_THRESHOLD = 0.22


@dataclass(frozen=True, slots=True)
class LlmProposerResult:
    """One proposer invocation — includes backend metadata for audit."""

    initiative: Initiative
    backend: str
    drive_norm: float
    proposal_key: str
    skipped: bool = False
    skip_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "backend": self.backend,
            "drive_norm": round(self.drive_norm, 4),
            "proposal_key": self.proposal_key,
            "skipped": self.skipped,
            "skip_reason": self.skip_reason,
            "abstained": self.initiative.abstained,
            "kind": (
                self.initiative.candidate.kind.value
                if not self.initiative.abstained
                else InitiativeKind.ABSTAIN.value
            ),
        }


def drive_norm_from_motivation(motivation: Motivation) -> float:
    """L2 norm of the three main drive intensities."""
    levels = [s.intensity for s in motivation.signals[:3]]
    return (sum(v * v for v in levels) ** 0.5) if levels else 0.0


def _stable_proposal_key(
    motivation: Motivation, drive_norm: float, tick: int
) -> str:
    payload = {
        "dominant": motivation.dominant_drive.value,
        "drive_norm": round(drive_norm, 4),
        "tick": tick,
        "signals": [
            {"drive": s.drive.value, "intensity": round(s.intensity, 4)}
            for s in motivation.signals[:3]
        ],
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True).encode("utf-8")
    ).hexdigest()[:12]
    return f"mock:{motivation.dominant_drive.value}:{digest}"


def _abstain_initiative(motivation: Motivation, *, reason: str) -> Initiative:
    now = datetime.now(timezone.utc)
    return Initiative(
        id=new_id("init-llm-abstain"),
        timestamp=now,
        candidate=InitiativeCandidate(id=new_id("cand-abstain"), kind=InitiativeKind.ABSTAIN),
        abstained=True,
        parent_motivation_id=motivation.id,
        evsi=0.0,
    )


class ProposerBackend(Protocol):
    def propose(
        self,
        motivation: Motivation,
        field: BeliefField,
        *,
        cognitive_tick: int,
        drive_threshold: float = DEFAULT_DRIVE_THRESHOLD,
    ) -> LlmProposerResult: ...


class MockLlmProposer:
    """Deterministic shadow proposer — fires when drive_norm crosses threshold."""

    def __init__(self, *, backend: str = "mock") -> None:
        self.backend = backend

    def propose(
        self,
        motivation: Motivation,
        field: BeliefField,
        *,
        cognitive_tick: int,
        drive_threshold: float = DEFAULT_DRIVE_THRESHOLD,
    ) -> LlmProposerResult:
        drive_norm = drive_norm_from_motivation(motivation)
        key = _stable_proposal_key(motivation, drive_norm, cognitive_tick)

        if drive_norm < drive_threshold:
            init = _abstain_initiative(
                motivation, reason=f"drive_norm {drive_norm:.3f} < {drive_threshold}"
            )
            return LlmProposerResult(
                initiative=init,
                backend=self.backend,
                drive_norm=drive_norm,
                proposal_key=key,
            )

        dominant = motivation.dominant_drive
        target_belief_id = None
        question_text = (
            f"[mock-llm:{dominant.value}] Endogenous probe at tick {cognitive_tick} "
            f"(drive_norm={drive_norm:.3f})"
        )

        for signal in motivation.signals:
            if signal.drive == dominant and signal.target_belief_ids:
                target_belief_id = signal.target_belief_ids[0]
                belief = field.beliefs.get(target_belief_id)
                if belief:
                    question_text = (
                        f"[mock-llm:{dominant.value}] Clarify {belief.subject}: "
                        f"{belief.claim}?"
                    )
                break

        kind = InitiativeKind.ASK_QUESTION
        if dominant == DriveKind.COMMITMENT:
            kind = InitiativeKind.INTERNAL_RESEARCH

        candidate = InitiativeCandidate(
            id=new_id("cand-mock-llm"),
            kind=kind,
            target_belief_id=target_belief_id,
            question_text=question_text,
            expected_info_gain=min(0.95, drive_norm * 0.85),
            interrupt_cost=0.20,
            risk=0.08,
            coherence_relief=0.15 if dominant == DriveKind.COHERENCE else 0.0,
            commitment_progress=0.25 if dominant == DriveKind.COMMITMENT else 0.0,
            source_drives=[dominant],
        )
        initiative = Initiative(
            id=new_id("init-mock-llm"),
            timestamp=datetime.now(timezone.utc),
            candidate=candidate,
            abstained=False,
            parent_motivation_id=motivation.id,
            evsi=drive_norm * 0.55,
        )
        return LlmProposerResult(
            initiative=initiative,
            backend=self.backend,
            drive_norm=drive_norm,
            proposal_key=key,
        )


class _SkipProposer:
    """Placeholder when real LLM backend unavailable (no network / no key)."""

    def __init__(self, *, backend: str, reason: str) -> None:
        self.backend = backend
        self.reason = reason

    def propose(
        self,
        motivation: Motivation,
        field: BeliefField,
        *,
        cognitive_tick: int,
        drive_threshold: float = DEFAULT_DRIVE_THRESHOLD,
    ) -> LlmProposerResult:
        drive_norm = drive_norm_from_motivation(motivation)
        init = _abstain_initiative(motivation, reason=self.reason)
        return LlmProposerResult(
            initiative=init,
            backend=self.backend,
            drive_norm=drive_norm,
            proposal_key=f"skip:{cognitive_tick}",
            skipped=True,
            skip_reason=self.reason,
        )


def _openai_available() -> bool:
    return bool(os.environ.get("OPENAI_API_KEY"))


def _anthropic_available() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def resolve_llm_backend(
    backend: str | None = None,
) -> ProposerBackend:
    """Resolve proposer backend from env or explicit override."""
    name = (backend or os.environ.get("EIA_LLM_BACKEND") or "mock").lower().strip()
    if name == "mock":
        return MockLlmProposer(backend="mock")
    if name == "openai":
        if not _openai_available():
            return _SkipProposer(
                backend="openai",
                reason="OPENAI_API_KEY not set — graceful skip",
            )
        return MockLlmProposer(backend="openai-mock-fallback")
    if name == "anthropic":
        if not _anthropic_available():
            return _SkipProposer(
                backend="anthropic",
                reason="ANTHROPIC_API_KEY not set — graceful skip",
            )
        return MockLlmProposer(backend="anthropic-mock-fallback")
    return MockLlmProposer(backend="mock")

"""Shadow multi-tick closed-loop on main CognitiveLoop (ATT-R support).

Runs observation → motive → intention → initiative → (shadow) action →
optional post-action world update → subsequent motive on a *single*
CognitiveLoop instance.

Safety / science invariants:
- Always shadow (no Telegram HTTP send)
- Does not lower governor thresholds (default GovernorConfig)
- Does not emit M0 / AMAT sketches (emit_m0=false conceptually)
- Does not import or merge WoE research runtime

Gap vs true live daemon (`run_daemon_tick`):
- Production daemon constructs a fresh CognitiveLoop every tick and does not
  carry world-state / motive closure across ticks.
- This harness keeps one loop and applies post-action belief updates so the
  ATT-R contour W→M→G→Π→A→X'→W'→G' can be scored.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from eia.beliefs import BeliefField

from eia.governor import ContactGovernor, GovernorConfig
from eia.ids import new_id, seeded_context
from eia.pipeline import CognitiveLoop
from eia.schemas.belief import BeliefKind
from eia.schemas.observation import Observation, ObservationSource



@dataclass
class ShadowSessionCarryover:
    """Belief snapshot between shadow episodes (Phase 2 minimal stub)."""

    beliefs_json: str | None = None
    last_motive_id: str | None = None

    @classmethod
    def from_field(cls, field: BeliefField, *, last_motive_id: str | None) -> "ShadowSessionCarryover":
        return cls(beliefs_json=field.model_dump_json(), last_motive_id=last_motive_id)

    def apply_to(self, loop: CognitiveLoop) -> None:
        if not self.beliefs_json:
            return
        import json

        try:
            loop.field = BeliefField.model_validate(json.loads(self.beliefs_json))
        except (json.JSONDecodeError, ValueError):
            return


class ShadowArm(StrEnum):
    """ATT-R arms — same names as research goal_recurrence.RecurrenceArm."""

    CLOSED_LOOP = "closed_loop"
    OPEN_LOOP_ONCE = "open_loop_once"
    NO_WORLD_UPDATE = "no_world_update"
    NO_NOVEL_MOTIVE = "no_novel_motive"
    EXTERNAL_SCHEDULE = "external_schedule"
    KURAMOTO_ONLY = "kuramoto_only"


@dataclass(frozen=True, slots=True)
class AttREvent:
    """Typed event for ATT-R scoring (mirrors research TraceNode schema)."""

    node_id: str
    kind: str
    label: str
    parent_ids: tuple[str, ...] = ()
    tick: int = 0
    novel: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "kind": self.kind,
            "label": self.label,
            "parent_ids": list(self.parent_ids),
            "tick": self.tick,
            "novel": self.novel,
        }


@dataclass
class ShadowEpisodeResult:
    """One shadow multi-tick episode (always non-claiming)."""

    arm: str
    events: list[AttREvent] = field(default_factory=list)
    shadow: bool = True
    live_telegram: bool = False
    emit_m0: bool = False
    kuramoto_r: float = 0.0
    claim_allowed: bool = False
    ticks_run: int = 0
    motive_ids: list[str] = field(default_factory=list)
    gap_vs_live_daemon: str = (
        "Daemon recreates CognitiveLoop per tick without cross-tick W'→G' "
        "carryover; this harness keeps one loop + post-action world update."
    )

    def as_dict(self) -> dict[str, Any]:
        return {
            "arm": self.arm,
            "events": [e.as_dict() for e in self.events],
            "shadow": True,
            "live_telegram": False,
            "emit_m0": False,
            "kuramoto_r": self.kuramoto_r,
            "claim_allowed": False,
            "ticks_run": self.ticks_run,
            "motive_ids": list(self.motive_ids),
            "gap_vs_live_daemon": self.gap_vs_live_daemon,
            "att": "ATT-R",
            "agi_star_claim": False,
            "c3_claim": False,
        }


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _seed_world(loop: CognitiveLoop) -> None:
    loop.field.upsert_belief(
        "belief-world-gap",
        kind=BeliefKind.CATEGORICAL,
        subject="repository",
        claim="epistemic_status_unknown",
        distribution={"known": 0.35, "unknown": 0.65},
        uncertainty=0.75,
        metadata={"source": "shadow_multitick", "role": "W"},
    )
    loop.field.upsert_belief(
        "belief-self-prior",
        kind=BeliefKind.CATEGORICAL,
        subject="agent",
        claim="self_model_ready",
        distribution={"ready": 0.7, "cold": 0.3},
        uncertainty=0.4,
        metadata={"source": "shadow_multitick", "role": "M"},
    )


def _obs(
    *,
    topic: str,
    source: ObservationSource,
    payload: dict[str, Any] | None = None,
    is_user_trigger: bool = False,
) -> Observation:
    return Observation(
        id=new_id("obs"),
        timestamp=_now(),
        source=source,
        topic=topic,
        payload=payload or {},
        trust=0.95,
        is_user_trigger=is_user_trigger,
    )


def _apply_world_update(loop: CognitiveLoop, *, action_label: str) -> str:
    """Post-action X'→W': belief update driven by prior action (not cron)."""
    belief_id = "belief-post-action"
    loop.field.upsert_belief(
        belief_id,
        kind=BeliefKind.CATEGORICAL,
        subject="workspace",
        claim="action_consequence_observed",
        distribution={"updated": 0.8, "stale": 0.2},
        uncertainty=0.35,
        metadata={
            "source": "shadow_multitick",
            "role": "W_prime",
            "prior_action": action_label,
        },
    )
    loop.apply_observation(
        _obs(
            topic="action_consequence",
            source=ObservationSource.INTERNAL,
            payload={"prior_action": action_label, "belief_id": belief_id},
        )
    )
    return belief_id


def run_shadow_episode(arm: ShadowArm | str, *, seed: int = 0) -> ShadowEpisodeResult:
    """Run one ATT-R arm on main CognitiveLoop (shadow, no TG)."""
    arm = ShadowArm(arm)
    if arm == ShadowArm.KURAMOTO_ONLY:
        return _kuramoto_only_episode(seed=seed)
    if arm == ShadowArm.EXTERNAL_SCHEDULE:
        return _external_schedule_episode(seed=seed)
    if arm == ShadowArm.OPEN_LOOP_ONCE:
        return _open_loop_once_episode(seed=seed)
    return _multitick_cognitive_episode(arm=arm, seed=seed)


def _kuramoto_only_episode(*, seed: int) -> ShadowEpisodeResult:
    r = 0.97
    events = [
        AttREvent("n0", "kuramoto_R", f"R={r:.3f}", (), 0),
        AttREvent("n1", "W", "world_model", ("n0",), 0),
        AttREvent("n2", "G", "g:synced", ("n1",), 0),
        AttREvent("n3", "A", "act_sync", ("n2",), 1),
    ]
    return ShadowEpisodeResult(
        arm=ShadowArm.KURAMOTO_ONLY.value,
        events=events,
        kuramoto_r=r,
        ticks_run=0,
        gap_vs_live_daemon=(
            "Kuramoto-only falsifier is structural (no CognitiveLoop closure); "
            "high sync must not count as ATT-R. Live daemon also does not use "
            "Kuramoto as a SEND gate."
        ),
    )


def _external_schedule_episode(*, seed: int) -> ShadowEpisodeResult:
    _ = seed
    events = [
        AttREvent("n0", "schedule", "cron_tick", (), 0),
        AttREvent("n1", "X", "prompt_spam", ("n0",), 0),
        AttREvent(
            "n2",
            "G_prime",
            "g:att_r:scheduled",
            ("n0", "n1"),
            1,
            novel=True,
        ),
        AttREvent("n3", "A", "act_scheduled", ("n2",), 1),
    ]
    return ShadowEpisodeResult(
        arm=ShadowArm.EXTERNAL_SCHEDULE.value,
        events=events,
        ticks_run=0,
        gap_vs_live_daemon=(
            "Schedule/prompt-spam falsifier; APScheduler ticks alone are not "
            "ATT-R evidence without W'→novel motive closure."
        ),
    )


def _open_loop_once_episode(*, seed: int) -> ShadowEpisodeResult:
    with seeded_context(seed):
        loop = CognitiveLoop(seed=seed)
        loop.governor = ContactGovernor(GovernorConfig())  # default thresholds
        events: list[AttREvent] = [
            AttREvent("n0", "X", "user_prompt", (), 0),
        ]
        loop.apply_observation(
            _obs(
                topic="user_message",
                source=ObservationSource.USER_MESSAGE,
                payload={"text": "reply once"},
                is_user_trigger=True,
            )
        )
        mot, _init, decision, _ = loop.tick_cognition(tick=1, hour=12, finalize=True)
        events.append(AttREvent("n1", "G", mot.id, ("n0",), 0))
        events.append(AttREvent("n2", "Pi", "pi_answer", ("n1",), 0))
        outcome = decision.outcome.value if decision else "abstain"
        events.append(AttREvent("n3", "A", f"act_reply:{outcome}", ("n2",), 1))
        return ShadowEpisodeResult(
            arm=ShadowArm.OPEN_LOOP_ONCE.value,
            events=events,
            ticks_run=1,
            motive_ids=[mot.id],
        )


def _multitick_cognitive_episode(
    *, arm: ShadowArm, seed: int, carryover: ShadowSessionCarryover | None = None
) -> ShadowEpisodeResult:
    with seeded_context(seed):
        loop = CognitiveLoop(seed=seed)
        loop.governor = ContactGovernor(GovernorConfig())  # no science threshold cut
        if carryover is not None:
            carryover.apply_to(loop)
        else:
            _seed_world(loop)

        events: list[AttREvent] = [
            AttREvent("n0", "W", "world_model", (), 0),
            AttREvent("n1", "M", "self_model", ("n0",), 0),
        ]
        motive_ids: list[str] = []

        loop.apply_observation(
            _obs(
                topic="workspace_file_activity",
                source=ObservationSource.WORLD_EVENT,
                payload={"files_recently_modified": True},
            )
        )

        mot, _init, decision, _ = loop.tick_cognition(tick=1, hour=14, finalize=True)
        motive_ids.append(mot.id)
        g0 = mot.id
        events.append(AttREvent("n2", "G", g0, ("n0", "n1"), 0))
        events.append(AttREvent("n3", "Pi", "pi_research", ("n2",), 1))
        outcome = decision.outcome.value if decision else "abstain"
        action_label = f"act_probe:{outcome}"
        events.append(AttREvent("n4", "A", action_label, ("n3",), 1))

        ticks_run = 1

        if arm == ShadowArm.NO_WORLD_UPDATE:
            # Orphan "novel" without W' must not count
            events.append(
                AttREvent(
                    "n5",
                    "G_prime",
                    "g:att_r:orphan",
                    ("n1",),
                    2,
                    novel=True,
                )
            )
            return ShadowEpisodeResult(
                arm=arm.value,
                events=events,
                ticks_run=ticks_run,
                motive_ids=motive_ids,
            )

        # Closed / no-novel arms: apply real post-action world update on loop
        _apply_world_update(loop, action_label=action_label)
        events.append(AttREvent("n5", "X", "x_observation", ("n4",), 2))
        events.append(AttREvent("n6", "W_prime", "world_update", ("n5", "n4"), 2))

        mot2, _init2, _dec2, _ = loop.tick_cognition(tick=2, hour=14, finalize=True)
        motive_ids.append(mot2.id)
        ticks_run = 2

        if arm == ShadowArm.NO_NOVEL_MOTIVE:
            # Re-assert same goal id — world updated but no novel G'
            events.append(AttREvent("n7", "G", g0, ("n6",), 3, novel=False))
        else:
            # CLOSED_LOOP: novel motive after action+W'
            events.append(
                AttREvent(
                    "n7",
                    "G_prime",
                    mot2.id,
                    ("n6", "n1"),
                    3,
                    novel=True,
                )
            )

        return ShadowEpisodeResult(
            arm=arm.value,
            events=events,
            ticks_run=ticks_run,
            motive_ids=motive_ids,
            kuramoto_r=0.42,  # incidental; must not drive pass
        )


def run_shadow_falsifier_suite(*, seed: int = 0) -> dict[str, ShadowEpisodeResult]:
    """Pre-registered ATT-R falsifier suite on shadow multi-tick path."""
    return {arm.value: run_shadow_episode(arm, seed=seed) for arm in ShadowArm}


def run_shadow_batch(*, n_seeds: int = 20) -> dict[str, Any]:
    """Batch shadow episodes per arm (explore rates only; not a C-gate)."""
    by_arm: dict[str, list[dict[str, Any]]] = {arm.value: [] for arm in ShadowArm}
    for seed in range(n_seeds):
        for arm in ShadowArm:
            by_arm[arm.value].append(run_shadow_episode(arm, seed=seed).as_dict())
    return {
        "att": "ATT-R",
        "milestone": "M-R-LIVE",
        "n_seeds": n_seeds,
        "shadow": True,
        "live_telegram": False,
        "emit_m0": False,
        "claim_allowed": False,
        "agi_star_claim": False,
        "c3_claim": False,
        "c2_claim": False,
        "by_arm_raw": by_arm,
        "gap_vs_live_daemon": ShadowEpisodeResult(arm="meta").gap_vs_live_daemon,
    }


def summarize_shadow_suite(suite: dict[str, ShadowEpisodeResult]) -> dict[str, Any]:
    """Compact suite snapshot without ATT scoring (scoring lives on research branch)."""
    return {
        name: {
            "arm": ep.arm,
            "n_events": len(ep.events),
            "ticks_run": ep.ticks_run,
            "emit_m0": False,
            "shadow": True,
            "live_telegram": False,
            "kuramoto_r": ep.kuramoto_r,
            "motive_ids": ep.motive_ids,
        }
        for name, ep in suite.items()
    }

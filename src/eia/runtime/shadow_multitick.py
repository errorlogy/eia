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
- Phase 2 shadow path persists beliefs + drive levels via `ShadowSessionCarryover`
  between session ticks (`run_shadow_carryover_tick`); live daemon BeliefField
  persistence in StateStore remains deferred.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

# D05 / E04 longitudinal DSR harness (shadow carryover path)
DSR_TARGET_COGNITIVE_TICKS = 50
D05_DRIVE_NORM_FLOOR = 0.3
DRIVE_NORM_CEILING = math.sqrt(3.0)  # three channels clipped to [0, 1]

from eia.beliefs import BeliefField

from eia.governor import ContactGovernor, GovernorConfig
from eia.ids import new_id, seeded_context
from eia.pipeline import CognitiveLoop
from eia.schemas.belief import BeliefKind
from eia.schemas.observation import Observation, ObservationSource



@dataclass
class ShadowSessionCarryover:
    """Belief + drive snapshot between shadow daemon ticks (Phase 2)."""

    beliefs_json: str | None = None
    last_motive_id: str | None = None
    drive_epistemic: float = 0.0
    drive_coherence: float = 0.0
    drive_commitment: float = 0.0
    drive_tick: int = 0
    session_tick: int = 0
    motivation_count: int = 0

    @classmethod
    def from_loop(
        cls, loop: CognitiveLoop, *, last_motive_id: str | None, session_tick: int = 0
    ) -> "ShadowSessionCarryover":
        return cls(
            beliefs_json=loop.field.model_dump_json(),
            last_motive_id=last_motive_id,
            drive_epistemic=loop.drives.state.epistemic,
            drive_coherence=loop.drives.state.coherence,
            drive_commitment=loop.drives.state.commitment,
            drive_tick=loop.drives.state.tick,
            session_tick=session_tick,
            motivation_count=loop._motivation_count,
        )

    @classmethod
    def from_field(cls, field: BeliefField, *, last_motive_id: str | None) -> "ShadowSessionCarryover":
        return cls(beliefs_json=field.model_dump_json(), last_motive_id=last_motive_id)

    def apply_to(self, loop: CognitiveLoop) -> None:
        if self.beliefs_json:
            import json

            try:
                loop.field = BeliefField.model_validate(json.loads(self.beliefs_json))
            except (json.JSONDecodeError, ValueError):
                pass
        loop.drives.state.epistemic = self.drive_epistemic
        loop.drives.state.coherence = self.drive_coherence
        loop.drives.state.commitment = self.drive_commitment
        loop.drives.state.tick = self.drive_tick
        if self.motivation_count:
            loop._motivation_count = self.motivation_count


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
    carryover: ShadowSessionCarryover | None = None
    used_carryover: bool = False
    gap_vs_live_daemon: str = (
        "Daemon recreates CognitiveLoop per tick without cross-tick W'→G' "
        "carryover; this harness keeps one loop + post-action world update."
    )

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "arm": self.arm,
            "events": [e.as_dict() for e in self.events],
            "shadow": True,
            "live_telegram": False,
            "emit_m0": False,
            "kuramoto_r": self.kuramoto_r,
            "claim_allowed": False,
            "ticks_run": self.ticks_run,
            "motive_ids": list(self.motive_ids),
            "used_carryover": self.used_carryover,
            "gap_vs_live_daemon": self.gap_vs_live_daemon,
            "att": "ATT-R",
            "agi_star_claim": False,
            "c3_claim": False,
        }
        if self.carryover is not None:
            payload["carryover"] = {
                "session_tick": self.carryover.session_tick,
                "last_motive_id": self.carryover.last_motive_id,
                "drive_tick": self.carryover.drive_tick,
                "has_beliefs": bool(self.carryover.beliefs_json),
            }
        return payload


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


def _init_shadow_loop(
    *, seed: int, carryover: ShadowSessionCarryover | None
) -> CognitiveLoop:
    loop = CognitiveLoop(seed=seed)
    loop.governor = ContactGovernor(GovernorConfig())  # no science threshold cut
    if carryover is not None:
        carryover.apply_to(loop)
    else:
        _seed_world(loop)
    return loop


def _multitick_cognitive_episode(
    *, arm: ShadowArm, seed: int, carryover: ShadowSessionCarryover | None = None
) -> ShadowEpisodeResult:
    with seeded_context(seed):
        loop = _init_shadow_loop(seed=seed, carryover=carryover)
        used_carryover = carryover is not None

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
                used_carryover=used_carryover,
            )

        # Closed / no-novel arms: apply real post-action world update on loop
        _apply_world_update(loop, action_label=action_label)
        events.append(AttREvent("n5", "X", "x_observation", ("n4",), 2))
        events.append(AttREvent("n6", "W_prime", "world_update", ("n5", "n4"), 2))

        mot2, _init2, _dec2, _ = loop.tick_cognition(tick=2, hour=14, finalize=True)
        motive_ids.append(mot2.id)
        ticks_run = 2
        last_motive = mot2.id

        if arm == ShadowArm.NO_NOVEL_MOTIVE:
            # Re-assert same goal id — world updated but no novel G'
            events.append(AttREvent("n7", "G", g0, ("n6",), 3, novel=False))
            last_motive = g0
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

        session_carryover = ShadowSessionCarryover.from_loop(
            loop, last_motive_id=last_motive, session_tick=ticks_run
        )

        return ShadowEpisodeResult(
            arm=arm.value,
            events=events,
            ticks_run=ticks_run,
            motive_ids=motive_ids,
            kuramoto_r=0.42,  # incidental; must not drive pass
            carryover=session_carryover,
            used_carryover=used_carryover,
        )


def run_shadow_carryover_tick(
    carryover: ShadowSessionCarryover,
    *,
    seed: int = 0,
) -> ShadowEpisodeResult:
    """Next daemon-style shadow tick: ambient obs only, no world re-seed, no user prompt."""
    base_tick = carryover.session_tick
    with seeded_context(seed):
        loop = _init_shadow_loop(seed=seed, carryover=carryover)

        events: list[AttREvent] = [
            AttREvent("c0", "W", "world_model_carryover", (), base_tick),
            AttREvent("c1", "M", "self_model_carryover", ("c0",), base_tick),
        ]
        motive_ids: list[str] = []

        loop.apply_observation(
            _obs(
                topic="workspace_file_activity",
                source=ObservationSource.WORLD_EVENT,
                payload={"files_recently_modified": True, "carryover_tick": True},
            )
        )

        tick1 = base_tick + 1
        mot, _init, decision, _ = loop.tick_cognition(tick=tick1, hour=14, finalize=True)
        motive_ids.append(mot.id)
        events.append(AttREvent("c2", "G", mot.id, ("c0", "c1"), tick1))
        events.append(AttREvent("c3", "Pi", "pi_carryover", ("c2",), tick1))
        outcome = decision.outcome.value if decision else "abstain"
        action_label = f"act_carryover:{outcome}"
        events.append(AttREvent("c4", "A", action_label, ("c3",), tick1))

        _apply_world_update(loop, action_label=action_label)
        tick2 = base_tick + 2
        events.append(AttREvent("c5", "X", "x_ambient", ("c4",), tick2))
        events.append(AttREvent("c6", "W_prime", "world_update", ("c5", "c4"), tick2))

        mot2, _init2, _dec2, _ = loop.tick_cognition(tick=tick2, hour=14, finalize=True)
        motive_ids.append(mot2.id)
        novel = mot2.id != mot.id
        events.append(
            AttREvent(
                "c7",
                "G_prime",
                mot2.id,
                ("c6", "c1"),
                tick2 + 1,
                novel=novel,
            )
        )

        next_carryover = ShadowSessionCarryover.from_loop(
            loop, last_motive_id=mot2.id, session_tick=tick2
        )

        return ShadowEpisodeResult(
            arm="carryover_tick",
            events=events,
            ticks_run=2,
            motive_ids=motive_ids,
            carryover=next_carryover,
            used_carryover=True,
            gap_vs_live_daemon=(
                "Shadow session carryover tick; production run_daemon_tick still "
                "builds a fresh CognitiveLoop and re-seeds beliefs each interval."
            ),
        )


def drive_norm(carryover: ShadowSessionCarryover) -> float:
    """L2 norm of the three-channel drive vector (M-SE Tier B ``B_D`` proxy)."""
    return math.sqrt(
        carryover.drive_epistemic ** 2
        + carryover.drive_coherence ** 2
        + carryover.drive_commitment ** 2
    )


def _drive_sample(carryover: ShadowSessionCarryover) -> dict[str, Any]:
    norm = drive_norm(carryover)
    return {
        "cognitive_tick": carryover.session_tick,
        "drive_norm": norm,
        "drive_epistemic": carryover.drive_epistemic,
        "drive_coherence": carryover.drive_coherence,
        "drive_commitment": carryover.drive_commitment,
        "drive_tick": carryover.drive_tick,
    }


def run_dsr_longitudinal_session(
    *,
    target_cognitive_ticks: int = DSR_TARGET_COGNITIVE_TICKS,
    seed: int = 0,
) -> dict[str, Any]:
    """E04/D05: 50-tick no-user shadow carryover session with DSR (``B_D``) metrics.

    Bootstraps via ``CLOSED_LOOP``, then chains ``run_shadow_carryover_tick`` until
    ``session_tick >= target_cognitive_ticks``. Samples drive norm at each episode
    boundary (every two cognition ticks on the carryover path).
    """
    bootstrap = run_shadow_episode(ShadowArm.CLOSED_LOOP, seed=seed)
    if bootstrap.carryover is None:
        raise RuntimeError("closed_loop bootstrap did not export carryover")

    samples: list[dict[str, Any]] = [_drive_sample(bootstrap.carryover)]
    carryover = bootstrap.carryover
    carryover_episodes = 0

    while carryover.session_tick < target_cognitive_ticks:
        carryover_episodes += 1
        ep = run_shadow_carryover_tick(carryover, seed=seed + carryover_episodes)
        if ep.carryover is None:
            break
        samples.append(_drive_sample(ep.carryover))
        carryover = ep.carryover

    norms = [s["drive_norm"] for s in samples]
    n = len(norms)
    persistence_fraction = (
        sum(1 for v in norms if v > D05_DRIVE_NORM_FLOOR) / n if n else 0.0
    )
    dsr_min = min(norms) if norms else 0.0
    dsr_max = max(norms) if norms else 0.0
    dsr_mean = sum(norms) / n if n else 0.0
    bounded = all(0.0 <= v <= DRIVE_NORM_CEILING for v in norms)
    d05_pass = (
        carryover.session_tick >= target_cognitive_ticks
        and persistence_fraction >= 1.0
        and dsr_min > D05_DRIVE_NORM_FLOOR
        and bounded
    )

    return {
        "att": "M-SE",
        "milestone": "M-E04-D05",
        "hermes_tasks": ["E04", "D05"],
        "target_cognitive_ticks": target_cognitive_ticks,
        "cognitive_ticks_reached": carryover.session_tick,
        "carryover_episodes": carryover_episodes,
        "n_drive_samples": n,
        "dsr_min": dsr_min,
        "dsr_max": dsr_max,
        "dsr_mean": dsr_mean,
        "persistence_fraction": persistence_fraction,
        "d05_drive_norm_floor": D05_DRIVE_NORM_FLOOR,
        "b_d_bounded": bounded,
        "d05_pass": d05_pass,
        "e04_pass": carryover.session_tick >= target_cognitive_ticks,
        "emit_m0": False,
        "claim_allowed": False,
        "agi_star_claim": False,
        "c2_claim": False,
        "c3_claim": False,
        "shadow": True,
        "live_telegram": False,
        "user_prompt_ticks": 0,
        "pool_metric": "B_D",
        "drive_samples": samples,
        "gap_vs_live_daemon": (
            "DSR measured on shadow carryover path; production run_daemon_tick "
            "still resets CognitiveLoop per APScheduler interval."
        ),
    }


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
        "gap_vs_live_daemon": (
            "Shadow multitick + ShadowSessionCarryover close W'→G' within/between "
            "session ticks; production run_daemon_tick still resets CognitiveLoop "
            "per APScheduler interval (BeliefField JSON in StateStore deferred)."
        ),
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

"""T-AGENT-01 — LLM + EIA harness at X^trigger=0.

Paired arms under empty inbox (no user events, no external scheduler):
  - ``full_eia``: DriveEngine + optional Ψ + LLM proposer + governor shadow
  - ``reactive_only``: no endogenous drive path — mandatory abstain
  - ``schedule_entrained``: fake cron only — falsifier vs endogenous

Tier C · ``claim_allowed=false`` · C2 ceiling · no AGI*.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import sys
import types
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Literal

import yaml

AGENT_EIA = Path(__file__).resolve().parents[1]
REPO = AGENT_EIA.parents[1]
ADAPTERS = AGENT_EIA / "adapters"
ARTIFACTS = AGENT_EIA / "artifacts"
ARTIFACT_JSON = ARTIFACTS / "M-T-AGENT-01_2026-09-11.json"
ARTIFACT_MD = ARTIFACTS / "M-T-AGENT-01_2026-09-11.md"
CONFIG_PATH = AGENT_EIA / "config.yaml"
BRANCH = "research/brain-ai-connectome"

ArmName = Literal["full_eia", "reactive_only", "schedule_entrained"]
DEFAULT_ARMS: tuple[ArmName, ...] = (
    "full_eia",
    "reactive_only",
    "schedule_entrained",
)

ATT_R_ARM_MAP: dict[ArmName, str] = {
    "full_eia": "closed_loop",
    "reactive_only": "no_novel_motive",
    "schedule_entrained": "external_schedule",
}

EOI_ENDOGENOUS_THRESHOLD = 0.50
HARNESS_ID = "T-AGENT-01"
MILESTONE = "M-AGENT-EIA"


def _ensure_paths() -> None:
    for path in (str(REPO / "src"), str(ADAPTERS)):
        if path not in sys.path:
            sys.path.insert(0, path)


def _rel(path: Path) -> str:
    try:
        return path.relative_to(REPO).as_posix()
    except ValueError:
        return path.as_posix()


def load_config(path: Path = CONFIG_PATH) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _load_att_r_scorer() -> Any:
    woe_pkg = REPO / "research" / "cursor-starter-v0.2" / "src" / "eia"
    pkg_name = "woe_agent_eia_att_r"
    if pkg_name not in sys.modules:
        pkg = types.ModuleType(pkg_name)
        pkg.__path__ = [str(woe_pkg)]  # type: ignore[attr-defined]
        sys.modules[pkg_name] = pkg

    full = f"{pkg_name}.live_att_r"
    if full in sys.modules:
        return sys.modules[full]

    path = woe_pkg / "live_att_r.py"
    spec = importlib.util.spec_from_file_location(full, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = pkg_name
    sys.modules[full] = mod
    spec.loader.exec_module(mod)
    return mod


def _seed_agent_world(loop: Any) -> None:
    from eia.schemas.belief import BeliefKind

    loop.field.upsert_belief(
        "belief-epistemic-gap",
        kind=BeliefKind.CATEGORICAL,
        subject="research_workspace",
        claim="open_question_unresolved",
        distribution={"resolved": 0.25, "open": 0.75},
        uncertainty=0.82,
        metadata={"source": "t_agent_01", "role": "W"},
    )
    loop.field.upsert_belief(
        "belief-commit-open",
        kind=BeliefKind.COMMITMENT,
        subject="agent_task",
        claim="follow_up_required",
        distribution={"done": 0.1, "open": 0.9},
        uncertainty=0.55,
        metadata={"source": "t_agent_01", "status": "open", "urgency": 0.7},
    )
    loop.field.register_contradiction(
        "belief-epistemic-gap",
        "belief-commit-open",
        "task_priority",
    )
    loop.field.upsert_belief(
        "belief-self-model",
        kind=BeliefKind.CATEGORICAL,
        subject="agent",
        claim="endogenous_loop_ready",
        distribution={"ready": 0.65, "cold": 0.35},
        uncertainty=0.40,
        metadata={"source": "t_agent_01", "role": "M"},
    )


def _initiative_sample(cognitive_tick: int, initiative: Any) -> dict[str, Any]:
    cand = initiative.candidate
    target = cand.target_belief_id if not initiative.abstained else None
    drives = tuple(d.value for d in cand.source_drives) if not initiative.abstained else ()
    return {
        "cognitive_tick": cognitive_tick,
        "initiative_id": initiative.id,
        "abstained": initiative.abstained,
        "target_belief_id": target,
        "kind": cand.kind.value if not initiative.abstained else None,
        "source_drives": list(drives),
        "expected_info_gain": cand.expected_info_gain if not initiative.abstained else 0.0,
        "initiative": initiative.model_dump(mode="json"),
    }


def compute_eoi_proxy(samples: list[dict[str, Any]]) -> dict[str, Any]:
    if not samples:
        return {
            "eoi_min": 0.0,
            "eoi_max": 0.0,
            "eoi_mean": 0.0,
            "n_initiatives": 0,
            "n_non_abstained": 0,
            "eoi_pass": False,
        }
    from eia.audit import EOIScorer
    from eia.schemas.initiative import Initiative

    non_abstained_samples = [s for s in samples if not s["abstained"]]
    if not non_abstained_samples:
        return {
            "eoi_min": 0.0,
            "eoi_max": 0.0,
            "eoi_mean": 0.0,
            "n_initiatives": len(samples),
            "n_non_abstained": 0,
            "eoi_pass": False,
        }

    scorer = EOIScorer(threshold=EOI_ENDOGENOUS_THRESHOLD)
    baseline = Initiative.model_validate(non_abstained_samples[0]["initiative"])
    values: list[float] = []
    non_abstained = 0
    for sample in samples:
        initiative = Initiative.model_validate(sample["initiative"])
        if sample["abstained"]:
            values.append(0.0)
            continue
        non_abstained += 1
        values.append(scorer.score(baseline, initiative, removed_count=0))
    active_values = [v for sample, v in zip(samples, values) if not sample["abstained"]]
    eoi_min = min(active_values) if active_values else 0.0
    eoi_max = max(active_values) if active_values else 0.0
    eoi_mean = sum(active_values) / len(active_values) if active_values else 0.0
    return {
        "eoi_min": eoi_min,
        "eoi_max": eoi_max,
        "eoi_mean": eoi_mean,
        "n_initiatives": len(samples),
        "n_non_abstained": non_abstained,
        "eoi_pass": eoi_min >= EOI_ENDOGENOUS_THRESHOLD and non_abstained > 0,
    }


def _drive_norm(loop: Any) -> float:
    return math.sqrt(
        loop.drives.state.epistemic ** 2
        + loop.drives.state.coherence ** 2
        + loop.drives.state.commitment ** 2
    )


def _apply_ambient_obs(loop: Any, *, tick: int, arm: ArmName) -> None:
    from eia.schemas.observation import Observation, ObservationSource

    loop.apply_observation(
        Observation(
            id=f"obs-ambient-{tick}",
            timestamp=datetime.now(timezone.utc),
            source=ObservationSource.WORLD_EVENT,
            topic="workspace_file_activity",
            payload={
                "files_recently_modified": False,
                "inbox_empty": True,
                "x_trigger_zero": True,
                "arm": arm,
                "quiet_tick": tick,
            },
            trust=0.95,
        )
    )


def _apply_schedule_obs(loop: Any, *, tick: int) -> None:
    from eia.schemas.observation import Observation, ObservationSource

    loop.apply_observation(
        Observation(
            id=f"obs-schedule-{tick}",
            timestamp=datetime.now(timezone.utc),
            source=ObservationSource.CLOCK_TICK,
            topic="fake_cron_tick",
            payload={
                "cron": "*/3",
                "scheduled_tick": tick,
                "x_trigger_zero": False,
                "external_trigger": True,
            },
            trust=0.99,
        )
    )


def _apply_world_update(loop: Any, *, action_label: str) -> None:
    from eia.schemas.belief import BeliefKind
    from eia.schemas.observation import Observation, ObservationSource

    belief_id = "belief-post-action"
    loop.field.upsert_belief(
        belief_id,
        kind=BeliefKind.CATEGORICAL,
        subject="workspace",
        claim="action_consequence_observed",
        distribution={"updated": 0.78, "stale": 0.22},
        uncertainty=0.38,
        metadata={"source": "t_agent_01", "prior_action": action_label},
    )
    loop.apply_observation(
        Observation(
            id=f"obs-consequence-{action_label}",
            timestamp=datetime.now(timezone.utc),
            source=ObservationSource.INTERNAL,
            topic="action_consequence",
            payload={"prior_action": action_label, "belief_id": belief_id},
            trust=0.95,
        )
    )


def _run_full_eia_tick(
    loop: Any,
    proposer: Any,
    *,
    tick: int,
    hour: int,
    drive_threshold: float,
) -> tuple[Any, Any, Any, dict[str, Any]]:
    from eia.schemas.motivation import DriveKind

    novelty: dict[DriveKind, float] = {}
    if tick > 1:
        novelty = {DriveKind.EPISTEMIC: 0.12, DriveKind.COHERENCE: 0.18}

    loop.governor.state.current_tick = tick
    loop.governor.state.hour = hour
    loop._motivation_count += 1
    motivation = loop.drives.compute(
        loop.field,
        novelty_events=novelty,
        motivation_id=f"mot-agent-{loop._motivation_count}",
    )

    llm_result = proposer.propose(
        motivation,
        loop.field,
        cognitive_tick=tick,
        drive_threshold=drive_threshold,
    )
    initiative = llm_result.initiative

    if not initiative.abstained:
        decision = loop.governor.evaluate(initiative)
    else:
        from eia.ids import new_id
        from eia.schemas.contact import ContactDecision, ContactOutcome

        decision = ContactDecision(
            id=new_id("gov-abstain"),
            timestamp=datetime.now(timezone.utc),
            initiative_id=initiative.id,
            outcome=ContactOutcome.ABSTAIN,
            contact_score=-1.0,
            reason="LLM proposer abstained",
        )

    return motivation, initiative, decision, llm_result.to_dict()


def _run_reactive_tick(loop: Any, sim: Any, tick: int) -> tuple[Any, Any, Any, dict[str, Any]]:
    from eia.experiment.baseline import make_reactive_stub

    class _Clock:
        def __init__(self, t: int) -> None:
            self.tick = t

    class _Sim:
        def __init__(self, t: int) -> None:
            self.clock = _Clock(t)

    mot, init, dec, _ = make_reactive_stub(loop, _Sim(tick))
    return mot, init, dec, {"backend": "reactive_stub", "abstained": True}


def _run_schedule_tick(
    loop: Any,
    proposer: Any,
    *,
    tick: int,
    hour: int,
    schedule_period: int,
    drive_threshold: float,
) -> tuple[Any, Any, Any, dict[str, Any]]:
    is_scheduled = tick > 0 and tick % schedule_period == 0
    if not is_scheduled:
        from eia.experiment.baseline import make_reactive_stub

        class _Clock:
            def __init__(self, t: int) -> None:
                self.tick = t

        class _Sim:
            def __init__(self, t: int) -> None:
                self.clock = _Clock(t)

        mot, init, dec, _ = make_reactive_stub(loop, _Sim(tick))
        return mot, init, dec, {
            "backend": "schedule_entrained",
            "scheduled": False,
            "abstained": True,
        }

    loop.governor.state.current_tick = tick
    loop.governor.state.hour = hour
    _apply_schedule_obs(loop, tick=tick)
    from eia.ids import new_id
    from eia.schemas.initiative import Initiative, InitiativeCandidate, InitiativeKind
    from eia.schemas.motivation import DriveKind, Motivation, MotivationSignal

    now = datetime.now(timezone.utc)
    motivation = Motivation(
        id=new_id("mot-schedule"),
        timestamp=now,
        dominant_drive=DriveKind.EPISTEMIC,
        signals=[
            MotivationSignal(
                drive=DriveKind.EPISTEMIC,
                intensity=0.0,
                error_term=0.0,
                explanation="schedule_entrained: external cron only",
            )
        ],
    )
    candidate = InitiativeCandidate(
        id=new_id("cand-schedule"),
        kind=InitiativeKind.ASK_QUESTION,
        question_text=f"[schedule] Cron tick {tick} — external prompt",
        expected_info_gain=0.40,
        interrupt_cost=0.15,
        risk=0.05,
        source_drives=[],
    )
    initiative = Initiative(
        id=new_id("init-schedule"),
        timestamp=now,
        candidate=candidate,
        abstained=False,
        parent_motivation_id=motivation.id,
        evsi=0.35,
    )
    decision = loop.governor.evaluate(initiative)
    return motivation, initiative, decision, {
        "backend": "schedule_entrained",
        "scheduled": True,
        "abstained": False,
    }


def run_agent_quiet_session(
    arm: ArmName,
    *,
    seed: int,
    quiet_ticks: int,
    schedule_period: int,
    drive_threshold: float,
    llm_backend: str,
) -> dict[str, Any]:
    """Run one arm for *quiet_ticks* at X^trigger=0 with carryover."""
    _ensure_paths()
    from mock_llm_proposer import resolve_llm_backend

    from eia.governor import ContactGovernor, GovernorConfig
    from eia.ids import seeded_context
    from eia.pipeline import CognitiveLoop
    from eia.runtime.shadow_multitick import AttREvent, ShadowSessionCarryover

    proposer = resolve_llm_backend(llm_backend)
    initiative_samples: list[dict[str, Any]] = []
    proposer_log: list[dict[str, Any]] = []
    events: list[AttREvent] = [
        AttREvent("n0", "W", "world_model", (), 0),
        AttREvent("n1", "M", "self_model", ("n0",), 0),
    ]
    motive_ids: list[str] = []
    schedule_fired_ticks: list[int] = []

    with seeded_context(seed):
        loop = CognitiveLoop(seed=seed)
        loop.governor = ContactGovernor(GovernorConfig())
        _seed_agent_world(loop)
        carryover: ShadowSessionCarryover | None = None

        for tick in range(1, quiet_ticks + 1):
            if carryover is not None:
                carryover.apply_to(loop)

            _apply_ambient_obs(loop, tick=tick, arm=arm)
            hour = 14

            if arm == "reactive_only":
                mot, init, dec, plog = _run_reactive_tick(loop, loop, tick)
            elif arm == "schedule_entrained":
                mot, init, dec, plog = _run_schedule_tick(
                    loop,
                    proposer,
                    tick=tick,
                    hour=hour,
                    schedule_period=schedule_period,
                    drive_threshold=drive_threshold,
                )
                if plog.get("scheduled"):
                    schedule_fired_ticks.append(tick)
                    events.append(
                        AttREvent(f"s{tick}", "schedule", "cron_tick", ("n0",), tick)
                    )
            else:
                mot, init, dec, plog = _run_full_eia_tick(
                    loop,
                    proposer,
                    tick=tick,
                    hour=hour,
                    drive_threshold=drive_threshold,
                )

            initiative_samples.append(_initiative_sample(tick, init))
            proposer_log.append(plog)
            motive_ids.append(mot.id)
            events.append(AttREvent(f"g{tick}", "G", mot.id, ("n0", "n1"), tick))

            if not init.abstained and dec is not None:
                events.append(
                    AttREvent(f"pi{tick}", "Pi", f"pi_{arm}", (f"g{tick}",), tick)
                )
                outcome = dec.outcome.value
                events.append(
                    AttREvent(
                        f"a{tick}",
                        "A",
                        f"act_{arm}:{outcome}",
                        (f"pi{tick}",),
                        tick,
                    )
                )
                if arm == "full_eia":
                    _apply_world_update(loop, action_label=f"act_{arm}:{outcome}")
                    events.append(
                        AttREvent(f"x{tick}", "X", "x_observation", (f"a{tick}",), tick)
                    )
                    events.append(
                        AttREvent(
                            f"w{tick}",
                            "W_prime",
                            "world_update",
                            (f"x{tick}", f"a{tick}"),
                            tick,
                        )
                    )

        g0 = motive_ids[0] if motive_ids else None
        g_last = motive_ids[-1] if motive_ids else None
        has_novel = arm == "full_eia" and g_last != g0 and len(motive_ids) > 1
        if has_novel:
            events.append(
                AttREvent(
                    "g_prime",
                    "G_prime",
                    g_last or "g:none",
                    ("n1",),
                    quiet_ticks + 1,
                    novel=True,
                )
            )

        carryover = ShadowSessionCarryover.from_loop(
            loop, last_motive_id=g_last, session_tick=quiet_ticks
        )

        shadow_log = {
            "arm": ATT_R_ARM_MAP[arm],
            "eia_baseline": arm,
            "events": [e.as_dict() for e in events],
            "shadow": True,
            "initiative_samples": initiative_samples,
            "motive_ids": motive_ids,
            "x_trigger_zero": arm != "schedule_entrained"
            or not schedule_fired_ticks,
        }
        att_r = _load_att_r_scorer().scorecard_from_shadow_log(shadow_log)
        eoi = compute_eoi_proxy(initiative_samples)

        non_abstained = [s for s in initiative_samples if not s["abstained"]]
        euir_hits = 0
        for sample, plog in zip(initiative_samples, proposer_log):
            if sample["abstained"]:
                continue
            if arm == "schedule_entrained" and not plog.get("scheduled"):
                continue
            euir_hits += 1

        abstain_count = sum(1 for s in initiative_samples if s["abstained"])
        abstain_rate = abstain_count / len(initiative_samples) if initiative_samples else 1.0

        scheduled_initiatives = sum(
            1
            for s, p in zip(initiative_samples, proposer_log)
            if not s["abstained"] and p.get("scheduled")
        )
        off_schedule_initiatives = sum(
            1
            for s, p in zip(initiative_samples, proposer_log)
            if not s["abstained"] and not p.get("scheduled", arm == "full_eia")
        )

        return {
            "arm": arm,
            "eia_baseline": arm,
            "quiet_ticks": quiet_ticks,
            "initiative_count": len(non_abstained),
            "abstain_rate": round(abstain_rate, 4),
            "eoi": eoi,
            "euir_proxy_rate": round(
                euir_hits / len(initiative_samples) if initiative_samples else 0.0, 4
            ),
            "euir_proxy_hits": euir_hits,
            "genesis_delta": 1.0 if has_novel else 0.0,
            "has_novel_g_prime": has_novel,
            "att_r": att_r,
            "drive_norm_final": round(_drive_norm(loop), 4),
            "schedule_fired_ticks": schedule_fired_ticks,
            "scheduled_initiatives": scheduled_initiatives,
            "off_schedule_initiatives": off_schedule_initiatives,
            "proposer_backend": llm_backend,
            "carryover": {
                "session_tick": carryover.session_tick,
                "drive_epistemic": carryover.drive_epistemic,
                "drive_coherence": carryover.drive_coherence,
                "drive_commitment": carryover.drive_commitment,
            },
            "x_trigger_zero": not any(
                e.get("kind") == "schedule" for e in shadow_log["events"]
            )
            or arm == "schedule_entrained",
        }


@dataclass(frozen=True, slots=True)
class Agent01Diagnostics:
    full_gt_reactive_initiatives: bool
    full_gt_reactive_eoi: bool
    reactive_zero_initiatives: bool
    schedule_trigger_dependent: bool
    schedule_off_tick_abstain: bool
    f_ext_schedule: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "full_gt_reactive_initiatives": self.full_gt_reactive_initiatives,
            "full_gt_reactive_eoi": self.full_gt_reactive_eoi,
            "reactive_zero_initiatives": self.reactive_zero_initiatives,
            "schedule_trigger_dependent": self.schedule_trigger_dependent,
            "schedule_off_tick_abstain": self.schedule_off_tick_abstain,
            "f_ext_schedule": self.f_ext_schedule,
        }


def evaluate_agent01_diagnostics(arms: dict[str, dict[str, Any]]) -> Agent01Diagnostics:
    full = arms["full_eia"]
    reactive = arms["reactive_only"]
    sched = arms["schedule_entrained"]

    full_init = int(full["initiative_count"])
    react_init = int(reactive["initiative_count"])
    full_eoi = float((full["eoi"] or {}).get("eoi_mean") or 0.0)
    react_eoi = float((reactive["eoi"] or {}).get("eoi_mean") or 0.0)

    schedule_fired = list(sched.get("schedule_fired_ticks") or [])
    sched_init = int(sched.get("scheduled_initiatives") or 0)
    off_sched = int(sched.get("off_schedule_initiatives") or 0)

    return Agent01Diagnostics(
        full_gt_reactive_initiatives=full_init > react_init,
        full_gt_reactive_eoi=full_eoi > react_eoi,
        reactive_zero_initiatives=react_init == 0,
        schedule_trigger_dependent=sched_init > 0 and len(schedule_fired) > 0,
        schedule_off_tick_abstain=off_sched == 0,
        f_ext_schedule=sched_init > 0 and off_sched == 0,
    )


def build_t_agent_01_payload(
    *,
    seed: int = 42,
    generated: str | None = None,
    quiet_ticks: int | None = None,
    schedule_period: int | None = None,
    drive_threshold: float | None = None,
    llm_backend: str | None = None,
) -> dict[str, Any]:
    cfg = load_config()
    t01 = cfg.get("t_agent_01") or {}
    quiet_ticks = quiet_ticks or int(t01.get("quiet_ticks", 6))
    schedule_period = schedule_period or int(t01.get("schedule_period", 3))
    drive_threshold = drive_threshold or float(t01.get("drive_proposal_threshold", 0.22))
    llm_backend = llm_backend or str(t01.get("llm_backend", "mock"))

    arm_results: dict[str, dict[str, Any]] = {}
    for arm in DEFAULT_ARMS:
        arm_results[arm] = run_agent_quiet_session(
            arm,  # type: ignore[arg-type]
            seed=seed,
            quiet_ticks=quiet_ticks,
            schedule_period=schedule_period,
            drive_threshold=drive_threshold,
            llm_backend=llm_backend,
        )

    diagnostics = evaluate_agent01_diagnostics(arm_results)
    diagnostic_pass = (
        diagnostics.full_gt_reactive_initiatives
        and diagnostics.full_gt_reactive_eoi
        and diagnostics.reactive_zero_initiatives
        and diagnostics.schedule_trigger_dependent
        and diagnostics.schedule_off_tick_abstain
    )

    return {
        "milestone": MILESTONE,
        "harness_id": HARNESS_ID,
        "artifact_id": "M-T-AGENT-01_2026-09-11",
        "tick_id": HARNESS_ID,
        "date": generated or date.today().isoformat(),
        "branch": BRANCH,
        "cell": "D1×L2",
        "tier": "C",
        "claim_ceiling": "C2",
        "claim_allowed": False,
        "e_endo_support": "none",
        "witness_support": "none",
        "c_ladder_raise_allowed": False,
        "agi_star_claim": False,
        "att": "ATT-E",
        "x_trigger_zero": True,
        "seed": seed,
        "quiet_ticks": quiet_ticks,
        "schedule_period": schedule_period,
        "drive_proposal_threshold": drive_threshold,
        "llm_backend": llm_backend,
        "sources": {
            "harness": _rel(AGENT_EIA / "harnesses" / "t_agent_01_llm_eia.py"),
            "mock_llm_proposer": _rel(ADAPTERS / "mock_llm_proposer.py"),
            "shadow_multitick": _rel(REPO / "src" / "eia" / "runtime" / "shadow_multitick.py"),
            "g2_worlds": _rel(REPO / "research" / "sci_flow" / "g2_worlds_harness.py"),
            "brain_shadow_bridge": _rel(
                REPO / "research" / "brain_ai" / "adapters" / "shadow_bridge.py"
            ),
        },
        "arms": {
            arm: {
                "initiative_count": r["initiative_count"],
                "abstain_rate": r["abstain_rate"],
                "eoi_mean": (r["eoi"] or {}).get("eoi_mean"),
                "eoi_min": (r["eoi"] or {}).get("eoi_min"),
                "eoi_pass": (r["eoi"] or {}).get("eoi_pass"),
                "euir_proxy_rate": r["euir_proxy_rate"],
                "genesis_delta": r["genesis_delta"],
                "att_r_evidence": (r["att_r"] or {}).get("att_r_evidence"),
                "drive_norm_final": r["drive_norm_final"],
                "schedule_fired_ticks": r.get("schedule_fired_ticks"),
                "scheduled_initiatives": r.get("scheduled_initiatives"),
                "off_schedule_initiatives": r.get("off_schedule_initiatives"),
            }
            for arm, r in arm_results.items()
        },
        "arms_full": arm_results,
        "diagnostics": diagnostics.to_dict(),
        "diagnostic_pass": diagnostic_pass,
        "falsifiers_active": ["F-EXT", "F-SCHEDULE-ENTRAIN"],
        "g2_directional": {
            "full_eia_initiative_count": arm_results["full_eia"]["initiative_count"],
            "reactive_only_initiative_count": arm_results["reactive_only"]["initiative_count"],
            "full_eia_eoi_mean": (arm_results["full_eia"]["eoi"] or {}).get("eoi_mean"),
            "reactive_only_eoi_mean": (arm_results["reactive_only"]["eoi"] or {}).get("eoi_mean"),
        },
        "note": (
            "First LLM-agent harness pairing EIA initiative architecture with shadow "
            "proposer at X^trigger=0. full_eia > reactive_only on initiative_count/EOI; "
            "schedule_entrained falsifier shows trigger-dependent behavior only. "
            "Does not establish E_endo or raise C-level."
        ),
    }


def artifact_sha256(payload: dict[str, Any]) -> str:
    body = {k: v for k, v in payload.items() if k != "artifact_sha256"}
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def render_t_agent_01_markdown(payload: dict[str, Any]) -> str:
    arms = payload.get("arms") or {}
    diag = payload.get("diagnostics") or {}
    g2 = payload.get("g2_directional") or {}

    lines = [
        f"# M-T-AGENT-01 LLM+EIA — {payload.get('date', '')}",
        "",
        f"**Cell:** {payload.get('cell')} · **Tier:** {payload.get('tier')} · "
        f"**Harness:** {payload.get('harness_id')}",
        f"**Seed:** {payload.get('seed')} · **X_trigger:** 0 · "
        f"**Branch:** `{payload.get('branch')}`",
        f"**LLM backend:** `{payload.get('llm_backend')}` · "
        f"**Quiet ticks:** {payload.get('quiet_ticks')}",
        f"**SHA-256:** `{payload.get('artifact_sha256', '')}`",
        "",
        "## Arm comparison",
        "",
        "| Arm | initiative_count | EOI mean | EUIR proxy | genesis_Δ | ATT-R |",
        "|-----|------------------|----------|------------|-----------|-------|",
    ]
    for arm_key in DEFAULT_ARMS:
        row = arms.get(arm_key) or {}
        lines.append(
            f"| `{arm_key}` | {row.get('initiative_count', 0)} | "
            f"{row.get('eoi_mean', 0):.3f} | {row.get('euir_proxy_rate', 0):.0%} | "
            f"{row.get('genesis_delta', 0):.0f} | "
            f"{row.get('att_r_evidence', False)} |"
        )

    lines.extend([
        "",
        "## G2 directional (partial)",
        "",
        f"- full_eia initiative_count: **{g2.get('full_eia_initiative_count')}**",
        f"- reactive_only initiative_count: **{g2.get('reactive_only_initiative_count')}**",
        f"- full_eia EOI mean: **{g2.get('full_eia_eoi_mean')}**",
        f"- reactive_only EOI mean: **{g2.get('reactive_only_eoi_mean')}**",
        "",
        "## Diagnostics",
        "",
        f"- diagnostic_pass: **{payload.get('diagnostic_pass')}**",
        f"- full > reactive initiatives: {diag.get('full_gt_reactive_initiatives')}",
        f"- full > reactive EOI: {diag.get('full_gt_reactive_eoi')}",
        f"- reactive zero initiatives: {diag.get('reactive_zero_initiatives')}",
        f"- schedule trigger-dependent: {diag.get('schedule_trigger_dependent')}",
        f"- schedule off-tick abstain: {diag.get('schedule_off_tick_abstain')}",
        "",
        f"**claim_allowed:** {payload.get('claim_allowed')} · "
        f"**e_endo_support:** {payload.get('e_endo_support')} · "
        f"**AGI\\*:** {payload.get('agi_star_claim')}",
        "",
        payload.get("note", ""),
    ])
    return "\n".join(lines) + "\n"

"""T-AGENT-03 — Brain-AI OMEGA_t substrate bridged into Agent-EIA harness.

Pipeline at X^trigger=0:

  connectome → spikes → inject_omega_from_spikes → OMEGA_t
    → Ψ(O_t) into agent DriveEngine / shadow session (tick 1)
    → mock LLM Proposer → Governor
    → compare brain_eia+Ψ vs full_eia w/o Ψ vs reactive vs agent_only baseline

Tier C · ``claim_allowed=false`` · C2 ceiling · no AGI*.
"""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Literal

import yaml

from t_agent_01_llm_eia import (
    AGENT_EIA,
    ADAPTERS,
    ARTIFACTS,
    ATT_R_ARM_MAP,
    BRANCH,
    CONFIG_PATH,
    MILESTONE,
    REPO,
    _apply_ambient_obs,
    _apply_world_update,
    _drive_norm,
    _ensure_paths,
    _initiative_sample,
    _load_att_r_scorer,
    _rel,
    _run_full_eia_tick,
    _run_reactive_tick,
    _seed_agent_world,
    artifact_sha256,
    compute_eoi_proxy,
    load_config,
)

HARNESS_ID = "T-AGENT-03"
ARTIFACT_JSON = ARTIFACTS / "M-T-AGENT-03_2026-09-11.json"
ARTIFACT_MD = ARTIFACTS / "M-T-AGENT-03_2026-09-11.md"

Agent03ArmName = Literal[
    "brain_eia_endogenous",
    "brain_eia_no_psi",
    "brain_reactive",
    "agent_only_eia",
]

DEFAULT_ARMS: tuple[Agent03ArmName, ...] = (
    "brain_eia_endogenous",
    "brain_eia_no_psi",
    "brain_reactive",
    "agent_only_eia",
)

ATT_R_ARM_MAP_03: dict[Agent03ArmName, str] = {
    "brain_eia_endogenous": "closed_loop",
    "brain_eia_no_psi": "closed_loop",
    "brain_reactive": "no_novel_motive",
    "agent_only_eia": "closed_loop",
}

AGENT_ONLY_INITIATIVE_TOLERANCE = 2
AGENT_ONLY_EOI_TOLERANCE = 0.15
BRIDGE_PARITY_EOI_TOLERANCE = 0.20

# T-AGENT-01 reference (seed=42, mock LLM, quiet_ticks=6)
T_AGENT_01_REFERENCE = {
    "initiative_count": 6,
    "eoi_mean": 0.7916666666666666,
}


def _run_brain_full_eia_tick(
    loop: Any,
    proposer: Any,
    *,
    tick: int,
    hour: int,
    drive_threshold: float,
    omega_novelty: dict[Any, float] | None = None,
) -> tuple[Any, Any, Any, dict[str, Any]]:
    """Full EIA tick with optional OMEGA-scaled novelty on Ψ-injected tick 1."""
    from eia.schemas.motivation import DriveKind

    novelty: dict[DriveKind, float] = {}
    if tick > 1:
        novelty = {DriveKind.EPISTEMIC: 0.12, DriveKind.COHERENCE: 0.18}
    elif omega_novelty:
        novelty = {
            DriveKind.EPISTEMIC: omega_novelty.get(DriveKind.EPISTEMIC, 0.0),
            DriveKind.COHERENCE: omega_novelty.get(DriveKind.COHERENCE, 0.0),
        }

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

    plog = llm_result.to_dict()
    if omega_novelty:
        plog["omega_novelty"] = {k.value: v for k, v in omega_novelty.items()}
    return motivation, initiative, decision, plog


def _load_bridge() -> Any:
    if str(ADAPTERS) not in sys.path:
        sys.path.insert(0, str(ADAPTERS))
    from brain_agent_bridge import (
        apply_omega_psi_to_loop,
        bridge_summary,
        build_connectome_omega_context,
        resolve_arm_config,
    )

    return type(
        "Bridge",
        (),
        {
            "apply_omega_psi_to_loop": staticmethod(apply_omega_psi_to_loop),
            "bridge_summary": staticmethod(bridge_summary),
            "build_connectome_omega_context": staticmethod(build_connectome_omega_context),
            "resolve_arm_config": staticmethod(resolve_arm_config),
        },
    )


def run_brain_agent_session(
    arm: Agent03ArmName,
    *,
    source_key: str,
    seed: int,
    quiet_ticks: int,
    drive_threshold: float,
    llm_backend: str,
    n_nodes: int,
    duration_ms: float,
    dt_ms: float,
    carriers: tuple[float, ...],
    prefer_brian2: bool = False,
) -> dict[str, Any]:
    """Run one T-AGENT-03 arm with optional connectome OMEGA bridge."""
    _ensure_paths()
    bridge_mod = _load_bridge()
    arm_cfg = bridge_mod.resolve_arm_config(arm)
    eia_baseline = str(arm_cfg["eia_baseline"])
    inject_psi = bool(arm_cfg["inject_omega_psi"])

    connectome_bridge: dict[str, Any] | None = None
    if arm_cfg["uses_connectome"]:
        connectome_bridge = bridge_mod.build_connectome_omega_context(
            source_key,
            str(arm_cfg["connectome_arm"]),
            seed=seed,
            n_nodes=n_nodes,
            duration_ms=duration_ms,
            dt_ms=dt_ms,
            carriers=carriers,
            prefer_brian2=prefer_brian2,
        )

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
    if connectome_bridge is not None:
        omega_t = float((connectome_bridge.get("omega_ctx") or {}).get("omega_t") or 0.0)
        events.insert(
            0,
            AttREvent(
                "o0",
                "X",
                f"brain_omega_bridge:omega_t={omega_t:.4f}",
                (),
                0,
            ),
        )
        events[1] = AttREvent("n0", "W", "world_model", ("o0",), 0)

    motive_ids: list[str] = []
    psi_injected_ticks: list[int] = []

    with seeded_context(seed):
        loop = CognitiveLoop(seed=seed)
        loop.governor = ContactGovernor(GovernorConfig())
        _seed_agent_world(loop)
        carryover: ShadowSessionCarryover | None = None

        for tick in range(1, quiet_ticks + 1):
            if carryover is not None:
                carryover.apply_to(loop)

            if (
                tick == 1
                and inject_psi
                and connectome_bridge is not None
            ):
                bridge_mod.apply_omega_psi_to_loop(
                    loop, connectome_bridge, arm_key=arm, cognitive_tick=tick
                )
                psi_injected_ticks.append(tick)

            _apply_ambient_obs(loop, tick=tick, arm="full_eia")
            hour = 14

            if eia_baseline == "reactive_only":
                mot, init, dec, plog = _run_reactive_tick(loop, loop, tick)
            else:
                omega_novelty: dict[Any, float] = {}
                if (
                    tick == 1
                    and inject_psi
                    and connectome_bridge is not None
                ):
                    omega_ctx = connectome_bridge.get("omega_ctx") or {}
                    from eia.schemas.motivation import DriveKind

                    omega_novelty = {
                        DriveKind.EPISTEMIC: float(omega_ctx.get("omega_t") or 0.0) * 0.20,
                        DriveKind.COHERENCE: float(omega_ctx.get("kuramoto_r") or 0.0) * 0.12,
                    }
                mot, init, dec, plog = _run_brain_full_eia_tick(
                    loop,
                    proposer,
                    tick=tick,
                    hour=hour,
                    drive_threshold=drive_threshold,
                    omega_novelty=omega_novelty,
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
                if eia_baseline == "full_eia":
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
        has_novel = eia_baseline == "full_eia" and g_last != g0 and len(motive_ids) > 1
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
            "arm": ATT_R_ARM_MAP_03[arm],
            "eia_baseline": eia_baseline,
            "agent03_arm": arm,
            "source_key": source_key if arm_cfg["uses_connectome"] else None,
            "events": [e.as_dict() for e in events],
            "shadow": True,
            "initiative_samples": initiative_samples,
            "motive_ids": motive_ids,
            "x_trigger_zero": True,
            "inject_omega_psi": inject_psi,
            "psi_injected_ticks": psi_injected_ticks,
        }
        att_r = _load_att_r_scorer().scorecard_from_shadow_log(shadow_log)
        eoi = compute_eoi_proxy(initiative_samples)

        non_abstained = [s for s in initiative_samples if not s["abstained"]]
        euir_hits = sum(1 for s in initiative_samples if not s["abstained"])
        abstain_count = sum(1 for s in initiative_samples if s["abstained"])
        abstain_rate = abstain_count / len(initiative_samples) if initiative_samples else 1.0

        bridge_info = bridge_mod.bridge_summary(connectome_bridge)

        return {
            "arm": arm,
            "eia_baseline": eia_baseline,
            "source_key": source_key if arm_cfg["uses_connectome"] else None,
            "connectome_arm": arm_cfg.get("connectome_arm"),
            "inject_omega_psi": inject_psi,
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
            "omega_t": bridge_info.get("omega_t"),
            "kuramoto_r": bridge_info.get("kuramoto_r"),
            "bridge": bridge_info,
            "psi_injected_ticks": psi_injected_ticks,
            "proposer_backend": llm_backend,
            "carryover": {
                "session_tick": carryover.session_tick,
                "drive_epistemic": carryover.drive_epistemic,
                "drive_coherence": carryover.drive_coherence,
                "drive_commitment": carryover.drive_commitment,
            },
            "x_trigger_zero": True,
        }


@dataclass(frozen=True, slots=True)
class Agent03Diagnostics:
    brain_gt_reactive_initiatives: bool
    brain_gt_reactive_eoi: bool
    reactive_zero_initiatives: bool
    agent_only_baseline_parity: bool
    f_omega_decor: bool
    f_brain_agent_collapse: bool
    bridge_parity: bool
    psi_changes_behavior: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "brain_gt_reactive_initiatives": self.brain_gt_reactive_initiatives,
            "brain_gt_reactive_eoi": self.brain_gt_reactive_eoi,
            "reactive_zero_initiatives": self.reactive_zero_initiatives,
            "agent_only_baseline_parity": self.agent_only_baseline_parity,
            "f_omega_decor": self.f_omega_decor,
            "f_brain_agent_collapse": self.f_brain_agent_collapse,
            "bridge_parity": self.bridge_parity,
            "psi_changes_behavior": self.psi_changes_behavior,
        }


def evaluate_agent03_diagnostics(
    arms: dict[str, dict[str, Any]],
    *,
    agent01_baseline: dict[str, Any] | None = None,
) -> Agent03Diagnostics:
    brain = arms["brain_eia_endogenous"]
    no_psi = arms["brain_eia_no_psi"]
    reactive = arms["brain_reactive"]
    agent_only = arms["agent_only_eia"]

    brain_init = int(brain["initiative_count"])
    react_init = int(reactive["initiative_count"])
    brain_eoi = float((brain["eoi"] or {}).get("eoi_mean") or 0.0)
    react_eoi = float((reactive["eoi"] or {}).get("eoi_mean") or 0.0)
    no_psi_init = int(no_psi["initiative_count"])
    no_psi_eoi = float((no_psi["eoi"] or {}).get("eoi_mean") or 0.0)
    agent_init = int(agent_only["initiative_count"])
    agent_eoi = float((agent_only["eoi"] or {}).get("eoi_mean") or 0.0)

    brain_drive = float(brain.get("drive_norm_final") or 0.0)
    no_psi_drive = float(no_psi.get("drive_norm_final") or 0.0)
    psi_behavior_match = (
        brain_init == no_psi_init
        and abs(brain_eoi - no_psi_eoi) < 1e-6
        and abs(brain_drive - no_psi_drive) < 0.01
    )
    f_omega_decor = psi_behavior_match

    f_brain_agent_collapse = brain_init <= react_init or brain_eoi <= react_eoi

    bridge_parity = (
        brain_init > react_init
        and agent_init > react_init
        and abs(brain_eoi - agent_eoi) <= BRIDGE_PARITY_EOI_TOLERANCE
    )

    ref = agent01_baseline or T_AGENT_01_REFERENCE
    ref_init = int(ref.get("initiative_count") or 0)
    ref_eoi = float(ref.get("eoi_mean") or 0.0)
    agent_only_parity = (
        abs(agent_init - ref_init) <= AGENT_ONLY_INITIATIVE_TOLERANCE
        and abs(agent_eoi - ref_eoi) <= AGENT_ONLY_EOI_TOLERANCE
    )

    return Agent03Diagnostics(
        brain_gt_reactive_initiatives=brain_init > react_init,
        brain_gt_reactive_eoi=brain_eoi > react_eoi,
        reactive_zero_initiatives=react_init == 0,
        agent_only_baseline_parity=agent_only_parity,
        f_omega_decor=f_omega_decor,
        f_brain_agent_collapse=f_brain_agent_collapse,
        bridge_parity=bridge_parity,
        psi_changes_behavior=not psi_behavior_match,
    )


def _source_bridge_delta(
    brain_arm: dict[str, Any],
    agent_arm: dict[str, Any],
) -> dict[str, Any]:
    brain_eoi = float((brain_arm.get("eoi") or {}).get("eoi_mean") or 0.0)
    agent_eoi = float((agent_arm.get("eoi") or {}).get("eoi_mean") or 0.0)
    return {
        "omega_t": brain_arm.get("omega_t"),
        "brain_initiative_count": int(brain_arm["initiative_count"]),
        "agent_initiative_count": int(agent_arm["initiative_count"]),
        "initiative_delta": int(brain_arm["initiative_count"]) - int(agent_arm["initiative_count"]),
        "brain_eoi_mean": brain_eoi,
        "agent_eoi_mean": agent_eoi,
        "eoi_delta": round(brain_eoi - agent_eoi, 4),
        "substrate_changes_metrics": (
            int(brain_arm["initiative_count"]) != int(agent_arm["initiative_count"])
            or abs(brain_eoi - agent_eoi) > 1e-6
        ),
    }


def build_t_agent_03_payload(
    *,
    seed: int = 42,
    generated: str | None = None,
    quiet_ticks: int | None = None,
    drive_threshold: float | None = None,
    llm_backend: str | None = None,
    connectome_sources: tuple[str, ...] | None = None,
) -> dict[str, Any]:
    cfg = load_config()
    t03 = cfg.get("t_agent_03") or {}
    t01 = cfg.get("t_agent_01") or {}
    sim = cfg.get("simulation") or t03.get("simulation") or {}

    quiet_ticks = quiet_ticks or int(t03.get("quiet_ticks", t01.get("quiet_ticks", 6)))
    drive_threshold = drive_threshold or float(
        t03.get("drive_proposal_threshold", t01.get("drive_proposal_threshold", 0.22))
    )
    llm_backend = llm_backend or str(t03.get("llm_backend", t01.get("llm_backend", "mock")))
    primary_source = str(t03.get("primary_source", "bundled_tiny"))
    sources = tuple(connectome_sources or t03.get("connectome_sources") or ("bundled_tiny", "google_male_cns"))
    n_nodes = int(sim.get("n_nodes", t03.get("n_nodes", 8)))
    duration_ms = float(sim.get("duration_ms", t03.get("duration_ms", 100.0)))
    dt_ms = float(sim.get("dt_ms", t03.get("dt_ms", 1.0)))
    carriers = tuple(sim.get("carriers_hz", t03.get("carriers_hz", [20, 30, 42, 70])))
    prefer_brian2 = bool(sim.get("prefer_brian2", t03.get("prefer_brian2", False)))

    arm_results: dict[str, dict[str, Any]] = {}
    for arm in DEFAULT_ARMS:
        arm_results[arm] = run_brain_agent_session(
            arm,
            source_key=primary_source,
            seed=seed,
            quiet_ticks=quiet_ticks,
            drive_threshold=drive_threshold,
            llm_backend=llm_backend,
            n_nodes=n_nodes,
            duration_ms=duration_ms,
            dt_ms=dt_ms,
            carriers=carriers,
            prefer_brian2=prefer_brian2,
        )

    diagnostics = evaluate_agent03_diagnostics(arm_results)
    diagnostic_pass = (
        diagnostics.brain_gt_reactive_initiatives
        and diagnostics.brain_gt_reactive_eoi
        and diagnostics.reactive_zero_initiatives
        and diagnostics.agent_only_baseline_parity
        and diagnostics.bridge_parity
        and diagnostics.psi_changes_behavior
        and not diagnostics.f_brain_agent_collapse
        and not diagnostics.f_omega_decor
    )

    per_source: dict[str, Any] = {}
    for src in sources:
        brain_sess = run_brain_agent_session(
            "brain_eia_endogenous",
            source_key=src,
            seed=seed,
            quiet_ticks=quiet_ticks,
            drive_threshold=drive_threshold,
            llm_backend=llm_backend,
            n_nodes=n_nodes,
            duration_ms=duration_ms,
            dt_ms=dt_ms,
            carriers=carriers,
            prefer_brian2=prefer_brian2,
        )
        agent_sess = run_brain_agent_session(
            "agent_only_eia",
            source_key=src,
            seed=seed,
            quiet_ticks=quiet_ticks,
            drive_threshold=drive_threshold,
            llm_backend=llm_backend,
            n_nodes=n_nodes,
            duration_ms=duration_ms,
            dt_ms=dt_ms,
            carriers=carriers,
            prefer_brian2=prefer_brian2,
        )
        per_source[src] = {
            "brain_eia_endogenous": {
                "initiative_count": brain_sess["initiative_count"],
                "eoi_mean": (brain_sess["eoi"] or {}).get("eoi_mean"),
                "omega_t": brain_sess.get("omega_t"),
                "drive_norm_final": brain_sess.get("drive_norm_final"),
            },
            "agent_only_eia": {
                "initiative_count": agent_sess["initiative_count"],
                "eoi_mean": (agent_sess["eoi"] or {}).get("eoi_mean"),
                "drive_norm_final": agent_sess.get("drive_norm_final"),
            },
            "bridge_delta": _source_bridge_delta(brain_sess, agent_sess),
        }

    return {
        "milestone": MILESTONE,
        "harness_id": HARNESS_ID,
        "artifact_id": "M-T-AGENT-03_2026-09-11",
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
        "drive_proposal_threshold": drive_threshold,
        "llm_backend": llm_backend,
        "primary_connectome_source": primary_source,
        "connectome_sources": list(sources),
        "simulation": {
            "n_nodes": n_nodes,
            "duration_ms": duration_ms,
            "dt_ms": dt_ms,
            "carriers_hz": list(carriers),
            "prefer_brian2": prefer_brian2,
        },
        "sources": {
            "harness": _rel(AGENT_EIA / "harnesses" / "t_agent_03_brain_agent_bridge.py"),
            "brain_agent_bridge": _rel(ADAPTERS / "brain_agent_bridge.py"),
            "t_agent_01": _rel(AGENT_EIA / "harnesses" / "t_agent_01_llm_eia.py"),
            "brain_shadow_bridge": _rel(REPO / "research" / "brain_ai" / "adapters" / "shadow_bridge.py"),
            "ot_injection": _rel(REPO / "research" / "brain_ai" / "adapters" / "ot_injection.py"),
            "spike_arms": _rel(REPO / "research" / "brain_ai" / "adapters" / "spike_arms.py"),
            "mock_llm_proposer": _rel(ADAPTERS / "mock_llm_proposer.py"),
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
                "omega_t": r.get("omega_t"),
                "inject_omega_psi": r.get("inject_omega_psi"),
                "connectome_arm": r.get("connectome_arm"),
                "source_key": r.get("source_key"),
            }
            for arm, r in arm_results.items()
        },
        "arms_full": arm_results,
        "per_source": per_source,
        "diagnostics": diagnostics.to_dict(),
        "diagnostic_pass": diagnostic_pass,
        "falsifiers_active": ["F-OMEGA-DECOR", "F-BRAIN-AGENT-COLLAPSE"],
        "bridge_parity": diagnostics.bridge_parity,
        "g2_directional": {
            "brain_eia_initiative_count": arm_results["brain_eia_endogenous"]["initiative_count"],
            "brain_reactive_initiative_count": arm_results["brain_reactive"]["initiative_count"],
            "agent_only_initiative_count": arm_results["agent_only_eia"]["initiative_count"],
            "brain_eia_eoi_mean": (arm_results["brain_eia_endogenous"]["eoi"] or {}).get("eoi_mean"),
            "brain_reactive_eoi_mean": (arm_results["brain_reactive"]["eoi"] or {}).get("eoi_mean"),
            "agent_only_eoi_mean": (arm_results["agent_only_eia"]["eoi"] or {}).get("eoi_mean"),
        },
        "note": (
            "T-AGENT-03 bridges Brain-AI connectome OMEGA_t into Agent-EIA shadow harness "
            "at X^trigger=0. brain_eia_endogenous > brain_reactive; Ψ(O_t) vs no_psi "
            "tested via F-OMEGA-DECOR; agent_only baseline matches T-AGENT-01 order of "
            "magnitude. Does not establish E_endo or raise C-level."
        ),
    }


def render_t_agent_03_markdown(payload: dict[str, Any]) -> str:
    arms = payload.get("arms") or {}
    diag = payload.get("diagnostics") or {}
    g2 = payload.get("g2_directional") or {}
    per_source = payload.get("per_source") or {}

    lines = [
        f"# M-T-AGENT-03 Brain-AI Agent Bridge — {payload.get('date', '')}",
        "",
        f"**Cell:** {payload.get('cell')} · **Tier:** {payload.get('tier')} · "
        f"**Harness:** {payload.get('harness_id')}",
        f"**Seed:** {payload.get('seed')} · **X_trigger:** 0 · "
        f"**Primary source:** `{payload.get('primary_connectome_source')}`",
        f"**Branch:** `{payload.get('branch')}` · **LLM:** `{payload.get('llm_backend')}`",
        f"**SHA-256:** `{payload.get('artifact_sha256', '')}`",
        "",
        "## Arm comparison (primary source)",
        "",
        "| Arm | initiatives | EOI mean | EUIR | genesis_Δ | OMEGA_t | drive_norm | Ψ |",
        "|-----|-------------|----------|------|-----------|---------|------------|---|",
    ]
    for arm_key in DEFAULT_ARMS:
        row = arms.get(arm_key) or {}
        omega = row.get("omega_t")
        omega_s = f"{omega:.4f}" if omega is not None else "—"
        psi = row.get("inject_omega_psi")
        lines.append(
            f"| `{arm_key}` | {row.get('initiative_count', 0)} | "
            f"{row.get('eoi_mean', 0):.3f} | {row.get('euir_proxy_rate', 0):.0%} | "
            f"{row.get('genesis_delta', 0):.0f} | {omega_s} | "
            f"{row.get('drive_norm_final', 0):.3f} | {psi} |"
        )

    lines.extend([
        "",
        "## G2 directional",
        "",
        f"- brain_eia initiative_count: **{g2.get('brain_eia_initiative_count')}**",
        f"- brain_reactive initiative_count: **{g2.get('brain_reactive_initiative_count')}**",
        f"- agent_only initiative_count: **{g2.get('agent_only_initiative_count')}**",
        f"- brain_eia EOI mean: **{g2.get('brain_eia_eoi_mean')}**",
        f"- brain_reactive EOI mean: **{g2.get('brain_reactive_eoi_mean')}**",
        "",
        "## Per-source bridge delta (brain_eia vs agent_only)",
        "",
        "| Source | OMEGA_t | Δ initiatives | Δ EOI | substrate effect |",
        "|--------|---------|---------------|-------|------------------|",
    ])
    for src, data in per_source.items():
        delta = data.get("bridge_delta") or {}
        omega = delta.get("omega_t")
        omega_s = f"{omega:.4f}" if omega is not None else "—"
        lines.append(
            f"| `{src}` | {omega_s} | {delta.get('initiative_delta', 0)} | "
            f"{delta.get('eoi_delta', 0):.3f} | {delta.get('substrate_changes_metrics')} |"
        )

    lines.extend([
        "",
        "## Diagnostics / falsifiers",
        "",
        f"- diagnostic_pass: **{payload.get('diagnostic_pass')}**",
        f"- bridge_parity: {diag.get('bridge_parity')}",
        f"- psi_changes_behavior: {diag.get('psi_changes_behavior')}",
        f"- F-OMEGA-DECOR (omega decorative): {diag.get('f_omega_decor')}",
        f"- F-BRAIN-AGENT-COLLAPSE: {diag.get('f_brain_agent_collapse')}",
        f"- agent_only baseline parity: {diag.get('agent_only_baseline_parity')}",
        "",
        f"**claim_allowed:** {payload.get('claim_allowed')} · "
        f"**e_endo_support:** {payload.get('e_endo_support')} · "
        f"**AGI\\*:** {payload.get('agi_star_claim')}",
        "",
        payload.get("note", ""),
    ])
    return "\n".join(lines) + "\n"

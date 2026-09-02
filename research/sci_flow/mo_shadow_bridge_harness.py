"""M-O shadow bridge — Neuraxon/OMEGA → OmegaWaveState → shadow multitick ATT-R compare.

Maps Neuraxon oscillator export through ``OmegaWaveState`` into a shadow
closed-loop multitick session, then scores ATT-R alongside a native shadow
baseline. Tier C only; ``claim_allowed=false``; no D1 ``e_endo_support`` bleed.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import types
from datetime import date
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SCI_FLOW = Path(__file__).resolve().parent
SRC = REPO / "src"
WOE_SRC = REPO / "research" / "cursor-starter-v0.2" / "src"
WOE_PKG = WOE_SRC / "eia"
OSCILLATORY = WOE_PKG / "oscillatory_state.py"
ARMS_ARTIFACT = SCI_FLOW / "M-MO_do_o_arms_2026-09-02.json"
BRIDGE_ARTIFACT_JSON = SCI_FLOW / "M-MO_shadow_bridge_2026-09-02.json"
BRIDGE_ARTIFACT_MD = SCI_FLOW / "M-MO_shadow_bridge_2026-09-02.md"


def _ensure_paths() -> None:
    for path in (str(SRC), str(SCI_FLOW)):
        if path not in sys.path:
            sys.path.insert(0, path)


def _load_oscillatory_module() -> Any:
    spec = importlib.util.spec_from_file_location("oscillatory_state_mo_shadow", OSCILLATORY)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {OSCILLATORY}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _load_woe_submodule(name: str) -> Any:
    pkg_name = "woe_eia_shadow_bridge"
    if pkg_name not in sys.modules:
        pkg = types.ModuleType(pkg_name)
        pkg.__path__ = [str(WOE_PKG)]  # type: ignore[attr-defined]
        sys.modules[pkg_name] = pkg

    full = f"{pkg_name}.{name}"
    if full in sys.modules:
        return sys.modules[full]

    path = WOE_PKG / f"{name}.py"
    spec = importlib.util.spec_from_file_location(full, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = pkg_name
    sys.modules[full] = mod
    spec.loader.exec_module(mod)
    return mod


def _rel(path: Path) -> str:
    try:
        return path.relative_to(REPO).as_posix()
    except ValueError:
        return path.as_posix()


def load_arms_payload(
    arms_path: Path = ARMS_ARTIFACT,
    *,
    regenerate: bool = False,
    steps: int = 50,
    seed: int = 42,
) -> dict[str, Any]:
    """Load paired do(O) arms artifact, optionally regenerating it first."""
    if regenerate or not arms_path.is_file():
        from mo_proof_bridge_harness import load_arms_payload as _load

        return _load(arms_path, regenerate=True, steps=steps, seed=seed)
    return json.loads(arms_path.read_text(encoding="utf-8"))


def extract_omega_crosswalk(arm: dict[str, Any]) -> dict[str, Any]:
    """Extract OmegaWaveState channels and OMEGA_t from a Neuraxon arm payload."""
    omega_t = (arm.get("omega_t") or {}).get("final")
    ows = arm.get("omega_wave_state") or {}
    kuramoto_r = arm.get("kuramoto_r_final")
    bands = arm.get("oscillator_bands_final") or {}
    return {
        "omega_t": omega_t,
        "kuramoto_r": kuramoto_r,
        "omega_wave_state": dict(ows),
        "n_bands": ows.get("n_bands", len(bands)),
        "crosswalk": arm.get("crosswalk") or {},
        "vendor": arm.get("vendor", "unknown"),
        "arm": arm.get("arm", "unknown"),
    }


def run_omega_bridged_shadow_episode(
    omega_ctx: dict[str, Any],
    *,
    seed: int = 0,
) -> dict[str, Any]:
    """Run one closed-loop shadow multitick with Neuraxon-derived omega context."""
    _ensure_paths()
    from eia.governor import ContactGovernor, GovernorConfig
    from eia.ids import seeded_context
    from eia.pipeline import CognitiveLoop
    from eia.runtime.shadow_multitick import AttREvent, ShadowSessionCarryover
    from eia.schemas.observation import Observation, ObservationSource

    omega_t = float(omega_ctx.get("omega_t") or 0.0)
    kuramoto_r = float(omega_ctx.get("kuramoto_r") or 0.0)
    ows = omega_ctx.get("omega_wave_state") or {}

    with seeded_context(seed):
        loop = CognitiveLoop(seed=seed)
        loop.governor = ContactGovernor(GovernorConfig())

        events: list[AttREvent] = [
            AttREvent("o0", "X", f"omega_bridge:omega_t={omega_t:.4f}", (), 0),
            AttREvent("n0", "W", "world_model", ("o0",), 0),
            AttREvent("n1", "M", "self_model", ("n0",), 0),
        ]
        motive_ids: list[str] = []

        loop.apply_observation(
            Observation(
                id="obs-omega-bridge",
                timestamp=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
                source=ObservationSource.INTERNAL,
                topic="omega_wave_bridge",
                payload={
                    "omega_t": omega_t,
                    "kuramoto_r": kuramoto_r,
                    "omega_wave_state": ows,
                    "bridge": "neuraxon_to_omega_wave_state",
                },
                trust=0.9,
            )
        )
        loop.apply_observation(
            Observation(
                id="obs-workspace",
                timestamp=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
                source=ObservationSource.WORLD_EVENT,
                topic="workspace_file_activity",
                payload={"files_recently_modified": True, "omega_bridged": True},
                trust=0.95,
            )
        )

        mot, _init1, decision, _ = loop.tick_cognition(tick=1, hour=14, finalize=True)
        motive_ids.append(mot.id)
        g0 = mot.id
        events.append(AttREvent("n2", "G", g0, ("n0", "n1", "o0"), 0))
        events.append(AttREvent("n3", "Pi", "pi_research", ("n2",), 1))
        outcome = decision.outcome.value if decision else "abstain"
        action_label = f"act_probe:{outcome}"
        events.append(AttREvent("n4", "A", action_label, ("n3",), 1))

        belief_id = "belief-post-action"
        loop.field.upsert_belief(
            belief_id,
            kind=__import__("eia.schemas.belief", fromlist=["BeliefKind"]).BeliefKind.CATEGORICAL,
            subject="workspace",
            claim="action_consequence_observed",
            distribution={"updated": 0.8, "stale": 0.2},
            uncertainty=0.35,
            metadata={"source": "mo_shadow_bridge", "role": "W_prime", "prior_action": action_label},
        )
        loop.apply_observation(
            Observation(
                id="obs-consequence",
                timestamp=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
                source=ObservationSource.INTERNAL,
                topic="action_consequence",
                payload={"prior_action": action_label, "belief_id": belief_id},
                trust=0.95,
            )
        )
        events.append(AttREvent("n5", "X", "x_observation", ("n4",), 2))
        events.append(AttREvent("n6", "W_prime", "world_update", ("n5", "n4"), 2))

        mot2, _init2, _dec2, _ = loop.tick_cognition(tick=2, hour=14, finalize=True)
        motive_ids.append(mot2.id)
        events.append(
            AttREvent(
                "n7",
                "G_prime",
                mot2.id,
                ("n6", "n1", "o0"),
                3,
                novel=True,
            )
        )

        carryover = ShadowSessionCarryover.from_loop(
            loop, last_motive_id=mot2.id, session_tick=2
        )

        return {
            "arm": "closed_loop",
            "bridge_kind": "omega_bridged_closed_loop",
            "events": [e.as_dict() for e in events],
            "shadow": True,
            "live_telegram": False,
            "emit_m0": False,
            "kuramoto_r": kuramoto_r,
            "omega_t": omega_t,
            "claim_allowed": False,
            "ticks_run": 2,
            "motive_ids": motive_ids,
            "used_carryover": False,
            "omega_bridge": omega_ctx,
            "carryover": {
                "session_tick": carryover.session_tick,
                "last_motive_id": carryover.last_motive_id,
                "drive_tick": carryover.drive_tick,
                "has_beliefs": bool(carryover.beliefs_json),
            },
            "gap_vs_live_daemon": (
                "Omega-bridged shadow multitick: Neuraxon O_t crosswalk injected as "
                "internal observation; live daemon does not ingest vendor omega context."
            ),
        }


def score_shadow_log(log: dict[str, Any]) -> dict[str, Any]:
    """Score one shadow log under ATT-R (explore proxy only)."""
    live_att_r = _load_woe_submodule("live_att_r")
    return live_att_r.scorecard_from_shadow_log(log)


def build_shadow_bridge_payload(
    arms_payload: dict[str, Any],
    *,
    seed: int = 42,
    generated: str | None = None,
) -> dict[str, Any]:
    """Build full M-O shadow bridge artifact from paired arms payload."""
    _ensure_paths()
    from eia.runtime.shadow_multitick import ShadowArm, run_shadow_episode

    baseline_arm = arms_payload.get("arms", {}).get("neuraxon_baseline") or {}
    plasticity_arm = arms_payload.get("arms", {}).get("do_o_neuraxon_plasticity_off") or {}
    native_arm = arms_payload.get("arms", {}).get("native_oscillatory_state") or {}

    baseline_omega = extract_omega_crosswalk(baseline_arm)
    plasticity_omega = extract_omega_crosswalk(plasticity_arm)
    native_omega = extract_omega_crosswalk(native_arm)

    native_shadow = run_shadow_episode(ShadowArm.CLOSED_LOOP, seed=seed).as_dict()
    bridged_baseline = run_omega_bridged_shadow_episode(baseline_omega, seed=seed)
    bridged_plasticity = run_omega_bridged_shadow_episode(plasticity_omega, seed=seed)

    native_att_r = score_shadow_log(native_shadow)
    bridged_baseline_att_r = score_shadow_log(bridged_baseline)
    bridged_plasticity_att_r = score_shadow_log(bridged_plasticity)

    comparison = arms_payload.get("paired_comparison") or {}
    omega_cmp = comparison.get("omega_t_final") or {}
    kuramoto_cmp = comparison.get("kuramoto_r_final") or {}

    att_r_parity = (
        native_att_r.get("att_r_evidence") == bridged_baseline_att_r.get("att_r_evidence")
        and native_att_r.get("closed_cycle_count") == bridged_baseline_att_r.get("closed_cycle_count")
    )

    return {
        "milestone": "M-O-SHADOW-BRIDGE",
        "artifact_id": "M-MO_shadow_bridge_2026-09-02",
        "tick_id": "M-MO-SHADOW-BRIDGE",
        "date": generated or date.today().isoformat(),
        "branch": "research/cursor-starter-v0.2-woe-eis",
        "cell": "D2×L2",
        "tier": "C",
        "claim_ceiling": "C2",
        "claim_allowed": False,
        "e_endo_support": "none",
        "witness_support": "none",
        "c_ladder_raise_allowed": False,
        "agi_star_claim": False,
        "att": "ATT-R",
        "seed": seed,
        "sources": {
            "arms": _rel(ARMS_ARTIFACT),
            "admissibility": "research/sci_flow/M-O_PROOF_ADMISSIBILITY.md",
            "shadow_runtime": "src/eia/runtime/shadow_multitick.py",
            "oscillatory_state": "research/cursor-starter-v0.2/src/eia/oscillatory_state.py",
            "att_r_scoring": "research/cursor-starter-v0.2/src/eia/live_att_r.py",
        },
        "omega_crosswalk": {
            "neuraxon_baseline": baseline_omega,
            "do_o_neuraxon_plasticity_off": plasticity_omega,
            "native_oscillatory_state": native_omega,
            "feasible": arms_payload.get("crosswalk_feasible", False),
        },
        "neuraxon_paired_delta": {
            "omega_t_final": omega_cmp.get("delta_plasticity_off_vs_baseline"),
            "kuramoto_r_final": kuramoto_cmp.get("delta_plasticity_off_vs_baseline"),
        },
        "shadow_sessions": {
            "native_closed_loop": native_shadow,
            "omega_bridged_baseline": bridged_baseline,
            "omega_bridged_plasticity_off": bridged_plasticity,
        },
        "att_r_comparison": {
            "native_closed_loop": native_att_r,
            "omega_bridged_baseline": bridged_baseline_att_r,
            "omega_bridged_plasticity_off": bridged_plasticity_att_r,
            "att_r_parity_native_vs_bridged_baseline": att_r_parity,
            "kuramoto_is_not_att_r": True,
        },
        "falsifier_hints": comparison.get("falsifier_hints") or {},
        "falsifiers_active": [
            "F-KURAMOTO-AS-E",
            "F-OMEGA-DECOR",
            "F-SYNC",
            "F-STRUCT≠E",
        ],
        "note": (
            "Neuraxon O_t → OmegaWaveState → shadow multitick crosswalk with ATT-R "
            "scorecard compare. Does not establish E_endo or raise C-level."
        ),
    }


def render_shadow_bridge_markdown(payload: dict[str, Any]) -> str:
    """Render markdown artifact for M-O shadow bridge."""
    att = payload.get("att_r_comparison") or {}
    native = att.get("native_closed_loop") or {}
    bridged = att.get("omega_bridged_baseline") or {}
    omega = payload.get("omega_crosswalk") or {}
    baseline_ows = (omega.get("neuraxon_baseline") or {}).get("omega_wave_state") or {}
    delta = payload.get("neuraxon_paired_delta") or {}

    lines = [
        f"# M-MO Shadow Bridge — {payload.get('date', '')}",
        "",
        f"**Cell:** {payload.get('cell', 'D2×L2')} · **Tier:** {payload.get('tier', 'C')} · "
        f"**ATT:** {payload.get('att', 'ATT-R')}",
        f"**Seed:** {payload.get('seed')} · **Arms:** `{_rel(ARMS_ARTIFACT)}`",
        "",
        "## Omega crosswalk (Neuraxon → OmegaWaveState)",
        "",
        f"- Baseline OMEGA_t: `{(omega.get('neuraxon_baseline') or {}).get('omega_t')}`",
        f"- Plasticity-off OMEGA_t: `{(omega.get('do_o_neuraxon_plasticity_off') or {}).get('omega_t')}`",
        f"- Δ OMEGA_t (plasticity_off vs baseline): `{delta.get('omega_t_final')}`",
        f"- phase_coherence: `{baseline_ows.get('phase_coherence')}` · "
        f"synchrony: `{baseline_ows.get('synchrony')}` · "
        f"productive_tension: `{baseline_ows.get('productive_tension')}`",
        "",
        "## ATT-R comparison (shadow multitick)",
        "",
        f"| Session | att_r_evidence | closed_cycles | novel_motive |",
        f"|---------|----------------|---------------|--------------|",
        f"| native_closed_loop | {native.get('att_r_evidence')} | "
        f"{native.get('closed_cycle_count')} | {native.get('has_novel_motive_after_action')} |",
        f"| omega_bridged_baseline | {bridged.get('att_r_evidence')} | "
        f"{bridged.get('closed_cycle_count')} | {bridged.get('has_novel_motive_after_action')} |",
        f"| parity native↔bridged | {att.get('att_r_parity_native_vs_bridged_baseline')} | — | — |",
        "",
        "## Invariants",
        "",
        "- `e_endo_support=none` (no D1 bleed)",
        "- `claim_allowed=false`",
        "- `c_ladder_raise_allowed=false`",
        "- `agi_star_claim=false`",
        "- Kuramoto R ≠ E_endo (F-KURAMOTO-AS-E annotation when R high)",
        "- Omega bridge is observational crosswalk; ATT-R closure unchanged on matched seed",
    ]
    return "\n".join(lines)


def maybe_refresh_adjunct_ledger(
    arms_payload: dict[str, Any],
    *,
    generated: str | None = None,
) -> dict[str, Any] | None:
    """Rebuild adjunct ledger only if witness_support would improve beyond partial."""
    from mo_proof_bridge_harness import ADJUNCT_ARTIFACT_JSON, build_adjunct_ledger

    new_ledger = build_adjunct_ledger(arms_payload, generated=generated)
    if ADJUNCT_ARTIFACT_JSON.is_file():
        current = json.loads(ADJUNCT_ARTIFACT_JSON.read_text(encoding="utf-8"))
        current_ws = current.get("witness_support", "none")
        new_ws = new_ledger.get("witness_support", "none")
        rank = {"none": 0, "partial": 1}
        if rank.get(new_ws, 0) <= rank.get(current_ws, 0):
            return None
    return new_ledger

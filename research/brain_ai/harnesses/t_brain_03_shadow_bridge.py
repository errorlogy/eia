"""T-BRAIN-03 — Brain-AI OMEGA_t → EIA shadow multitick bridge at X_trigger=0.

Three-arm connectome suite (coupled_active, passive_quiescent, phase_scramble_control):
native shadow vs omega-bridged ATT-R parity, ΔG(genesis) per arm, F-OMEGA-DECOR / F-BEHAV-OMEGA-MISMATCH.

Tier C only; ``claim_allowed=false``; no D1 bleed; no AGI* claims.
"""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Literal

import yaml

BRAIN_AI = Path(__file__).resolve().parents[1]
REPO = BRAIN_AI.parents[1]
ADAPTERS = BRAIN_AI / "adapters"
ARTIFACTS = BRAIN_AI / "artifacts"
ARTIFACT_JSON = ARTIFACTS / "M-T-BRAIN-03_2026-09-10.json"
ARTIFACT_MD = ARTIFACTS / "M-T-BRAIN-03_2026-09-10.md"
CONFIG_PATH = BRAIN_AI / "config.yaml"
BRANCH = "research/brain-ai-connectome"

T03_ARM_KEYS: tuple[str, ...] = (
    "coupled_active",
    "passive_quiescent",
    "phase_scramble_control",
)

OMEGA_SPAN_MIN = 0.05
GENESIS_EPSILON = 1e-9
BEHAVIOR_MATCH_EPS = 1e-4

ArmKey = Literal["coupled_active", "passive_quiescent", "phase_scramble_control"]


def _ensure_paths() -> None:
    for path in (str(ADAPTERS), str(REPO / "src")):
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


def shadow_initiative_fingerprint(ep: dict[str, Any]) -> str:
    """Compact goal/action fingerprint from shadow ATT-R events."""
    parts: list[str] = []
    for event in ep.get("events") or []:
        kind = event.get("kind")
        if kind in ("G", "G_prime", "A", "Pi"):
            parts.append(f"{kind}:{event.get('label', '')}")
    return "|".join(parts)


def extract_genesis_metrics(ep: dict[str, Any]) -> dict[str, Any]:
    """ΔG / genesis delta from one shadow episode (G → G_prime under X_trigger=0)."""
    motive_ids = list(ep.get("motive_ids") or [])
    events = ep.get("events") or []
    g0 = motive_ids[0] if motive_ids else None
    g_prime = motive_ids[-1] if len(motive_ids) > 1 else None
    has_novel_g_prime = any(
        e.get("kind") == "G_prime" and e.get("novel") for e in events
    )
    goal_symbol_changed = has_novel_g_prime
    genesis_delta = 1.0 if has_novel_g_prime else 0.0
    return {
        "g0_id": g0,
        "g_prime_id": g_prime,
        "goal_symbol_changed": goal_symbol_changed,
        "genesis_delta": genesis_delta,
        "has_novel_g_prime": has_novel_g_prime,
        "initiative_fingerprint": shadow_initiative_fingerprint(ep),
        "x_trigger_zero": not any(
            e.get("label") == "user_prompt" for e in events
        ),
        "behavior_gated_novel_genesis": ep.get("behavior_gated_novel_genesis"),
    }


@dataclass(frozen=True, slots=True)
class ShadowBridgeDiagnostics:
    active_vs_passive_genesis_diff: bool
    scramble_omega_breaks: bool
    scramble_genesis_unchanged: bool
    scramble_behavior_matched: bool
    f_omega_decor: bool
    f_behav_omega_mismatch: bool
    att_r_parity_active: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "active_vs_passive_genesis_diff": self.active_vs_passive_genesis_diff,
            "scramble_omega_breaks": self.scramble_omega_breaks,
            "scramble_genesis_unchanged": self.scramble_genesis_unchanged,
            "scramble_behavior_matched": self.scramble_behavior_matched,
            "f_omega_decor": self.f_omega_decor,
            "f_behav_omega_mismatch": self.f_behav_omega_mismatch,
            "att_r_parity_active": self.att_r_parity_active,
        }


def evaluate_shadow_bridge_diagnostics(
    arm_probes: list[dict[str, Any]],
    *,
    native_att_r: dict[str, Any],
) -> ShadowBridgeDiagnostics:
    """Acceptance checks for T-BRAIN-03 shadow bridge."""
    by_key = {p["arm_key"]: p for p in arm_probes}
    active = by_key["coupled_active"]
    passive = by_key["passive_quiescent"]
    scramble = by_key["phase_scramble_control"]

    active_vs_passive = (
        active["genesis"]["genesis_delta"] != passive["genesis"]["genesis_delta"]
        or active["genesis"]["has_novel_g_prime"] != passive["genesis"]["has_novel_g_prime"]
    )

    omega_delta = abs(float(scramble["omega_t"]) - float(active["omega_t"]))
    scramble_omega_breaks = omega_delta >= OMEGA_SPAN_MIN

    scramble_genesis_unchanged = (
        scramble["genesis"]["genesis_delta"] == active["genesis"]["genesis_delta"]
        and scramble["genesis"]["initiative_fingerprint"]
        == active["genesis"]["initiative_fingerprint"]
    )

    beh_a = active["behavior"]
    beh_s = scramble["behavior"]
    scramble_behavior_matched = (
        beh_a["n_spikes"] == beh_s["n_spikes"]
        and abs(
            beh_a["activity_rate_per_node_ms"] - beh_s["activity_rate_per_node_ms"]
        )
        < BEHAVIOR_MATCH_EPS
    )

    f_omega_decor = (
        scramble_omega_breaks
        and scramble_behavior_matched
        and scramble_genesis_unchanged
    )

    f_behav_omega_mismatch = scramble_omega_breaks and scramble_behavior_matched

    bridged_att = active["bridged_att_r"]
    att_r_parity = (
        native_att_r.get("att_r_evidence") == bridged_att.get("att_r_evidence")
        and native_att_r.get("closed_cycle_count") == bridged_att.get("closed_cycle_count")
    )

    return ShadowBridgeDiagnostics(
        active_vs_passive_genesis_diff=active_vs_passive,
        scramble_omega_breaks=scramble_omega_breaks,
        scramble_genesis_unchanged=scramble_genesis_unchanged,
        scramble_behavior_matched=scramble_behavior_matched,
        f_omega_decor=f_omega_decor,
        f_behav_omega_mismatch=f_behav_omega_mismatch,
        att_r_parity_active=att_r_parity,
    )


def build_t_brain_03_payload(
    *,
    seed: int | None = None,
    generated: str | None = None,
    prefer_brian2: bool | None = None,
) -> dict[str, Any]:
    """Build full T-BRAIN-03 artifact payload."""
    _ensure_paths()
    from behavior_metrics import compute_behavior_metrics
    from connectome_export import load_subgraph
    from ot_injection import inject_omega_from_spikes, _load_oscillatory_module
    from shadow_bridge import run_brain_omega_bridged_shadow_episode, score_shadow_log
    from spike_arms import run_spike_arm, scramble_spike_phases_for_omega

    from eia.runtime.shadow_multitick import ShadowArm, run_shadow_episode

    cfg = load_config()
    sim = cfg.get("simulation") or {}
    seed = int(seed if seed is not None else sim.get("seed", 42))
    prefer_brian2 = (
        prefer_brian2 if prefer_brian2 is not None else bool(sim.get("prefer_brian2", False))
    )
    n_nodes = int(sim.get("n_nodes", 8))
    duration_ms = float(sim.get("duration_ms", 100.0))
    dt_ms = float(sim.get("dt_ms", 1.0))
    carriers = tuple(cfg.get("carriers_hz") or [20, 30, 42, 70])

    subgraph = load_subgraph(n_nodes=n_nodes, seed=seed, prefer_bundled=True)
    osc_mod = _load_oscillatory_module()

    native_shadow = run_shadow_episode(ShadowArm.CLOSED_LOOP, seed=seed).as_dict()
    native_att_r = score_shadow_log(native_shadow)
    native_genesis = extract_genesis_metrics(native_shadow)

    arm_probes: list[dict[str, Any]] = []
    coupled_ref: dict[str, Any] | None = None

    for arm_key in T03_ARM_KEYS:
        spike_payload = run_spike_arm(
            subgraph,
            arm_key,  # type: ignore[arg-type]
            seed=seed,
            duration_ms=duration_ms,
            dt_ms=dt_ms,
            prefer_brian2=prefer_brian2,
            coupled_reference=coupled_ref,
        )
        if arm_key == "coupled_active":
            coupled_ref = spike_payload
        behavior = compute_behavior_metrics(spike_payload)

        if arm_key == "phase_scramble_control":
            phases = scramble_spike_phases_for_omega(
                spike_payload,
                subgraph.node_ids,
                carriers=carriers,
                duration_ms=duration_ms,
                seed=seed + 99,
            )
            amps = [
                min(1.0, 0.3 + 0.1 * len(spike_payload["spike_times_ms"].get(nid, [])))
                for nid in subgraph.node_ids[: len(carriers)]
            ]
            while len(amps) < len(carriers):
                amps.append(1.0)
            ows = osc_mod.OmegaWaveState.from_carrier_phases(
                phases, carriers=carriers, amplitudes=amps
            )
            omega_ctx = {
                "omega_t": float(osc_mod.omega_metric(ows)),
                "kuramoto_r": float(osc_mod.kuramoto_order_parameter(phases)),
                "omega_wave_state": {
                    "phase_coherence": ows.phase_coherence,
                    "synchrony": ows.synchrony,
                    "productive_tension": ows.productive_tension,
                },
                "crosswalk": {"phase_scramble_control": True},
                "vendor": "brain_ai.ot_injection",
                "arm": arm_key,
            }
        else:
            omega_ctx = inject_omega_from_spikes(
                spike_payload, subgraph.node_ids, carriers=carriers
            )
            omega_ctx["arm"] = arm_key

        bridged = run_brain_omega_bridged_shadow_episode(
            omega_ctx,
            behavior,
            seed=seed,
            arm_key=arm_key,
        )
        genesis = extract_genesis_metrics(bridged)
        bridged_att_r = score_shadow_log(bridged)

        arm_probes.append({
            "arm_key": arm_key,
            "omega_t": omega_ctx.get("omega_t"),
            "kuramoto_r": omega_ctx.get("kuramoto_r"),
            "behavior": behavior,
            "spike_backend": spike_payload.get("backend"),
            "n_spikes": spike_payload.get("n_spikes"),
            "genesis": genesis,
            "bridged_att_r": bridged_att_r,
            "bridged_shadow": {
                "bridge_kind": bridged.get("bridge_kind"),
                "behavior_gated_novel_genesis": bridged.get("behavior_gated_novel_genesis"),
                "motive_ids": bridged.get("motive_ids"),
                "initiative_fingerprint": genesis["initiative_fingerprint"],
            },
        })

    diagnostics = evaluate_shadow_bridge_diagnostics(arm_probes, native_att_r=native_att_r)
    diagnostic_pass = (
        diagnostics.active_vs_passive_genesis_diff
        and diagnostics.f_omega_decor
        and diagnostics.scramble_behavior_matched
    )

    return {
        "milestone": "M-BRAIN-AI",
        "harness_id": "T-BRAIN-03",
        "artifact_id": "M-T-BRAIN-03_2026-09-10",
        "tick_id": "T-BRAIN-03",
        "date": generated or date.today().isoformat(),
        "branch": BRANCH,
        "cell": "D2×L2",
        "tier": "C",
        "claim_ceiling": "C2",
        "claim_allowed": False,
        "e_endo_support": "none",
        "witness_support": "none",
        "c_ladder_raise_allowed": False,
        "agi_star_claim": False,
        "att": "ATT-R",
        "x_trigger_zero": True,
        "seed": seed,
        "sources": {
            "t_brain_02": _rel(BRAIN_AI / "harnesses" / "t_brain_02_omega_behavior.py"),
            "shadow_bridge": _rel(BRAIN_AI / "adapters" / "shadow_bridge.py"),
            "mo_shadow_bridge": _rel(REPO / "research" / "sci_flow" / "mo_shadow_bridge_harness.py"),
            "omega_delta_g": _rel(REPO / "research" / "sci_flow" / "omega_delta_g_harness.py"),
            "shadow_runtime": _rel(REPO / "src" / "eia" / "runtime" / "shadow_multitick.py"),
            "oscillatory_state": "research/cursor-starter-v0.2/src/eia/oscillatory_state.py",
            "att_r_scoring": "research/cursor-starter-v0.2/src/eia/live_att_r.py",
        },
        "native_shadow": {
            "att_r": native_att_r,
            "genesis": native_genesis,
        },
        "arms": {
            p["arm_key"]: {
                "omega_t": p["omega_t"],
                "kuramoto_r": p["kuramoto_r"],
                "behavior": p["behavior"],
                "genesis_delta": p["genesis"]["genesis_delta"],
                "goal_symbol_changed": p["genesis"]["goal_symbol_changed"],
                "has_novel_g_prime": p["genesis"]["has_novel_g_prime"],
                "initiative_fingerprint": p["genesis"]["initiative_fingerprint"],
                "bridged_att_r_evidence": p["bridged_att_r"].get("att_r_evidence"),
                "bridged_closed_cycles": p["bridged_att_r"].get("closed_cycle_count"),
                "behavior_gated_novel_genesis": p["bridged_shadow"]["behavior_gated_novel_genesis"],
            }
            for p in arm_probes
        },
        "att_r_comparison": {
            "native_closed_loop": native_att_r,
            "omega_bridged_coupled_active": arm_probes[0]["bridged_att_r"],
            "att_r_parity_native_vs_bridged_active": diagnostics.att_r_parity_active,
        },
        "shadow_bridge_diagnostics": diagnostics.to_dict(),
        "diagnostic_pass": diagnostic_pass,
        "f_omega_decor": {
            "status": "confirmed" if diagnostics.f_omega_decor else "not_confirmed",
            "phase_scramble_control": diagnostics.f_omega_decor,
        },
        "f_behav_omega_mismatch": {
            "status": "confirmed" if diagnostics.f_behav_omega_mismatch else "not_confirmed",
            "scramble_omega_breaks": diagnostics.scramble_omega_breaks,
            "scramble_behavior_matched": diagnostics.scramble_behavior_matched,
        },
        "falsifiers_active": [
            "F-KURAMOTO-AS-E",
            "F-OMEGA-DECOR",
            "F-BEHAV-OMEGA-MISMATCH",
            "F-SYNC",
            "F-STRUCT≠E",
        ],
        "connectome_source": subgraph.source,
        "n_nodes": subgraph.n_nodes,
        "note": (
            "Connectome OMEGA_t crosswalk into shadow multitick at X_trigger=0. "
            "Genesis gated by behavioral activity proxy; omega alone decorative under "
            "phase_scramble_control (F-OMEGA-DECOR). Does not establish E_endo or raise C-level."
        ),
    }


def artifact_sha256(payload: dict[str, Any]) -> str:
    """Stable SHA-256 over canonical JSON (excludes sha field)."""
    body = {k: v for k, v in payload.items() if k != "artifact_sha256"}
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def render_t_brain_03_markdown(payload: dict[str, Any]) -> str:
    """Render markdown artifact for T-BRAIN-03."""
    arms = payload.get("arms") or {}
    diag = payload.get("shadow_bridge_diagnostics") or {}
    att = payload.get("att_r_comparison") or {}
    native = att.get("native_closed_loop") or {}
    bridged = att.get("omega_bridged_coupled_active") or {}
    decor = payload.get("f_omega_decor") or {}

    lines = [
        f"# M-T-BRAIN-03 Shadow Bridge — {payload.get('date', '')}",
        "",
        f"**Cell:** {payload.get('cell', 'D2×L2')} · **Tier:** {payload.get('tier', 'C')} · "
        f"**Harness:** {payload.get('harness_id', 'T-BRAIN-03')}",
        f"**Seed:** {payload.get('seed')} · **X_trigger:** 0 · **Branch:** `{payload.get('branch')}`",
        f"**SHA-256:** `{payload.get('artifact_sha256', '')}`",
        "",
        "## Arms (OMEGA_t vs ΔG bridged shadow)",
        "",
        "| Arm | OMEGA_t | genesis_Δ | novel G' | behavior regime | ATT-R evidence |",
        "|-----|---------|-----------|----------|-----------------|----------------|",
    ]
    for key, arm in arms.items():
        beh = arm.get("behavior") or {}
        lines.append(
            f"| `{key}` | `{arm.get('omega_t')}` | `{arm.get('genesis_delta')}` | "
            f"`{arm.get('has_novel_g_prime')}` | `{beh.get('regime_label')}` | "
            f"`{arm.get('bridged_att_r_evidence')}` |"
        )

    lines.extend([
        "",
        "## ATT-R comparison (native vs bridged active)",
        "",
        f"| Session | att_r_evidence | closed_cycles |",
        f"|---------|----------------|---------------|",
        f"| native_closed_loop | {native.get('att_r_evidence')} | {native.get('closed_cycle_count')} |",
        f"| omega_bridged_coupled_active | {bridged.get('att_r_evidence')} | "
        f"{bridged.get('closed_cycle_count')} |",
        f"| parity | {att.get('att_r_parity_native_vs_bridged_active')} | — |",
        "",
        "## Shadow bridge diagnostics",
        "",
        f"- active↔passive genesis diff: `{diag.get('active_vs_passive_genesis_diff')}`",
        f"- scramble OMEGA break: `{diag.get('scramble_omega_breaks')}`",
        f"- scramble genesis unchanged: `{diag.get('scramble_genesis_unchanged')}`",
        f"- scramble behavior matched: `{diag.get('scramble_behavior_matched')}`",
        f"- **F-OMEGA-DECOR:** `{decor.get('status')}`",
        f"- diagnostic_pass: `{payload.get('diagnostic_pass')}`",
        "",
        "## Invariants",
        "",
        "- `e_endo_support=none` (no D1 bleed)",
        "- `claim_allowed=false`",
        "- `c_ladder_raise_allowed=false`",
        "- `agi_star_claim=false`",
        "- Kuramoto R ≠ E_endo (F-KURAMOTO-AS-E)",
        "- Omega bridge observational; genesis gated by behavior proxy at X_trigger=0",
    ])
    return "\n".join(lines)

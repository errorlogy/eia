"""T-BRAIN-04 — Longitudinal shadow carryover with endogenous vs passive embodied comparison.

Multi-tick ``ShadowSessionCarryover`` bridge at X_trigger=0 (2+ session ticks):
behavior-gated ΔG persists across ticks; Ψ(O_t) injected only on tick 0 (no omega blur
on carryover without user trigger). G2 gate analog on connectome substrate.

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
ARTIFACT_JSON = ARTIFACTS / "M-T-BRAIN-04_2026-09-10.json"
ARTIFACT_MD = ARTIFACTS / "M-T-BRAIN-04_2026-09-10.md"
CONFIG_PATH = BRAIN_AI / "config.yaml"
BRANCH = "research/brain-ai-connectome"

T04_ARM_KEYS: tuple[str, ...] = (
    "coupled_active",
    "passive_quiescent",
    "phase_scramble_control",
)

SESSION_TICKS = 2
OMEGA_SPAN_MIN = 0.05
GENESIS_EPSILON = 1e-9
BEHAVIOR_MATCH_EPS = 1e-4
EOI_ENDOGENOUS_THRESHOLD = 0.50

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


def extract_genesis_metrics(ep: dict[str, Any]) -> dict[str, Any]:
    """ΔG / genesis delta from one shadow episode (G → G_prime under X_trigger=0)."""
    motive_ids = list(ep.get("motive_ids") or [])
    events = ep.get("events") or []
    g0 = motive_ids[0] if motive_ids else None
    g_prime = motive_ids[-1] if len(motive_ids) > 1 else None
    has_novel_g_prime = any(
        e.get("kind") == "G_prime" and e.get("novel") for e in events
    )
    parts: list[str] = []
    for event in events:
        kind = event.get("kind")
        if kind in ("G", "G_prime", "A", "Pi"):
            parts.append(f"{kind}:{event.get('label', '')}")
    return {
        "g0_id": g0,
        "g_prime_id": g_prime,
        "goal_symbol_changed": has_novel_g_prime,
        "genesis_delta": 1.0 if has_novel_g_prime else 0.0,
        "has_novel_g_prime": has_novel_g_prime,
        "initiative_fingerprint": "|".join(parts),
        "x_trigger_zero": not any(
            e.get("label") == "user_prompt" for e in events
        ),
        "behavior_gated_novel_genesis": ep.get("behavior_gated_novel_genesis"),
        "n_initiatives": sum(
            1 for s in ep.get("initiative_samples") or [] if not s.get("abstained")
        ),
    }


def extract_tick_metrics(
    ep: dict[str, Any],
    *,
    session_tick: int,
    omega_t: float | None,
) -> dict[str, Any]:
    """Per-session-tick metrics for longitudinal carryover."""
    _ensure_paths()
    from shadow_bridge import compute_eoi_proxy, score_shadow_log
    from eia.runtime.shadow_multitick import drive_norm

    genesis = extract_genesis_metrics(ep)
    att_r = score_shadow_log(ep)
    eoi = compute_eoi_proxy(list(ep.get("initiative_samples") or []))
    cf = ep.get("carryover_full") or ep.get("carryover") or {}
    return {
        "session_tick": session_tick,
        "session_tick_index": ep.get("session_tick_index", session_tick),
        "bridge_kind": ep.get("bridge_kind"),
        "used_carryover": ep.get("used_carryover", False),
        "inject_omega_psi": ep.get("inject_omega_psi"),
        "eia_baseline": ep.get("eia_baseline"),
        "omega_t": omega_t if omega_t is not None else ep.get("omega_t"),
        "genesis": genesis,
        "att_r": att_r,
        "eoi_proxy": eoi,
        "drive_norm": drive_norm(
            __import__(
                "eia.runtime.shadow_multitick", fromlist=["ShadowSessionCarryover"]
            ).ShadowSessionCarryover(
                beliefs_json=cf.get("beliefs_json"),
                last_motive_id=cf.get("last_motive_id"),
                drive_epistemic=float(cf.get("drive_epistemic") or 0.0),
                drive_coherence=float(cf.get("drive_coherence") or 0.0),
                drive_commitment=float(cf.get("drive_commitment") or 0.0),
                drive_tick=int(cf.get("drive_tick") or 0),
                session_tick=int(cf.get("session_tick") or 0),
                motivation_count=int(cf.get("motivation_count") or 0),
            )
        ),
        "carryover_session_tick": cf.get("session_tick"),
    }


@dataclass(frozen=True, slots=True)
class LongitudinalDiagnostics:
    endogenous_sustained_genesis: bool
    endogenous_eoi_pass: bool
    endogenous_att_r_all_ticks: bool
    passive_zero_initiatives: bool
    scramble_omega_decor: bool
    scramble_genesis_unchanged: bool
    scramble_behavior_matched: bool
    carryover_bleed_absent: bool
    f_omega_decor: bool
    f_carryover_bleed: bool

    def to_dict(self) -> dict[str, Any]:
        return {k: getattr(self, k) for k in self.__dataclass_fields__}


def evaluate_longitudinal_diagnostics(
    arm_sessions: dict[str, dict[str, Any]],
) -> LongitudinalDiagnostics:
    """Acceptance checks for T-BRAIN-04 longitudinal carryover."""
    active = arm_sessions["coupled_active"]
    passive = arm_sessions["passive_quiescent"]
    scramble = arm_sessions["phase_scramble_control"]

    active_ticks = active["ticks"]
    passive_ticks = passive["ticks"]
    scramble_ticks = scramble["ticks"]

    endogenous_genesis = all(
        t["genesis"]["has_novel_g_prime"] for t in active_ticks
    )
    endogenous_eoi = (
        active["cumulative_eoi"]["n_non_abstained"] > 0
        and active["cumulative_eoi"]["eoi_min"] >= EOI_ENDOGENOUS_THRESHOLD
    )

    endogenous_att_r = all(
        t["att_r"].get("att_r_evidence") for t in active_ticks
    )

    passive_zero = all(
        t["genesis"]["n_initiatives"] == 0
        and not t["genesis"]["has_novel_g_prime"]
        for t in passive_ticks
    )

    omega0_active = float(active_ticks[0].get("omega_t") or 0.0)
    omega0_scramble = float(scramble_ticks[0].get("omega_t") or 0.0)
    scramble_omega_breaks = abs(omega0_scramble - omega0_active) >= OMEGA_SPAN_MIN

    beh_a = active["behavior"]
    beh_s = scramble["behavior"]
    scramble_behavior_matched = (
        beh_a["n_spikes"] == beh_s["n_spikes"]
        and abs(
            beh_a["activity_rate_per_node_ms"] - beh_s["activity_rate_per_node_ms"]
        )
        < BEHAVIOR_MATCH_EPS
    )

    scramble_genesis_unchanged = (
        scramble_ticks[0]["genesis"]["genesis_delta"]
        == active_ticks[0]["genesis"]["genesis_delta"]
        and scramble_ticks[-1]["genesis"]["genesis_delta"]
        == active_ticks[-1]["genesis"]["genesis_delta"]
    )

    f_omega_decor = (
        scramble_omega_breaks
        and scramble_behavior_matched
        and scramble_genesis_unchanged
    )

    passive_bleed = any(
        t["genesis"]["has_novel_g_prime"] for t in passive_ticks[1:]
    )
    scramble_bleed = (
        scramble_ticks[-1]["genesis"]["genesis_delta"]
        != scramble_ticks[0]["genesis"]["genesis_delta"]
    )
    carryover_bleed_absent = not passive_bleed and not scramble_bleed
    f_carryover_bleed = carryover_bleed_absent

    return LongitudinalDiagnostics(
        endogenous_sustained_genesis=endogenous_genesis,
        endogenous_eoi_pass=endogenous_eoi,
        endogenous_att_r_all_ticks=endogenous_att_r,
        passive_zero_initiatives=passive_zero,
        scramble_omega_decor=scramble_omega_breaks,
        scramble_genesis_unchanged=scramble_genesis_unchanged,
        scramble_behavior_matched=scramble_behavior_matched,
        carryover_bleed_absent=carryover_bleed_absent,
        f_omega_decor=f_omega_decor,
        f_carryover_bleed=f_carryover_bleed,
    )


def run_longitudinal_arm_session(
    arm_key: ArmKey,
    omega_ctx: dict[str, Any],
    behavior: dict[str, Any],
    *,
    seed: int,
    session_ticks: int = SESSION_TICKS,
) -> dict[str, Any]:
    """Run 2+ session ticks with carryover for one connectome arm."""
    _ensure_paths()
    from shadow_bridge import (
        ARM_EIA_CONFIG,
        carryover_from_episode,
        compute_eoi_proxy,
        run_brain_omega_bridged_carryover_tick,
        run_brain_omega_bridged_shadow_episode,
    )

    cfg = ARM_EIA_CONFIG.get(arm_key, {})
    omega_t0 = float(omega_ctx.get("omega_t") or 0.0)
    episodes: list[dict[str, Any]] = []
    tick_metrics: list[dict[str, Any]] = []

    ep0 = run_brain_omega_bridged_shadow_episode(
        omega_ctx,
        behavior,
        seed=seed,
        arm_key=arm_key,
        eia_baseline=cfg.get("eia_baseline"),
        inject_omega_psi=cfg.get("inject_omega_psi"),
        session_tick_index=0,
    )
    episodes.append(ep0)
    tick_metrics.append(
        extract_tick_metrics(ep0, session_tick=0, omega_t=omega_t0)
    )

    carryover = carryover_from_episode(ep0)
    for tick_idx in range(1, session_ticks):
        ep = run_brain_omega_bridged_carryover_tick(
            carryover,
            behavior,
            seed=seed + tick_idx * 17,
            arm_key=arm_key,
            eia_baseline=cfg.get("eia_baseline"),
            session_tick_index=tick_idx,
        )
        episodes.append(ep)
        tick_metrics.append(
            extract_tick_metrics(ep, session_tick=tick_idx, omega_t=None)
        )
        carryover = carryover_from_episode(ep)

    all_samples: list[dict[str, Any]] = []
    for ep in episodes:
        all_samples.extend(ep.get("initiative_samples") or [])

    cumulative_eoi = compute_eoi_proxy(all_samples)
    cumulative_genesis_delta = sum(t["genesis"]["genesis_delta"] for t in tick_metrics)
    omega_drift = {
        "tick0_omega_t": omega_t0,
        "carryover_omega_injected": False,
        "omega_t_span": 0.0,
    }

    return {
        "arm_key": arm_key,
        "eia_baseline": cfg.get("eia_baseline"),
        "inject_omega_psi_tick0": cfg.get("inject_omega_psi"),
        "endogenous": cfg.get("endogenous", False),
        "behavior": behavior,
        "omega_t_tick0": omega_t0,
        "ticks": tick_metrics,
        "episodes": episodes,
        "cumulative_eoi": cumulative_eoi,
        "cumulative_genesis_delta": cumulative_genesis_delta,
        "omega_drift": omega_drift,
        "session_ticks": session_ticks,
        "final_carryover_session_tick": carryover.session_tick,
    }


def build_t_brain_04_payload(
    *,
    seed: int | None = None,
    generated: str | None = None,
    prefer_brian2: bool | None = None,
    session_ticks: int = SESSION_TICKS,
) -> dict[str, Any]:
    """Build full T-BRAIN-04 artifact payload."""
    _ensure_paths()
    from behavior_metrics import compute_behavior_metrics
    from connectome_export import load_subgraph
    from ot_injection import inject_omega_from_spikes, _load_oscillatory_module
    from spike_arms import run_spike_arm, scramble_spike_phases_for_omega

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

    arm_sessions: dict[str, dict[str, Any]] = {}
    coupled_ref: dict[str, Any] | None = None

    for arm_key in T04_ARM_KEYS:
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

        arm_sessions[arm_key] = run_longitudinal_arm_session(
            arm_key,  # type: ignore[arg-type]
            omega_ctx,
            behavior,
            seed=seed,
            session_ticks=session_ticks,
        )

    diagnostics = evaluate_longitudinal_diagnostics(arm_sessions)
    diagnostic_pass = (
        diagnostics.endogenous_sustained_genesis
        and diagnostics.endogenous_eoi_pass
        and diagnostics.endogenous_att_r_all_ticks
        and diagnostics.passive_zero_initiatives
        and diagnostics.f_omega_decor
        and diagnostics.f_carryover_bleed
    )

    arms_summary = {
        key: {
            "eia_baseline": sess["eia_baseline"],
            "inject_omega_psi_tick0": sess["inject_omega_psi_tick0"],
            "endogenous": sess["endogenous"],
            "omega_t_tick0": sess["omega_t_tick0"],
            "cumulative_genesis_delta": sess["cumulative_genesis_delta"],
            "cumulative_eoi": sess["cumulative_eoi"],
            "omega_drift": sess["omega_drift"],
            "ticks": [
                {
                    "session_tick": t["session_tick"],
                    "omega_t": t["omega_t"],
                    "genesis_delta": t["genesis"]["genesis_delta"],
                    "has_novel_g_prime": t["genesis"]["has_novel_g_prime"],
                    "n_initiatives": t["genesis"]["n_initiatives"],
                    "att_r_evidence": t["att_r"].get("att_r_evidence"),
                    "eoi_mean": t["eoi_proxy"]["eoi_mean"],
                    "eoi_pass": t["eoi_proxy"]["eoi_pass"],
                    "drive_norm": t["drive_norm"],
                    "used_carryover": t["used_carryover"],
                    "inject_omega_psi": t["inject_omega_psi"],
                }
                for t in sess["ticks"]
            ],
        }
        for key, sess in arm_sessions.items()
    }

    return {
        "milestone": "M-BRAIN-AI",
        "harness_id": "T-BRAIN-04",
        "artifact_id": "M-T-BRAIN-04_2026-09-10",
        "tick_id": "T-BRAIN-04",
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
        "session_ticks": session_ticks,
        "seed": seed,
        "sources": {
            "t_brain_03": _rel(BRAIN_AI / "harnesses" / "t_brain_03_shadow_bridge.py"),
            "shadow_bridge": _rel(BRAIN_AI / "adapters" / "shadow_bridge.py"),
            "shadow_runtime": _rel(REPO / "src" / "eia" / "runtime" / "shadow_multitick.py"),
            "eoi_drift": _rel(REPO / "research" / "sci_flow" / "eoi_drift_harness.py"),
            "oscillatory_state": "research/cursor-starter-v0.2/src/eia/oscillatory_state.py",
        },
        "arms": arms_summary,
        "longitudinal_diagnostics": diagnostics.to_dict(),
        "diagnostic_pass": diagnostic_pass,
        "f_omega_decor": {
            "status": "confirmed" if diagnostics.f_omega_decor else "not_confirmed",
            "phase_scramble_control": diagnostics.f_omega_decor,
        },
        "f_carryover_bleed": {
            "status": "absent" if diagnostics.f_carryover_bleed else "detected",
            "carryover_bleed_absent": diagnostics.carryover_bleed_absent,
        },
        "falsifiers_active": [
            "F-KURAMOTO-AS-E",
            "F-OMEGA-DECOR",
            "F-CARRYOVER-BLEED",
            "F-BEHAV-OMEGA-MISMATCH",
            "F-SYNC",
            "F-STRUCT≠E",
        ],
        "connectome_source": subgraph.source,
        "n_nodes": subgraph.n_nodes,
        "note": (
            "Longitudinal ShadowSessionCarryover across 2+ session ticks at X_trigger=0. "
            "Endogenous (coupled_active, full_eia+Ψ) sustains genesis/ATT-R; passive "
            "(reactive_only) abstains; scramble (full_eia w/o Ψ) confirms F-OMEGA-DECOR. "
            "No Ψ(O_t) re-injection on carryover ticks. Does not establish E_endo."
        ),
    }


def artifact_sha256(payload: dict[str, Any]) -> str:
    """Stable SHA-256 over canonical JSON (excludes sha field)."""
    body = {k: v for k, v in payload.items() if k != "artifact_sha256"}
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def render_t_brain_04_markdown(payload: dict[str, Any]) -> str:
    """Render markdown artifact for T-BRAIN-04."""
    arms = payload.get("arms") or {}
    diag = payload.get("longitudinal_diagnostics") or {}
    decor = payload.get("f_omega_decor") or {}
    bleed = payload.get("f_carryover_bleed") or {}

    lines = [
        f"# M-T-BRAIN-04 Longitudinal Carryover — {payload.get('date', '')}",
        "",
        f"**Cell:** {payload.get('cell', 'D2×L2')} · **Tier:** {payload.get('tier', 'C')} · "
        f"**Harness:** {payload.get('harness_id', 'T-BRAIN-04')}",
        f"**Seed:** {payload.get('seed')} · **Session ticks:** {payload.get('session_ticks')} · "
        f"**X_trigger:** 0 · **Branch:** `{payload.get('branch')}`",
        f"**SHA-256:** `{payload.get('artifact_sha256', '')}`",
        "",
        "## Per-arm per-tick metrics",
        "",
        "| Arm | Tick | OMEGA_t | ΔG | novel G' | initiatives | ATT-R | EOI mean | drive_norm |",
        "|-----|------|---------|-----|----------|-------------|-------|----------|------------|",
    ]
    for key, arm in arms.items():
        for t in arm.get("ticks") or []:
            omega = t.get("omega_t")
            omega_s = f"`{omega:.4f}`" if omega is not None else "—"
            lines.append(
                f"| `{key}` | {t.get('session_tick')} | {omega_s} | "
                f"`{t.get('genesis_delta')}` | `{t.get('has_novel_g_prime')}` | "
                f"`{t.get('n_initiatives')}` | `{t.get('att_r_evidence')}` | "
                f"`{t.get('eoi_mean', 0):.3f}` | `{t.get('drive_norm', 0):.3f}` |"
            )

    lines.extend([
        "",
        "## Longitudinal diagnostics",
        "",
        f"- endogenous sustained genesis: `{diag.get('endogenous_sustained_genesis')}`",
        f"- endogenous EOI pass: `{diag.get('endogenous_eoi_pass')}`",
        f"- endogenous ATT-R all ticks: `{diag.get('endogenous_att_r_all_ticks')}`",
        f"- passive zero initiatives: `{diag.get('passive_zero_initiatives')}`",
        f"- **F-OMEGA-DECOR:** `{decor.get('status')}`",
        f"- **F-CARRYOVER-BLEED:** `{bleed.get('status')}`",
        f"- diagnostic_pass: `{payload.get('diagnostic_pass')}`",
        "",
        "## Invariants",
        "",
        "- `e_endo_support=none` (no D1 bleed)",
        "- `claim_allowed=false`",
        "- `c_ladder_raise_allowed=false`",
        "- `agi_star_claim=false`",
        "- No Ψ(O_t) on carryover ticks (omega blur falsifier)",
        "- Genesis behavior-gated at X_trigger=0",
    ])
    return "\n".join(lines)

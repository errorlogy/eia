"""T-BRAIN-06 — Integrated EIA modeling across connectome sources.

Full pipeline per source (``google_male_cns`` | ``flywire_female`` | ``bundled_tiny`` |
``synthetic``):

  connectome → spike dynamics → OMEGA_t + behavior
  → shadow bridge (X_trigger=0) → 2-tick longitudinal carryover
  → EIA metrics (genesis_Δ, EOI, ATT-R, drive_norm)

Compares **endogenous embodied** (``coupled_active``, full_eia + Ψ) vs **passive**
(``passive_quiescent``, reactive_only) per source.

Honest framing: Drosophila connectome substrate (Google MaleCNS / FlyWire) —
**not** mammalian neocortex. Tier C · ``claim_allowed=false`` · C2 ceiling.
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

from t_brain_04_longitudinal_carryover import (
    EOI_ENDOGENOUS_THRESHOLD,
    SESSION_TICKS,
    load_config,
    run_longitudinal_arm_session,
)
from t_brain_05_connectome_parity import (
    OMEGA_SPAN_MIN,
    PARITY_SOURCES,
    SOURCE_SEED_OFFSET,
    source_fallback_info,
)

BRAIN_AI = Path(__file__).resolve().parents[1]
REPO = BRAIN_AI.parents[1]
ADAPTERS = BRAIN_AI / "adapters"
ARTIFACTS = BRAIN_AI / "artifacts"
ARTIFACT_JSON = ARTIFACTS / "M-T-BRAIN-06_2026-09-11.json"
ARTIFACT_MD = ARTIFACTS / "M-T-BRAIN-06_2026-09-11.md"
CONFIG_PATH = BRAIN_AI / "config.yaml"
BRANCH = "research/brain-ai-connectome"

INTEGRATED_ARMS: tuple[str, ...] = (
    "coupled_active",
    "passive_quiescent",
)

ENDOGENOUS_ARM = "coupled_active"
PASSIVE_ARM = "passive_quiescent"
HARNESS_ID = "T-BRAIN-06"
MILESTONE = "M-BRAIN-AI"


def _ensure_paths() -> None:
    for path in (str(ADAPTERS), str(REPO / "src")):
        if path not in sys.path:
            sys.path.insert(0, path)


def _rel(path: Path) -> str:
    try:
        return path.relative_to(REPO).as_posix()
    except ValueError:
        return path.as_posix()


ArmKey = Literal["coupled_active", "passive_quiescent"]


def _summarize_arm_session(sess: dict[str, Any]) -> dict[str, Any]:
    """Compact per-arm summary for artifact payload."""
    ticks = []
    for t in sess["ticks"]:
        ticks.append({
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
        })
    return {
        "arm_key": sess["arm_key"],
        "eia_baseline": sess["eia_baseline"],
        "inject_omega_psi_tick0": sess["inject_omega_psi_tick0"],
        "endogenous": sess["endogenous"],
        "omega_t_tick0": sess["omega_t_tick0"],
        "cumulative_genesis_delta": sess["cumulative_genesis_delta"],
        "cumulative_eoi": sess["cumulative_eoi"],
        "ticks": ticks,
    }


def compute_separation_score(
    endogenous: dict[str, Any],
    passive: dict[str, Any],
) -> dict[str, Any]:
    """Endogenous vs passive separation on genesis and EOI."""
    endo_gen = float(endogenous["cumulative_genesis_delta"])
    pass_gen = float(passive["cumulative_genesis_delta"])
    endo_eoi = float((endogenous["cumulative_eoi"] or {}).get("eoi_min") or 0.0)
    pass_eoi = float((passive["cumulative_eoi"] or {}).get("eoi_min") or 0.0)
    genesis_sep = endo_gen - pass_gen
    eoi_sep = endo_eoi - pass_eoi
    return {
        "genesis_separation": genesis_sep,
        "eoi_separation": eoi_sep,
        "endogenous_genesis_delta": endo_gen,
        "passive_genesis_delta": pass_gen,
        "endogenous_eoi_min": endo_eoi,
        "passive_eoi_min": pass_eoi,
        "endogenous_gt_passive_genesis": endo_gen > pass_gen,
        "endogenous_gt_passive_eoi": endo_eoi > pass_eoi,
        "separation_score": genesis_sep + eoi_sep,
    }


def run_source_integrated_probe(
    source_key: str,
    *,
    seed: int,
    n_nodes: int,
    duration_ms: float,
    dt_ms: float,
    prefer_brian2: bool,
    carriers: tuple[float, ...],
    session_ticks: int = SESSION_TICKS,
) -> dict[str, Any]:
    """Run full integrated pipeline for one connectome source."""
    _ensure_paths()
    from behavior_metrics import compute_behavior_metrics
    from connectome_export import load_subgraph
    from ot_injection import inject_omega_from_spikes
    from spike_arms import run_spike_arm

    src_seed = seed + SOURCE_SEED_OFFSET.get(source_key, 0)
    fallback = source_fallback_info(source_key)
    subgraph = load_subgraph(
        connectome_source=source_key,
        n_nodes=n_nodes,
        seed=src_seed,
        prefer_bundled=(source_key == "bundled_tiny"),
    )

    arm_sessions: dict[str, dict[str, Any]] = {}
    coupled_ref: dict[str, Any] | None = None

    for arm_key in INTEGRATED_ARMS:
        spike_payload = run_spike_arm(
            subgraph,
            arm_key,  # type: ignore[arg-type]
            seed=src_seed,
            duration_ms=duration_ms,
            dt_ms=dt_ms,
            prefer_brian2=prefer_brian2,
            coupled_reference=coupled_ref,
        )
        if arm_key == ENDOGENOUS_ARM:
            coupled_ref = spike_payload
        behavior = compute_behavior_metrics(spike_payload)
        omega_ctx = inject_omega_from_spikes(
            spike_payload, subgraph.node_ids, carriers=carriers
        )
        omega_ctx["arm"] = arm_key

        arm_sessions[arm_key] = run_longitudinal_arm_session(
            arm_key,  # type: ignore[arg-type]
            omega_ctx,
            behavior,
            seed=src_seed,
            session_ticks=session_ticks,
        )

    endo = arm_sessions[ENDOGENOUS_ARM]
    passive = arm_sessions[PASSIVE_ARM]
    separation = compute_separation_score(endo, passive)

    return {
        "source_key": source_key,
        "connectome_source_tag": subgraph.source,
        "n_nodes": subgraph.n_nodes,
        "source_fallback": fallback,
        "seed_used": src_seed,
        "omega_t_endogenous": endo["omega_t_tick0"],
        "omega_t_passive": passive["omega_t_tick0"],
        "arms": {
            key: _summarize_arm_session(sess) for key, sess in arm_sessions.items()
        },
        "separation": separation,
    }


@dataclass(frozen=True, slots=True)
class IntegratedDiagnostics:
    per_source_endogenous_pass: bool
    omega_span_measurable: bool
    genesis_span_measurable: bool
    all_omega_valid: bool
    invariants_ok: bool

    def to_dict(self) -> dict[str, Any]:
        return {k: getattr(self, k) for k in self.__dataclass_fields__}


def evaluate_integrated_diagnostics(
    probes: list[dict[str, Any]],
    *,
    omega_span: float,
    genesis_span: float,
) -> IntegratedDiagnostics:
    """Acceptance checks for T-BRAIN-06 integrated EIA modeling."""
    per_source_pass = all(
        p["separation"]["endogenous_gt_passive_genesis"]
        and p["separation"]["endogenous_gt_passive_eoi"]
        for p in probes
    )

    omega_values = []
    for p in probes:
        omega_values.append(float(p["omega_t_endogenous"]))
        omega_values.append(float(p["omega_t_passive"]))
    all_omega_valid = all(0.0 <= v <= 1.0 for v in omega_values)

    return IntegratedDiagnostics(
        per_source_endogenous_pass=per_source_pass,
        omega_span_measurable=omega_span >= OMEGA_SPAN_MIN,
        genesis_span_measurable=genesis_span > 0.0,
        all_omega_valid=all_omega_valid,
        invariants_ok=True,
    )


def build_t_brain_06_payload(
    *,
    seed: int | None = None,
    generated: str | None = None,
    prefer_brian2: bool | None = None,
    session_ticks: int = SESSION_TICKS,
    sources: tuple[str, ...] | None = None,
) -> dict[str, Any]:
    """Build full T-BRAIN-06 integrated EIA artifact payload."""
    _ensure_paths()

    cfg = load_config()
    sim = cfg.get("simulation") or {}
    conn = cfg.get("connectome") or {}
    seed = int(seed if seed is not None else sim.get("seed", 42))
    prefer_brian2 = (
        prefer_brian2 if prefer_brian2 is not None else bool(sim.get("prefer_brian2", False))
    )
    n_nodes = int(sim.get("n_nodes", 8))
    max_nodes = int(conn.get("max_subgraph_nodes", 500))
    n_nodes = min(n_nodes, max_nodes)
    duration_ms = float(sim.get("duration_ms", 100.0))
    dt_ms = float(sim.get("dt_ms", 1.0))
    carriers = tuple(cfg.get("carriers_hz") or [20, 30, 42, 70])
    source_list = tuple(sources or PARITY_SOURCES)

    probes: list[dict[str, Any]] = []
    for source_key in source_list:
        probe = run_source_integrated_probe(
            source_key,
            seed=seed,
            n_nodes=n_nodes,
            duration_ms=duration_ms,
            dt_ms=dt_ms,
            prefer_brian2=prefer_brian2,
            carriers=carriers,
            session_ticks=session_ticks,
        )
        probes.append(probe)

    omega_values = [float(p["omega_t_endogenous"]) for p in probes]
    genesis_values = [
        float(p["separation"]["endogenous_genesis_delta"]) for p in probes
    ]
    omega_span = max(omega_values) - min(omega_values) if omega_values else 0.0
    genesis_span = max(genesis_values) - min(genesis_values) if genesis_values else 0.0

    diagnostics = evaluate_integrated_diagnostics(
        probes, omega_span=omega_span, genesis_span=genesis_span
    )
    diagnostic_pass = (
        diagnostics.per_source_endogenous_pass
        and diagnostics.omega_span_measurable
        and diagnostics.all_omega_valid
        and diagnostics.invariants_ok
    )

    per_source = {p["source_key"]: p for p in probes}
    separation_scores = [p["separation"]["separation_score"] for p in probes]
    mean_separation = (
        sum(separation_scores) / len(separation_scores) if separation_scores else 0.0
    )

    any_fallback = any(p["source_fallback"]["fallback"] for p in probes)
    run_mode = "mixed" if any_fallback else "offline_exports"

    return {
        "milestone": MILESTONE,
        "harness_id": HARNESS_ID,
        "artifact_id": "M-T-BRAIN-06_2026-09-11",
        "tick_id": HARNESS_ID,
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
        "run_mode": run_mode,
        "substrate_framing": {
            "biological_scope": "drosophila_cns",
            "not_mammalian_neocortex": True,
            "google_male_cns": "MaleCNS v1.0 (Cell 2026, neuPrint male-cns:v1.0)",
            "flywire_female": "FlyWire v783 female brain",
            "horizon": "zebrafish/mouse connectomics (Google blog roadmap)",
        },
        "sources": {
            "connectome_export": _rel(BRAIN_AI / "adapters" / "connectome_export.py"),
            "shadow_bridge": _rel(BRAIN_AI / "adapters" / "shadow_bridge.py"),
            "t_brain_03": _rel(BRAIN_AI / "harnesses" / "t_brain_03_shadow_bridge.py"),
            "t_brain_04": _rel(BRAIN_AI / "harnesses" / "t_brain_04_longitudinal_carryover.py"),
            "t_brain_05": _rel(BRAIN_AI / "harnesses" / "t_brain_05_connectome_parity.py"),
            "oscillatory_state": "research/cursor-starter-v0.2/src/eia/oscillatory_state.py",
        },
        "connectome_sources": list(source_list),
        "arms_compared": list(INTEGRATED_ARMS),
        "per_source": per_source,
        "aggregate_metrics": {
            "omega_t_min": min(omega_values) if omega_values else None,
            "omega_t_max": max(omega_values) if omega_values else None,
            "omega_span": omega_span,
            "genesis_delta_min": min(genesis_values) if genesis_values else None,
            "genesis_delta_max": max(genesis_values) if genesis_values else None,
            "genesis_span": genesis_span,
            "mean_endogenous_passive_separation": mean_separation,
            "eoi_endogenous_threshold": EOI_ENDOGENOUS_THRESHOLD,
        },
        "integrated_diagnostics": diagnostics.to_dict(),
        "diagnostic_pass": diagnostic_pass,
        "falsifiers_active": [
            "F-SOURCE-PARITY",
            "F-OMEGA-DECOR",
            "F-CARRYOVER-BLEED",
            "F-KURAMOTO-AS-E",
            "F-STRUCT≠E",
            "F-ENDO-PASSIVE-COLLAPSE",
        ],
        "claim_invariants": {
            "claim_allowed": False,
            "e_endo_support": "none",
            "c_ladder_raise_allowed": False,
            "agi_star_claim": False,
            "tier": "C",
            "claim_ceiling": "C2",
        },
        "note": (
            "Integrated connectome-grounded EIA modeling: per-source endogenous "
            "(coupled_active, full_eia+Ψ) vs passive (reactive_only) with 2-tick "
            "shadow carryover at X_trigger=0. Drosophila connectome substrate — "
            "not mammalian neocortex. Does not establish E_endo or raise C-level."
        ),
    }


def artifact_sha256(payload: dict[str, Any]) -> str:
    """Stable SHA-256 over canonical JSON (excludes sha field)."""
    body = {k: v for k, v in payload.items() if k != "artifact_sha256"}
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def render_t_brain_06_markdown(payload: dict[str, Any]) -> str:
    """Render markdown artifact for T-BRAIN-06."""
    per_source = payload.get("per_source") or {}
    agg = payload.get("aggregate_metrics") or {}
    diag = payload.get("integrated_diagnostics") or {}
    framing = payload.get("substrate_framing") or {}

    lines = [
        f"# M-T-BRAIN-06 Integrated EIA Modeling — {payload.get('date', '')}",
        "",
        f"**Cell:** {payload.get('cell', 'D2×L2')} · **Tier:** {payload.get('tier', 'C')} · "
        f"**Harness:** {payload.get('harness_id', HARNESS_ID)}",
        f"**Seed:** {payload.get('seed')} · **Session ticks:** {payload.get('session_ticks')} · "
        f"**Run mode:** `{payload.get('run_mode')}` · **Branch:** `{payload.get('branch')}`",
        f"**SHA-256:** `{payload.get('artifact_sha256', '')}`",
        "",
        "## Substrate framing (honest scope)",
        "",
        f"- Biological scope: **{framing.get('biological_scope')}** (not mammalian neocortex)",
        f"- Google MaleCNS: {framing.get('google_male_cns')}",
        f"- FlyWire female: {framing.get('flywire_female')}",
        f"- Horizon: {framing.get('horizon')}",
        "",
        "## Per-source per-arm per-tick metrics",
        "",
        "| Source | Arm | Tick | OMEGA_t | ΔG | ATT-R | EOI mean | drive_norm |",
        "|--------|-----|------|---------|-----|-------|----------|------------|",
    ]
    for key, src in per_source.items():
        for arm_key, arm in (src.get("arms") or {}).items():
            for t in arm.get("ticks") or []:
                omega = t.get("omega_t")
                omega_s = f"`{omega:.4f}`" if omega is not None else "—"
                lines.append(
                    f"| `{key}` | `{arm_key}` | {t.get('session_tick')} | {omega_s} | "
                    f"`{t.get('genesis_delta')}` | `{t.get('att_r_evidence')}` | "
                    f"`{t.get('eoi_mean', 0):.3f}` | `{t.get('drive_norm', 0):.3f}` |"
                )

    lines.extend([
        "",
        "## Endogenous vs passive separation (per source)",
        "",
        "| Source | endo ΔG | passive ΔG | genesis_sep | endo EOI | passive EOI | eoi_sep | pass |",
        "|--------|---------|------------|-------------|----------|-------------|---------|------|",
    ])
    for key, src in per_source.items():
        sep = src.get("separation") or {}
        pass_ok = (
            sep.get("endogenous_gt_passive_genesis")
            and sep.get("endogenous_gt_passive_eoi")
        )
        lines.append(
            f"| `{key}` | `{sep.get('endogenous_genesis_delta')}` | "
            f"`{sep.get('passive_genesis_delta')}` | `{sep.get('genesis_separation')}` | "
            f"`{sep.get('endogenous_eoi_min', 0):.3f}` | `{sep.get('passive_eoi_min', 0):.3f}` | "
            f"`{sep.get('eoi_separation', 0):.3f}` | `{pass_ok}` |"
        )

    lines.extend([
        "",
        "## Aggregate spans",
        "",
        f"- omega_span: `{agg.get('omega_span')}` (min `{agg.get('omega_t_min')}`, "
        f"max `{agg.get('omega_t_max')}`)",
        f"- genesis_span: `{agg.get('genesis_span')}`",
        f"- mean endogenous-passive separation: `{agg.get('mean_endogenous_passive_separation')}`",
        "",
        "## Integrated diagnostics",
        "",
        f"- per-source endogenous > passive (genesis + EOI): `{diag.get('per_source_endogenous_pass')}`",
        f"- omega span measurable: `{diag.get('omega_span_measurable')}`",
        f"- genesis span across sources: `{agg.get('genesis_span')}` "
        f"(informational; behavior-gated genesis may be uniform)",
        f"- all OMEGA in [0,1]: `{diag.get('all_omega_valid')}`",
        f"- diagnostic_pass: `{payload.get('diagnostic_pass')}`",
        "",
        "## Claim invariants",
        "",
        "- `e_endo_support=none` (no D1 bleed)",
        "- `claim_allowed=false`",
        "- `c_ladder_raise_allowed=false`",
        "- `agi_star_claim=false`",
        "- Fly connectome ≠ neocortex; Google/Janelia as empirical substrate anchor",
        "- Genesis behavior-gated at X_trigger=0; Kuramoto R ≠ E_endo",
    ])
    return "\n".join(lines)

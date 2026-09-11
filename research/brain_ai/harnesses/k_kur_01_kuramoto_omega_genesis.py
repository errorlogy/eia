"""K-KUR-01 — Kuramoto R vs OMEGA_t vs genesis_Δ on T-BRAIN-06 arms/sources.

Tier C Kairologos explore battery: correlate oscillatory descriptors with shadow
genesis at X_trigger=0. Tests F-KURAMOTO-AS-E (high R without genesis linkage)
and F-OMEGA-DECOR adjunct. Does not establish E_endo.
"""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import yaml

BRAIN_AI = Path(__file__).resolve().parents[1]
REPO = BRAIN_AI.parents[1]
KAIRO = REPO / "research" / "kairologos_experiments"
ADAPTERS = BRAIN_AI / "adapters"
ARTIFACTS = KAIRO / "artifacts"
ARTIFACT_JSON = ARTIFACTS / "M-K-KUR-01_2026-09-11.json"
ARTIFACT_MD = ARTIFACTS / "M-K-KUR-01_2026-09-11.md"
CONFIG_PATH = BRAIN_AI / "config.yaml"
BRANCH = "main"

KURAMOTO_HIGH = 0.85
OMEGA_DECOR_THRESHOLD = 0.75
GENESIS_EPSILON = 1e-9
HARNESS_ID = "K-KUR-01"
MILESTONE = "M-KAIRO-TIER-C"

PROBE_ARMS: tuple[str, ...] = (
    "coupled_active",
    "passive_quiescent",
    "phase_scramble_control",
)


def _ensure_paths() -> None:
    for path in (str(ADAPTERS), str(BRAIN_AI / "harnesses"), str(REPO / "src")):
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


@dataclass(frozen=True, slots=True)
class KurOmegaGenesisCorrelation:
    r_kuramoto_genesis: float | None
    r_omega_genesis: float | None
    r_kuramoto_omega: float | None
    kuramoto_span: float
    omega_span: float
    genesis_span: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "r_kuramoto_genesis": (
                round(self.r_kuramoto_genesis, 6)
                if self.r_kuramoto_genesis is not None
                else None
            ),
            "r_omega_genesis": (
                round(self.r_omega_genesis, 6) if self.r_omega_genesis is not None else None
            ),
            "r_kuramoto_omega": (
                round(self.r_kuramoto_omega, 6) if self.r_kuramoto_omega is not None else None
            ),
            "kuramoto_span": round(self.kuramoto_span, 6),
            "omega_span": round(self.omega_span, 6),
            "genesis_span": round(self.genesis_span, 6),
        }


def evaluate_correlations(rows: list[dict[str, Any]]) -> KurOmegaGenesisCorrelation:
    from behavior_metrics import pearson_r

    kuramoto = [float(r["kuramoto_r"]) for r in rows]
    omega = [float(r["omega_t"]) for r in rows]
    genesis = [float(r["genesis_delta"]) for r in rows]
    return KurOmegaGenesisCorrelation(
        r_kuramoto_genesis=pearson_r(kuramoto, genesis),
        r_omega_genesis=pearson_r(omega, genesis),
        r_kuramoto_omega=pearson_r(kuramoto, omega),
        kuramoto_span=max(kuramoto) - min(kuramoto) if kuramoto else 0.0,
        omega_span=max(omega) - min(omega) if omega else 0.0,
        genesis_span=max(genesis) - min(genesis) if genesis else 0.0,
    )


def evaluate_falsifiers(
    rows: list[dict[str, Any]],
    *,
    osc_mod: Any,
) -> dict[str, Any]:
    f_kuramoto_as_e_rows: list[dict[str, Any]] = []
    f_omega_decor_rows: list[dict[str, Any]] = []
    for row in rows:
        r = float(row["kuramoto_r"])
        omega = float(row["omega_t"])
        genesis = float(row["genesis_delta"])
        if r >= KURAMOTO_HIGH and abs(genesis) <= GENESIS_EPSILON:
            f_kuramoto_as_e_rows.append(row)
        if osc_mod.falsifier_f_omega_decor(
            omega=omega, genesis_delta=genesis, omega_threshold=OMEGA_DECOR_THRESHOLD
        ):
            f_omega_decor_rows.append(row)
    return {
        "F-KURAMOTO-AS-E": {
            "status": "annotation" if f_kuramoto_as_e_rows else "absent",
            "firing_rows": len(f_kuramoto_as_e_rows),
            "high_r_without_genesis": bool(f_kuramoto_as_e_rows),
            "note": "Annotation only — Kuramoto R must not be read as E_endo",
        },
        "F-OMEGA-DECOR": {
            "status": "confirmed" if f_omega_decor_rows else "absent",
            "firing_rows": len(f_omega_decor_rows),
            "high_omega_without_genesis": bool(f_omega_decor_rows),
        },
    }


def run_source_kur_probe(
    source_key: str,
    *,
    seed: int,
    n_nodes: int,
    duration_ms: float,
    dt_ms: float,
    prefer_brian2: bool,
    carriers: tuple[float, ...],
    session_ticks: int,
) -> dict[str, Any]:
    """One connectome source × three arms × session ticks."""
    _ensure_paths()
    from behavior_metrics import compute_behavior_metrics
    from connectome_export import load_subgraph
    from ot_injection import inject_omega_from_spikes, _load_oscillatory_module
    from spike_arms import run_spike_arm, scramble_spike_phases_for_omega
    from t_brain_04_longitudinal_carryover import run_longitudinal_arm_session
    from t_brain_05_connectome_parity import SOURCE_SEED_OFFSET, source_fallback_info

    src_seed = seed + SOURCE_SEED_OFFSET.get(source_key, 0)
    fallback = source_fallback_info(source_key)
    subgraph = load_subgraph(
        connectome_source=source_key,
        n_nodes=n_nodes,
        seed=src_seed,
        prefer_bundled=(source_key == "bundled_tiny"),
    )
    osc_mod = _load_oscillatory_module()
    rows: list[dict[str, Any]] = []
    arm_summaries: dict[str, Any] = {}
    coupled_ref: dict[str, Any] | None = None

    for arm_key in PROBE_ARMS:
        spike_payload = run_spike_arm(
            subgraph,
            arm_key,  # type: ignore[arg-type]
            seed=src_seed,
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
                seed=src_seed + 99,
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
                "arm": arm_key,
            }
        else:
            omega_ctx = inject_omega_from_spikes(
                spike_payload, subgraph.node_ids, carriers=carriers, osc_mod=osc_mod
            )
            omega_ctx["arm"] = arm_key

        sess = run_longitudinal_arm_session(
            arm_key,  # type: ignore[arg-type]
            omega_ctx,
            behavior,
            seed=src_seed,
            session_ticks=session_ticks,
        )
        arm_summaries[arm_key] = {
            "kuramoto_r_tick0": omega_ctx["kuramoto_r"],
            "omega_t_tick0": omega_ctx["omega_t"],
            "cumulative_genesis_delta": sess["cumulative_genesis_delta"],
        }
        for tick in sess["ticks"]:
            omega_tick = tick["omega_t"]
            if omega_tick is None:
                omega_tick = omega_ctx["omega_t"]
            rows.append(
                {
                    "source_key": source_key,
                    "arm_key": arm_key,
                    "session_tick": tick["session_tick"],
                    "kuramoto_r": omega_ctx["kuramoto_r"],
                    "omega_t": float(omega_tick),
                    "genesis_delta": tick["genesis"]["genesis_delta"],
                    "has_novel_g_prime": tick["genesis"]["has_novel_g_prime"],
                }
            )

    return {
        "source_key": source_key,
        "connectome_source_tag": subgraph.source,
        "source_fallback": fallback,
        "rows": rows,
        "arm_summaries": arm_summaries,
    }


def build_k_kur_01_payload(
    *,
    seed: int | None = None,
    generated: str | None = None,
    prefer_brian2: bool | None = None,
    session_ticks: int = 2,
    sources: tuple[str, ...] | None = None,
) -> dict[str, Any]:
    _ensure_paths()
    from ot_injection import _load_oscillatory_module
    from t_brain_05_connectome_parity import PARITY_SOURCES

    cfg = load_config()
    sim = cfg.get("simulation") or {}
    conn = cfg.get("connectome") or {}
    seed = int(seed if seed is not None else sim.get("seed", 42))
    prefer_brian2 = (
        prefer_brian2 if prefer_brian2 is not None else bool(sim.get("prefer_brian2", False))
    )
    n_nodes = min(int(sim.get("n_nodes", 8)), int(conn.get("max_subgraph_nodes", 500)))
    duration_ms = float(sim.get("duration_ms", 100.0))
    dt_ms = float(sim.get("dt_ms", 1.0))
    carriers = tuple(cfg.get("carriers_hz") or [20, 30, 42, 70])
    source_list = tuple(sources or PARITY_SOURCES)
    osc_mod = _load_oscillatory_module()

    probes: list[dict[str, Any]] = []
    all_rows: list[dict[str, Any]] = []
    for source_key in source_list:
        probe = run_source_kur_probe(
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
        all_rows.extend(probe["rows"])

    correlation = evaluate_correlations(all_rows)
    falsifiers = evaluate_falsifiers(all_rows, osc_mod=osc_mod)
    per_source_corr = {
        p["source_key"]: evaluate_correlations(p["rows"]).to_dict() for p in probes
    }

    diagnostic_pass = (
        len(all_rows) > 0
        and correlation.kuramoto_span > 0.0
        and correlation.omega_span > 0.0
        and falsifiers["F-KURAMOTO-AS-E"]["status"] in ("annotation", "absent")
    )

    return {
        "milestone": MILESTONE,
        "harness_id": HARNESS_ID,
        "artifact_id": "M-K-KUR-01_2026-09-11",
        "tick_id": HARNESS_ID,
        "date": generated or date.today().isoformat(),
        "branch": BRANCH,
        "cell": "D2×L2",
        "tier": "C",
        "claim_ceiling": "C2",
        "ceiling": "C2",
        "theory_strand": "kairologos_explore",
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
            "t_brain_06": _rel(BRAIN_AI / "harnesses" / "t_brain_06_eia_integrated.py"),
            "t_brain_04": _rel(BRAIN_AI / "harnesses" / "t_brain_04_longitudinal_carryover.py"),
            "oscillatory_state": "research/cursor-starter-v0.2/src/eia/oscillatory_state.py",
        },
        "connectome_sources": list(source_list),
        "probe_arms": list(PROBE_ARMS),
        "per_source": {p["source_key"]: p for p in probes},
        "all_rows_count": len(all_rows),
        "correlation": correlation.to_dict(),
        "per_source_correlation": per_source_corr,
        "falsifiers": falsifiers,
        "diagnostic_pass": diagnostic_pass,
        "falsifiers_active": ["F-KURAMOTO-AS-E", "F-OMEGA-DECOR"],
        "claim_invariants": {
            "claim_allowed": False,
            "e_endo_support": "none",
            "tier": "C",
            "ceiling": "C2",
            "theory_strand": "kairologos_explore",
            "agi_star_claim": False,
        },
        "note": (
            "Kairologos Tier C probe: Kuramoto R and OMEGA_t correlated against shadow "
            "genesis_Δ on T-BRAIN-06 arms/sources. High R without genesis fires "
            "F-KURAMOTO-AS-E annotation only. Does not establish E_endo."
        ),
    }


def artifact_sha256(payload: dict[str, Any]) -> str:
    body = {k: v for k, v in payload.items() if k != "artifact_sha256"}
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def render_k_kur_01_markdown(payload: dict[str, Any]) -> str:
    corr = payload.get("correlation") or {}
    fals = payload.get("falsifiers") or {}
    lines = [
        f"# M-K-KUR-01 Kuramoto×OMEGA×genesis — {payload.get('date', '')}",
        "",
        f"**Harness:** {payload.get('harness_id')} · **Tier:** C · **Theory:** kairologos_explore",
        f"**SHA-256:** `{payload.get('artifact_sha256', '')}`",
        "",
        "## Cross-arm correlations",
        "",
        f"- r(Kuramoto R, genesis_Δ): `{corr.get('r_kuramoto_genesis')}`",
        f"- r(OMEGA_t, genesis_Δ): `{corr.get('r_omega_genesis')}`",
        f"- r(Kuramoto R, OMEGA_t): `{corr.get('r_kuramoto_omega')}`",
        f"- spans: R `{corr.get('kuramoto_span')}` · OMEGA `{corr.get('omega_span')}` · ΔG `{corr.get('genesis_span')}`",
        "",
        "## Falsifiers",
        "",
        f"- F-KURAMOTO-AS-E: `{fals.get('F-KURAMOTO-AS-E', {}).get('status')}` "
        f"({fals.get('F-KURAMOTO-AS-E', {}).get('firing_rows', 0)} rows)",
        f"- F-OMEGA-DECOR: `{fals.get('F-OMEGA-DECOR', {}).get('status')}` "
        f"({fals.get('F-OMEGA-DECOR', {}).get('firing_rows', 0)} rows)",
        "",
        f"**diagnostic_pass:** `{payload.get('diagnostic_pass')}`",
    ]
    return "\n".join(lines)

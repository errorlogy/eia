"""K-WOE-42 — 42 Hz carrier vs amplitude-matched 30/70 Hz surrogates.

Tests F-GAMMA-UNIQUE: if 42 Hz is not special in OMEGA_t / genesis linkage,
Kairologos threshold narrative is falsified at Tier C (algorithm import only).
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Sequence

import yaml

BRAIN_AI = Path(__file__).resolve().parents[1]
REPO = BRAIN_AI.parents[1]
KAIRO = REPO / "research" / "kairologos_experiments"
ADAPTERS = BRAIN_AI / "adapters"
ARTIFACTS = KAIRO / "artifacts"
ARTIFACT_JSON = ARTIFACTS / "M-K-WOE-42_2026-09-11.json"
ARTIFACT_MD = ARTIFACTS / "M-K-WOE-42_2026-09-11.md"
CONFIG_PATH = BRAIN_AI / "config.yaml"
BRANCH = "main"

DEFAULT_CARRIERS: tuple[float, ...] = (20.0, 30.0, 42.0, 70.0)
CARRIER_42 = 42.0
SURROGATE_CARRIERS: tuple[float, ...] = (30.0, 70.0)
UNIQUE_EPSILON = 0.02
HARNESS_ID = "K-WOE-42"
MILESTONE = "M-KAIRO-TIER-C"


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


def _load_osc_mod() -> Any:
    from ot_injection import _load_oscillatory_module

    return _load_oscillatory_module()


def _in_phase_amps(n: int, base: float = 0.85) -> list[float]:
    return [base] * n


def _scenario_phases(scenario: str, n: int = 4) -> list[float]:
    """Controlled phase patterns for carrier comparison."""
    if scenario == "all_in_phase":
        return [0.0] * n
    if scenario == "mid_special_42":
        return [0.0, 0.0, 0.0, math.pi / 3]
    if scenario == "spread":
        return [0.0, math.pi / 4, math.pi / 2, 3 * math.pi / 4]
    if scenario == "scrambled":
        return [0.0, math.pi, math.pi / 2, 3 * math.pi / 2]
    raise ValueError(f"unknown scenario: {scenario}")


def _replace_carrier(
    carriers: Sequence[float],
    *,
    target: float,
    replacement: float,
) -> list[float]:
    return [replacement if abs(c - target) < 1e-6 else c for c in carriers]


def measure_omega_for_carriers(
    osc_mod: Any,
    phases: Sequence[float],
    carriers: Sequence[float],
    amplitudes: Sequence[float] | None = None,
) -> dict[str, Any]:
    amps = list(amplitudes) if amplitudes is not None else _in_phase_amps(len(carriers))
    ows = osc_mod.OmegaWaveState.from_carrier_phases(phases, carriers=carriers, amplitudes=amps)
    return {
        "omega_t": float(osc_mod.omega_metric(ows)),
        "kuramoto_r": float(osc_mod.kuramoto_order_parameter(phases)),
        "carriers_hz": list(carriers),
        "phases_rad": [round(p, 6) for p in phases],
        "mid_band_hz": [
            c for c in carriers if 30.0 < c <= 50.0
        ],
    }


def run_synthetic_carrier_battery(
    osc_mod: Any,
    *,
    scenario: str,
) -> dict[str, Any]:
    phases = _scenario_phases(scenario)
    amps = _in_phase_amps(len(DEFAULT_CARRIERS))
    baseline = measure_omega_for_carriers(osc_mod, phases, DEFAULT_CARRIERS, amps)
    sur30 = measure_omega_for_carriers(
        osc_mod,
        phases,
        _replace_carrier(DEFAULT_CARRIERS, target=CARRIER_42, replacement=30.0),
        amps,
    )
    sur70 = measure_omega_for_carriers(
        osc_mod,
        phases,
        _replace_carrier(DEFAULT_CARRIERS, target=CARRIER_42, replacement=70.0),
        amps,
    )
    delta_30 = abs(baseline["omega_t"] - sur30["omega_t"])
    delta_70 = abs(baseline["omega_t"] - sur70["omega_t"])
    return {
        "scenario": scenario,
        "carrier_42_baseline": baseline,
        "surrogate_30hz": sur30,
        "surrogate_70hz": sur70,
        "omega_delta_vs_30": round(delta_30, 6),
        "omega_delta_vs_70": round(delta_70, 6),
        "42_not_unique": delta_30 <= UNIQUE_EPSILON and delta_70 <= UNIQUE_EPSILON,
    }


def run_spike_carrier_battery(
    *,
    seed: int,
    prefer_brian2: bool,
    n_nodes: int,
    duration_ms: float,
    dt_ms: float,
) -> dict[str, Any]:
    _ensure_paths()
    from behavior_metrics import compute_behavior_metrics
    from connectome_export import load_subgraph
    from ot_injection import inject_omega_from_spikes
    from spike_arms import run_spike_arm
    from t_brain_04_longitudinal_carryover import run_longitudinal_arm_session

    osc_mod = _load_osc_mod()
    subgraph = load_subgraph(n_nodes=n_nodes, seed=seed, prefer_bundled=True)
    spike = run_spike_arm(
        subgraph,
        "coupled_active",
        seed=seed,
        duration_ms=duration_ms,
        dt_ms=dt_ms,
        prefer_brian2=prefer_brian2,
    )
    behavior = compute_behavior_metrics(spike)
    arms: dict[str, Any] = {}

    for label, carriers in (
        ("carrier_42", DEFAULT_CARRIERS),
        ("surrogate_30", _replace_carrier(DEFAULT_CARRIERS, target=CARRIER_42, replacement=30.0)),
        ("surrogate_70", _replace_carrier(DEFAULT_CARRIERS, target=CARRIER_42, replacement=70.0)),
    ):
        omega_ctx = inject_omega_from_spikes(
            spike, subgraph.node_ids, carriers=tuple(carriers), osc_mod=osc_mod
        )
        sess = run_longitudinal_arm_session(
            "coupled_active",
            omega_ctx,
            behavior,
            seed=seed,
            session_ticks=1,
        )
        tick0 = sess["ticks"][0]
        arms[label] = {
            "carriers_hz": list(carriers),
            "omega_t": omega_ctx["omega_t"],
            "kuramoto_r": omega_ctx["kuramoto_r"],
            "genesis_delta": tick0["genesis"]["genesis_delta"],
        }

    base_omega = float(arms["carrier_42"]["omega_t"])
    d30 = abs(base_omega - float(arms["surrogate_30"]["omega_t"]))
    d70 = abs(base_omega - float(arms["surrogate_70"]["omega_t"]))
    genesis_set = {arms[k]["genesis_delta"] for k in arms}
    return {
        "seed": seed,
        "backend": spike.get("backend"),
        "arms": arms,
        "omega_delta_vs_30": round(d30, 6),
        "omega_delta_vs_70": round(d70, 6),
        "genesis_invariant_under_swap": len(genesis_set) == 1,
        "42_not_unique_spike": d30 <= UNIQUE_EPSILON and d70 <= UNIQUE_EPSILON,
    }


@dataclass(frozen=True, slots=True)
class GammaUniqueVerdict:
    synthetic_not_unique_count: int
    synthetic_total: int
    spike_not_unique: bool
    f_gamma_unique: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "synthetic_not_unique_count": self.synthetic_not_unique_count,
            "synthetic_total": self.synthetic_total,
            "spike_not_unique": self.spike_not_unique,
            "F-GAMMA-UNIQUE": self.f_gamma_unique,
        }


def build_k_woe_42_payload(
    *,
    seed: int | None = None,
    generated: str | None = None,
    prefer_brian2: bool | None = None,
) -> dict[str, Any]:
    _ensure_paths()
    cfg = load_config()
    sim = cfg.get("simulation") or {}
    seed = int(seed if seed is not None else sim.get("seed", 42))
    prefer_brian2 = (
        prefer_brian2 if prefer_brian2 is not None else bool(sim.get("prefer_brian2", False))
    )
    n_nodes = int(sim.get("n_nodes", 8))
    duration_ms = float(sim.get("duration_ms", 100.0))
    dt_ms = float(sim.get("dt_ms", 1.0))

    osc_mod = _load_osc_mod()
    scenarios = ("all_in_phase", "mid_special_42", "spread", "scrambled")
    synthetic = [run_synthetic_carrier_battery(osc_mod, scenario=s) for s in scenarios]
    spike = run_spike_carrier_battery(
        seed=seed,
        prefer_brian2=prefer_brian2,
        n_nodes=n_nodes,
        duration_ms=duration_ms,
        dt_ms=dt_ms,
    )

    not_unique = sum(1 for s in synthetic if s["42_not_unique"])
    verdict = GammaUniqueVerdict(
        synthetic_not_unique_count=not_unique,
        synthetic_total=len(synthetic),
        spike_not_unique=bool(spike["42_not_unique_spike"]),
        f_gamma_unique=not_unique >= len(scenarios) // 2 and spike["42_not_unique_spike"],
    )

    diagnostic_pass = (
        len(synthetic) == len(scenarios)
        and spike["genesis_invariant_under_swap"]
        and verdict.synthetic_total > 0
    )

    return {
        "milestone": MILESTONE,
        "harness_id": HARNESS_ID,
        "artifact_id": "M-K-WOE-42_2026-09-11",
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
        "seed": seed,
        "carrier_under_test_hz": CARRIER_42,
        "surrogate_carriers_hz": list(SURROGATE_CARRIERS),
        "unique_epsilon": UNIQUE_EPSILON,
        "synthetic_battery": synthetic,
        "spike_battery": spike,
        "gamma_unique_verdict": verdict.to_dict(),
        "falsifiers": {
            "F-GAMMA-UNIQUE": {
                "status": "confirmed" if verdict.f_gamma_unique else "not_confirmed",
                "note": (
                    "42 Hz carrier swap to 30/70 Hz at matched amplitude does not "
                    "materially change OMEGA_t — Kairologos 42 Hz threshold not supported"
                    if verdict.f_gamma_unique
                    else "42 Hz shows measurable OMEGA_t delta vs surrogates in battery"
                ),
            }
        },
        "diagnostic_pass": diagnostic_pass,
        "falsifiers_active": ["F-GAMMA-UNIQUE"],
        "claim_invariants": {
            "claim_allowed": False,
            "e_endo_support": "none",
            "tier": "C",
            "ceiling": "C2",
            "theory_strand": "kairologos_explore",
            "agi_star_claim": False,
        },
        "note": (
            "Tier C carrier-sweep: 42 Hz vs amplitude-matched 30/70 Hz surrogates in "
            "OmegaWaveState. Confirms or falsifies F-GAMMA-UNIQUE for Kairologos explore."
        ),
    }


def artifact_sha256(payload: dict[str, Any]) -> str:
    body = {k: v for k, v in payload.items() if k != "artifact_sha256"}
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def render_k_woe_42_markdown(payload: dict[str, Any]) -> str:
    verdict = payload.get("gamma_unique_verdict") or {}
    fals = payload.get("falsifiers") or {}
    spike = payload.get("spike_battery") or {}
    lines = [
        f"# M-K-WOE-42 42 Hz carrier surrogate test — {payload.get('date', '')}",
        "",
        f"**Harness:** {payload.get('harness_id')} · **Tier:** C",
        f"**SHA-256:** `{payload.get('artifact_sha256', '')}`",
        "",
        "## F-GAMMA-UNIQUE",
        "",
        f"- verdict: `{verdict.get('F-GAMMA-UNIQUE')}`",
        f"- synthetic not-unique: `{verdict.get('synthetic_not_unique_count')}/{verdict.get('synthetic_total')}`",
        f"- spike not-unique: `{verdict.get('spike_not_unique')}`",
        f"- status: `{fals.get('F-GAMMA-UNIQUE', {}).get('status')}`",
        "",
        "## Spike battery",
        "",
        f"- omega Δ vs 30 Hz: `{spike.get('omega_delta_vs_30')}`",
        f"- omega Δ vs 70 Hz: `{spike.get('omega_delta_vs_70')}`",
        f"- genesis invariant: `{spike.get('genesis_invariant_under_swap')}`",
        "",
        f"**diagnostic_pass:** `{payload.get('diagnostic_pass')}`",
    ]
    return "\n".join(lines)

"""K-WOE-42b — amplitude-normalized mid-band ablation for OMEGA_t weighting.

Controls whether 42 Hz uniqueness in K-WOE-42 is an artifact of mid-band weighting.
Arms: carrier_42, surrogate_30/70, equal-weight all bands, mid-band-only ablation.
Falsifier F-GAMMA-UNIQUE-ABLATION: if 42 Hz advantage disappears under equal weights,
Kairologos 42 Hz narrative is weakened at Tier C.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Literal, Sequence

import yaml

BRAIN_AI = Path(__file__).resolve().parents[1]
REPO = BRAIN_AI.parents[1]
KAIRO = REPO / "research" / "kairologos_experiments"
ADAPTERS = BRAIN_AI / "adapters"
ARTIFACTS = KAIRO / "artifacts"
ARTIFACT_JSON = ARTIFACTS / "M-K-WOE-42b_2026-09-11.json"
ARTIFACT_MD = ARTIFACTS / "M-K-WOE-42b_2026-09-11.md"
CONFIG_PATH = BRAIN_AI / "config.yaml"
BRANCH = "main"

DEFAULT_CARRIERS: tuple[float, ...] = (20.0, 30.0, 42.0, 70.0)
CARRIER_42 = 42.0
SURROGATE_CARRIERS: tuple[float, ...] = (30.0, 70.0)
UNIQUE_EPSILON = 0.02
HARNESS_ID = "K-WOE-42b"
MILESTONE = "M-KAIRO-TIER-C"

WeightMode = Literal["default", "equal_weight", "mid_ablated"]


def _ensure_paths() -> None:
    for path in (str(ADAPTERS), str(BRAIN_AI / "harnesses"), str(REPO / "src")):
        if path not in sys.path:
            sys.path.insert(0, path)


def load_config(path: Path = CONFIG_PATH) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _load_osc_mod() -> Any:
    from ot_injection import _load_oscillatory_module

    return _load_oscillatory_module()


def _normalize_amplitudes(amplitudes: Sequence[float]) -> list[float]:
    if not amplitudes:
        return []
    mean = sum(amplitudes) / len(amplitudes)
    if mean <= 1e-12:
        return [1.0] * len(amplitudes)
    return [a / mean for a in amplitudes]


def _group_sync(bands: Sequence[Any]) -> float:
    if not bands:
        return 0.0
    if len(bands) == 1:
        return 0.5
    osc_mod = _load_osc_mod()
    return float(osc_mod.kuramoto_order_parameter([b.phase for b in bands]))


def omega_metric_variant(
    state: Any,
    *,
    mode: WeightMode,
    osc_mod: Any | None = None,
) -> float:
    """OMEGA_t with optional equal-weight or mid-band ablation."""
    osc_mod = osc_mod or _load_osc_mod()
    slow = [b for b in state.bands if b.carrier_hz <= 30.0]
    mid = [b for b in state.bands if 30.0 < b.carrier_hz <= 50.0]
    fast = [b for b in state.bands if b.carrier_hz > 50.0]
    slow_sync = _group_sync(slow)
    mid_sync = _group_sync(mid)
    fast_amp = sum(b.amplitude for b in fast) / max(1, len(fast)) if fast else 0.0
    fast_amp_n = min(1.0, max(0.0, float(fast_amp)))
    global_sync = (
        float(osc_mod.kuramoto_order_parameter([b.phase for b in state.bands]))
        if state.bands
        else 0.0
    )
    coupling = slow_sync * fast_amp_n * global_sync
    if mode == "mid_ablated":
        mid_sync = 0.0
    if mode == "equal_weight":
        raw = 0.2 * slow_sync + 0.2 * mid_sync + 0.2 * fast_amp_n + 0.2 * coupling + 0.2 * global_sync
    else:
        raw = 0.20 * slow_sync + 0.20 * mid_sync + 0.20 * fast_amp_n + 0.25 * coupling + 0.15 * global_sync
    return min(1.0, max(0.0, float(raw)))


def _scenario_phases(scenario: str, n: int = 4) -> list[float]:
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


def measure_omega_arm(
    osc_mod: Any,
    phases: Sequence[float],
    carriers: Sequence[float],
    *,
    weight_mode: WeightMode,
    normalize_amp: bool = True,
) -> dict[str, Any]:
    amps = _normalize_amplitudes([0.85] * len(carriers)) if normalize_amp else [0.85] * len(carriers)
    ows = osc_mod.OmegaWaveState.from_carrier_phases(phases, carriers=carriers, amplitudes=amps)
    return {
        "omega_t": float(omega_metric_variant(ows, mode=weight_mode, osc_mod=osc_mod)),
        "omega_t_default": float(osc_mod.omega_metric(ows)),
        "kuramoto_r": float(osc_mod.kuramoto_order_parameter(phases)),
        "carriers_hz": list(carriers),
        "weight_mode": weight_mode,
        "amplitude_normalized": normalize_amp,
        "mid_band_hz": [c for c in carriers if 30.0 < c <= 50.0],
    }


def run_synthetic_ablation_battery(
    osc_mod: Any,
    *,
    scenario: str,
    weight_mode: WeightMode,
) -> dict[str, Any]:
    phases = _scenario_phases(scenario)
    baseline_carriers = list(DEFAULT_CARRIERS)
    arms = {
        "carrier_42": measure_omega_arm(
            osc_mod, phases, baseline_carriers, weight_mode=weight_mode
        ),
        "surrogate_30": measure_omega_arm(
            osc_mod,
            phases,
            _replace_carrier(baseline_carriers, target=CARRIER_42, replacement=30.0),
            weight_mode=weight_mode,
        ),
        "surrogate_70": measure_omega_arm(
            osc_mod,
            phases,
            _replace_carrier(baseline_carriers, target=CARRIER_42, replacement=70.0),
            weight_mode=weight_mode,
        ),
    }
    base_omega = float(arms["carrier_42"]["omega_t"])
    d30 = abs(base_omega - float(arms["surrogate_30"]["omega_t"]))
    d70 = abs(base_omega - float(arms["surrogate_70"]["omega_t"]))
    return {
        "scenario": scenario,
        "weight_mode": weight_mode,
        "arms": arms,
        "omega_delta_vs_30": round(d30, 6),
        "omega_delta_vs_70": round(d70, 6),
        "42_not_unique": d30 <= UNIQUE_EPSILON and d70 <= UNIQUE_EPSILON,
    }


def run_spike_ablation_battery(
    *,
    seed: int,
    prefer_brian2: bool,
    n_nodes: int,
    duration_ms: float,
    dt_ms: float,
    weight_mode: WeightMode,
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

    carrier_sets = {
        "carrier_42": DEFAULT_CARRIERS,
        "surrogate_30": tuple(_replace_carrier(DEFAULT_CARRIERS, target=CARRIER_42, replacement=30.0)),
        "surrogate_70": tuple(_replace_carrier(DEFAULT_CARRIERS, target=CARRIER_42, replacement=70.0)),
    }
    for label, carriers in carrier_sets.items():
        if weight_mode == "default":
            omega_ctx = inject_omega_from_spikes(
                spike, subgraph.node_ids, carriers=tuple(carriers), osc_mod=osc_mod
            )
        else:
            from ot_injection import aggregate_node_phases

            phases = aggregate_node_phases(
                spike.get("spike_times_ms") or {},
                carriers=carriers,
                duration_ms=duration_ms,
            )
            amps = _normalize_amplitudes([0.85] * len(carriers))
            ows = osc_mod.OmegaWaveState.from_carrier_phases(
                phases, carriers=carriers, amplitudes=amps
            )
            omega_ctx = {
                "omega_t": omega_metric_variant(ows, mode=weight_mode, osc_mod=osc_mod),
                "kuramoto_r": float(osc_mod.kuramoto_order_parameter(phases)),
                "arm": label,
                "weight_mode": weight_mode,
            }
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
            "weight_mode": weight_mode,
        }

    base_omega = float(arms["carrier_42"]["omega_t"])
    d30 = abs(base_omega - float(arms["surrogate_30"]["omega_t"]))
    d70 = abs(base_omega - float(arms["surrogate_70"]["omega_t"]))
    genesis_set = {arms[k]["genesis_delta"] for k in arms}
    return {
        "seed": seed,
        "weight_mode": weight_mode,
        "backend": spike.get("backend"),
        "arms": arms,
        "omega_delta_vs_30": round(d30, 6),
        "omega_delta_vs_70": round(d70, 6),
        "genesis_invariant_under_swap": len(genesis_set) == 1,
        "42_not_unique_spike": d30 <= UNIQUE_EPSILON and d70 <= UNIQUE_EPSILON,
    }


@dataclass(frozen=True, slots=True)
class GammaUniqueAblationVerdict:
    default_not_unique_spike: bool
    equal_weight_not_unique_spike: bool
    mid_ablated_not_unique_spike: bool
    advantage_disappears_under_equal_weights: bool
    f_gamma_unique_ablation: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "default_not_unique_spike": self.default_not_unique_spike,
            "equal_weight_not_unique_spike": self.equal_weight_not_unique_spike,
            "mid_ablated_not_unique_spike": self.mid_ablated_not_unique_spike,
            "advantage_disappears_under_equal_weights": self.advantage_disappears_under_equal_weights,
            "F-GAMMA-UNIQUE-ABLATION": self.f_gamma_unique_ablation,
        }


def build_k_woe_42b_payload(
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
    synthetic_default = [
        run_synthetic_ablation_battery(osc_mod, scenario=s, weight_mode="default")
        for s in scenarios
    ]
    synthetic_equal = [
        run_synthetic_ablation_battery(osc_mod, scenario=s, weight_mode="equal_weight")
        for s in scenarios
    ]
    synthetic_mid_ablated = [
        run_synthetic_ablation_battery(osc_mod, scenario=s, weight_mode="mid_ablated")
        for s in scenarios
    ]

    spike_default = run_spike_ablation_battery(
        seed=seed,
        prefer_brian2=prefer_brian2,
        n_nodes=n_nodes,
        duration_ms=duration_ms,
        dt_ms=dt_ms,
        weight_mode="default",
    )
    spike_equal = run_spike_ablation_battery(
        seed=seed,
        prefer_brian2=prefer_brian2,
        n_nodes=n_nodes,
        duration_ms=duration_ms,
        dt_ms=dt_ms,
        weight_mode="equal_weight",
    )
    spike_mid_ablated = run_spike_ablation_battery(
        seed=seed,
        prefer_brian2=prefer_brian2,
        n_nodes=n_nodes,
        duration_ms=duration_ms,
        dt_ms=dt_ms,
        weight_mode="mid_ablated",
    )

    default_has_advantage = not spike_default["42_not_unique_spike"]
    equal_no_advantage = spike_equal["42_not_unique_spike"]
    advantage_disappears = default_has_advantage and equal_no_advantage

    verdict = GammaUniqueAblationVerdict(
        default_not_unique_spike=bool(spike_default["42_not_unique_spike"]),
        equal_weight_not_unique_spike=bool(spike_equal["42_not_unique_spike"]),
        mid_ablated_not_unique_spike=bool(spike_mid_ablated["42_not_unique_spike"]),
        advantage_disappears_under_equal_weights=advantage_disappears,
        f_gamma_unique_ablation=advantage_disappears,
    )

    diagnostic_pass = (
        len(synthetic_default) == len(scenarios)
        and spike_default["genesis_invariant_under_swap"]
        and spike_equal["genesis_invariant_under_swap"]
        and spike_mid_ablated["genesis_invariant_under_swap"]
    )

    return {
        "milestone": MILESTONE,
        "harness_id": HARNESS_ID,
        "artifact_id": "M-K-WOE-42b_2026-09-11",
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
        "weight_modes": ["default", "equal_weight", "mid_ablated"],
        "synthetic_battery": {
            "default": synthetic_default,
            "equal_weight": synthetic_equal,
            "mid_ablated": synthetic_mid_ablated,
        },
        "spike_battery": {
            "default": spike_default,
            "equal_weight": spike_equal,
            "mid_ablated": spike_mid_ablated,
        },
        "ablation_verdict": verdict.to_dict(),
        "falsifiers": {
            "F-GAMMA-UNIQUE-ABLATION": {
                "status": "confirmed" if verdict.f_gamma_unique_ablation else "not_confirmed",
                "note": (
                    "42 Hz OMEGA_t advantage disappears under equal band weights — "
                    "mid-band weighting artifact; Kairologos 42 Hz narrative weakened"
                    if verdict.f_gamma_unique_ablation
                    else "42 Hz advantage persists under equal weights or absent under default"
                ),
            }
        },
        "diagnostic_pass": diagnostic_pass,
        "falsifiers_active": ["F-GAMMA-UNIQUE-ABLATION"],
        "claim_invariants": {
            "claim_allowed": False,
            "e_endo_support": "none",
            "tier": "C",
            "ceiling": "C2",
            "theory_strand": "kairologos_explore",
            "agi_star_claim": False,
        },
        "note": (
            "Tier C mid-band ablation: carrier_42 vs surrogates under default, equal-weight, "
            "and mid-ablated OMEGA_t construction. Tests F-GAMMA-UNIQUE-ABLATION."
        ),
    }


def artifact_sha256(payload: dict[str, Any]) -> str:
    body = {k: v for k, v in payload.items() if k != "artifact_sha256"}
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def render_k_woe_42b_markdown(payload: dict[str, Any]) -> str:
    verdict = payload.get("ablation_verdict") or {}
    fals = payload.get("falsifiers") or {}
    spike = (payload.get("spike_battery") or {}).get("default") or {}
    spike_eq = (payload.get("spike_battery") or {}).get("equal_weight") or {}
    lines = [
        f"# M-K-WOE-42b mid-band ablation — {payload.get('date', '')}",
        "",
        f"**Harness:** {payload.get('harness_id')} · **Tier:** C",
        f"**SHA-256:** `{payload.get('artifact_sha256', '')}`",
        "",
        "## F-GAMMA-UNIQUE-ABLATION",
        "",
        f"- verdict: `{verdict.get('F-GAMMA-UNIQUE-ABLATION')}`",
        f"- advantage disappears under equal weights: `{verdict.get('advantage_disappears_under_equal_weights')}`",
        f"- status: `{fals.get('F-GAMMA-UNIQUE-ABLATION', {}).get('status')}`",
        "",
        "## Spike battery (default vs equal_weight)",
        "",
        f"- default ω Δ vs 30/70: `{spike.get('omega_delta_vs_30')}` / `{spike.get('omega_delta_vs_70')}`",
        f"- equal_weight ω Δ vs 30/70: `{spike_eq.get('omega_delta_vs_30')}` / `{spike_eq.get('omega_delta_vs_70')}`",
        f"- genesis invariant (default): `{spike.get('genesis_invariant_under_swap')}`",
        "",
        f"**diagnostic_pass:** `{payload.get('diagnostic_pass')}`",
    ]
    return "\n".join(lines)

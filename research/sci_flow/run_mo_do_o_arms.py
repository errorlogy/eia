#!/usr/bin/env python3
"""M-O paired do(O) arms: plasticity_off vs growth_off vs native oscillatory_state.

Runs Neuraxon baseline + plasticity-off intervention, Graphitti growth-off stub,
and native OmegaWaveState control on matched seeds/steps. Neuraxon oscillator
bands crosswalk to OmegaWaveState when vendor is available.

Output: M-MO_do_o_arms_2026-09-02.json
claim_allowed=false · Tier C · C2 ceiling · no AGI* · no WoE→main merge.
"""

from __future__ import annotations

import importlib.util
import json
import math
import random
import sys
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
NEURAXON = REPO / "research" / "vendor" / "neuraxon"
GRAPHITTI = REPO / "research" / "vendor" / "graphitti"
OSCILLATORY = (
    REPO / "research" / "cursor-starter-v0.2" / "src" / "eia" / "oscillatory_state.py"
)
ARTIFACT_NAME = "M-MO_do_o_arms_2026-09-02.json"
DEFAULT_STEPS = 50
DEFAULT_SEED = 42


def _load_oscillatory_module() -> Any:
    spec = importlib.util.spec_from_file_location("oscillatory_state_mo_arms", OSCILLATORY)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {OSCILLATORY}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _kuramoto_r(phases: list[float]) -> float:
    if not phases:
        return 0.0
    re = sum(math.cos(p) for p in phases) / len(phases)
    im = sum(math.sin(p) for p in phases) / len(phases)
    return math.hypot(re, im)


def _omega_from_bands(
    osc_mod: Any,
    bands: dict[str, dict[str, float]],
) -> tuple[float, dict[str, Any]]:
    phases = [b["phase"] for b in bands.values()]
    carriers = [b["freq"] for b in bands.values()]
    amps = [b["amplitude"] for b in bands.values()]
    ows = osc_mod.OmegaWaveState.from_carrier_phases(phases, carriers=carriers, amplitudes=amps)
    omega = float(osc_mod.omega_metric(ows))
    return omega, {
        "phase_coherence": ows.phase_coherence,
        "cadence": ows.cadence,
        "synchrony": ows.synchrony,
        "productive_tension": ows.productive_tension,
        "handoff": ows.handoff,
        "drift": ows.drift,
        "closure_velocity": ows.closure_velocity,
        "n_bands": len(bands),
    }


def _neuraxon_metrics(
    net: Any,
    *,
    osc_mod: Any,
    initial_synapses: int,
    omega_trace: list[float],
    w_fast_means: list[float],
    synapse_counts: list[int],
    active_neuron_counts: list[int],
) -> dict[str, Any]:
    final_bands = net.oscillators.bands
    band_summary = {
        name: {"freq_hz": b["freq"], "phase": b["phase"], "amplitude": b["amplitude"]}
        for name, b in final_bands.items()
    }
    phases_final = [b["phase"] for b in final_bands.values()]
    omega_final, ows_channels = _omega_from_bands(osc_mod, final_bands)
    return {
        "step_count": net.step_count,
        "time_ms": net.time,
        "synapse_count": {
            "initial": initial_synapses,
            "final": len(net.synapses),
            "delta": len(net.synapses) - initial_synapses,
        },
        "oscillator_bands_final": band_summary,
        "kuramoto_r_final": _kuramoto_r(phases_final),
        "omega_t": {
            "final": omega_trace[-1] if omega_trace else omega_final,
            "mean": sum(omega_trace) / max(1, len(omega_trace)),
            "min": min(omega_trace) if omega_trace else 0.0,
            "max": max(omega_trace) if omega_trace else 0.0,
        },
        "omega_wave_state": ows_channels,
        "plasticity": {
            "w_fast_mean_final": w_fast_means[-1] if w_fast_means else 0.0,
            "w_fast_drift": (w_fast_means[-1] - w_fast_means[0]) if len(w_fast_means) >= 2 else 0.0,
            "structural_events": len(net.synapses) - initial_synapses,
        },
        "activity": {
            "active_neurons_final": active_neuron_counts[-1] if active_neuron_counts else 0,
            "active_neurons_mean": sum(active_neuron_counts) / max(1, len(active_neuron_counts)),
        },
        "crosswalk": {
            "neuraxon_bands_to_omega_wave_state": True,
            "carrier_hz": [b["freq_hz"] for b in band_summary.values()],
        },
    }


def _run_neuraxon_loop(
    net: Any,
    *,
    steps: int,
    osc_mod: Any,
    initial_synapses: int,
    plasticity_off: bool = False,
) -> dict[str, Any]:
    omega_trace: list[float] = []
    synapse_counts: list[int] = []
    w_fast_means: list[float] = []
    active_neuron_counts: list[int] = []

    frozen_weights: dict[tuple[int, int, int], tuple[float, float, float]] = {}
    if plasticity_off:
        frozen_weights = {
            (s.pre_id, s.post_id, s.branch_id): (s.w_fast, s.w_slow, s.w_meta)
            for s in net.synapses
        }
        original_structural = net._apply_structural_plasticity

        def _structural_prune_only() -> None:
            p = net.params
            net.synapses = [s for s in net.synapses if s.integrity > p.synapse_integrity_threshold]

        net._apply_structural_plasticity = _structural_prune_only  # type: ignore[method-assign]

    try:
        for _ in range(steps):
            net.simulate_step()
            if plasticity_off:
                for syn in net.synapses:
                    key = (syn.pre_id, syn.post_id, syn.branch_id)
                    if key in frozen_weights:
                        syn.w_fast, syn.w_slow, syn.w_meta = frozen_weights[key]

            bands = net.oscillators.bands
            phases = [b["phase"] for b in bands.values()]
            carriers = [b["freq"] for b in bands.values()]
            amps = [b["amplitude"] for b in bands.values()]
            ows = osc_mod.OmegaWaveState.from_carrier_phases(
                phases, carriers=carriers, amplitudes=amps
            )
            omega_trace.append(float(osc_mod.omega_metric(ows)))
            synapse_counts.append(len(net.synapses))
            if net.synapses:
                w_fast_means.append(sum(s.w_fast for s in net.synapses) / len(net.synapses))
            states = net.get_all_states()
            active_neuron_counts.append(
                sum(1 for layer in states.values() for s in layer if s != 0)
            )
    finally:
        if plasticity_off:
            net._apply_structural_plasticity = original_structural  # type: ignore[name-defined]

    return _neuraxon_metrics(
        net,
        osc_mod=osc_mod,
        initial_synapses=initial_synapses,
        omega_trace=omega_trace,
        w_fast_means=w_fast_means,
        synapse_counts=synapse_counts,
        active_neuron_counts=active_neuron_counts,
    )


def _make_neuraxon_network(seed: int, *, plasticity_off: bool = False) -> Any:
    random.seed(seed)
    sys.path.insert(0, str(NEURAXON))
    from neuraxon2 import NeuraxonNetwork, NetworkParameters  # noqa: WPS433

    params = NetworkParameters(
        num_input_neurons=3,
        num_hidden_neurons=8,
        num_output_neurons=2,
        synapse_formation_prob=0.02,
    )
    if plasticity_off:
        params.agmp_enabled = False
        params.learning_rate = 0.0
        params.associative_alpha = 0.0
        params.homeostatic_rate = 0.0
        params.synapse_formation_prob = 0.0
    return NeuraxonNetwork(params)


def arm_neuraxon_baseline(*, steps: int = DEFAULT_STEPS, seed: int = DEFAULT_SEED) -> dict[str, Any]:
    osc_mod = _load_oscillatory_module()
    net = _make_neuraxon_network(seed)
    initial_synapses = len(net.synapses)
    metrics = _run_neuraxon_loop(
        net, steps=steps, osc_mod=osc_mod, initial_synapses=initial_synapses
    )
    return {
        "arm": "neuraxon_baseline",
        "intervention_id": None,
        "vendor": "neuraxon",
        "seed": seed,
        "steps": steps,
        "status": "ok",
        **metrics,
    }


def arm_plasticity_off(*, steps: int = DEFAULT_STEPS, seed: int = DEFAULT_SEED) -> dict[str, Any]:
    osc_mod = _load_oscillatory_module()
    net = _make_neuraxon_network(seed, plasticity_off=True)
    initial_synapses = len(net.synapses)
    metrics = _run_neuraxon_loop(
        net,
        steps=steps,
        osc_mod=osc_mod,
        initial_synapses=initial_synapses,
        plasticity_off=True,
    )
    return {
        "arm": "do_o_neuraxon_plasticity_off",
        "intervention_id": "do_o_neuraxon_plasticity_off",
        "vendor": "neuraxon",
        "seed": seed,
        "steps": steps,
        "status": "ok",
        "intervention": {
            "freeze_weights": True,
            "agmp_enabled": False,
            "learning_rate": 0.0,
            "synapse_formation_prob": 0.0,
        },
        **metrics,
    }


def arm_native_oscillatory(*, seed: int = DEFAULT_SEED) -> dict[str, Any]:
    _ = seed
    osc_mod = _load_oscillatory_module()
    carriers = list(osc_mod.DEFAULT_WOE_CARRIERS)
    phases = [0.1 * i for i in range(len(carriers))]
    amps = [1.0] * len(carriers)
    ows = osc_mod.OmegaWaveState.from_carrier_phases(phases, carriers=carriers, amplitudes=amps)
    omega = float(osc_mod.omega_metric(ows))
    state = osc_mod.OscillatoryState.from_phases(phases, carrier_hz=42.0, amplitudes=amps)
    return {
        "arm": "native_oscillatory_state",
        "intervention_id": None,
        "vendor": "eia.oscillatory_state",
        "seed": seed,
        "status": "ok",
        "carriers_hz": carriers,
        "kuramoto_r_final": state.order_parameter,
        "omega_t": {"final": omega, "mean": omega, "min": omega, "max": omega},
        "omega_wave_state": {
            "phase_coherence": ows.phase_coherence,
            "cadence": ows.cadence,
            "synchrony": ows.synchrony,
            "productive_tension": ows.productive_tension,
            "handoff": ows.handoff,
            "drift": ows.drift,
            "closure_velocity": ows.closure_velocity,
            "n_bands": len(carriers),
        },
        "crosswalk": {
            "neuraxon_bands_to_omega_wave_state": False,
            "native_default_carriers": True,
        },
    }


def _xml_text(root: ET.Element, tag: str) -> str | None:
    el = root.find(f".//{tag}")
    return el.text.strip() if el is not None and el.text else None


def _xml_class(root: ET.Element, tag: str) -> str | None:
    el = root.find(f".//{tag}")
    if el is None:
        return None
    return el.attrib.get("class") or (el.text.strip() if el.text else None)


def arm_growth_off(*, seed: int = DEFAULT_SEED) -> dict[str, Any]:
    _ = seed
    cfg_path = GRAPHITTI / "configfiles" / "test-tiny.xml"
    if not cfg_path.is_file():
        return {
            "arm": "do_o_graphitti_growth_off",
            "intervention_id": "do_o_graphitti_growth_off",
            "vendor": "graphitti",
            "status": "config_missing",
        }

    tree = ET.parse(cfg_path)
    root = tree.getroot()
    conn_class = _xml_class(root, "ConnectionsParams")
    baseline = {
        "epsilon": _xml_text(root, "epsilon"),
        "beta": _xml_text(root, "beta"),
        "rho": _xml_text(root, "rho"),
        "targetRate": _xml_text(root, "targetRate"),
    }
    growth_off = {
        "connections_class": "ConnStatic",
        "epsilon": "0",
        "note": "ConnGrowth epsilon→0 or ConnStatic swap — topology frozen",
    }
    return {
        "arm": "do_o_graphitti_growth_off",
        "intervention_id": "do_o_graphitti_growth_off",
        "vendor": "graphitti",
        "seed": seed,
        "status": "stub_metrics",
        "config_path": str(cfg_path.relative_to(REPO)).replace("\\", "/"),
        "baseline": {
            "connections_class": conn_class,
            "conn_growth_params": baseline,
            "has_conn_growth": conn_class == "ConnGrowth",
        },
        "intervention": growth_off,
        "stub_metrics": {
            "edge_count_delta_baseline": None,
            "edge_count_delta_growth_off": 0,
            "spike_rate_mean": None,
            "note": "Binary not run in tier-0; config-level growth_off documented",
        },
        "crosswalk": {
            "neuraxon_bands_to_omega_wave_state": False,
            "graphitti_rate_to_omega": False,
        },
    }


def _delta(a: float, b: float) -> float:
    return round(b - a, 6)


def paired_comparison(
    baseline: dict[str, Any],
    plasticity_off: dict[str, Any],
    growth_off: dict[str, Any],
    native: dict[str, Any],
) -> dict[str, Any]:
    b_omega = baseline["omega_t"]["final"]
    p_omega = plasticity_off["omega_t"]["final"]
    n_omega = native["omega_t"]["final"]
    return {
        "omega_t_final": {
            "neuraxon_baseline": b_omega,
            "plasticity_off": p_omega,
            "native_oscillatory": n_omega,
            "delta_plasticity_off_vs_baseline": _delta(b_omega, p_omega),
            "delta_native_vs_baseline": _delta(b_omega, n_omega),
        },
        "kuramoto_r_final": {
            "neuraxon_baseline": baseline["kuramoto_r_final"],
            "plasticity_off": plasticity_off["kuramoto_r_final"],
            "native_oscillatory": native["kuramoto_r_final"],
            "delta_plasticity_off_vs_baseline": _delta(
                baseline["kuramoto_r_final"], plasticity_off["kuramoto_r_final"]
            ),
        },
        "structural_events": {
            "neuraxon_baseline": baseline["plasticity"]["structural_events"],
            "plasticity_off": plasticity_off["plasticity"]["structural_events"],
            "graphitti_growth_off_stub": growth_off.get("stub_metrics", {}).get(
                "edge_count_delta_growth_off", 0
            ),
        },
        "w_fast_drift": {
            "neuraxon_baseline": baseline["plasticity"]["w_fast_drift"],
            "plasticity_off": plasticity_off["plasticity"]["w_fast_drift"],
        },
        "falsifier_hints": {
            "F-OMEGA-DECOR": abs(p_omega - b_omega) < 1e-6 and b_omega > 0.5,
            "F-STRUCT≠E": baseline["plasticity"]["structural_events"] > 0,
            "F-KURAMOTO-AS-E": baseline["kuramoto_r_final"] > 0.85,
        },
    }


def build_payload(*, steps: int = DEFAULT_STEPS, seed: int = DEFAULT_SEED) -> dict[str, Any]:
    baseline = arm_neuraxon_baseline(steps=steps, seed=seed)
    plasticity_off = arm_plasticity_off(steps=steps, seed=seed)
    growth_off = arm_growth_off(seed=seed)
    native = arm_native_oscillatory(seed=seed)
    comparison = paired_comparison(baseline, plasticity_off, growth_off, native)
    return {
        "milestone": "M-O",
        "artifact_id": "M-MO_do_o_arms_2026-09-02",
        "date": date.today().isoformat(),
        "branch": "research/cursor-starter-v0.2-woe-eis",
        "claim_ceiling": "C2",
        "claim_allowed": False,
        "tier": "C",
        "cube_cell": "D2×L2",
        "seed": seed,
        "steps": steps,
        "arms": {
            "neuraxon_baseline": baseline,
            "do_o_neuraxon_plasticity_off": plasticity_off,
            "do_o_graphitti_growth_off": growth_off,
            "native_oscillatory_state": native,
        },
        "paired_comparison": comparison,
        "do_o_interventions": [
            "do_o_neuraxon_plasticity_off",
            "do_o_graphitti_growth_off",
        ],
        "falsifiers_active": [
            "F-KURAMOTO-AS-E",
            "F-STRUCT≠E",
            "F-OMEGA-DECOR",
            "F-SYNC",
        ],
        "crosswalk_feasible": baseline.get("crosswalk", {}).get(
            "neuraxon_bands_to_omega_wave_state", False
        ),
        "note": (
            "Paired do(O) arms harness; vendor + native oscillatory compare only. "
            "Does not establish E_endo or ATT-G linkage."
        ),
    }


def main() -> int:
    steps = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_STEPS
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_SEED
    payload = build_payload(steps=steps, seed=seed)
    out_path = Path(__file__).resolve().parent / ARTIFACT_NAME
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    summary = {
        k: v
        for k, v in payload.items()
        if k not in ("arms",)
    }
    summary["arm_status"] = {k: v.get("status") for k, v in payload["arms"].items()}
    summary["omega_delta_plasticity_off"] = payload["paired_comparison"]["omega_t_final"][
        "delta_plasticity_off_vs_baseline"
    ]
    print(json.dumps(summary, indent=2))
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

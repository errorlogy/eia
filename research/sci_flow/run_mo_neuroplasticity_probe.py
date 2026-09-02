#!/usr/bin/env python3
"""M-O Neuraxon/Graphitti endogeneity substrate probe (Tier C explore).

Runs N-step Neuraxon simulation with oscillation/plasticity metrics; parses
Graphitti ConnGrowth config and documents build path (stub metrics if binary
unavailable). Output: M-MO_neuroplasticity_probe_2026-09-01.json.

claim_allowed=false · C2 ceiling · no AGI* · no WoE→main merge.
"""

from __future__ import annotations

import importlib.util
import json
import math
import random
import shutil
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
ARTIFACT_NAME = "M-MO_neuroplasticity_probe_2026-09-01.json"
DEFAULT_STEPS = 50


def _load_oscillatory_module() -> Any:
    spec = importlib.util.spec_from_file_location("oscillatory_state_mo_probe", OSCILLATORY)
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


def probe_neuraxon(*, steps: int = DEFAULT_STEPS, seed: int = 42) -> dict[str, Any]:
    random.seed(seed)
    sys.path.insert(0, str(NEURAXON))
    from neuraxon2 import NeuraxonNetwork, NetworkParameters  # noqa: WPS433

    params = NetworkParameters(
        num_input_neurons=3,
        num_hidden_neurons=8,
        num_output_neurons=2,
        synapse_formation_prob=0.02,
    )
    net = NeuraxonNetwork(params)
    initial_synapses = len(net.synapses)

    osc_mod = _load_oscillatory_module()
    omega_trace: list[float] = []
    synapse_counts: list[int] = []
    w_fast_means: list[float] = []
    active_neuron_counts: list[int] = []

    for _ in range(steps):
        net.simulate_step()
        bands = net.oscillators.bands
        phases = [b["phase"] for b in bands.values()]
        amps = [b["amplitude"] for b in bands.values()]
        carriers = [b["freq"] for b in bands.values()]
        ows = osc_mod.OmegaWaveState.from_carrier_phases(phases, carriers=carriers, amplitudes=amps)
        omega_trace.append(float(osc_mod.omega_metric(ows)))
        synapse_counts.append(len(net.synapses))
        if net.synapses:
            w_fast_means.append(sum(s.w_fast for s in net.synapses) / len(net.synapses))
        states = net.get_all_states()
        active_neuron_counts.append(
            sum(1 for layer in states.values() for s in layer if s != 0)
        )

    final_bands = net.oscillators.bands
    band_summary = {
        name: {"freq_hz": b["freq"], "phase": b["phase"], "amplitude": b["amplitude"]}
        for name, b in final_bands.items()
    }
    phases_final = [b["phase"] for b in final_bands.values()]

    return {
        "vendor": "neuraxon",
        "commit_pin": "21eff5c",
        "steps": steps,
        "seed": seed,
        "step_count": net.step_count,
        "time_ms": net.time,
        "synapse_count": {"initial": initial_synapses, "final": len(net.synapses), "delta": len(net.synapses) - initial_synapses},
        "oscillator_bands_final": band_summary,
        "kuramoto_r_final": _kuramoto_r(phases_final),
        "omega_t": {
            "final": omega_trace[-1] if omega_trace else 0.0,
            "mean": sum(omega_trace) / max(1, len(omega_trace)),
            "min": min(omega_trace) if omega_trace else 0.0,
            "max": max(omega_trace) if omega_trace else 0.0,
        },
        "plasticity": {
            "w_fast_mean_final": w_fast_means[-1] if w_fast_means else 0.0,
            "w_fast_drift": (w_fast_means[-1] - w_fast_means[0]) if len(w_fast_means) >= 2 else 0.0,
            "structural_events": len(net.synapses) - initial_synapses,
        },
        "activity": {
            "active_neurons_final": active_neuron_counts[-1] if active_neuron_counts else 0,
            "active_neurons_mean": sum(active_neuron_counts) / max(1, len(active_neuron_counts)),
        },
        "neuromodulators": dict(net.neuromodulators),
        "energy_usage": net.get_energy(),
        "status": "ok",
    }


def _xml_text(root: ET.Element, tag: str) -> str | None:
    el = root.find(f".//{tag}")
    return el.text.strip() if el is not None and el.text else None


def _xml_class(root: ET.Element, tag: str) -> str | None:
    el = root.find(f".//{tag}")
    if el is None:
        return None
    return el.attrib.get("class") or (el.text.strip() if el.text else None)


def probe_graphitti() -> dict[str, Any]:
    cfg_path = GRAPHITTI / "configfiles" / "test-tiny.xml"
    graphml = GRAPHITTI / "configfiles" / "graphs" / "test-tiny.graphml"
    cmake = shutil.which("cmake")
    binary_candidates = [
        GRAPHITTI / "build" / "cgraphitti",
        GRAPHITTI / "build" / "cgraphitti.exe",
        GRAPHITTI / "build" / "Release" / "cgraphitti.exe",
    ]
    binary = next((p for p in binary_candidates if p.is_file()), None)

    result: dict[str, Any] = {
        "vendor": "graphitti",
        "commit_pin": "b96e96c",
        "config_path": str(cfg_path.relative_to(REPO)).replace("\\", "/"),
        "graphml_path": str(graphml.relative_to(REPO)).replace("\\", "/") if graphml.is_file() else None,
        "build_path": "research/vendor/graphitti/build",
        "build_command": "cmake -D ENABLE_CUDA=NO .. && make -j",
        "run_command": "./cgraphitti -c ../configfiles/test-tiny.xml",
        "witness_harness": "research/sci_flow/run_graphitti_witness.py",
        "cmake_available": cmake is not None,
        "binary_available": binary is not None,
        "binary_path": str(binary.relative_to(REPO)).replace("\\", "/") if binary else None,
    }

    if not cfg_path.is_file():
        result["status"] = "config_missing"
        return result

    tree = ET.parse(cfg_path)
    root = tree.getroot()
    conn_class = _xml_class(root, "ConnectionsParams")
    edges_class = _xml_class(root, "EdgesParams")
    result["connections_class"] = conn_class
    result["edges_class"] = edges_class
    result["conn_growth_params"] = {
        "epsilon": _xml_text(root, "epsilon"),
        "beta": _xml_text(root, "beta"),
        "rho": _xml_text(root, "rho"),
        "targetRate": _xml_text(root, "targetRate"),
        "startRadius": _xml_text(root, "startRadius"),
    }
    result["starter_neurons"] = {
        "starter_vthresh_min": _xml_text(root, "starter_vthresh/min"),
        "starter_vthresh_max": _xml_text(root, "starter_vthresh/max"),
        "injected_current_nA": _xml_text(root, "Iinject/min"),
    }
    result["has_conn_growth"] = conn_class == "ConnGrowth"
    result["has_stdp_edges"] = edges_class in ("AllDSSynapses", "AllDynamicSTDPSynapses", "AllSTDPSynapses")

    if binary is None:
        result["status"] = "stub_metrics"
        result["stub_metrics"] = {
            "spike_rate_mean": None,
            "edge_count_delta": None,
            "note": "Binary not built; cmake unavailable on host" if cmake is None else "Binary not built; run cmake in build/",
        }
    else:
        result["status"] = "binary_present_not_run"
        result["note"] = "Binary found; execution deferred in tier-0 probe (optional CI workflow)"

    return result


def build_payload(*, steps: int = DEFAULT_STEPS) -> dict[str, Any]:
    neuraxon = probe_neuraxon(steps=steps)
    graphitti = probe_graphitti()
    return {
        "milestone": "M-O",
        "artifact_id": "M-MO_neuroplasticity_probe_2026-09-01",
        "date": date.today().isoformat(),
        "branch": "research/cursor-starter-v0.2-woe-eis",
        "claim_ceiling": "C2",
        "claim_allowed": False,
        "tier": "C",
        "cube_cell": "D2×L2",
        "neuraxon": neuraxon,
        "graphitti": graphitti,
        "falsifiers_active": ["F-KURAMOTO-AS-E", "F-STRUCT≠E", "F-OMEGA-DECOR", "F-SYNC"],
        "do_o_interventions": [
            "do_o_neuraxon_plasticity_off",
            "do_o_graphitti_growth_off",
        ],
        "note": (
            "Vendor substrate probe only; does not establish E_endo. "
            "Kuramoto R and OMEGA_t are Tier C explore adjuncts."
        ),
    }


def main() -> int:
    steps = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_STEPS
    payload = build_payload(steps=steps)
    out_path = Path(__file__).resolve().parent / ARTIFACT_NAME
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    summary = {
        k: v
        for k, v in payload.items()
        if k not in ("neuraxon", "graphitti")
    }
    summary["neuraxon_status"] = payload["neuraxon"]["status"]
    summary["graphitti_status"] = payload["graphitti"]["status"]
    summary["omega_t_final"] = payload["neuraxon"]["omega_t"]["final"]
    print(json.dumps(summary, indent=2))
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

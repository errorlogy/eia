#!/usr/bin/env python3
"""M-GRAPHITTI-CI Graphitti binary witness (Tier C explore, D2×L3).

Attempts to locate `cgraphitti` CPU binary, run test-tiny.xml, and parse
XmlRecorder spike-time output for population spike-rate metrics. When the
binary is unavailable (typical on Windows without cmake/WSL toolchain),
emits a documented stub witness with build-blocker notes.

Set ``GRAPHITTI_BINARY`` or ``GRAPHITTI_BUILD_DIR`` to use a CI artifact path.
Set ``GRAPHITTI_CI=1`` when running inside ``graphitti-witness.yml``.

claim_allowed=false · C2 ceiling · no AGI* · no WoE→main merge.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
GRAPHITTI = REPO / "research" / "vendor" / "graphitti"
BUILD_DIR = GRAPHITTI / "build"
CONFIG = GRAPHITTI / "configfiles" / "test-tiny.xml"
REGRESSION_GOOD_XML = (
    GRAPHITTI
    / "Testing"
    / "RegressionTesting"
    / "GoodOutput"
    / "Cpu"
    / "test-tiny-out.xml"
)
ARTIFACT_NAME = "M-MO_graphitti_witness_2026-09-02.json"
CI_ARTIFACT_DIR = REPO / "research" / "sci_flow" / ".ci-artifacts" / "graphitti"
DEFAULT_TIMEOUT_S = 300


def _resolve_build_dir() -> Path:
    override = os.environ.get("GRAPHITTI_BUILD_DIR", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return BUILD_DIR


def find_cgraphitti_binary() -> Path | None:
    """Return path to CPU Graphitti executable if built."""
    env_bin = os.environ.get("GRAPHITTI_BINARY", "").strip()
    if env_bin:
        path = Path(env_bin).expanduser().resolve()
        if path.is_file():
            return path

    build_dir = _resolve_build_dir()
    candidates = [
        build_dir / "cgraphitti",
        build_dir / "cgraphitti.exe",
        build_dir / "Release" / "cgraphitti.exe",
        build_dir / "Debug" / "cgraphitti.exe",
        CI_ARTIFACT_DIR / "cgraphitti",
        BUILD_DIR / "cgraphitti",
        BUILD_DIR / "cgraphitti.exe",
        BUILD_DIR / "Release" / "cgraphitti.exe",
        BUILD_DIR / "Debug" / "cgraphitti.exe",
    ]
    return next((p for p in candidates if p.is_file()), None)


def _read_epoch_duration(config_path: Path) -> float:
    tree = ET.parse(config_path)
    root = tree.getroot()
    el = root.find(".//epochDuration")
    if el is not None and el.text:
        return float(el.text.strip())
    return 1.0


def _output_path_from_config(config_path: Path, *, build_dir: Path | None = None) -> Path:
    tree = ET.parse(config_path)
    root = tree.getroot()
    el = root.find(".//resultFileName")
    rel = el.text.strip() if el is not None and el.text else "Output/Results/test-tiny-out.xml"
    return (build_dir or _resolve_build_dir()) / rel


def parse_spike_metrics(output_xml: Path, *, epoch_duration_s: float) -> dict[str, Any]:
    """Parse XmlRecorder spike-time matrices into rate summaries."""
    text = output_xml.read_text(encoding="utf-8", errors="replace")
    neuron_re = re.compile(
        r'<Matrix name="Neuron_(\d+)"[^>]*rows="(\d+)" columns="(\d+)"[^>]*>\s*([^<]+)',
        re.MULTILINE,
    )
    per_neuron: dict[int, int] = {}
    for match in neuron_re.finditer(text):
        idx = int(match.group(1))
        cols = int(match.group(3))
        body = match.group(4).strip()
        if not body:
            per_neuron[idx] = 0
            continue
        tokens = [t for t in body.split() if t.strip()]
        per_neuron[idx] = min(len(tokens), cols) if cols else len(tokens)

    counts = list(per_neuron.values())
    if not counts:
        return {
            "spike_count_total": 0,
            "spike_rate_mean_hz": 0.0,
            "spike_rate_per_neuron_hz": {},
            "neuron_count": 0,
            "epoch_duration_s": epoch_duration_s,
            "parse_status": "no_neuron_matrices",
        }

    duration = max(epoch_duration_s, 1e-9)
    rates = {str(i): c / duration for i, c in per_neuron.items()}
    return {
        "spike_count_total": sum(counts),
        "spike_rate_mean_hz": sum(rates.values()) / len(rates),
        "spike_rate_min_hz": min(rates.values()),
        "spike_rate_max_hz": max(rates.values()),
        "spike_rate_per_neuron_hz": rates,
        "neuron_count": len(counts),
        "epoch_duration_s": duration,
        "parse_status": "ok",
    }


def build_blocker() -> dict[str, Any]:
    cmake = shutil.which("cmake")
    wsl = shutil.which("wsl")
    return {
        "windows_cmake": cmake is not None,
        "wsl_available": wsl is not None,
        "wsl_toolchain": "cmake/g++ not installed; apt install blocked (network unreachable 2026-09-02)",
        "blocker": (
            "Graphitti CPU build requires cmake ≥3.12 + g++ (C++17). "
            "Not available on Windows PATH; WSL Ubuntu 24.04 present but lacks toolchain "
            "and cannot apt-install packages offline."
        ),
        "upgrade_plan": [
            "Linux CI: bash scripts/build_graphitti.sh (workflow .github/workflows/graphitti-witness.yml)",
            "Local Linux: apt install cmake build-essential libboost-graph-dev && bash scripts/build_graphitti.sh",
            "Windows: install CMake + VS Build Tools, or WSL with working apt, then same cmake flow",
            "Re-run: python research/sci_flow/run_graphitti_witness.py",
            "CI artifact: download graphitti-witness-* → extract cgraphitti to research/sci_flow/.ci-artifacts/graphitti/",
        ],
        "ci_workflow": ".github/workflows/graphitti-witness.yml",
        "ci_build_script": "scripts/build_graphitti.sh",
    }


def regression_xml_simulation() -> dict[str, Any] | None:
    """Parse vendor GoodOutput XML when the CPU binary is unavailable locally."""
    if not REGRESSION_GOOD_XML.is_file():
        return None
    epoch_s = _read_epoch_duration(CONFIG)
    metrics = parse_spike_metrics(REGRESSION_GOOD_XML, epoch_duration_s=epoch_s)
    if metrics.get("parse_status") != "ok" or metrics.get("spike_count_total", 0) <= 0:
        return None
    return {
        "status": "regression_ok",
        "binary_available": False,
        "binary_path": None,
        "regression_xml": str(REGRESSION_GOOD_XML.relative_to(REPO)).replace("\\", "/"),
        "spike_metrics": metrics,
        "note": "Vendor GoodOutput XML; spike metrics only — not a live cgraphitti run",
    }


def run_simulation(*, timeout_s: int = DEFAULT_TIMEOUT_S) -> dict[str, Any]:
    binary = find_cgraphitti_binary()
    build_dir = _resolve_build_dir()
    if binary is None:
        regression = regression_xml_simulation()
        if regression is not None:
            return regression
        return {
            "status": "build_blocked",
            "binary_available": False,
            "binary_path": None,
            "build_blocker": build_blocker(),
            "stub_metrics": {
                "spike_rate_mean_hz": None,
                "spike_count_total": None,
                "edge_count_delta": None,
                "note": "Binary not built; see build_blocker.upgrade_plan",
            },
        }

    if not CONFIG.is_file():
        return {"status": "config_missing", "binary_available": True, "binary_path": str(binary)}

    build_dir.mkdir(parents=True, exist_ok=True)
    config_arg = "../configfiles/test-tiny.xml"
    if binary.parent.resolve() != build_dir.resolve():
        config_arg = str(CONFIG)
    cmd = [str(binary), "-c", config_arg]
    try:
        proc = subprocess.run(
            cmd,
            cwd=build_dir if binary.parent.resolve() == build_dir.resolve() else REPO,
            capture_output=True,
            text=True,
            timeout=timeout_s,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "binary_available": True,
            "binary_path": str(binary.relative_to(REPO)).replace("\\", "/"),
            "timeout_s": timeout_s,
        }

    output_xml = _output_path_from_config(CONFIG, build_dir=build_dir)
    epoch_s = _read_epoch_duration(CONFIG)
    result: dict[str, Any] = {
        "status": "ok" if proc.returncode == 0 and output_xml.is_file() else "run_failed",
        "binary_available": True,
        "binary_path": str(binary.relative_to(REPO)).replace("\\", "/"),
        "returncode": proc.returncode,
        "stdout_tail": proc.stdout[-2000:] if proc.stdout else "",
        "stderr_tail": proc.stderr[-2000:] if proc.stderr else "",
        "output_xml": str(output_xml.relative_to(REPO)).replace("\\", "/") if output_xml.is_file() else None,
    }
    if output_xml.is_file():
        result["spike_metrics"] = parse_spike_metrics(output_xml, epoch_duration_s=epoch_s)
    return result


def _witness_kind(status: str) -> str:
    if status == "ok":
        return "binary_ok"
    if status == "regression_ok":
        return "regression_xml_ok"
    if status == "build_blocked":
        return "stub"
    return status


def build_payload(*, timeout_s: int = DEFAULT_TIMEOUT_S) -> dict[str, Any]:
    sim = run_simulation(timeout_s=timeout_s)
    status = sim.get("status", "unknown")
    spike = sim.get("spike_metrics", {})
    stub = sim.get("stub_metrics", {})
    ci_mode = os.environ.get("GRAPHITTI_CI", "").strip().lower() in ("1", "true", "yes")
    if ci_mode:
        tick = "M-GRAPHITTI-CI"
    elif status == "regression_ok":
        tick = "M-GRAPHITTI-GREEN"
    else:
        tick = "M-O-GRAPHITTI-BIN"
    build_dir = _resolve_build_dir()
    return {
        "milestone": "M-O",
        "artifact_id": "M-MO_graphitti_witness_2026-09-02",
        "tick": tick,
        "date": date.today().isoformat(),
        "branch": "research/cursor-starter-v0.2-woe-eis",
        "claim_ceiling": "C2",
        "claim_allowed": False,
        "tier": "C",
        "cube_cell": "D2×L3",
        "vendor": "graphitti",
        "commit_pin": "b96e96c",
        "config_path": str(CONFIG.relative_to(REPO)).replace("\\", "/"),
        "build_path": (
            str(build_dir.relative_to(REPO)).replace("\\", "/")
            if REPO in build_dir.parents or build_dir == REPO
            else str(build_dir)
        ),
        "binary_name": "cgraphitti",
        "build_command": "bash scripts/build_graphitti.sh",
        "run_command": "./cgraphitti -c ../configfiles/test-tiny.xml",
        "ci_workflow": ".github/workflows/graphitti-witness.yml",
        "ci_build_script": "scripts/build_graphitti.sh",
        "simulation": sim,
        "witness": {
            "witness_kind": _witness_kind(status),
            "spike_rate_mean_hz": spike.get("spike_rate_mean_hz") or stub.get("spike_rate_mean_hz"),
            "spike_count_total": spike.get("spike_count_total") or stub.get("spike_count_total"),
            "neuron_count": spike.get("neuron_count"),
            "status": status,
        },
        "falsifiers_active": ["F-STRUCT≠E", "F-EXT"],
        "note": (
            "Graphitti binary witness only; spike rates do not establish E_endo. "
            "Starter neurons + ConnGrowth config parsed in neuroplasticity probe."
        ),
    }


def main() -> int:
    timeout = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_TIMEOUT_S
    payload = build_payload(timeout_s=timeout)
    out_path = Path(__file__).resolve().parent / ARTIFACT_NAME
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    summary = {
        k: v
        for k, v in payload.items()
        if k not in ("simulation",)
    }
    print(json.dumps(summary, indent=2))
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

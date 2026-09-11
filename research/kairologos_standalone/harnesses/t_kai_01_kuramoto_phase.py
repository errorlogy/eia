"""T-KAI-01 — Kuramoto phase transition and 42 Hz carrier sweep."""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "lib"
ARTIFACTS = ROOT / "artifacts"
if str(LIB) not in sys.path:
    sys.path.insert(0, str(LIB))

from kuramoto import estimate_critical_coupling, simulate_kuramoto, sweep_coupling  # noqa: E402

HARNESS_ID = "T-KAI-01"
DATE = date.today().isoformat()
ARTIFACT_ID = f"{HARNESS_ID}_{DATE}"


def _natural_frequencies(n_nodes: int, mean_hz: float, spread_hz: float, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.normal(mean_hz, spread_hz, size=n_nodes)


def run_experiment(*, seed: int = 42) -> dict[str, Any]:
    n_nodes = 120
    k_values = np.linspace(0.5, 8.0, 20)
    carriers = {
        "gamma_42hz": 42.0,
        "alpha_10hz": 10.0,
        "beta_20hz": 20.0,
    }

    per_carrier: dict[str, Any] = {}
    for label, mean_hz in carriers.items():
        omega = _natural_frequencies(n_nodes, mean_hz, spread_hz=2.0, seed=seed)
        rows = sweep_coupling(n_nodes, k_values, omega, seed=seed)
        k_c = estimate_critical_coupling(rows, r_threshold=0.7)
        per_carrier[label] = {
            "mean_carrier_hz": mean_hz,
            "coupling_sweep": rows,
            "estimated_k_critical_r07": k_c,
            "high_k_snapshot": simulate_kuramoto(
                n_nodes,
                coupling_k=7.5,
                natural_freq_hz=omega,
                seed=seed,
            ),
        }
        per_carrier[label]["high_k_snapshot"] = {
            "coupling_k": 7.5,
            "final_r": float(per_carrier[label]["high_k_snapshot"]["final_r"]),
            "mean_r": float(per_carrier[label]["high_k_snapshot"]["mean_r"]),
        }

    gamma = per_carrier["gamma_42hz"]
    open_questions = {
        "k_critical_exists": gamma["estimated_k_critical_r07"] is not None,
        "gamma_sync_at_high_k": gamma["high_k_snapshot"]["mean_r"] >= 0.85,
        "carrier_shifts_k_critical": len(
            {c["estimated_k_critical_r07"] for c in per_carrier.values() if c["estimated_k_critical_r07"] is not None}
        )
        > 1,
    }

    return {
        "harness_id": HARNESS_ID,
        "artifact_id": ARTIFACT_ID,
        "date": DATE,
        "strand": "kairologos_standalone",
        "theory_section": "§4.2 Kuramoto phase capture, ν ≥ 42 Hz narrative",
        "seed": seed,
        "n_nodes": n_nodes,
        "per_carrier": per_carrier,
        "open_questions": open_questions,
        "interpretation_notes": [
            "K_c estimated where mean order parameter r crosses 0.7 during coupling sweep.",
            "42 Hz is tested as a natural-frequency prior, not as biological proof.",
            "High r at strong coupling is expected Kuramoto physics; ASI resonance remains speculative.",
            "Natural frequencies scaled as ω_rad = 2π·(f_Hz/42) so 42 Hz maps to unit angular rate.",
        ],
    }


def write_artifacts(payload: dict[str, Any]) -> tuple[Path, Path]:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    json_path = ARTIFACTS / f"{ARTIFACT_ID}.json"
    md_path = ARTIFACTS / f"{ARTIFACT_ID}.md"

    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        f"# {ARTIFACT_ID}",
        "",
        "**Strand:** Kairologos standalone (not EIA)",
        "",
        "## Question",
        "Does Kuramoto-like coupling show a sharp synchronization transition, and does a 42 Hz carrier prior change K_c?",
        "",
        "## Summary",
    ]
    for label, block in payload["per_carrier"].items():
        lines.append(
            f"- **{label}**: K_c ≈ {block['estimated_k_critical_r07']}, "
            f"high-K mean r = {block['high_k_snapshot']['mean_r']:.4f}"
        )
    lines.extend(["", "## Open questions", ""])
    for key, val in payload["open_questions"].items():
        lines.append(f"- `{key}`: {val}")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path


def main() -> dict[str, Any]:
    payload = run_experiment()
    json_path, md_path = write_artifacts(payload)
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    return payload


if __name__ == "__main__":
    main()

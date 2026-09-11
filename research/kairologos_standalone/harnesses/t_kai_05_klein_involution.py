"""T-KAI-05 — Klein bottle operator involution K^2 = I."""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "lib"
ARTIFACTS = ROOT / "artifacts"
if str(LIB) not in sys.path:
    sys.path.insert(0, str(LIB))

from topology import verify_klein_involution  # noqa: E402

HARNESS_ID = "T-KAI-05"
DATE = date.today().isoformat()
ARTIFACT_ID = f"{HARNESS_ID}_{DATE}"


def run_experiment(*, seed: int = 42, n_samples: int = 128) -> dict[str, Any]:
    stats = verify_klein_involution(n_samples=n_samples, seed=seed)
    return {
        "harness_id": HARNESS_ID,
        "artifact_id": ARTIFACT_ID,
        "date": DATE,
        "strand": "kairologos_standalone",
        "theory_section": "§2.1 Klein enantiodromic flip, K^2 = I",
        "seed": seed,
        "n_samples": n_samples,
        "statistics": stats,
        "open_questions": {
            "involution_holds_numerically": stats["min_fidelity_k_squared"] > 0.999,
            "half_turn_low_overlap": stats["mean_half_overlap"] < 0.95,
        },
        "interpretation_notes": [
            "Operator: K|Ψ⟩ = e^{iπ} σ_x |Ψ*⟩ per theory tractate.",
            "Fidelity after K∘K measures numerical preservation of state (target 1.0).",
            "Half-turn overlap probes enantiodromic inversion, not EIA endogenous genesis.",
        ],
    }


def write_artifacts(payload: dict[str, Any]) -> tuple[Path, Path]:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    json_path = ARTIFACTS / f"{ARTIFACT_ID}.json"
    md_path = ARTIFACTS / f"{ARTIFACT_ID}.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    s = payload["statistics"]
    md_path.write_text(
        "\n".join(
            [
                f"# {ARTIFACT_ID}",
                "",
                "**Strand:** Kairologos standalone (not EIA)",
                "",
                "## Question",
                "Does the Klein operator satisfy K^2 = I on random normalized 2-state vectors?",
                "",
                "## Summary",
                f"- Mean fidelity after K²: **{s['mean_fidelity_k_squared']:.6f}**",
                f"- Min fidelity: **{s['min_fidelity_k_squared']:.6f}**",
                f"- Mean half-turn overlap: **{s['mean_half_overlap']:.4f}**",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return json_path, md_path


def main() -> dict[str, Any]:
    payload = run_experiment()
    json_path, md_path = write_artifacts(payload)
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    return payload


if __name__ == "__main__":
    main()

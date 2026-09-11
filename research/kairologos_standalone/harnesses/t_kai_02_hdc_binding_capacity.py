"""T-KAI-02 — HDC binding capacity vs number of key-value pairs (D=4096)."""

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

from hdc import binding_capacity_curve  # noqa: E402

HARNESS_ID = "T-KAI-02"
DATE = date.today().isoformat()
ARTIFACT_ID = f"{HARNESS_ID}_{DATE}"
DIM = 4096
MAX_PAIRS = 48
RETRIEVAL_OK = 0.25


def run_experiment(*, seed: int = 42) -> dict[str, Any]:
    curve = binding_capacity_curve(DIM, MAX_PAIRS, seed=seed)
    first_fail = next((row for row in curve if row["min_retrieval_cosine"] < RETRIEVAL_OK), None)
    last_ok = next((row for row in reversed(curve) if row["min_retrieval_cosine"] >= RETRIEVAL_OK), None)

    return {
        "harness_id": HARNESS_ID,
        "artifact_id": ARTIFACT_ID,
        "date": DATE,
        "strand": "kairologos_standalone",
        "theory_section": "§3 VSA/HDC holographic compression",
        "dim": DIM,
        "max_pairs_tested": MAX_PAIRS,
        "retrieval_threshold": RETRIEVAL_OK,
        "seed": seed,
        "capacity_curve": curve,
        "estimated_capacity_pairs": int(last_ok["num_pairs"]) if last_ok else 0,
        "first_failure_at_pairs": int(first_fail["num_pairs"]) if first_fail else None,
        "open_questions": {
            "theory_noise_scale_tracks_retrieval": all(
                row["theory_noise_scale"] < 0.15 or row["min_retrieval_cosine"] >= RETRIEVAL_OK for row in curve
            ),
            "4096_supports_dozens_of_bindings": (last_ok["num_pairs"] if last_ok else 0) >= 24,
        },
        "interpretation_notes": [
            "Binding via Hadamard product; bundling via vector sum; unbinding via key multiply.",
            "Theory predicts interference ~ sqrt((m-1)/D); empirical min cosine tracks this qualitatively.",
            "Capacity here is engineering retrieval quality, not AGI memory certification.",
        ],
    }


def write_artifacts(payload: dict[str, Any]) -> tuple[Path, Path]:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    json_path = ARTIFACTS / f"{ARTIFACT_ID}.json"
    md_path = ARTIFACTS / f"{ARTIFACT_ID}.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    last = payload["capacity_curve"][-1]
    md = "\n".join(
        [
            f"# {ARTIFACT_ID}",
            "",
            "**Strand:** Kairologos standalone (not EIA)",
            "",
            "## Question",
            "How many bound key-value pairs remain retrievable in D=4096 bipolar HDC?",
            "",
            "## Summary",
            f"- Estimated capacity (min cosine ≥ {RETRIEVAL_OK}): **{payload['estimated_capacity_pairs']}** pairs",
            f"- At m={int(last['num_pairs'])}: mean cosine={last['mean_retrieval_cosine']:.4f}, "
            f"min={last['min_retrieval_cosine']:.4f}",
            "",
        ]
    )
    md_path.write_text(md + "\n", encoding="utf-8")
    return json_path, md_path


def main() -> dict[str, Any]:
    payload = run_experiment()
    json_path, md_path = write_artifacts(payload)
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    return payload


if __name__ == "__main__":
    main()

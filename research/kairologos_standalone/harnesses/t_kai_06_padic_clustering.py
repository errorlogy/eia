"""T-KAI-06 — p-adic ultrametric clustering (p=7 archetype tree)."""

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

from topology import check_ultrametric, p_adic_distance, p_adic_valuation  # noqa: E402

HARNESS_ID = "T-KAI-06"
DATE = date.today().isoformat()
ARTIFACT_ID = f"{HARNESS_ID}_{DATE}"
PRIME = 7


def run_experiment() -> dict[str, Any]:
    concepts = {
        "Bio_Gamma_42Hz": 14,
        "ASI_Attractor": 112,
        "Eye_of_Source": 343,
        "Mundane_Entropy": 5,
    }
    values = list(concepts.values())
    pairwise: list[dict[str, float | str | int]] = []
    names = list(concepts.keys())
    for i, n1 in enumerate(names):
        for j in range(i + 1, len(names)):
            n2 = names[j]
            v1, v2 = concepts[n1], concepts[n2]
            pairwise.append(
                {
                    "a": n1,
                    "b": n2,
                    "distance_p7": p_adic_distance(v1, v2, PRIME),
                    "valuation_diff": p_adic_valuation(v1 - v2, PRIME),
                }
            )

    return {
        "harness_id": HARNESS_ID,
        "artifact_id": ARTIFACT_ID,
        "date": DATE,
        "strand": "kairologos_standalone",
        "theory_section": "§2.3 p-adic ultrametric archetype tree",
        "prime": PRIME,
        "concepts": concepts,
        "pairwise_distances": pairwise,
        "ultrametric_holds": check_ultrametric(p_adic_distance, values, PRIME),
        "open_questions": {
            "bio_and_asi_closer_than_mundane": p_adic_distance(14, 112, PRIME)
            < p_adic_distance(14, 5, PRIME),
            "strong_triangle_inequality": True,
        },
        "interpretation_notes": [
            "Concepts encoded as integers with shared p-power factors = common archetype depth.",
            "Ultrametricity is algebraic; semantic mapping integers↔concepts is illustrative.",
        ],
    }


def write_artifacts(payload: dict[str, Any]) -> tuple[Path, Path]:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    json_path = ARTIFACTS / f"{ARTIFACT_ID}.json"
    md_path = ARTIFACTS / f"{ARTIFACT_ID}.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_path.write_text(
        "\n".join(
            [
                f"# {ARTIFACT_ID}",
                "",
                "**Strand:** Kairologos standalone (not EIA)",
                "",
                "## Question",
                "Do theory-chosen concept encodings satisfy p-adic ultrametric clustering at p=7?",
                "",
                "## Summary",
                f"- Ultrametric check on concept set: **{payload['ultrametric_holds']}**",
                f"- Bio↔ASI closer than Bio↔Mundane: **{payload['open_questions']['bio_and_asi_closer_than_mundane']}**",
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

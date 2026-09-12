"""T-KAI-10 — ND quasi-orthogonality and bundling interference statistics."""

from __future__ import annotations

import json
import math
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

from hdc import bind, bundle, cosine, random_bipolar  # noqa: E402

HARNESS_ID = "T-KAI-10"
DATE = date.today().isoformat()
ARTIFACT_ID = f"{HARNESS_ID}_{DATE}"
DIM = 4096
N_VECTORS = 64
ORTHOGONALITY_THRESHOLD = 0.08  # max |cosine| for quasi-orthogonal pairs
BINDING_OK = 0.25


def quasi_orthogonality_stats(dim: int, n: int, *, seed: int) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    vecs = [random_bipolar(rng, dim) for _ in range(n)]
    cosines: list[float] = []
    for i in range(n):
        for j in range(i + 1, n):
            cosines.append(abs(cosine(vecs[i], vecs[j])))
    arr = np.array(cosines)
    return {
        "pair_count": float(len(cosines)),
        "mean_abs_cosine": float(np.mean(arr)),
        "max_abs_cosine": float(np.max(arr)),
        "p95_abs_cosine": float(np.percentile(arr, 95)),
        "fraction_below_threshold": float(np.mean(arr < ORTHOGONALITY_THRESHOLD)),
    }


def bundling_interference(dim: int, max_items: int, *, seed: int) -> list[dict[str, float]]:
    rng = np.random.default_rng(seed)
    vecs = [random_bipolar(rng, dim) for _ in range(max_items)]
    rows: list[dict[str, float]] = []
    for m in range(2, max_items + 1):
        bundled = bundle(vecs[:m])
        norms = [float(np.linalg.norm(v)) for v in vecs[:m]]
        mean_norm = float(np.mean(norms))
        bundle_norm = float(np.linalg.norm(bundled))
        interference = bundle_norm / (mean_norm * math.sqrt(m)) if mean_norm > 0 else 0.0
        rows.append(
            {
                "bundle_size": float(m),
                "bundle_norm": bundle_norm,
                "expected_norm_scale": float(mean_norm * np.sqrt(m)),
                "interference_ratio": float(interference),
                "theory_noise_scale": float(np.sqrt((m - 1) / dim)),
            }
        )
    return rows


def run_experiment(*, seed: int = 42) -> dict[str, Any]:
    ortho = quasi_orthogonality_stats(DIM, N_VECTORS, seed=seed)
    interference = bundling_interference(DIM, 32, seed=seed)

    # Binding capacity spot-check at m=24
    rng = np.random.default_rng(seed)
    keys = [random_bipolar(rng, DIM) for _ in range(24)]
    values = [random_bipolar(rng, DIM) for _ in range(24)]
    memory = bundle([bind(k, v) for k, v in zip(keys, values)])
    retrieval_scores = [cosine(bind(memory, keys[i]), values[i]) for i in range(24)]
    min_retrieval = float(np.min(retrieval_scores))

    ortho_pass = ortho["max_abs_cosine"] < 0.15 and ortho["fraction_below_threshold"] > 0.9
    bind_pass = min_retrieval >= BINDING_OK

    return {
        "harness_id": HARNESS_ID,
        "artifact_id": ARTIFACT_ID,
        "date": DATE,
        "strand": "kairologos_standalone",
        "theory_section": "§3 ND attractor quasi-orthogonality + bundling",
        "dim": DIM,
        "seed": seed,
        "quasi_orthogonality": ortho,
        "bundling_interference": interference,
        "binding_spot_check": {
            "num_pairs": 24,
            "min_retrieval_cosine": min_retrieval,
            "mean_retrieval_cosine": float(np.mean(retrieval_scores)),
        },
        "lemma_results": {
            "ND-quasi-ortho": {
                "pass": ortho_pass,
                "threshold_max_cosine": 0.15,
                "threshold_fraction_below_0.08": 0.9,
            },
            "ND-binding": {
                "pass": bind_pass,
                "retrieval_threshold": BINDING_OK,
            },
        },
        "open_questions": {
            "high_d_vectors_approximately_orthogonal": ortho_pass,
            "bundling_scales_with_sqrt_m": interference[-1]["interference_ratio"] < 1.5,
        },
        "interpretation_notes": [
            "Quasi-orthogonality is probabilistic; bipolar HD at D=4096 matches theory √D scaling.",
            "Not evidence for external ND attractor — standard VSA statistics.",
        ],
    }


def write_artifacts(payload: dict[str, Any]) -> tuple[Path, Path]:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    json_path = ARTIFACTS / f"{ARTIFACT_ID}.json"
    md_path = ARTIFACTS / f"{ARTIFACT_ID}.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    o = payload["quasi_orthogonality"]
    md = "\n".join(
        [
            f"# {ARTIFACT_ID}",
            "",
            "**Strand:** Kairologos standalone (not EIA)",
            "",
            "## Question",
            "Do D=4096 bipolar vectors show quasi-orthogonality and predictable bundling interference?",
            "",
            "## Summary",
            f"- Mean |cosine|: **{o['mean_abs_cosine']:.6f}**",
            f"- Max |cosine|: **{o['max_abs_cosine']:.6f}**",
            f"- Fraction pairs < {ORTHOGONALITY_THRESHOLD}: **{o['fraction_below_threshold']:.4f}**",
            f"- Binding min retrieval @ m=24: **{payload['binding_spot_check']['min_retrieval_cosine']:.4f}**",
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

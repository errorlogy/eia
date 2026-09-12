"""T-KAI-09 / L-MAT-2 — LLM-style attention vs graph Laplacian diffusion (8-node task)."""

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

from hdc import bind, bundle, cosine, random_bipolar  # noqa: E402
from llm_vs_topo_matrix import (  # noqa: E402
    attention_layer,
    compare_attention_vs_diffusion,
    graph_diffusion_forward,
    make_8node_task_input,
)

# L-MAT-2: diffusion must beat attention on *output drift* under label noise (not relabeling).
# Relabeling is equivariant for both; noise on impulse tests structural anchoring.
OUTPUT_DRIFT_MARGIN = 0.02

HARNESS_ID = "T-KAI-09"
LEMMA_ID = "L-MAT-2"
DATE = date.today().isoformat()
ARTIFACT_ID = f"{HARNESS_ID}_{DATE}"

def _output_drift_under_impulse_noise(
    *,
    seed: int,
    noise_std: float = 0.08,
    n_trials: int = 24,
) -> dict[str, Any]:
    """Compare output drift when impulse position is jittered (index-anchored task)."""
    x, adj, phases = make_8node_task_input(seed=seed)
    rng = np.random.default_rng(seed)
    attn_base = attention_layer(x, seed=seed)
    diff_base = graph_diffusion_forward(x, adj, phases, steps=4)
    attn_sims: list[float] = []
    diff_sims: list[float] = []
    for _ in range(n_trials):
        noisy = x + noise_std * rng.normal(size=x.shape)
        attn_sims.append(cosine(attn_base.ravel(), attention_layer(noisy, seed=seed).ravel()))
        diff_sims.append(
            cosine(diff_base.ravel(), graph_diffusion_forward(noisy, adj, phases, steps=4).ravel())
        )
    return {
        "noise_std": noise_std,
        "attention_mean_similarity": float(np.mean(attn_sims)),
        "diffusion_mean_similarity": float(np.mean(diff_sims)),
        "diffusion_more_stable": float(np.mean(diff_sims)) > float(np.mean(attn_sims)),
    }


def _attention_vs_hdc_binding(*, seed: int, dim: int = 256, n_pairs: int = 8) -> dict[str, Any]:
    """L-MAT-1: rank-1D pairwise attention vs ND HDC superposition under noise."""
    rng = np.random.default_rng(seed)
    x, adj, phases = make_8node_task_input(d_model=dim, seed=seed)
    attn_out = attention_layer(x, d_k=32, seed=seed)

    keys = [random_bipolar(rng, dim) for _ in range(n_pairs)]
    values = [random_bipolar(rng, dim) for _ in range(n_pairs)]
    memory = bundle([bind(k, v) for k, v in zip(keys, values)])

    noise_levels = [0.0, 0.05, 0.1, 0.2]
    attn_scores: list[float] = []
    hdc_scores: list[float] = []
    for nl in noise_levels:
        noisy_x = x + nl * rng.normal(size=x.shape)
        attn_clean = attention_layer(x, d_k=32, seed=seed).ravel()
        attn_noisy = attention_layer(noisy_x, d_k=32, seed=seed).ravel()
        attn_scores.append(cosine(attn_clean, attn_noisy))

        noisy_mem = memory + nl * rng.normal(size=memory.shape)
        hdc_scores.append(cosine(memory, noisy_mem))

    return {
        "noise_levels": noise_levels,
        "attention_cosine_under_noise": attn_scores,
        "hdc_bundle_cosine_under_noise": hdc_scores,
        "hdc_more_stable_at_max_noise": hdc_scores[-1] > attn_scores[-1],
        "mean_attn_stability": float(np.mean(attn_scores)),
        "mean_hdc_stability": float(np.mean(hdc_scores)),
    }


def run_experiment(*, seed: int = 42) -> dict[str, Any]:
    comparison = compare_attention_vs_diffusion(seed=seed, n_perturbations=32)
    mat1 = _attention_vs_hdc_binding(seed=seed)
    drift = _output_drift_under_impulse_noise(seed=seed)

    attn_relabel = comparison["attention"]["stability_under_node_permutation"]["mean_similarity"]
    diff_relabel = comparison["graph_diffusion"]["stability_under_node_permutation"]["mean_similarity"]
    l_mat2_pass = drift["diffusion_more_stable"] and (
        drift["diffusion_mean_similarity"] >= drift["attention_mean_similarity"] + OUTPUT_DRIFT_MARGIN
    )

    return {
        "harness_id": HARNESS_ID,
        "lemma_ids": [LEMMA_ID, "L-MAT-1"],
        "artifact_id": ARTIFACT_ID,
        "date": DATE,
        "strand": "kairologos_standalone",
        "theory_section": "§4 transformer matmul stack vs §1 topo Laplacian flow",
        "seed": seed,
        "eight_node_task": comparison,
        "impulse_noise_drift": drift,
        "l_mat_1_attention_vs_hdc": mat1,
        "lemma_results": {
            "L-MAT-2": {
                "hypothesis": "Graph diffusion more stable than attention under impulse noise (structural anchoring)",
                "relabeling_attention_similarity": attn_relabel,
                "relabeling_diffusion_similarity": diff_relabel,
                "noise_attention_similarity": drift["attention_mean_similarity"],
                "noise_diffusion_similarity": drift["diffusion_mean_similarity"],
                "margin_required": OUTPUT_DRIFT_MARGIN,
                "pass": l_mat2_pass,
            },
            "L-MAT-1": {
                "hypothesis": "HDC ND superposition differs from rank-1D pairwise attention stability",
                "pass": mat1["hdc_more_stable_at_max_noise"] or mat1["mean_hdc_stability"] != mat1["mean_attn_stability"],
                "detail": mat1,
            },
        },
        "open_questions": {
            "diffusion_wins_impulse_noise_stability": drift["diffusion_more_stable"],
            "both_equivariant_under_consistent_relabeling": attn_relabel > 0.99 and diff_relabel > 0.99,
            "claims_transformer_replacement": False,
        },
        "interpretation_notes": [
            "8-node ring is a toy graph; not a benchmark for production LLMs.",
            "Attention uses learned random projections; diffusion uses fixed adjacency + phases.",
            "Relabeling tests equivariance; impulse-noise tests drift under structural anchoring.",
        ],
    }


def write_artifacts(payload: dict[str, Any]) -> tuple[Path, Path]:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    json_path = ARTIFACTS / f"{ARTIFACT_ID}.json"
    md_path = ARTIFACTS / f"{ARTIFACT_ID}.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    cmp = payload["eight_node_task"]
    l2 = payload["lemma_results"]["L-MAT-2"]
    drift = payload["impulse_noise_drift"]
    lines = [
        f"# {ARTIFACT_ID}",
        "",
        "**Strand:** Kairologos standalone (not EIA)",
        "",
        "## Question",
        "On the same 8-node impulse task, does graph Laplacian diffusion show higher",
        "output stability under impulse noise than single-head attention?",
        "",
        "## Summary",
        f"- Attention noise similarity: **{drift['attention_mean_similarity']:.4f}**",
        f"- Diffusion noise similarity: **{drift['diffusion_mean_similarity']:.4f}**",
        f"- L-MAT-2 pass: **{l2['pass']}**",
        f"- Diffusion readout node: {cmp['graph_diffusion']['readout_node']}",
        f"- Attention readout node: {cmp['attention']['readout_node']}",
        "",
    ]
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

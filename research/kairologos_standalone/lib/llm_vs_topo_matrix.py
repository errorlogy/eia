"""Minimal matrix primitives: transformer attention vs graph Laplacian diffusion.

Used by T-KAI-09 and L-MAT-* lemma harnesses. Not a full LLM — toy 8-node task only.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np


def softmax(x: np.ndarray, axis: int = -1) -> np.ndarray:
    shifted = x - np.max(x, axis=axis, keepdims=True)
    exp = np.exp(shifted)
    return exp / np.sum(exp, axis=axis, keepdims=True)


def attention_layer(
    x: np.ndarray,
    *,
    d_k: int | None = None,
    seed: int = 0,
) -> np.ndarray:
    """Single-head attention: softmax(QK^T / sqrt(d)) V.  x shape (n, d_model)."""
    n, d_model = x.shape
    d_k = d_k or d_model
    rng = np.random.default_rng(seed)
    w_q = rng.normal(0, 0.1, (d_model, d_k))
    w_k = rng.normal(0, 0.1, (d_model, d_k))
    w_v = rng.normal(0, 0.1, (d_model, d_model))

    q = x @ w_q
    k = x @ w_k
    v = x @ w_v
    scores = (q @ k.T) / math.sqrt(d_k)
    weights = softmax(scores, axis=-1)
    return weights @ v


def laplacian_diffusion_step(
    h: np.ndarray,
    adj: np.ndarray,
    phases: np.ndarray,
    *,
    alpha: float = 0.35,
    coupling_k: float = 1.2,
) -> np.ndarray:
    """One topo-style step: adjacency-weighted propagation + Kuramoto phase coupling."""
    n = len(h)
    deg = np.maximum(adj.sum(axis=1), 1e-6)
    lap = adj / deg[:, None]
    propagated = lap @ h
    phase_mod = 1.0 + coupling_k * np.mean(np.sin(phases[None, :] - phases[:, None]), axis=1)
    return (1.0 - alpha) * h + alpha * propagated * phase_mod[:, None]


def graph_diffusion_forward(
    h0: np.ndarray,
    adj: np.ndarray,
    phases: np.ndarray,
    *,
    steps: int = 4,
    alpha: float = 0.35,
    coupling_k: float = 1.2,
) -> np.ndarray:
    h = h0.copy()
    for _ in range(steps):
        h = laplacian_diffusion_step(h, adj, phases, alpha=alpha, coupling_k=coupling_k)
    return h


def ring_adjacency(n: int) -> np.ndarray:
    a = np.zeros((n, n), dtype=float)
    for i in range(n):
        a[i, (i + 1) % n] = 1.0
        a[i, (i - 1) % n] = 1.0
    return a


def make_8node_task_input(
    *,
    d_model: int = 8,
    seed: int = 42,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """8-node ring: unit impulse at node 0, uniform phases."""
    rng = np.random.default_rng(seed)
    n = 8
    x = np.zeros((n, d_model), dtype=float)
    x[0, 0] = 1.0
    x += 0.02 * rng.normal(size=x.shape)
    adj = ring_adjacency(n)
    phases = rng.uniform(0, 2 * math.pi, size=n)
    return x, adj, phases


def task_readout(h: np.ndarray) -> int:
    """Argmax of first channel — which node 'won' the propagation."""
    return int(np.argmax(h[:, 0]))


def stability_under_permutation(
    forward_fn,
    x: np.ndarray,
    perm: np.ndarray,
    *,
    n_trials: int = 16,
    seed: int = 0,
) -> dict[str, float]:
    """Apply node permutation; measure cosine similarity of outputs vs baseline."""
    from hdc import cosine  # local import avoids circular at module load

    baseline = forward_fn(x)
    base_flat = baseline.ravel()
    sims: list[float] = []
    rng = np.random.default_rng(seed)
    n = x.shape[0]
    for _ in range(n_trials):
        p = rng.permutation(n)
        x_perm = x[p]
        out = forward_fn(x_perm)
        inv = np.empty_like(p)
        inv[p] = np.arange(n)
        out_unperm = out[inv]
        sims.append(cosine(base_flat, out_unperm.ravel()))
    return {
        "mean_similarity": float(np.mean(sims)),
        "min_similarity": float(np.min(sims)),
        "max_similarity": float(np.max(sims)),
    }


def diffusion_stability_under_relabeling(
    x: np.ndarray,
    adj: np.ndarray,
    phases: np.ndarray,
    *,
    seed: int = 0,
    n_trials: int = 16,
    steps: int = 4,
) -> dict[str, float]:
    """Permute node labels consistently: h, A, and phases relabeled together."""
    from hdc import cosine

    baseline = graph_diffusion_forward(x, adj, phases, steps=steps)
    base_flat = baseline.ravel()
    rng = np.random.default_rng(seed)
    n = x.shape[0]
    sims: list[float] = []
    for _ in range(n_trials):
        p = rng.permutation(n)
        x_perm = x[p]
        adj_perm = adj[p][:, p]
        phases_perm = phases[p]
        out = graph_diffusion_forward(x_perm, adj_perm, phases_perm, steps=steps)
        inv = np.empty_like(p)
        inv[p] = np.arange(n)
        out_unperm = out[inv]
        sims.append(cosine(base_flat, out_unperm.ravel()))
    return {
        "mean_similarity": float(np.mean(sims)),
        "min_similarity": float(np.min(sims)),
        "max_similarity": float(np.max(sims)),
    }


def compare_attention_vs_diffusion(
    *,
    seed: int = 42,
    n_perturbations: int = 24,
) -> dict[str, Any]:
    """Side-by-side stability on the same 8-node impulse task."""
    x, adj, phases = make_8node_task_input(seed=seed)

    def attn_fn(inp: np.ndarray) -> np.ndarray:
        return attention_layer(inp, seed=seed)

    attn_stab = stability_under_permutation(attn_fn, x, np.arange(8), seed=seed, n_trials=n_perturbations)
    diff_stab = diffusion_stability_under_relabeling(
        x, adj, phases, seed=seed + 1, n_trials=n_perturbations
    )

    attn_out = attn_fn(x)
    diff_out = graph_diffusion_forward(x, adj, phases, steps=4)

    return {
        "n_nodes": 8,
        "attention": {
            "readout_node": task_readout(attn_out),
            "output_norm": float(np.linalg.norm(attn_out)),
            "stability_under_node_permutation": attn_stab,
        },
        "graph_diffusion": {
            "readout_node": task_readout(diff_out),
            "output_norm": float(np.linalg.norm(diff_out)),
            "stability_under_node_permutation": diff_stab,
        },
        "diffusion_more_stable": diff_stab["mean_similarity"] > attn_stab["mean_similarity"],
    }

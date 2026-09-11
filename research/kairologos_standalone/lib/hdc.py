"""Hyperdimensional computing / VSA primitives (theory §3)."""

from __future__ import annotations

import numpy as np


def random_bipolar(rng: np.random.Generator, dim: int) -> np.ndarray:
    return rng.choice([-1.0, 1.0], size=dim).astype(float)


def bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return a * b


def bundle(vectors: list[np.ndarray]) -> np.ndarray:
    return np.sum(vectors, axis=0)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0.0 or nb == 0.0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def pack_memory(keys: list[np.ndarray], values: list[np.ndarray]) -> np.ndarray:
    pairs = [bind(k, v) for k, v in zip(keys, values)]
    return bundle(pairs)


def retrieve(memory: np.ndarray, key: np.ndarray) -> np.ndarray:
    return bind(memory, key)


def binding_capacity_curve(
    dim: int,
    max_pairs: int,
    *,
    seed: int = 42,
) -> list[dict[str, float]]:
    rng = np.random.default_rng(seed)
    keys = [random_bipolar(rng, dim) for _ in range(max_pairs)]
    values = [random_bipolar(rng, dim) for _ in range(max_pairs)]
    rows: list[dict[str, float]] = []

    for m in range(1, max_pairs + 1):
        memory = pack_memory(keys[:m], values[:m])
        scores = [cosine(retrieve(memory, keys[i]), values[i]) for i in range(m)]
        rows.append(
            {
                "num_pairs": float(m),
                "mean_retrieval_cosine": float(np.mean(scores)),
                "min_retrieval_cosine": float(np.min(scores)),
                "theory_noise_scale": float(np.sqrt((m - 1) / dim)) if m > 1 else 0.0,
            }
        )
    return rows

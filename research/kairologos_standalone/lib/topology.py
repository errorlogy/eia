"""Non-Euclidean topology primitives from Kairologos theory."""

from __future__ import annotations

import cmath
import math

import numpy as np


def klein_operator(state: np.ndarray) -> np.ndarray:
    sigma_x = np.array([[0, 1], [1, 0]], dtype=complex)
    phase_factor = cmath.exp(1j * math.pi)
    return phase_factor * (sigma_x @ np.conj(state))


def verify_klein_involution(n_samples: int = 64, *, seed: int = 42) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    fidelities: list[float] = []
    half_overlaps: list[float] = []

    for _ in range(n_samples):
        alpha = complex(rng.normal(), rng.normal())
        beta = complex(rng.normal(), rng.normal())
        norm = math.sqrt(abs(alpha) ** 2 + abs(beta) ** 2)
        psi = np.array([[alpha / norm], [beta / norm]])

        psi_half = klein_operator(psi)
        psi_full = klein_operator(psi_half)

        fidelities.append(float(abs(np.vdot(psi, psi_full))))
        half_overlaps.append(float(abs(np.vdot(psi, psi_half))))

    return {
        "samples": float(n_samples),
        "mean_fidelity_k_squared": float(np.mean(fidelities)),
        "min_fidelity_k_squared": float(np.min(fidelities)),
        "max_fidelity_k_squared": float(np.max(fidelities)),
        "mean_half_overlap": float(np.mean(half_overlaps)),
    }


def poincare_distance(u: np.ndarray, v: np.ndarray) -> float:
    euclid_dist_sq = float(np.sum((u - v) ** 2))
    denom = (1.0 - float(np.sum(u**2))) * (1.0 - float(np.sum(v**2)))
    delta = max(1.0, 1.0 + 2.0 * (euclid_dist_sq / denom))
    return float(math.acosh(delta))


def p_adic_valuation(n: int, prime: int) -> int:
    if n == 0:
        return 10**9
    val = 0
    n = abs(n)
    while n % prime == 0:
        val += 1
        n //= prime
    return val


def p_adic_distance(n1: int, n2: int, prime: int) -> float:
    diff = n1 - n2
    v = p_adic_valuation(diff, prime)
    if v >= 10**8:
        return 0.0
    return float(prime ** (-v))


def check_ultrametric(dist_fn, points: list[int], prime: int) -> bool:
    for i, x in enumerate(points):
        for j, y in enumerate(points):
            if j <= i:
                continue
            for k, z in enumerate(points):
                if k <= j:
                    continue
                d_xy = dist_fn(x, y, prime)
                d_yz = dist_fn(y, z, prime)
                d_xz = dist_fn(x, z, prime)
                if d_xz > max(d_xy, d_yz) + 1e-12:
                    return False
    return True


def hyperbolic_vs_euclidean_expansion(
    nodes: dict[str, np.ndarray],
    pairs: list[tuple[str, str]],
) -> list[dict[str, float | str]]:
    rows: list[dict[str, float | str]] = []
    for name1, name2 in pairs:
        u = nodes[name1]
        v = nodes[name2]
        d_e = float(np.linalg.norm(u - v))
        d_h = poincare_distance(u, v)
        rows.append(
            {
                "pair": f"{name1} <-> {name2}",
                "euclidean": d_e,
                "hyperbolic": d_h,
                "expansion_ratio": d_h / d_e if d_e > 0 else 0.0,
            }
        )
    return rows

"""Endogenous initiative on network topologies (toy, X_trigger = 0).

Each node = one EIA-like drive unit (spec §7.2) extended with two internal
generators that the current DriveEngine lacks:
  * uncertainty aging:  u_i <- u_i + a (1 - u_i)       (knowledge goes stale)
  * noise:              sigma * xi                      (Schurger-style accumulator)
and one coupling term: an initiative at node j injects novelty into neighbours
AND raises their uncertainty (an answer somewhere opens questions elsewhere).

No external input at all. Question: how does the topology W shape the amount,
timing and self-sustainment of initiative?

Metrics per topology:
  rate        initiatives per node per tick
  n_hat       branching ratio: mean # initiatives at t+1 caused per initiative at t
              (estimated from coupling-attributed excess over isolated baseline)
  cv_isi      coefficient of variation of inter-initiative intervals (1 = Poisson)
  aval_alpha  power-law-ish exponent of avalanche sizes (log-log slope)
  persist     fraction of activity that remains when noise is switched off
              after warm-up (self-sustaining internal loop)
"""

from __future__ import annotations

import sys
from pathlib import Path

import networkx as nx
import numpy as np

N = 200
T = 3000
RHO, ALPHA, THETA = 0.12, 0.10, 0.60
AGE, RESOLVE, SIGMA = 0.004, 0.6, 0.03
BETA_U = 0.15  # neighbour initiative -> my uncertainty


def topologies(seed: int) -> dict[str, nx.Graph]:
    rng = seed
    return {
        "isolated": nx.empty_graph(N),
        "ring_k4": nx.watts_strogatz_graph(N, 4, 0.0, seed=rng),
        "small_world": nx.watts_strogatz_graph(N, 4, 0.1, seed=rng),
        "erdos_renyi": nx.erdos_renyi_graph(N, 4 / N, seed=rng),
        "scale_free": nx.barabasi_albert_graph(N, 2, seed=rng),
        "modular_sbm": nx.stochastic_block_model(
            [40] * 5, [[0.1 if i == j else 0.002 for j in range(5)] for i in range(5)], seed=rng
        ),
        "tree": nx.balanced_tree(2, 7).subgraph(range(N)).copy(),
        "complete": nx.complete_graph(N),
    }


def coupling(g: nx.Graph, gain: float) -> np.ndarray:
    """Normalise so spectral radius of W == gain (equal effective loop gain)."""
    a = nx.to_numpy_array(g, nodelist=range(N))
    if a.sum() == 0:
        return a
    lam = np.max(np.abs(np.linalg.eigvals(a)))
    return a * (gain / lam)


def simulate(w: np.ndarray, rng: np.random.Generator, noise_off_at: int | None = None):
    d = rng.uniform(0, 0.3, N)
    u = rng.uniform(0.2, 0.6, N)
    s = np.zeros(N)
    refr = np.zeros(N)
    spikes = np.zeros((T, N), dtype=bool)
    for t in range(T):
        sig = 0.0 if (noise_off_at is not None and t >= noise_off_at) else SIGMA
        drive_in = w @ s
        u = np.clip(u + AGE * (1 - u) + BETA_U * drive_in * (1 - u) - RESOLVE * u * s, 0, 1)
        d = (1 - RHO) * d + ALPHA * u + drive_in + sig * rng.standard_normal(N) - 0.8 * s
        d = np.clip(d, 0, 1)
        s = ((d > THETA) & (refr <= 0)).astype(float)
        refr = np.where(s > 0, 5, refr - 1)
        spikes[t] = s > 0
    return spikes


def metrics(spikes: np.ndarray, base_rate: float) -> dict[str, float]:
    burn = 500
    sp = spikes[burn:]
    rate = sp.mean()
    counts = sp.sum(1)
    # branching ratio: regress count(t+1) on count(t) after removing baseline
    x, y = counts[:-1], counts[1:]
    n_hat = float(np.cov(x, y)[0, 1] / (np.var(x) + 1e-9)) if np.var(x) > 0 else 0.0
    # ISI CV
    cvs = []
    for i in range(sp.shape[1]):
        ts = np.flatnonzero(sp[:, i])
        if len(ts) > 3:
            isi = np.diff(ts)
            cvs.append(isi.std() / isi.mean())
    cv = float(np.mean(cvs)) if cvs else float("nan")
    # avalanches: runs of consecutive non-empty ticks
    sizes, cur = [], 0
    for c in counts:
        if c > 0:
            cur += c
        elif cur:
            sizes.append(cur)
            cur = 0
    alpha = float("nan")
    if len(sizes) > 20:
        vals, freq = np.unique(sizes, return_counts=True)
        m = freq > 1
        if m.sum() > 3:
            alpha = float(np.polyfit(np.log(vals[m]), np.log(freq[m]), 1)[0])
    return {
        "rate": float(rate),
        "rate_x_base": float(rate / base_rate) if base_rate else float("nan"),
        "n_hat": n_hat,
        "cv_isi": cv,
        "aval_alpha": alpha,
        "max_aval": float(max(sizes) if sizes else 0),
    }


def main(gain: float = 0.5, seed: int = 42) -> None:
    rows = []
    base = None
    for name, g in topologies(seed).items():
        w = coupling(g, gain)
        rng = np.random.default_rng(seed)
        sp = simulate(w, rng)
        if base is None:
            base = sp[500:].mean()
        m = metrics(sp, base)
        rng2 = np.random.default_rng(seed)
        sp_off = simulate(w, rng2, noise_off_at=1500)
        on = sp_off[1000:1500].mean()
        off = sp_off[2500:].mean()
        m["persist"] = float(off / on) if on else 0.0
        rows.append((name, m))
    keys = ["rate", "rate_x_base", "n_hat", "cv_isi", "aval_alpha", "max_aval", "persist"]
    print(f"gain={gain} seed={seed}")
    print(f"{'topology':<13}" + "".join(f"{k:>12}" for k in keys))
    for name, m in rows:
        print(f"{name:<13}" + "".join(f"{m[k]:>12.3f}" for k in keys))


if __name__ == "__main__":
    gains = [float(a) for a in sys.argv[1:]] or [0.5]
    for gn in gains:
        main(gn)
        print()

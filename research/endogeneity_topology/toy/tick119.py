"""Tick 119: tick 118 controllability with more samples (6 seeds x 3 motives = 18 boosts per architecture);
also the spill-over to the rest (does the workspace turn a motive boost into agent-wide activation?)."""
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs
from tick118 import sim, sim_boost, build, layers, mods, N, T0

z = lambda x: x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))
print(f"{'architecture':<18}{'d self':>8}{'z':>7}{'d rest':>9}{'z':>7}")
for name, w in (("hier alone", 0.0), ("hier + workspace", 0.4)):
    a, b = [], []
    for seed in range(1, 7):
        H = nx.to_scipy_sparse_array(build("hier_modular", seed)[0], nodelist=range(N), format="csr", dtype=float)
        H = H / abs(eigs(H, k=1, which="LM", return_eigenvectors=False)[0]); _, B = layers(seed)
        lo, hi = 0.3, 1.4
        for _ in range(10):
            mid = (lo+hi)/2; lo, hi = (mid, hi) if sim(H*mid + B*w, seed, 1000)[500:].mean() < 0.03 else (lo, mid)
        W = sps.csr_matrix(H*(lo+hi)/2 + B*w); tw = sim_boost(W, seed)
        for m in (2, 5, 8):
            ins = mods == m; pe = sim_boost(W, seed, np.flatnonzero(ins))
            a.append(int(pe[T0:, ins].sum()) - int(tw[T0:, ins].sum())); b.append(int(pe[T0:, ~ins].sum()) - int(tw[T0:, ~ins].sum()))
    a, b = np.array(a), np.array(b)
    print(f"{name:<18}{a.mean():>8.1f}{z(a):>7.2f}{b.mean():>9.1f}{z(b):>7.2f}", flush=True)

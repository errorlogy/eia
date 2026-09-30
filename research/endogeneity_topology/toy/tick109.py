"""Tick 109: re-check A30 (modularity protects against externalised endogeneity: SBM 0.15 vs ER 0.32) with scattered
sensors/motors — in SBM the contiguous block was exactly one module. w=1, D=20, 3 seeds."""
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs
import tick98
from tick104 import graph as g104
N = 1000
print(f"{'topology':<9}{'placement':<11}{'hidden world support':>21}")
for kind in ("SBM", "ER"):
    for place in ("contiguous", "scattered"):
        vals = []
        for seed in (1, 2, 3):
            if place == "contiguous": tick98.sens, tick98.motor = np.arange(0, 100), np.arange(900, 1000)
            else:
                perm = np.random.default_rng(seed + 11).permutation(N); tick98.sens, tick98.motor = np.sort(perm[:100]), np.sort(perm[100:200])
            A = nx.to_scipy_sparse_array(g104(kind, seed), nodelist=range(N), format="csr", dtype=float); A1 = A / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0])
            lo, hi = 0.3, 1.5
            for _ in range(9):
                mid = (lo+hi)/2; lo, hi = (mid, hi) if tick98.sim(sps.csr_matrix(A1*mid), seed, 1.0, 1500)[0].mean() < 0.03 else (lo, mid)
            W = sps.csr_matrix(A1*(lo+hi)/2)
            f1, _ = tick98.sim(W, seed, 1.0); c1, _ = tick98.sim(W, seed, 1.0, cut=True)
            f0, _ = tick98.sim(W, seed, 0.0); c0, _ = tick98.sim(W, seed, 0.0, cut=True)
            vals.append((1 - c1.mean() / f1.mean()) - (1 - c0.mean() / f0.mean()))
        print(f"{kind:<9}{place:<11}{np.mean(vals):>21.2f}", flush=True)

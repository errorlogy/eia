"""Tick 110: A31 (contingency vs volume) with a SCATTERED sensor/motor interface. SBM and ER agents, 3 seeds.
Same modes as tick 100: contingent echo, cut world, non-contingent block-shuffled replay."""
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs
import tick100
from tick100 import agent, NA

print(f"{'agent':<5}{'kept: cut':>10}{'kept: replay':>13}{'contingency share':>19}")
for kind in ("SBM", "ER"):
    rows = []
    for seed in (1, 2, 3):
        perm = np.random.default_rng(seed + 11).permutation(NA); tick100.sens, tick100.motor = np.sort(perm[:100]), np.sort(perm[100:200])
        A = nx.to_scipy_sparse_array(agent(kind, seed), nodelist=range(NA), format="csr", dtype=float); A1 = A / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0])
        lo, hi = 0.3, 1.5
        for _ in range(9):
            mid = (lo+hi)/2; lo, hi = (mid, hi) if tick100.sim(sps.csr_matrix(A1*mid), seed, "contingent", 1500)[0].mean() < 0.03 else (lo, mid)
        W = sps.csr_matrix(A1*(lo+hi)/2)
        full, rec = tick100.sim(W, seed, "contingent")
        blocks = np.array_split(np.arange(len(rec)), len(rec) // 50); order = np.random.default_rng(seed + 5).permutation(len(blocks))
        cut, _ = tick100.sim(W, seed, "cut"); rep, _ = tick100.sim(W, seed, "replay", replay=np.concatenate([rec[blocks[i]] for i in order]))
        kc, kr = cut.mean() / full.mean(), rep.mean() / full.mean(); rows.append((kc, kr, (1 - kr) / max(1 - kc, 1e-9)))
    m = np.mean(rows, 0); print(f"{kind:<5}{m[0]:>10.2f}{m[1]:>13.2f}{m[2]:>19.2f}", flush=True)

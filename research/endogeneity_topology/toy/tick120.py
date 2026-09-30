"""Tick 120: hierarchy + workspace (w 0.4) with and without the leaky Governor (tick 93: slow upward-only share cap +
global budget loop with slow integral). Per-motive controllability (u-only boost of motives 2, 5, 8; exact twin) and
spill-over. No strong generator here — tests whether the Governor restores control lost to the workspace. 6 seeds."""
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs
import topo_endo as te
from tick93 import sim, N, mods, T0
from tick118 import build, layers

z = lambda x: x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))
alpha = np.full(N, te.ALPHA)
print(f"{'condition':<24}{'d self':>8}{'z':>7}{'d rest':>9}{'z':>7}")
for name, gov in (("hier+ws, no governor", False), ("hier+ws + leaky governor", True)):
    a, b = [], []
    for seed in range(1, 7):
        H = nx.to_scipy_sparse_array(build("hier_modular", seed)[0], nodelist=range(N), format="csr", dtype=float)
        H = H / abs(eigs(H, k=1, which="LM", return_eigenvectors=False)[0]); _, B = layers(seed)
        lo, hi = 0.3, 1.4
        for _ in range(10):
            mid = (lo+hi)/2; lo, hi = (mid, hi) if sim(sps.csr_matrix(H*mid + B*0.4), alpha, seed, False)[500:1500].mean() < 0.03 else (lo, mid)
        W = sps.csr_matrix(H*(lo+hi)/2 + B*0.4); tw = sim(W, alpha, seed, gov)
        for m in (2, 5, 8):
            ins = mods == m; pe = sim(W, alpha, seed, gov, boost=np.flatnonzero(ins))
            a.append(int(pe[T0:, ins].sum()) - int(tw[T0:, ins].sum())); b.append(int(pe[T0:, ~ins].sum()) - int(tw[T0:, ~ins].sum()))
    a, b = np.array(a), np.array(b)
    print(f"{name:<24}{a.mean():>8.1f}{z(a):>7.2f}{b.mean():>9.1f}{z(b):>7.2f}", flush=True)

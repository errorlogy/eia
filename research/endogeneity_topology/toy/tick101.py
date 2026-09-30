"""Tick 101: core-periphery topology. Core 200 units (dense, p_cc), periphery 800 units (sparse among themselves, attached
to the core). Mean degree ~5. A26 signature of core vs periphery (out-influence per unit share, independence) and share of
initiatives originating in each (first unit of each cascade = unit firing with no active in-neighbour at t-1). 3 seeds."""
import numpy as np, scipy.sparse as sps
from scipy.sparse.linalg import eigs
from tick85 import sim, te
N = 1000; core = np.arange(N) < 200

def build(seed):
    rng = np.random.default_rng(seed)
    P = np.where(core[:, None] & core[None, :], 0.06, np.where(core[:, None] | core[None, :], 0.006, 0.0015))
    A = np.triu(rng.random((N, N)) < P, 1); A = (A | A.T).astype(float); return sps.csr_matrix(A)

print(f"{'block':<10}{'out/unit share':>15}{'indep':>7}{'share of cascade starts':>25}{'share of activity':>19}")
res = {"core": [], "periphery": []}
for seed in (1, 2, 3):
    A = build(seed); A1 = A / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0]); alpha = np.full(N, te.ALPHA)
    lo, hi = 0.5, 1.5
    for _ in range(9):
        mid = (lo+hi)/2; lo, hi = (mid, hi) if sim(sps.csr_matrix(A1*mid), alpha, seed, 1500).mean() < 0.03 else (lo, mid)
    W = sps.csr_matrix(A1*(lo+hi)/2); base = sim(W, alpha, seed)
    prev_in = np.vstack([np.zeros((1, N)), (sps.csr_matrix(base[:-1].astype(float)) @ (W > 0).T.astype(float)).toarray()])
    starts = base & (prev_in == 0)
    for name, blk in (("core", core), ("periphery", ~core)):
        sil = sim(W, alpha, seed, silent=blk); out = (1 - sil[:, ~blk].mean() / base[:, ~blk].mean()) / blk.mean()
        Wc = W.toarray(); Wc[np.ix_(blk, ~blk)] = 0; indep = sim(sps.csr_matrix(Wc), alpha, seed)[:, blk].mean() / base[:, blk].mean()
        res[name].append((out, indep, starts[:, blk].sum() / starts.sum(), base[:, blk].sum() / base.sum()))
for name, rows in res.items():
    m = np.mean(rows, 0); print(f"{name:<10}{m[0]:>15.2f}{m[1]:>7.2f}{m[2]:>25.2f}{m[3]:>19.2f}", flush=True)
print(f"(core = {core.mean():.0%} of units)")

"""Tick 145: per-motive controllability across dynamic-routing regimes (A38). SBM 10x100 (mu 0.2) with co-activity gating beta
in {0, 0.5, 2}; u-only do(Z) on anatomical module 3 or 7 at t0 = 2000; exact twin; 600 ticks. 5 seeds x 2 modules."""
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs
import topo_endo as te
from tick142 import sim as sim_plain
N = 1000; mods = np.arange(N) // 100; T, T0 = 2600, 2000

def sim(W, seed, beta, S=None):
    rng = np.random.default_rng(seed); Wc = W.tocoo(); r, c, w0 = Wc.row, Wc.col, Wc.data
    d = rng.uniform(0, .3, N); u = rng.uniform(.2, .6, N); s = np.zeros(N); refr = np.zeros(N); tr = np.full(N, 0.03); out = np.zeros((T, N), bool)
    for t in range(T):
        if S is not None and t == T0: u[S] = 1.0
        if beta:
            z = (tr - tr.mean()) / (tr.std() + 1e-9); g = np.clip(1 + beta * (z[r] * z[c] - 1), 0, None)
            inp = np.bincount(r, weights=w0 * g * s[c], minlength=N)
        else:
            inp = W @ s
        u = np.clip(u + te.AGE*(1-u) + te.BETA_U*inp*(1-u) - te.RESOLVE*u*s, 0, 1)
        d = np.clip((1-te.RHO)*d + te.ALPHA*u + inp + te.SIGMA*rng.standard_normal(N) - .8*s, 0, 1)
        s = ((d > te.THETA) & (refr <= 0)).astype(float); refr = np.where(s > 0, 5, refr-1); tr += (s - tr) / 20; out[t] = s > 0
    return out

z = lambda x: x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))
print(f"{'beta':>5}{'d self':>8}{'z':>7}{'d rest':>9}{'z':>7}")
for beta in (0.0, 0.5, 2.0):
    a, b = [], []
    for seed in range(1, 6):
        g = nx.stochastic_block_model([100]*10, [[5*0.8/99 if i == j else 5*0.2/900 for j in range(10)] for i in range(10)], seed=seed, sparse=True)
        A = nx.to_scipy_sparse_array(g, nodelist=range(N), format="csr", dtype=float); A1 = A / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0])
        lo, hi = 0.3, 8.0
        for _ in range(11):
            mid = (lo+hi)/2; lo, hi = (mid, hi) if sim_plain(sps.csr_matrix(A1*mid), seed, beta, 1500)[0].mean() < 0.03 else (lo, mid)
        W = sps.csr_matrix(A1*(lo+hi)/2); tw = sim(W, seed, beta)
        for m in (3, 7):
            ins = mods == m; pe = sim(W, seed, beta, np.flatnonzero(ins))
            a.append(int(pe[T0:, ins].sum()) - int(tw[T0:, ins].sum())); b.append(int(pe[T0:, ~ins].sum()) - int(tw[T0:, ~ins].sum()))
    a, b = np.array(a), np.array(b); print(f"{beta:>5}{a.mean():>8.1f}{z(a):>7.2f}{b.mean():>9.1f}{z(b):>7.2f}", flush=True)

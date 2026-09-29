"""Tick 92: a leaky, chronic-dominance Governor. Per-motive threshold theta_m = theta0 + kp * max(0, S_m - cap), where S_m
is a slow EMA of the motive's activity share (tau ~1000 ticks) -> reacts to chronic dominance, not to transient surges;
no integration, thresholds never go below theta0. Global loop: offset = kg * (R - 0.03) with R a slow EMA of rate.
Metrics: generator share, overall rate, and controllability of a non-dominant motive (u-only do(Z), exact twin).
Module 0 x2.5; 6 seeds x 2 targets."""
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs
import topo_endo as te
N = 1000; mods = np.arange(N) // 100; tgt0 = mods == 0; T, T0 = 2600, 2000
M = np.stack([mods == m for m in range(10)], 1).astype(float)

def sim(W, alpha, seed, gov, boost=None, kp=1.5, kg=2.0, tau=1000.0):
    rng = np.random.default_rng(seed); S = np.full(10, 0.1); R = 0.03
    d = rng.uniform(0, .3, N); u = rng.uniform(.2, .6, N); s = np.zeros(N); refr = np.zeros(N); out = np.zeros((T, N), bool)
    for t in range(T):
        if boost is not None and t == T0: u[boost] = 1.0
        theta = te.THETA + (kp * np.maximum(0, S - 0.15) if gov else 0) + (kg * (R - 0.03) if gov else 0)
        inp = W @ s
        u = np.clip(u + te.AGE*(1-u) + te.BETA_U*inp*(1-u) - te.RESOLVE*u*s, 0, 1)
        d = np.clip((1-te.RHO)*d + alpha*u + inp + te.SIGMA*rng.standard_normal(N) - .8*s, 0, 1)
        thr = theta[mods] if np.ndim(theta) else theta
        s = ((d > thr) & (refr <= 0)).astype(float); refr = np.where(s > 0, 5, refr-1); out[t] = s > 0
        tot = s.sum()
        if tot: S += (s @ M / tot - S) / tau
        R += (s.mean() - R) / tau
    return out

z = lambda x: x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))
print(f"{'condition':<16}{'gen share':>10}{'rate':>7}{'d self':>8}{'z':>7}{'d rest':>9}{'z':>7}")
for name, gov in (("no governor", False), ("leaky governor", True)):
    a, b, shares, rates = [], [], [], []
    for seed in range(1, 7):
        g = nx.stochastic_block_model([100]*10, [[5*0.9/99 if i == j else 5*0.1/900 for j in range(10)] for i in range(10)], seed=seed, sparse=True)
        A = nx.to_scipy_sparse_array(g, nodelist=range(N), format="csr", dtype=float); A1 = A / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0])
        alpha = np.full(N, te.ALPHA); alpha[tgt0] *= 2.5
        lo, hi = 0.3, 1.5
        for _ in range(9):
            mid = (lo+hi)/2; lo, hi = (mid, hi) if sim(sps.csr_matrix(A1*mid), alpha, seed, False)[500:1500].mean() < 0.03 else (lo, mid)
        W = sps.csr_matrix(A1*(lo+hi)/2); tw = sim(W, alpha, seed, gov)
        shares.append(tw[1000:T0, tgt0].sum() / tw[1000:T0].sum()); rates.append(tw[1000:T0].mean())
        for m in (5, 8):
            ins = mods == m; pe = sim(W, alpha, seed, gov, boost=np.flatnonzero(ins))
            a.append(int(pe[T0:, ins].sum()) - int(tw[T0:, ins].sum())); b.append(int(pe[T0:, ~ins].sum()) - int(tw[T0:, ~ins].sum()))
    a, b = np.array(a), np.array(b)
    print(f"{name:<16}{np.mean(shares):>10.2f}{np.mean(rates):>7.3f}{a.mean():>8.1f}{z(a):>7.2f}{b.mean():>9.1f}{z(b):>7.2f}", flush=True)

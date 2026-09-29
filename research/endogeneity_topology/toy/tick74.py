"""Tick 74: causal reach of an internal intervention in EDR space. u-only do(Z) on the 50 units nearest the centre;
exact twin; SIGNED extra initiatives in distance rings over 400 ticks, per unit (abs values measure only
trajectory divergence, which is global — see tick 6). Fit an exponential decay length
ell of the effect vs distance and compare with lambda. 2 lambdas x 4 seeds (x 2 centres)."""
import numpy as np, scipy.sparse as sps
from scipy.sparse.linalg import eigs
import topo_endo as te
from tick73 import edr, N

T, T0 = 1400, 1000
def sim(W, seed, S=None):
    rng = np.random.default_rng(seed)
    d = rng.uniform(0, .3, N); u = rng.uniform(.2, .6, N); s = np.zeros(N); refr = np.zeros(N); out = np.zeros((T, N), bool)
    for t in range(T):
        if S is not None and t == T0: u[S] = 1.0
        xi = rng.standard_normal(N); inp = W @ s
        u = np.clip(u + te.AGE*(1-u) + te.BETA_U*inp*(1-u) - te.RESOLVE*u*s, 0, 1)
        d = np.clip((1-te.RHO)*d + te.ALPHA*u + inp + te.SIGMA*xi - .8*s, 0, 1)
        s = ((d > te.THETA) & (refr <= 0)).astype(float); refr = np.where(s > 0, 5, refr-1); out[t] = s > 0
    return out

edges = np.array([0, 0.05, 0.1, 0.15, 0.2, 0.3, 0.45])
print(f"{'lambda':>7} | mean SIGNED extra initiatives per unit in rings " + " ".join(f"{a:.2f}-{b:.2f}" for a, b in zip(edges[:-1], edges[1:])) + " | ell | ell/lambda")
for lam in (0.05, 0.12):
    prof = []
    for seed in (1, 2, 3, 4):
        A, xy = edr(seed, lam); A1 = A / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0])
        lo, hi = 0.7, 1.4
        for _ in range(10):
            mid = (lo+hi)/2; lo, hi = (mid, hi) if sim(A1*mid, seed)[500:1000].mean() < 0.03 else (lo, mid)
        W = sps.csr_matrix(A1*(lo+hi)/2); tw = sim(W, seed)
        for c in ((0.35, 0.35), (0.65, 0.65)):
            dist = np.sqrt(((xy - np.array(c)) ** 2).sum(1)); S = np.argsort(dist)[:50]
            pe = sim(W, seed, S); diff = pe[T0:].sum(0).astype(int) - tw[T0:].sum(0).astype(int)
            prof.append([diff[(dist >= a) & (dist < b)].mean() for a, b in zip(edges[:-1], edges[1:])])
    p = np.mean(prof, 0); mids = (edges[:-1] + edges[1:]) / 2
    ok = p > 0
    ell = -1 / np.polyfit(mids[ok][1:], np.log(p[ok][1:]), 1)[0] if ok[1:].sum() >= 2 else float("nan")
    print(f"{lam:>7} | {'':>40}" + " ".join(f"{x:>9.2f}" for x in p) + f" | {ell:.3f} | {ell/lam:.1f}", flush=True)

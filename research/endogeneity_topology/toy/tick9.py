"""Tick 9: discharge hypothesis for negative spill-over in hierarchy.
do(Z) variants on module S at t0: full (d=1,u=1), u_only (u=1), d_only (d=1).
If negative spill-over comes from forced discharge, it should persist in d_only and vanish in u_only."""
import io, contextlib, runpy
import numpy as np, networkx as nx
from scipy.sparse.linalg import eigs
import topo_endo as te
with contextlib.redirect_stdout(io.StringIO()):
    ns = runpy.run_path("tick6.py")
build, N, T, T0 = ns["build"], ns["N"], ns["T"], ns["T0"]
TARGET = 0.03

def sim(W, seed, S=None, mode="full"):
    rng = np.random.default_rng(seed)
    d = rng.uniform(0, .3, N); u = rng.uniform(.2, .6, N); s = np.zeros(N); refr = np.zeros(N)
    out = np.zeros((T, N), bool)
    for t in range(T):
        if S is not None and t == T0:
            if mode in ("full", "d_only"): d[S] = 1.0
            if mode in ("full", "u_only"): u[S] = 1.0
        xi = rng.standard_normal(N); inp = W @ s
        u = np.clip(u + te.AGE*(1-u) + te.BETA_U*inp*(1-u) - te.RESOLVE*u*s, 0, 1)
        d = np.clip((1-te.RHO)*d + te.ALPHA*u + inp + te.SIGMA*xi - .8*s, 0, 1)
        s = ((d > te.THETA) & (refr <= 0)).astype(float); refr = np.where(s > 0, 5, refr-1)
        out[t] = s > 0
    return out

z = lambda x: x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))
modes = ["full", "u_only", "d_only"]
print(f"{'topology':<13}{'mode':<8}{'dI_in':>8}{'z_in':>7}{'dI_out':>9}{'z_out':>7}{'dI_out_early':>13}{'z_early':>8}")
for name in ["erdos_renyi", "hier_modular"]:
    acc = {m: ([], [], []) for m in modes}
    for seed in range(1, 11):
        g, mods, _ = build(name, seed)
        A = nx.to_scipy_sparse_array(g, nodelist=range(N), format="csr", dtype=float)
        A1 = A / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0])
        lo, hi = 0.8, 1.2
        for _ in range(10):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if sim(A1*mid, seed)[500:T0].mean() < TARGET else (lo, mid)
        W = A1 * (lo + hi) / 2
        tw = sim(W, seed)
        for S in mods:
            ins = np.zeros(N, bool); ins[S] = True
            for m in modes:
                pe = sim(W, seed, S, m)
                acc[m][0].append(int(pe[T0:, ins].sum()) - int(tw[T0:, ins].sum()))
                acc[m][1].append(int(pe[T0:, ~ins].sum()) - int(tw[T0:, ~ins].sum()))
                acc[m][2].append(int(pe[T0:T0+100, ~ins].sum()) - int(tw[T0:T0+100, ~ins].sum()))
    for m in modes:
        a, b, c = map(np.array, acc[m])
        print(f"{name:<13}{m:<8}{a.mean():>8.1f}{z(a):>7.2f}{b.mean():>9.1f}{z(b):>7.2f}{c.mean():>13.1f}{z(c):>8.2f}")

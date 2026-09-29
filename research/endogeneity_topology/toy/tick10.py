"""Tick 10: fuel-depletion test. Variant 'no_trig_resolve': initiatives that were triggered by
neighbour input (inp>0 at that tick) do NOT resolve uncertainty; spontaneous ones still do.
(RESOLVE=0 globally is degenerate: u->1 everywhere, drive fixed point > threshold.)
Prediction if fuel depletion is the mechanism: hier negative spill-over vanishes."""
import io, contextlib, runpy
import numpy as np, networkx as nx
from scipy.sparse.linalg import eigs
import topo_endo as te
with contextlib.redirect_stdout(io.StringIO()):
    ns = runpy.run_path("tick6.py")
build, N, T, T0 = ns["build"], ns["N"], ns["T"], ns["T0"]
TARGET = 0.03

def sim(W, seed, S=None, variant="base"):
    rng = np.random.default_rng(seed)
    d = rng.uniform(0, .3, N); u = rng.uniform(.2, .6, N); s = np.zeros(N); refr = np.zeros(N)
    trig = np.zeros(N, bool)
    out = np.zeros((T, N), bool)
    for t in range(T):
        if S is not None and t == T0:
            u[S] = 1.0                                   # u-only do(Z) (strongest effect in tick 9)
        xi = rng.standard_normal(N); inp = W @ s
        res = s if variant == "base" else s * (~trig)
        u = np.clip(u + te.AGE*(1-u) + te.BETA_U*inp*(1-u) - te.RESOLVE*u*res, 0, 1)
        d = np.clip((1-te.RHO)*d + te.ALPHA*u + inp + te.SIGMA*xi - .8*s, 0, 1)
        s = ((d > te.THETA) & (refr <= 0)).astype(float); refr = np.where(s > 0, 5, refr-1)
        trig = (s > 0) & (inp > 1e-12)
        out[t] = s > 0
    return out

z = lambda x: x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))
print(f"{'topology':<13}{'variant':<16}{'gain':>6}{'trig%':>7}{'dI_in':>8}{'z_in':>7}{'dI_out':>9}{'z_out':>7}")
for name in ["erdos_renyi", "hier_modular"]:
    for variant in ["base", "no_trig_resolve"]:
        a, b, gs, tf = [], [], [], []
        for seed in range(1, 11):
            g, mods, _ = build(name, seed)
            A = nx.to_scipy_sparse_array(g, nodelist=range(N), format="csr", dtype=float)
            A1 = A / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0])
            lo, hi = 0.5, 1.3
            for _ in range(11):
                mid = (lo + hi) / 2
                lo, hi = (mid, hi) if sim(A1*mid, seed, variant=variant)[500:T0].mean() < TARGET else (lo, mid)
            W = A1 * (lo + hi) / 2; gs.append((lo + hi) / 2)
            tw = sim(W, seed, variant=variant)
            sp = tw[500:]; prev = np.vstack([np.zeros((1, N), bool), sp[:-1]])
            tf.append((sp & ((prev.astype(float) @ W.T.toarray() if hasattr(W,'toarray') else prev @ W.T) > 0)).sum() / max(1, sp.sum()))
            for S in mods:
                ins = np.zeros(N, bool); ins[S] = True
                pe = sim(W, seed, S, variant)
                a.append(int(pe[T0:, ins].sum()) - int(tw[T0:, ins].sum()))
                b.append(int(pe[T0:, ~ins].sum()) - int(tw[T0:, ~ins].sum()))
        a, b = np.array(a), np.array(b)
        print(f"{name:<13}{variant:<16}{np.mean(gs):>6.3f}{100*np.mean(tf):>6.0f}%{a.mean():>8.1f}{z(a):>7.2f}{b.mean():>9.1f}{z(b):>7.2f}")

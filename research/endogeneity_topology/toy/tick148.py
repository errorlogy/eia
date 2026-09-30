"""Tick 148: open-endedness of initiative patterns. A 'pattern' = which of the 10 modules burst together in a tick
(binary 10-vector, module bursting = >= 10 % active). Over a long silent run, count distinct multi-module patterns discovered
over time (discovery curve) and the late discovery rate (new patterns in the last third per 1000 ticks), plus pattern entropy.
Topologies: ER, SBM (mu 0.1), hier-modular, SBM + dynamic routing beta 2 (tick 142). Rate-matched 0.03; 2 seeds; 15 000 ticks."""
import io, contextlib, runpy
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs
import topo_endo as te
with contextlib.redirect_stdout(io.StringIO()):
    build = runpy.run_path("tick6.py")["build"]
from tick142 import sim as sim_route
N = 1000; mods = np.arange(N) // 100; T = 15000

def sim(W, seed, T):
    rng = np.random.default_rng(seed)
    d = rng.uniform(0, .3, N); u = rng.uniform(.2, .6, N); s = np.zeros(N); refr = np.zeros(N); out = np.zeros((T, 10), bool)
    for t in range(T):
        inp = W @ s
        u = np.clip(u + te.AGE*(1-u) + te.BETA_U*inp*(1-u) - te.RESOLVE*u*s, 0, 1)
        d = np.clip((1-te.RHO)*d + te.ALPHA*u + inp + te.SIGMA*rng.standard_normal(N) - .8*s, 0, 1)
        s = ((d > te.THETA) & (refr <= 0)).astype(float); refr = np.where(s > 0, 5, refr-1)
        out[t] = np.bincount(mods, weights=s, minlength=10) >= 10
    return out

def discovery(P):
    seen, curve = set(), []
    for row in P:
        if row.sum() >= 2: seen.add(row.tobytes())
        curve.append(len(seen))
    c = np.array(curve); late = (c[-1] - c[2 * len(c) // 3]) / (len(c) / 3) * 1000
    pats = [r.tobytes() for r in P if r.sum() >= 2]; _, cnt = np.unique(pats, return_counts=True); p = cnt / cnt.sum()
    return c[-1], late, float(-(p * np.log2(p)).sum())

def graph(kind, seed):
    if kind == "ER": return nx.erdos_renyi_graph(N, 5/N, seed=seed)
    if kind == "hier": return build("hier_modular", seed)[0]
    return nx.stochastic_block_model([100]*10, [[5*0.9/99 if i == j else 5*0.1/900 for j in range(10)] for i in range(10)], seed=seed, sparse=True)

print(f"{'topology':<18}{'distinct patterns':>18}{'late new / 1000t':>18}{'pattern entropy':>17}")
for kind in ("ER", "SBM", "hier", "SBM + routing b2"):
    rows = []
    for seed in (1, 2):
        A = nx.to_scipy_sparse_array(graph(kind, seed), nodelist=range(N), format="csr", dtype=float); A1 = A / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0])
        if kind.startswith("SBM +"):
            lo, hi = 0.3, 8.0
            for _ in range(10):
                mid = (lo+hi)/2; lo, hi = (mid, hi) if sim_route(sps.csr_matrix(A1*mid), seed, 2.0, 1500)[0].mean() < 0.03 else (lo, mid)
            sp, _ = sim_route(sps.csr_matrix(A1*(lo+hi)/2), seed, 2.0, T)
            P = np.stack([sp[:, mods == m].mean(1) >= 0.10 for m in range(10)], 1)
        else:
            # rate-match on unit activity via the routing sim with beta 0 (same dynamics)
            lo, hi = 0.5, 1.5
            for _ in range(9):
                mid = (lo+hi)/2; lo, hi = (mid, hi) if sim_route(sps.csr_matrix(A1*mid), seed, 0.0, 1500)[0].mean() < 0.03 else (lo, mid)
            P = sim(sps.csr_matrix(A1*(lo+hi)/2), seed, T)[500:]
        rows.append(discovery(P))
    m = np.mean(rows, 0); print(f"{kind:<18}{m[0]:>18.0f}{m[1]:>18.2f}{m[2]:>17.2f}", flush=True)

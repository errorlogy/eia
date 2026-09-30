"""Tick 94: robustness of the Governor recipe (tick 93) across topologies. Motive labels = 10 blocks of 100 units.
  SBM (tick 93), hierarchical-modular (100x10 modules, 20 super-modules; motive = 100 consecutive units = 2 super-modules... see build),
  ER (labels carry no structure). Module 0 x2.5; 4 seeds x 2 targets. Generator share and controllability, gov vs none."""
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs
import topo_endo as te
from tick93 import sim, N, mods, tgt0, T0
import runpy, io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    build6 = runpy.run_path("tick6.py")["build"]

def graph(kind, seed):
    if kind == "SBM":
        return nx.stochastic_block_model([100]*10, [[5*0.9/99 if i == j else 5*0.1/900 for j in range(10)] for i in range(10)], seed=seed, sparse=True)
    if kind == "hier":
        return build6("hier_modular", seed)[0]
    return nx.erdos_renyi_graph(N, 5/N, seed=seed)

z = lambda x: x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))
print(f"{'topology':<8}{'governor':<9}{'gen share':>10}{'rate':>7}{'d self':>8}{'z':>7}")
for kind in ("SBM", "hier", "ER"):
    for gov in (False, True):
        a, shares, rates = [], [], []
        for seed in range(1, 5):
            A = nx.to_scipy_sparse_array(graph(kind, seed), nodelist=range(N), format="csr", dtype=float)
            A1 = A / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0])
            alpha = np.full(N, te.ALPHA); alpha[tgt0] *= 2.5
            lo, hi = 0.3, 1.5
            for _ in range(9):
                mid = (lo+hi)/2; lo, hi = (mid, hi) if sim(sps.csr_matrix(A1*mid), alpha, seed, False)[500:1500].mean() < 0.03 else (lo, mid)
            W = sps.csr_matrix(A1*(lo+hi)/2); tw = sim(W, alpha, seed, gov)
            shares.append(tw[1000:T0, tgt0].sum() / tw[1000:T0].sum()); rates.append(tw[1000:T0].mean())
            for m in (5, 8):
                ins = mods == m; pe = sim(W, alpha, seed, gov, boost=np.flatnonzero(ins))
                a.append(int(pe[T0:, ins].sum()) - int(tw[T0:, ins].sum()))
        a = np.array(a)
        print(f"{kind:<8}{('yes' if gov else 'no'):<9}{np.mean(shares):>10.2f}{np.mean(rates):>7.3f}{a.mean():>8.1f}{z(a):>7.2f}", flush=True)

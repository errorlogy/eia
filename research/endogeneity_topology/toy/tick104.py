"""Tick 104: resilience of endogenous initiative to lesions. Topologies: ER, SBM (mu 0.1), hier-modular, scale-free (BA m=3).
Gain fixed at the intact rate-matched value (0.03); remove 5 / 10 / 20 % of units either at random or highest-degree first
(silenced permanently). Metric: activity of the remaining units relative to intact. 2 seeds."""
import io, contextlib, runpy
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs
with contextlib.redirect_stdout(io.StringIO()):
    ns6 = runpy.run_path("tick6.py")
build = ns6["build"]
from tick85 import sim, te
N = 1000

def graph(kind, seed):
    if kind == "ER": return nx.erdos_renyi_graph(N, 5/N, seed=seed)
    if kind == "SBM": return nx.stochastic_block_model([100]*10, [[5*0.9/99 if i == j else 5*0.1/900 for j in range(10)] for i in range(10)], seed=seed, sparse=True)
    if kind == "hier": return build("hier_modular", seed)[0]
    return nx.barabasi_albert_graph(N, 3, seed=seed)

fracs = [0.05, 0.10, 0.20]
print(f"{'topology':<9}{'removal':<9}" + "".join(f"{int(f*100):>6}%" for f in fracs) + "   (remaining units' activity / intact)")
for kind in ("ER", "SBM", "hier", "BA"):
    out = {"random": [], "hubs": []}
    for seed in (1, 2):
        g = graph(kind, seed); A = nx.to_scipy_sparse_array(g, nodelist=range(N), format="csr", dtype=float)
        A1 = A / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0]); alpha = np.full(N, te.ALPHA)
        lo, hi = 0.5, 1.5
        for _ in range(9):
            mid = (lo+hi)/2; lo, hi = (mid, hi) if sim(sps.csr_matrix(A1*mid), alpha, seed, 1500).mean() < 0.03 else (lo, mid)
        W = sps.csr_matrix(A1*(lo+hi)/2); base = sim(W, alpha, seed, 2000)
        deg = np.asarray(A.sum(1)).ravel(); rng = np.random.default_rng(seed)
        for mode in out:
            row = []
            for f in fracs:
                k = int(f * N)
                gone = np.argsort(-deg)[:k] if mode == "hubs" else rng.choice(N, k, replace=False)
                mask = np.zeros(N, bool); mask[gone] = True
                les = sim(W, alpha, seed, 2000, silent=mask)
                row.append(les[:, ~mask].mean() / base[:, ~mask].mean())
            out[mode].append(row)
    for mode, rows in out.items():
        print(f"{kind:<9}{mode:<9}" + "".join(f"{x:>7.2f}" for x in np.mean(rows, 0)), flush=True)

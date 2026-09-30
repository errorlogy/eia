"""Tick 99: world echo delay as memory. w = 1, delay D in {5, 20, 100, 300}; hidden support (1 - activity kept when world
cut, minus the w=0 noise floor) vs directly attributed share; SBM agent (as tick 98) and ER agent. 3 seeds."""
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs
from tick98 import sim, NA

def agent(kind, seed):
    if kind == "SBM":
        return nx.stochastic_block_model([100]*10, [[5*0.9/99 if i == j else 5*0.1/900 for j in range(10)] for i in range(10)], seed=seed, sparse=True)
    return nx.erdos_renyi_graph(NA, 5/NA, seed=seed)

print(f"{'agent':<5}{'D':>5}{'direct share':>14}{'hidden support':>16}{'ratio':>7}")
for kind in ("SBM", "ER"):
    for D in (5, 20, 100, 300):
        rows = []
        for seed in (1, 2, 3):
            A = nx.to_scipy_sparse_array(agent(kind, seed), nodelist=range(NA), format="csr", dtype=float); A1 = A / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0])
            lo, hi = 0.3, 1.5
            for _ in range(9):
                mid = (lo+hi)/2; lo, hi = (mid, hi) if sim(sps.csr_matrix(A1*mid), seed, 1.0, 1500, D=D)[0].mean() < 0.03 else (lo, mid)
            W = sps.csr_matrix(A1*(lo+hi)/2)
            full, via = sim(W, seed, 1.0, D=D); cut, _ = sim(W, seed, 1.0, D=D, cut=True)
            f0, _ = sim(W, seed, 0.0, D=D); c0, _ = sim(W, seed, 0.0, D=D, cut=True)
            hidden = (1 - cut.mean() / full.mean()) - (1 - c0.mean() / f0.mean())
            rows.append((via, hidden))
        m = np.mean(rows, 0); print(f"{kind:<5}{D:>5}{m[0]:>14.3f}{m[1]:>16.3f}{m[1]/max(m[0],1e-9):>7.1f}", flush=True)

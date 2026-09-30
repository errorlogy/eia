"""Tick 107: fill the '?' cells of the topology scorecard. For small-world (k=4, p=0.1), EDR (lambda 0.05), hier-modular, BA:
lesion resilience (10 % random / 10 % hubs, fixed gain), noise-off kept (small-world only missing), hidden world support
(w=1, D=20; net of noise floor). 2 seeds."""
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs
from tick85 import sim, te
from tick104 import graph as g104
from tick73 import edr
from tick106 import run as run_noise
from tick98 import sim as sim_world
N = 1000

def adj(kind, seed):
    if kind == "EDR": return edr(seed, 0.05)[0]
    if kind == "SW": return nx.to_scipy_sparse_array(nx.watts_strogatz_graph(N, 4, 0.1, seed=seed), nodelist=range(N), format="csr", dtype=float)
    return nx.to_scipy_sparse_array(g104(kind, seed), nodelist=range(N), format="csr", dtype=float)

print(f"{'topology':<9}{'lesion rand10':>14}{'lesion hub10':>13}{'noise-off kept':>15}{'hidden world':>13}")
for kind in ("SW", "EDR", "hier", "BA"):
    rows = []
    for seed in (1, 2):
        A = adj(kind, seed); A1 = A / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0]); alpha = np.full(N, te.ALPHA)
        lo, hi = 0.5, 1.5
        for _ in range(9):
            mid = (lo+hi)/2; lo, hi = (mid, hi) if sim(sps.csr_matrix(A1*mid), alpha, seed, 1500).mean() < 0.03 else (lo, mid)
        W = sps.csr_matrix(A1*(lo+hi)/2); base = sim(W, alpha, seed, 2000); rng = np.random.default_rng(seed)
        deg = np.asarray(A.sum(1)).ravel(); r = []
        for gone in (rng.choice(N, 100, replace=False), np.argsort(-deg)[:100]):
            m = np.zeros(N, bool); m[gone] = True; r.append(sim(W, alpha, seed, 2000, silent=m)[:, ~m].mean() / base[:, ~m].mean())
        o = run_noise(W, seed); r.append(o[2500:].mean() / o[500:2000].mean())
        lo, hi = 0.3, 1.5
        for _ in range(9):
            mid = (lo+hi)/2; lo, hi = (mid, hi) if sim_world(sps.csr_matrix(A1*mid), seed, 1.0, 1500)[0].mean() < 0.03 else (lo, mid)
        Ww = sps.csr_matrix(A1*(lo+hi)/2)
        f1, _ = sim_world(Ww, seed, 1.0); c1, _ = sim_world(Ww, seed, 1.0, cut=True)
        f0, _ = sim_world(Ww, seed, 0.0); c0, _ = sim_world(Ww, seed, 0.0, cut=True)
        r.append((1 - c1.mean() / f1.mean()) - (1 - c0.mean() / f0.mean()))
        rows.append(r)
    m = np.mean(rows, 0); print(f"{kind:<9}{m[0]:>14.2f}{m[1]:>13.2f}{m[2]:>15.2f}{m[3]:>13.2f}", flush=True)

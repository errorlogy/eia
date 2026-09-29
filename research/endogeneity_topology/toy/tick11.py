"""Tick 11: level-dependent endogeneity. For boundary partition L, an initiative at node i is
endogenous w.r.t. its part if spontaneous (no neighbour input) or >=50% of its triggering input
came from inside the same part. E(size) for aligned (structural) vs random partitions."""
import io, contextlib, runpy
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs
with contextlib.redirect_stdout(io.StringIO()):
    ns = runpy.run_path("tick6.py")
sim, build, N = ns["sim"], ns["build"], ns["N"]
TARGET, SIZES = 0.03, [1, 10, 50, 250, 1000]

def E_of(sp, W, labels):
    Sp = sps.csr_matrix(sp[:-1].astype(float)); Sn = sp[1:]
    Wc = W.tocoo(); keep = labels[Wc.row] == labels[Wc.col]
    Win = sps.csr_matrix((Wc.data[keep], (Wc.row[keep], Wc.col[keep])), shape=W.shape)
    tot = (Sp @ W.T).toarray(); ins = (Sp @ Win.T).toarray()
    endo = (tot <= 1e-12) | (ins >= 0.5 * tot)
    return endo[Sn].mean()

def aligned(name, g, size, rng):
    if size == 1: return np.arange(N)
    if name == "erdos_renyi":     # greedy BFS-ball partition = best structural guess for ER
        lab = -np.ones(N, int); k = 0
        for c in rng.permutation(N):
            if lab[c] >= 0: continue
            ball = [v for v in nx.bfs_tree(g, c).nodes() if lab[v] < 0][:size]
            lab[ball] = k; k += 1
        return lab
    return np.arange(N) // size   # SBM / hier / ring: contiguous blocks follow structure

print(f"{'topology':<13}{'partition':<9}" + "".join(f"{s:>8}" for s in SIZES))
for name in ["small_world", "erdos_renyi", "modular_sbm", "hier_modular"]:
    rowA, rowR = [], []
    for seed in [1, 2, 3]:
        rng = np.random.default_rng(seed)
        g = nx.watts_strogatz_graph(N, 4, 0.1, seed=seed) if name == "small_world" else build(name, seed)[0]
        A = nx.to_scipy_sparse_array(g, nodelist=range(N), format="csr", dtype=float)
        A1 = A / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0])
        lo, hi = 0.8, 1.2
        for _ in range(10):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if sim(A1*mid, seed)[500:1000].mean() < TARGET else (lo, mid)
        W = sps.csr_matrix(A1 * (lo + hi) / 2); sp = sim(W, seed)[500:]
        rowA.append([E_of(sp, W, aligned(name, g, s, rng)) for s in SIZES])
        rowR.append([E_of(sp, W, rng.permutation(N) // s) for s in SIZES])
    for tag, r in [("aligned", rowA), ("random", rowR)]:
        print(f"{name:<13}{tag:<9}" + "".join(f"{v:>8.2f}" for v in np.mean(r, 0)))

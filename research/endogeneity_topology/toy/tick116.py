"""Tick 116: integration & TSE neural complexity vs endogeneity across topologies.
Module-level signals: 10 blocks of 100 units, activity per 10-tick bin. Gaussian estimates:
  integration I(X) = sum_i H(x_i) - H(X);  TSE complexity C = sum_k [(k/n) I(X) - <I(X_k)>] over random k-subsets.
Also module endogeneity E_norm (true W, blocks) for the same runs. Rate-matched 0.03, 2 seeds."""
import io, contextlib, runpy
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs
with contextlib.redirect_stdout(io.StringIO()):
    ns = runpy.run_path("tick12.py")
sim, E_of, N = ns["sim"], ns["E_of"], ns["N"]
from tick104 import graph as g104
mods = np.arange(N) // 100

def gH(S):
    S = np.atleast_2d(S); return 0.5 * np.linalg.slogdet(2 * np.pi * np.e * (S + 1e-9 * np.eye(len(S))))[1]

def integ(Sig, idx):
    sub = Sig[np.ix_(idx, idx)]; return sum(gH(sub[i:i+1, i:i+1]) for i in range(len(idx))) - gH(sub)

def tse(X, rng, samples=30):
    Sig = np.cov(X); n = len(Sig); I = integ(Sig, np.arange(n)); C = 0.0
    for k in range(1, n):
        C += (k / n) * I - np.mean([integ(Sig, rng.choice(n, k, replace=False)) for _ in range(samples)])
    return I, C

def graph(kind, seed):
    if kind == "SW": return nx.watts_strogatz_graph(N, 4, 0.1, seed=seed)
    return g104(kind, seed)

if __name__ == "__main__":
    print(f"{'topology':<9}{'integration':>12}{'TSE':>8}{'module E_norm':>15}")
    for kind in ("ER", "SW", "SBM", "hier", "BA"):
        rows = []
        for seed in (1, 2):
            A = nx.to_scipy_sparse_array(graph(kind, seed), nodelist=range(N), format="csr", dtype=float); A1 = A / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0])
            lo, hi = 0.7, 1.4
            for _ in range(10):
                mid = (lo+hi)/2; lo, hi = (mid, hi) if sim(A1*mid, seed, 1000)[500:].mean() < 0.03 else (lo, mid)
            W = sps.csr_matrix(A1*(lo+hi)/2); sp = sim(W, seed, 6500)[500:]
            X = np.stack([sp[:, mods == m].reshape(-1, 10, 100).mean((1, 2)) for m in range(10)])
            rng = np.random.default_rng(seed); I, C = tse(X, rng)
            en = np.mean([E_of(sp, W, mods[rng.permutation(N)]) for _ in range(5)]); e = (E_of(sp, W, mods) - en) / (1 - en)
            rows.append((I, C, e))
        m = np.mean(rows, 0); print(f"{kind:<9}{m[0]:>12.2f}{m[1]:>8.2f}{m[2]:>15.2f}", flush=True)

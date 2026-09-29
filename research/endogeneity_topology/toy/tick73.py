"""Tick 73: spatial networks with the exponential distance rule (cortex-like EDR). N=1000 points in the unit square,
P(edge) proportional to exp(-d/lambda), mean degree 5; no explicit modules. Partition space into k x k grid blocks and
compute E_norm (true W) per block size. Question: does the spatial scale lambda set a characteristic sub-agent size
(block side where E_norm crosses 0.5)? Rate-matched 0.03, 2 seeds."""
import io, contextlib, runpy
import numpy as np, scipy.sparse as sps
from scipy.sparse.linalg import eigs
with contextlib.redirect_stdout(io.StringIO()):
    ns = runpy.run_path("tick12.py")
sim, E_of, N = ns["sim"], ns["E_of"], ns["N"]

def edr(seed, lam, deg=5.0):
    rng = np.random.default_rng(seed); xy = rng.random((N, 2))
    D = np.sqrt(((xy[:, None] - xy[None]) ** 2).sum(-1)); K = np.exp(-D / lam); np.fill_diagonal(K, 0)
    K *= deg * N / 2 / K[np.triu_indices(N, 1)].sum()
    A = np.triu(rng.random((N, N)) < np.minimum(K, 1), 1); A = (A | A.T).astype(float)
    return sps.csr_matrix(A), xy

def enorm(sp, W, lab, rng):
    en = np.mean([E_of(sp, W, lab[rng.permutation(N)]) for _ in range(5)]); return (E_of(sp, W, lab) - en) / (1 - en)

if __name__ == "__main__":
    ks = [12, 8, 5, 3, 2]
    print(f"{'lambda':>7} | E_norm for grid block side " + " ".join(f"{1/k:>6.3f}" for k in ks) + " | side at E_norm=0.5")
    for lam in (0.02, 0.05, 0.12):
        rows = []
        for seed in (1, 2):
            A, xy = edr(seed, lam); A1 = A / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0])
            lo, hi = 0.7, 1.4
            for _ in range(10):
                mid = (lo+hi)/2; lo, hi = (mid, hi) if sim(A1*mid, seed, 1000)[500:].mean() < 0.03 else (lo, mid)
            W = sps.csr_matrix(A1*(lo+hi)/2); sp = sim(W, seed, 3500)[500:]; rng = np.random.default_rng(seed)
            rows.append([enorm(sp, W, (np.minimum((xy[:, 0]*k).astype(int), k-1) * k + np.minimum((xy[:, 1]*k).astype(int), k-1)), rng) for k in ks])
        m = np.mean(rows, 0); sides = np.array([1/k for k in ks])
        cross = np.interp(0.5, m, sides) if m.min() < 0.5 < m.max() else float("nan")
        print(f"{lam:>7} | {'':>26}" + " ".join(f"{x:>6.2f}" for x in m) + f" | {cross:.3f}", flush=True)

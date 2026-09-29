"""Tick 67: multilayer — modular motive layer + sparse 'global workspace' hub layer (Dehaene-style ignition).
Layer A: SBM 10x100, mu=0.05, normalised to spectral radius 1. Layer B: 50 hub units (5 per module), cross-module
links p=0.3, normalised to spectral radius 1. W = g*A + w*B; g bisected for rate 0.03 at each w. 2 seeds.
Per tick: number of modules 'bursting' (>=10% of their units active). Global ignition = tick with >=5 modules.
Metrics: ignition rate per 1000 ticks, share of multi-module ticks that are global, module E_norm (true W)."""
import io, contextlib, runpy
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs
with contextlib.redirect_stdout(io.StringIO()):
    ns = runpy.run_path("tick12.py")
sim, E_of, N = ns["sim"], ns["E_of"], ns["N"]
mods = np.arange(N) // 100

def layers(seed):
    rng = np.random.default_rng(seed)
    g = nx.stochastic_block_model([100]*10, [[5*0.95/99 if i == j else 5*0.05/900 for j in range(10)] for i in range(10)], seed=seed, sparse=True)
    A = nx.to_scipy_sparse_array(g, nodelist=range(N), format="csr", dtype=float)
    A = A / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0])
    hubs = np.concatenate([np.arange(m*100, m*100+5) for m in range(10)])
    B = sps.lil_matrix((N, N))
    for a in hubs:
        for b in hubs:
            if a < b and a // 100 != b // 100 and rng.random() < 0.3:
                B[a, b] = B[b, a] = 1.0
    B = B.tocsr(); B = B / abs(eigs(B, k=1, which="LM", return_eigenvectors=False)[0])
    return A, B

def enorm(sp, W, lab, rng):
    en = np.mean([E_of(sp, W, lab[rng.permutation(N)]) for _ in range(5)]); return (E_of(sp, W, lab) - en) / (1 - en)

print(f"{'w_ws':>5}{'g':>6}{'ignitions/1000t':>16}{'global | multi':>15}{'max modules':>12}{'module E_norm':>14}")
for w in (0.0, 0.1, 0.2, 0.4):
    rows = []
    for seed in (1, 2):
        A, B = layers(seed)
        lo, hi = 0.5, 1.4
        for _ in range(10):
            mid = (lo+hi)/2; lo, hi = (mid, hi) if sim(A*mid + B*w, seed, 1000)[500:].mean() < 0.03 else (lo, mid)
        g = (lo+hi)/2; W = sps.csr_matrix(A*g + B*w); sp = sim(W, seed, 5500)[500:]
        burst = np.stack([sp[:, mods == m].mean(1) >= 0.10 for m in range(10)], 1).sum(1)
        multi = burst >= 2; glob = burst >= 5
        rows.append((g, glob.sum() / len(sp) * 1000, glob.sum() / max(multi.sum(), 1), burst.max(), enorm(sp, W, mods, np.random.default_rng(seed))))
    m = np.mean(rows, 0); print(f"{w:>5}{m[0]:>6.2f}{m[1]:>16.2f}{m[2]:>15.3f}{m[3]:>12.1f}{m[4]:>14.2f}", flush=True)

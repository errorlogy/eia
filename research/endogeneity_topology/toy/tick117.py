"""Tick 117: can a workspace layer give BOTH whole-level integration and part-level endogeneity (A35 vs A21)?
SBM 10x100 (mu 0.05) + hub workspace layer weight w (tick 67 layers, separately normalised), rate-matched.
Integration / TSE (block-level Gaussian, tick 116) and module E_norm; hier-modular and ER as references. 2 seeds."""
import io, contextlib, runpy
import numpy as np, scipy.sparse as sps
with contextlib.redirect_stdout(io.StringIO()):
    ns = runpy.run_path("tick12.py")
sim, E_of, N = ns["sim"], ns["E_of"], ns["N"]
from tick67 import layers
from tick116 import tse, mods

print(f"{'w (workspace)':<14}{'integration':>12}{'TSE':>8}{'module E_norm':>15}")
for w in (0.0, 0.2, 0.4, 0.8):
    rows = []
    for seed in (1, 2):
        A, B = layers(seed)
        lo, hi = 0.3, 1.4
        for _ in range(10):
            mid = (lo+hi)/2; lo, hi = (mid, hi) if sim(A*mid + B*w, seed, 1000)[500:].mean() < 0.03 else (lo, mid)
        W = sps.csr_matrix(A*(lo+hi)/2 + B*w); sp = sim(W, seed, 6500)[500:]
        X = np.stack([sp[:, mods == m].reshape(-1, 10, 100).mean((1, 2)) for m in range(10)])
        rng = np.random.default_rng(seed); I, C = tse(X, rng)
        en = np.mean([E_of(sp, W, mods[rng.permutation(N)]) for _ in range(5)]); e = (E_of(sp, W, mods) - en) / (1 - en)
        rows.append((I, C, e))
    m = np.mean(rows, 0); print(f"{w:<14}{m[0]:>12.2f}{m[1]:>8.2f}{m[2]:>15.2f}", flush=True)

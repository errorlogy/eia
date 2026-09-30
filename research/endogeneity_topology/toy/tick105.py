"""Tick 105: gain homeostasis after a 10 % hub lesion. Re-bisect gain so surviving units return to rate 0.03.
Report: gain factor needed, survivors' burst CV (ISI CV of population bursts; ~0 = clock/seizure-like, ~1 = graded),
and module endogeneity E_norm (true W, 10 blocks of 100) for SBM / hier, intact vs lesioned+retuned. 2 seeds."""
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs
from tick85 import sim, te
from tick104 import graph, N
import runpy, io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    E_of = runpy.run_path("tick12.py")["E_of"]
mods = np.arange(N) // 100

def enorm(sp, W, keep, rng):
    lab = mods.copy(); lab[~keep] = -1 - np.arange((~keep).sum())      # removed units as singletons
    en = np.mean([E_of(sp, W, lab[rng.permutation(N)]) for _ in range(5)]); return (E_of(sp, W, lab) - en) / (1 - en)

def cv(sp, keep):
    x = sp[:, keep].mean(1); ev = np.flatnonzero(x > np.percentile(x, 90)); isi = np.diff(ev); isi = isi[isi > 1]
    return isi.std() / isi.mean() if len(isi) > 2 else float("nan")

def tune(A1, alpha, seed, mask):
    lo, hi = 0.3, 3.0
    for _ in range(10):
        mid = (lo+hi)/2; r = sim(sps.csr_matrix(A1*mid), alpha, seed, 1500, silent=mask)[:, ~mask].mean()
        lo, hi = (mid, hi) if r < 0.03 else (lo, mid)
    return (lo+hi)/2

print(f"{'topology':<9}{'gain x':>8}{'CV intact':>10}{'CV retuned':>11}{'E_norm intact':>14}{'E_norm retuned':>15}")
for kind in ("ER", "SBM", "hier", "BA"):
    rows = []
    for seed in (1, 2):
        A = nx.to_scipy_sparse_array(graph(kind, seed), nodelist=range(N), format="csr", dtype=float)
        A1 = A / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0]); alpha = np.full(N, te.ALPHA)
        none = np.zeros(N, bool); g0 = tune(A1, alpha, seed, none)
        mask = np.zeros(N, bool); mask[np.argsort(-np.asarray(A.sum(1)).ravel())[:100]] = True; g1 = tune(A1, alpha, seed, mask)
        W0, W1 = sps.csr_matrix(A1*g0), sps.csr_matrix(A1*g1)
        s0, s1 = sim(W0, alpha, seed), sim(W1, alpha, seed, silent=mask); rng = np.random.default_rng(seed)
        e0 = enorm(s0, W0, ~none, rng) if kind in ("SBM", "hier") else np.nan
        e1 = enorm(s1, W1, ~mask, rng) if kind in ("SBM", "hier") else np.nan
        rows.append((g1 / g0, cv(s0, ~none), cv(s1, ~mask), e0, e1))
    m = np.nanmean(rows, 0) if kind in ("SBM", "hier") else np.nanmean(np.array(rows)[:, :3], 0).tolist() + [np.nan, np.nan]
    print(f"{kind:<9}{m[0]:>8.2f}{m[1]:>10.2f}{m[2]:>11.2f}{m[3]:>14.2f}{m[4]:>15.2f}", flush=True)

"""Tick 87: which module-level topology creates a dominant generator (A26 signature) vs collective endogeneity?
10 modules x 100 units, within p gives degree ~4.5; inter-module links only along a module graph: RING, STAR (module 0 hub),
COMPLETE; same total cross-module edge count. Rate-matched 0.03, 2 seeds. For modules 0 and 5: out (rest drop when
silenced, per unit share) and indep (activity kept when its incoming cross links are cut)."""
import numpy as np, scipy.sparse as sps
from scipy.sparse.linalg import eigs
from tick85 import sim, te, N
mods = np.arange(N) // 100

def build(kind, seed, cross_total=500):
    rng = np.random.default_rng(seed)
    A = np.triu(rng.random((N, N)) < np.where(mods[:, None] == mods[None, :], 4.5/99, 0), 1)
    if kind == "ring": pairs = [(i, (i+1) % 10) for i in range(10)]
    elif kind == "star": pairs = [(0, j) for j in range(1, 10)]
    else: pairs = [(i, j) for i in range(10) for j in range(i+1, 10)]
    per = cross_total // len(pairs)
    for a, b in pairs:
        ia = rng.integers(a*100, a*100+100, per); ib = rng.integers(b*100, b*100+100, per)
        A[np.minimum(ia, ib), np.maximum(ia, ib)] = True
    A = (A | A.T).astype(float); return sps.csr_matrix(A)

print(f"{'module graph':<10}{'out m0':>8}{'indep m0':>9}{'out m5':>8}{'indep m5':>9}")
for kind in ("ring", "star", "complete"):
    rows = []
    for seed in (1, 2):
        A = build(kind, seed); A1 = A / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0]); alpha = np.full(N, te.ALPHA)
        lo, hi = 0.5, 1.5
        for _ in range(9):
            mid = (lo+hi)/2; lo, hi = (mid, hi) if sim(sps.csr_matrix(A1*mid), alpha, seed, 1500).mean() < 0.03 else (lo, mid)
        W = (A1*(lo+hi)/2).tolil(); Wcsr = W.tocsr(); base = sim(Wcsr, alpha, seed); r = []
        for m in (0, 5):
            ins = mods == m
            sil = sim(Wcsr, alpha, seed, silent=ins); out = (1 - sil[:, ~ins].mean() / base[:, ~ins].mean()) / ins.mean()
            Wc = Wcsr.toarray(); Wc[np.ix_(ins, ~ins)] = 0
            r += [out, sim(sps.csr_matrix(Wc), alpha, seed)[:, ins].mean() / base[:, ins].mean()]
        rows.append(r)
    m = np.mean(rows, 0); print(f"{kind:<10}{m[0]:>8.2f}{m[1]:>9.2f}{m[2]:>8.2f}{m[3]:>9.2f}", flush=True)

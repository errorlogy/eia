"""Tick 88: generator strength vs enslavement. SBM 10x100 (mu 0.1); module 0 excitability x f, f in {1, 1.3, 1.8, 2.5}.
Measures: module 0 out-influence & independence (A26), its share of total activity, and the mean raw endogeneity E of the
OTHER modules (do they stay sub-agents or become driven by the generator?). Rate-matched 0.03, 2 seeds."""
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs
from tick85 import sim, te, N
mods = np.arange(N) // 100; tgt = mods == 0

def E_others(sp, W):
    P = sps.csr_matrix(sp[:-1].astype(float)); Sn = sp[1:]
    Wc = W.tocoo(); k = mods[Wc.row] == mods[Wc.col]
    Win = sps.csr_matrix((Wc.data[k], (Wc.row[k], Wc.col[k])), shape=W.shape)
    tot = (P @ W.T).toarray(); ins = (P @ Win.T).toarray(); endo = (tot <= 1e-12) | (ins >= 0.5 * tot)
    return endo[:, ~tgt][Sn[:, ~tgt]].mean()

print(f"{'f':>5}{'out':>7}{'indep':>7}{'gen share':>11}{'E others':>10}")
for f in (1.0, 1.3, 1.8, 2.5):
    rows = []
    for seed in (1, 2):
        g = nx.stochastic_block_model([100]*10, [[5*0.9/99 if i == j else 5*0.1/900 for j in range(10)] for i in range(10)], seed=seed, sparse=True)
        A = nx.to_scipy_sparse_array(g, nodelist=range(N), format="csr", dtype=float); A1 = A / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0])
        alpha = np.full(N, te.ALPHA); alpha[tgt] *= f
        lo, hi = 0.3, 1.5
        for _ in range(9):
            mid = (lo+hi)/2; lo, hi = (mid, hi) if sim(sps.csr_matrix(A1*mid), alpha, seed, 1500).mean() < 0.03 else (lo, mid)
        W = sps.csr_matrix(A1*(lo+hi)/2); base = sim(W, alpha, seed)
        sil = sim(W, alpha, seed, silent=tgt); out = (1 - sil[:, ~tgt].mean() / base[:, ~tgt].mean()) / tgt.mean()
        Wc = W.toarray(); Wc[np.ix_(tgt, ~tgt)] = 0; indep = sim(sps.csr_matrix(Wc), alpha, seed)[:, tgt].mean() / base[:, tgt].mean()
        rows.append((out, indep, base[:, tgt].sum() / base.sum(), E_others(base, W)))
    m = np.mean(rows, 0); print(f"{f:>5}{m[0]:>7.2f}{m[1]:>7.2f}{m[2]:>11.2f}{m[3]:>10.2f}", flush=True)

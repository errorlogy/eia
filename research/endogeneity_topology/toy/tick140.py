"""Tick 140: lag-selective blind detector. For each ordered pair (j -> i), lagged excess co-activation at each lag 1..10;
keep the best lag per pair; for each target, regress s_i(t) on the top-20 candidates each at its own best lag; Louvain
(best resolution). Compare with lag-1 and summed multi-lag detectors (tick 139), no delays vs delays 0-9. 2 seeds."""
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs
from tick139 import sim, split, detect, N
import tick35_lib as t35
L = 10

def lag_selective(sp):
    S = sp.astype(float); T = len(S); r = S.mean(0); Ks = []
    for l in range(1, L + 1):
        K = (S[:-l].T @ S[l:]).T - np.outer(r, r) * (T - l); np.fill_diagonal(K, 0); Ks.append(K)
    Ks = np.stack(Ks); best = Ks.argmax(0) + 1; Kb = np.clip(Ks.max(0), 0, None)
    B = np.zeros((N, N)); Lmax = L
    for i in range(N):
        js = np.argsort(Kb[i])[-20:]; js = js[Kb[i, js] > 0]
        if len(js) == 0 or S[Lmax:, i].sum() < 3: continue
        cols = [S[Lmax - best[i, j]: T - best[i, j], j] for j in js]
        Xi = np.column_stack([np.ones(T - Lmax), S[Lmax - 1: T - 1, i]] + cols)
        B[i, js] = np.clip(np.linalg.lstsq(Xi, S[Lmax:, i], rcond=None)[0][2:], 0, None)
    return sps.csr_matrix(B)

print(f"{'delays':<8}{'lag-selective detector ARI':>28}")
for cond in ("none", "0-9"):
    r = []
    for seed in (1, 2):
        g = nx.stochastic_block_model([100]*10, [[5*0.9/99 if i == j else 5*0.1/900 for j in range(10)] for i in range(10)], seed=seed, sparse=True)
        A = nx.to_scipy_sparse_array(g, nodelist=range(N), format="csr", dtype=float); A1 = A / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0])
        delays = np.zeros(A1.nnz, int) if cond == "none" else np.random.default_rng(seed).integers(0, 10, A1.tocoo().nnz)
        lo, hi = 0.5, 2.0
        for _ in range(9):
            mid = (lo+hi)/2; lo, hi = (mid, hi) if sim(split(sps.csr_matrix(A1*mid), delays), seed, 1500).mean() < 0.03 else (lo, mid)
        sp = sim(split(sps.csr_matrix(A1*(lo+hi)/2), delays), seed, 4500)[:2000]
        r.append(detect(t35.top10(lag_selective(sp).toarray()), seed))
    print(f"{cond:<8}{np.mean(r):>28.2f}   (tick 139: lag-1 {'0.82' if cond == 'none' else '0.08'}, multi-lag {'0.34' if cond == 'none' else '0.58'})", flush=True)

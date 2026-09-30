"""Tick 143: tick 142 re-run with a wider gain search (0.3-8) and the achieved rate / gain reported (was the beta 0.5
anomaly a failed rate match?). 3 seeds."""
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs
from tick142 import sim, detect, E_of, ari, N

print(f"{'beta':>5}{'gain':>7}{'rate':>7}{'split-half ARI':>15}{'ARI vs modules':>15}{'held-out E_norm':>16}")
for beta in (0.0, 0.5, 1.0, 2.0):
    rows = []
    for seed in (1, 2, 3):
        g = nx.stochastic_block_model([100]*10, [[5*0.8/99 if i == j else 5*0.2/900 for j in range(10)] for i in range(10)], seed=seed, sparse=True)
        A = nx.to_scipy_sparse_array(g, nodelist=range(N), format="csr", dtype=float); A1 = A / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0])
        lo, hi = 0.3, 8.0
        for _ in range(11):
            mid = (lo+hi)/2; lo, hi = (mid, hi) if sim(sps.csr_matrix(A1*mid), seed, beta, 1500)[0].mean() < 0.03 else (lo, mid)
        gn = (lo+hi)/2; sp, Wm = sim(sps.csr_matrix(A1*gn), seed, beta, 8500); h1, h2 = sp[:4000], sp[4000:]
        l1, l2 = detect(h1, seed), detect(h2, seed + 1); rng = np.random.default_rng(seed)
        en = np.mean([E_of(h2, Wm, l1[rng.permutation(N)]) for _ in range(5)]); e = (E_of(h2, Wm, l1) - en) / (1 - en)
        rows.append((gn, sp.mean(), ari(l1, l2), ari(l1, np.arange(N) // 100), e))
    m = np.mean(rows, 0); print(f"{beta:>5}{m[0]:>7.2f}{m[1]:>7.3f}{m[2]:>15.2f}{m[3]:>15.2f}{m[4]:>16.2f}", flush=True)

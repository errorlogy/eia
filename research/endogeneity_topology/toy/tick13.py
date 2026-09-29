"""Tick 13: fully blind pipeline. Attribution uses inferred directed W_hat (positive lagged excess,
top 10%) instead of true W; partition chosen by blind score. Compare blind vs true E."""
import io, contextlib, runpy
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs
with contextlib.redirect_stdout(io.StringIO()):
    ns = runpy.run_path("tick12.py")
sim, E_of, ari, build, N = ns["sim"], ns["E_of"], ns["ari"], ns["build"], ns["N"]

def infer_dir(sp):
    S = sps.csr_matrix(sp.astype(float)); r = sp.mean(0)
    K = (S[:-1].T @ S[1:]).toarray().T - np.outer(r, r) * (len(sp) - 1)   # K[i,j]: j -> i
    np.fill_diagonal(K, 0); K = np.clip(K, 0, None)
    thr = np.percentile(K[K > 0], 90)
    return sps.csr_matrix(np.where(K >= thr, K, 0))

print(f"{'topology':<13}{'E_true(found)':>14}{'E_blind(found)':>15}{'E_blind(null)':>14}{'E_true(struct)':>15}{'E_blind(struct)':>16}{'ARI':>6}")
for name in ["small_world", "erdos_renyi", "modular_sbm", "hier_modular"]:
    for seed in [1, 2]:
        rng = np.random.default_rng(seed)
        g = nx.watts_strogatz_graph(N, 4, 0.1, seed=seed) if name == "small_world" else build(name, seed)[0]
        A = nx.to_scipy_sparse_array(g, nodelist=range(N), format="csr", dtype=float)
        A1 = A / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0])
        lo, hi = 0.8, 1.2
        for _ in range(10):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if sim(A1*mid, seed, 1000)[500:].mean() < 0.03 else (lo, mid)
        W = sps.csr_matrix(A1 * (lo + hi) / 2)
        sp = sim(W, seed, 4500)[500:]; train, test = sp[:2000], sp[2000:]
        Wh = infer_dir(train); G = nx.from_scipy_sparse_array(Wh + Wh.T)
        best = None
        for res in [0.5, 1, 1.5, 2, 3, 4, 8]:
            lab = np.empty(N, int)
            for k, c in enumerate(nx.community.louvain_communities(G, weight="weight", resolution=res, seed=seed)): lab[list(c)] = k
            sc = E_of(test, Wh, lab) - E_of(test, Wh, lab[rng.permutation(N)])
            if best is None or sc > best[0]: best = (sc, lab)
        lab = best[1]
        struct = np.arange(N) // (10 if name == "small_world" else 50)
        truth = np.arange(N) // 50
        print(f"{name:<13}{E_of(test, W, lab):>14.2f}{E_of(test, Wh, lab):>15.2f}{E_of(test, Wh, lab[rng.permutation(N)]):>14.2f}"
              f"{E_of(test, W, struct):>15.2f}{E_of(test, Wh, struct):>16.2f}{ari(lab, truth):>6.2f}")

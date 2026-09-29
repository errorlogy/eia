"""Tick 23: locate alpha_c for p-adic ultrametric graphs. P(d) = c * 10^(-alpha (d-1)), c set so mean
degree = 5 for every alpha (removes degree confound). alpha 1.0..1.6, 3 seeds.
Metrics: blind E gain (found - null), median part, ARI vs leaf (10) / mid (100) groups, max rate jump."""
import io, contextlib, runpy
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs
import topo_endo as te
with contextlib.redirect_stdout(io.StringIO()):
    ns = runpy.run_path("tick12.py")
sim, E_of, infer, ari, N = ns["sim"], ns["E_of"], ns["infer"], ns["ari"], ns["N"]

def padic(seed, a, p=10, deg=5.0):
    c = deg / (9 + 90*10**(-a) + 900*10**(-2*a))
    rng = np.random.default_rng(seed); i = np.arange(N)
    d = np.where(i[:, None]//p == i[None, :]//p, 1, np.where(i[:, None]//p**2 == i[None, :]//p**2, 2, 3))
    A = np.triu(rng.random((N, N)) < np.minimum(1, c*10.0**(-a*(d-1))), 1); A = A | A.T
    return sps.csr_matrix(A.astype(float))

alphas = [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6]
gains = [round(0.85 + 0.05*i, 2) for i in range(9)]
leaf, mid = np.arange(N)//10, np.arange(N)//100
print(f"{'alpha':>6}{'c':>7}{'E gain':>8}{'E found':>8}{'med part':>9}{'ARI leaf':>9}{'ARI mid':>8}{'jump':>6}")
for a in alphas:
    rows = []
    for seed in [1, 2, 3]:
        A = padic(seed, a); A1 = A / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0])
        b0 = sim(sps.csr_matrix((N, N)), seed, 1500)[500:].mean()
        r = [sim(A1*g, seed, 1500)[500:].mean()/b0 for g in gains]
        lo, hi = 0.7, 1.4
        for _ in range(10):
            m_ = (lo+hi)/2; lo, hi = (m_, hi) if sim(A1*m_, seed, 1000)[500:].mean() < 0.03 else (lo, m_)
        W = sps.csr_matrix(A1*(lo+hi)/2); sp = sim(W, seed, 4500)[500:]; tr, tst = sp[:2000], sp[2000:]
        G = infer(tr); rng = np.random.default_rng(seed); best = None
        for res in [0.5, 1, 2, 4]:
            lab = np.empty(N, int)
            for k, cset in enumerate(nx.community.louvain_communities(G, weight="weight", resolution=res, seed=seed)): lab[list(cset)] = k
            ef, en = E_of(tst, W, lab), E_of(tst, W, lab[rng.permutation(N)])
            if best is None or ef-en > best[0]: best = (ef-en, ef, lab)
        rows.append((best[0], best[1], np.median(np.bincount(best[2])), ari(best[2], leaf), ari(best[2], mid), max(np.diff(r))))
    m = np.mean(rows, 0); c = 5/(9 + 90*10**(-a) + 900*10**(-2*a))
    print(f"{a:>6.1f}{c:>7.3f}{m[0]:>8.2f}{m[1]:>8.2f}{m[2]:>9.0f}{m[3]:>9.2f}{m[4]:>8.2f}{m[5]:>6.1f}")

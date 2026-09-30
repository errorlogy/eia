"""Tick 95: does the discoverability threshold mu_c (A12, found with pairwise lagged excess in tick 24) move when the
graph is inferred with calibrated conditional attribution (tick 35)? SBM 10x100, degree 5, rate 0.03, 2 seeds.
Louvain on (a) pairwise top-10% graph, (b) conditional top-10% graph; resolution chosen by blind E gain."""
import io, contextlib, runpy
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs
with contextlib.redirect_stdout(io.StringIO()):
    ns = runpy.run_path("tick12.py")
sim, E_of, infer, ari, N = ns["sim"], ns["E_of"], ns["infer"], ns["ari"], ns["N"]
import tick35_lib as t35

def detect(G, Wh, tst, rng, seed):
    best = None
    for res in [0.5, 1, 2, 4]:
        lab = np.empty(N, int)
        for k, c in enumerate(nx.community.louvain_communities(G, weight="weight", resolution=res, seed=seed)): lab[list(c)] = k
        sc = E_of(tst, Wh, lab) - E_of(tst, Wh, lab[rng.permutation(N)])
        if best is None or sc > best[0]: best = (sc, lab)
    return best[1]

mus = [0.3, 0.2, 0.15, 0.1, 0.07, 0.05]
print(f"{'method':<12}" + "".join(f"{'mu='+str(m):>9}" for m in mus) + "   (ARI vs true modules)")
res = {"pairwise": [], "conditional": []}
for mu in mus:
    r = {"pairwise": [], "conditional": []}
    for seed in (1, 2):
        g = nx.stochastic_block_model([100]*10, [[5*(1-mu)/99 if i == j else 5*mu/900 for j in range(10)] for i in range(10)], seed=seed, sparse=True)
        A = nx.to_scipy_sparse_array(g, nodelist=range(N), format="csr", dtype=float); A1 = A / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0])
        lo, hi = 0.7, 1.4
        for _ in range(10):
            mid = (lo+hi)/2; lo, hi = (mid, hi) if sim(A1*mid, seed, 1000)[500:].mean() < 0.03 else (lo, mid)
        W = sps.csr_matrix(A1*(lo+hi)/2); sp = sim(W, seed, 4500)[500:]; tr, tst = sp[:2000], sp[2000:]
        truth = np.arange(N) // 100; rng = np.random.default_rng(seed)
        Kp = t35.pairwise(tr); Wp = t35.top10(Kp); Wc = t35.top10(t35.conditional(tr, Kp))
        r["pairwise"].append(ari(detect(nx.from_scipy_sparse_array(Wp + Wp.T), Wp, tst, rng, seed), truth))
        r["conditional"].append(ari(detect(nx.from_scipy_sparse_array(Wc + Wc.T), Wc, tst, rng, seed), truth))
    for k in r: res[k].append(np.mean(r[k]))
for k, v in res.items():
    print(f"{k:<12}" + "".join(f"{x:>9.2f}" for x in v), flush=True)

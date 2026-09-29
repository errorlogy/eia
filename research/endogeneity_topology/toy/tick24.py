"""Tick 24: is the mu ~ 0.1 self-boundary rule universal? Mean degree 5, tuned mixing mu.
Families: SBM 10x100, SBM 20x50, LFR (heterogeneous degrees & community sizes).
Metric: ARI(found, true communities), blind E gain; rate-matched 0.03. 3 seeds."""
import io, contextlib, runpy
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs
with contextlib.redirect_stdout(io.StringIO()):
    ns = runpy.run_path("tick12.py")
sim, E_of, infer, ari, N = ns["sim"], ns["E_of"], ns["infer"], ns["ari"], ns["N"]

def sbm(seed, mu, size, deg=5.0):
    k = N // size; p_in = deg*(1-mu)/(size-1); p_out = deg*mu/(N-size)
    g = nx.stochastic_block_model([size]*k, [[p_in if i == j else p_out for j in range(k)] for i in range(k)], seed=seed, sparse=True)
    return g, np.arange(N)//size

def lfr(seed, mu):
    for s in range(seed, seed+20):
        try:
            g = nx.LFR_benchmark_graph(N, 2.5, 1.5, mu, average_degree=5, max_degree=40, min_community=40, max_community=150, seed=s, max_iters=500)
            break
        except nx.ExceededMaxIterations:
            continue
    lab = np.empty(N, int)
    for k, c in enumerate({frozenset(g.nodes[v]["community"]) for v in g}): lab[list(c)] = k
    g.remove_edges_from(nx.selfloop_edges(g)); return g, lab

mus = [0.3, 0.2, 0.15, 0.1, 0.07, 0.05, 0.03]
fams = {"SBM 10x100": lambda s, m: sbm(s, m, 100), "SBM 20x50": lambda s, m: sbm(s, m, 50), "LFR": lfr}
print(f"{'family':<12}" + "".join(f"{'mu='+str(m):>12}" for m in mus) + "    (cells: ARI / E gain)")
for fam, gen in fams.items():
    cells = []
    for mu in mus:
        r = []
        for seed in [1, 2, 3]:
            g, truth = gen(seed, mu)
            A = nx.to_scipy_sparse_array(g, nodelist=range(N), format="csr", dtype=float)
            A1 = A / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0])
            lo, hi = 0.7, 1.4
            for _ in range(10):
                m_ = (lo+hi)/2; lo, hi = (m_, hi) if sim(A1*m_, seed, 1000)[500:].mean() < 0.03 else (lo, m_)
            W = sps.csr_matrix(A1*(lo+hi)/2); sp = sim(W, seed, 4500)[500:]; tr, tst = sp[:2000], sp[2000:]
            G = infer(tr); rng = np.random.default_rng(seed); best = None
            for res in [0.5, 1, 2, 4]:
                lab = np.empty(N, int)
                for k, c in enumerate(nx.community.louvain_communities(G, weight="weight", resolution=res, seed=seed)): lab[list(c)] = k
                ef, en = E_of(tst, W, lab), E_of(tst, W, lab[rng.permutation(N)])
                if best is None or ef-en > best[0]: best = (ef-en, lab)
            r.append((ari(best[1], truth), best[0]))
        m = np.mean(r, 0); cells.append(f"{m[0]:.2f}/{m[1]:.2f}")
    print(f"{fam:<12}" + "".join(f"{c:>12}" for c in cells), flush=True)

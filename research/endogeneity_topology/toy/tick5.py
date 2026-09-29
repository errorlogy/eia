"""Tick 4: N=3000, 5 seeds, same gains. Inter-module degree kept equal to tick 3."""
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs
import topo_endo as te
te.N = N = 3000; te.T = 2000

def hier_mod(seed):
    M = N // 10
    P = np.full((M, M), 0.285 / (N - 50))
    for i in range(M):
        for j in range(M):
            if i == j: P[i, j] = 0.35
            elif i // 5 == j // 5: P[i, j] = 0.03
    return nx.stochastic_block_model([10]*M, P.tolist(), seed=seed, sparse=True)

def topos(seed):
    M = N // 50
    return {
        "small_world": nx.watts_strogatz_graph(N, 4, 0.1, seed=seed),
        "erdos_renyi": nx.erdos_renyi_graph(N, 4/N, seed=seed),
        "modular_sbm": nx.stochastic_block_model([50]*M, [[0.08 if i==j else 0.475/(N-50) for j in range(M)] for i in range(M)], seed=seed, sparse=True),
        "hier_modular": hier_mod(seed),
    }

gains = [round(0.95 + 0.025*i, 3) for i in range(15)]  # 0.95 .. 1.30
seeds = [1, 2, 3, 4, 5]
names = ["erdos_renyi", "modular_sbm", "hier_modular"]
res = {}
for sd in seeds:
    base = te.simulate(sps.csr_matrix((N, N)), np.random.default_rng(sd))[500:].mean()
    tp = topos(sd)
    for name in names:
        A = nx.to_scipy_sparse_array(tp[name], nodelist=range(N), format="csr", dtype=float)
        lam = abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0])
        for gn in gains:
            res.setdefault((name, gn), []).append(te.metrics(te.simulate(A * (gn / lam), np.random.default_rng(sd)), base))
def rich(m): return m["rate_x_base"] > 1.5 and 0.7 <= m["cv_isi"] <= 2.5
print(f"{'topology':<13}" + "".join(f"{g:>6}" for g in gains) + "  width  per-seed")
for name in names:
    row, w = "", 0
    for gn in gains:
        ms = res[(name, gn)]; ok = np.mean([rich(m) for m in ms]) >= 0.6; w += ok
        row += f"{np.nanmean([m['cv_isi'] for m in ms]):>5.2f}{'*' if ok else ' '}"
    ps = [sum(rich(res[(name, g)][i]) for g in gains) for i in range(len(seeds))]
    print(f"{name:<13}{row}  {w:>4}   {ps}")
print("rate_x_base:")
for name in names:
    print(f"{name:<13}" + "".join(f"{np.mean([m['rate_x_base'] for m in res[(name, g)]]):>6.1f}" for g in gains))
print("max avalanche (mean):")
for name in names:
    print(f"{name:<13}" + "".join(f"{np.mean([m['max_aval'] for m in res[(name, g)]]):>6.0f}" for g in gains))

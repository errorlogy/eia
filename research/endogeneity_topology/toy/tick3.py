"""Tick 3: N=1000, gain 0.85-1.10 step 0.025, 3 seeds. Sparse W. Griffiths-phase test."""
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs
import topo_endo as te
te.N = N = 1000; te.T = 2000

def hier_mod(seed):
    k = 20; sizes = [N // (k*5)]*0 or [10]*100  # 100 modules of 10, 20 super-modules of 5
    P = np.zeros((100,100))
    for i in range(100):
        for j in range(100):
            P[i,j] = 0.35 if i==j else (0.03 if i//5==j//5 else 0.0003)
    return nx.stochastic_block_model(sizes, P.tolist(), seed=seed, sparse=True)

def topos(seed):
    return {
        "small_world": nx.watts_strogatz_graph(N, 4, 0.1, seed=seed),
        "erdos_renyi": nx.erdos_renyi_graph(N, 4/N, seed=seed),
        "modular_sbm": nx.stochastic_block_model([50]*20, [[0.08 if i==j else 0.0005 for j in range(20)] for i in range(20)], seed=seed, sparse=True),
        "hier_modular": hier_mod(seed),
    }

gains = [round(0.85 + 0.025*i, 3) for i in range(11)]
seeds = [1, 2, 3]
res = {}
for sd in seeds:
    base = te.simulate(sps.csr_matrix((N, N)), np.random.default_rng(sd))[500:].mean()
    for name, g in topos(sd).items():
        A = nx.to_scipy_sparse_array(g, nodelist=range(N), format="csr", dtype=float)
        lam = abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0])
        for gn in gains:
            m = te.metrics(te.simulate(A * (gn / lam), np.random.default_rng(sd)), base)
            res.setdefault((name, gn), []).append(m)
def rich(m): return m["rate_x_base"] > 1.5 and 0.7 <= m["cv_isi"] <= 2.5
print(f"{'topology':<13}" + "".join(f"{g:>7}" for g in gains) + "  width")
for name in ["small_world", "erdos_renyi", "modular_sbm", "hier_modular"]:
    row, w = "", 0
    for gn in gains:
        ms = res[(name, gn)]; ok = np.mean([rich(m) for m in ms]) >= 2/3; w += ok
        row += f"{np.nanmean([m['cv_isi'] for m in ms]):>6.2f}{'*' if ok else ' '}"
    print(f"{name:<13}{row}  {w}")
print("cells = mean CV_ISI; * rich in >=2/3 seeds")
print("rate_x_base:")
for name in ["small_world", "erdos_renyi", "modular_sbm", "hier_modular"]:
    print(f"{name:<13}" + "".join(f"{np.mean([m['rate_x_base'] for m in res[(name,g)]]):>7.1f}" for g in gains))

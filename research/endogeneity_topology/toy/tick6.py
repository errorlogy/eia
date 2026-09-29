"""Tick 6: do(Z) — intervene on internal state of one 50-node module; exact twin with same noise.
Measures how an internal intervention propagates: local vs global, transient vs persistent."""
import numpy as np, networkx as nx
from scipy.sparse.linalg import eigs
import topo_endo as te

N, T, T0, H = 1000, 1600, 1000, 400
def sim(W, seed, S=None):
    rng = np.random.default_rng(seed)
    d = rng.uniform(0, .3, N); u = rng.uniform(.2, .6, N); s = np.zeros(N); refr = np.zeros(N)
    out = np.zeros((T, N), bool)
    for t in range(T):
        if S is not None and t == T0:
            d[S] = 1.0; u[S] = 1.0          # do(Z): set drives + uncertainty of module S
        xi = rng.standard_normal(N)          # same noise stream in twin
        inp = W @ s
        u = np.clip(u + te.AGE*(1-u) + te.BETA_U*inp*(1-u) - te.RESOLVE*u*s, 0, 1)
        d = np.clip((1-te.RHO)*d + te.ALPHA*u + inp + te.SIGMA*xi - .8*s, 0, 1)
        s = ((d > te.THETA) & (refr <= 0)).astype(float); refr = np.where(s > 0, 5, refr-1)
        out[t] = s > 0
    return out

def build(name, seed):
    if name == "erdos_renyi":
        g = nx.erdos_renyi_graph(N, 4/N, seed=seed); gc = max(nx.connected_components(g), key=len)
        mods = []
        for c in np.random.default_rng(seed).choice(list(gc), 5, replace=False):
            ball = list(nx.bfs_tree(g, c).nodes())[:50]; mods.append(np.array(ball))
        return g, mods, 0.94
    if name == "modular_sbm":
        g = nx.stochastic_block_model([50]*20, [[.08 if i==j else .0005 for j in range(20)] for i in range(20)], seed=seed, sparse=True)
        return g, [np.arange(m*50, m*50+50) for m in range(5)], 1.01
    P = np.zeros((100, 100))
    for i in range(100):
        for j in range(100): P[i,j] = .35 if i==j else (.03 if i//5==j//5 else .0003)
    g = nx.stochastic_block_model([10]*100, P.tolist(), seed=seed, sparse=True)
    return g, [np.arange(m*50, m*50+50) for m in range(5)], 1.05   # one super-module = 50 nodes

rows = {}
for name in ["erdos_renyi", "modular_sbm", "hier_modular"]:
    for seed in [1, 2, 3]:
        g, mods, gain = build(name, seed)
        A = nx.to_scipy_sparse_array(g, nodelist=range(N), format="csr", dtype=float)
        W = A * (gain / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0]))
        twin = sim(W, seed)
        for S in mods:
            p = sim(W, seed, S)
            diff = (p[T0:] != twin[T0:])
            inside = np.zeros(N, bool); inside[S] = True
            ham_in = diff[:, inside].mean(1); ham_out = diff[:, ~inside].mean(1)
            nz = np.flatnonzero(diff.any(1))
            last = nz[-1] if len(nz) else 0
            dI_in = int(p[T0:, inside].sum()) - int(twin[T0:, inside].sum())
            dI_out = int(p[T0:, ~inside].sum()) - int(twin[T0:, ~inside].sum())
            nodes_touched = int(diff.any(0).sum())
            rows.setdefault(name, []).append((ham_in[:50].mean(), ham_out[:50].mean(), ham_out[-100:].mean(),
                                               last, nodes_touched, dI_in, dI_out))
print(f"{'topology':<13}{'ham_in@50':>10}{'ham_out@50':>11}{'ham_out_end':>12}{'last_diff_t':>12}{'nodes_touched':>14}{'dI_in':>8}{'dI_out':>8}")
for name, r in rows.items():
    a = np.array(r, float)
    print(f"{name:<13}" + "".join(f"{v:>{w}.{p}f}" for v, w, p in zip(a.mean(0), [10,11,12,12,14,8,8], [3,4,4,0,0,1,1])))
    print(f"{'  sd':<13}" + "".join(f"{v:>{w}.{p}f}" for v, w, p in zip(a.std(0), [10,11,12,12,14,8,8], [3,4,4,0,0,1,1])))

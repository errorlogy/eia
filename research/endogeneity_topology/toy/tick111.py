"""Tick 111: a dedicated interface module. SBM with 11 modules x 100 (N=1100): 10 motive modules + 1 interface module.
Placements of the 100 sensors / 100 motors: TWO motive modules (sensors in module 0, motors in module 9), DEDICATED (both in
the interface module 10, 50/50 split... sensors = first 50 + motors = last 50 of module 10, echoing 50 units), SCATTERED
(random over motive modules). Hidden world support net of noise floor, w=1, D=20; 3 seeds."""
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs
import topo_endo as te
N = 1100; K = 11; mods = np.arange(N) // 100

def sim(W, seed, sens, motor, w_world, T=3000, D=20, p=0.8, cut=False):
    rng = np.random.default_rng(seed)
    d = rng.uniform(0, .3, N); u = rng.uniform(.2, .6, N); s = np.zeros(N); refr = np.zeros(N); hist = np.zeros((T, N), bool)
    for t in range(T):
        echo = np.zeros(N); r = rng.random(len(motor))
        if t >= D and not cut: echo[sens] = w_world * (hist[t - D, motor] & (r < p))
        inp = W @ s + echo
        u = np.clip(u + te.AGE*(1-u) + te.BETA_U*inp*(1-u) - te.RESOLVE*u*s, 0, 1)
        d = np.clip((1-te.RHO)*d + te.ALPHA*u + inp + te.SIGMA*rng.standard_normal(N) - .8*s, 0, 1)
        s = ((d > te.THETA) & (refr <= 0)).astype(float); refr = np.where(s > 0, 5, refr-1); hist[t] = s > 0
    return hist[500:]

def placement(kind, seed):
    if kind == "two motive modules": return np.arange(0, 100), np.arange(900, 1000)
    if kind == "dedicated interface": return np.arange(1000, 1050), np.arange(1050, 1100)
    perm = np.random.default_rng(seed + 11).permutation(1000); return np.sort(perm[:100]), np.sort(perm[100:200])

print(f"{'placement':<22}{'hidden world support':>21}{'motive-module activity kept':>29}")
for kind in ("two motive modules", "dedicated interface", "scattered"):
    vals = []
    for seed in (1, 2, 3):
        g = nx.stochastic_block_model([100]*K, [[5*0.9/99 if i == j else 5*0.1/1000 for j in range(K)] for i in range(K)], seed=seed, sparse=True)
        A = nx.to_scipy_sparse_array(g, nodelist=range(N), format="csr", dtype=float); A1 = A / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0])
        sens, motor = placement(kind, seed)
        lo, hi = 0.3, 1.5
        for _ in range(9):
            mid = (lo+hi)/2; lo, hi = (mid, hi) if sim(sps.csr_matrix(A1*mid), seed, sens, motor, 1.0, 1500).mean() < 0.03 else (lo, mid)
        W = sps.csr_matrix(A1*(lo+hi)/2); motive = mods < 10
        f1 = sim(W, seed, sens, motor, 1.0); c1 = sim(W, seed, sens, motor, 1.0, cut=True)
        vals.append((1 - c1.mean() / f1.mean(), c1[:, motive].mean() / f1[:, motive].mean()))
    m = np.mean(vals, 0); print(f"{kind:<22}{m[0]:>21.2f}{m[1]:>29.2f}", flush=True)

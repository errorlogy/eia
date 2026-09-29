"""Tick 90: redistributing Governor. Share cap (tick 89) + a global threshold offset that holds the total rate at the
target 0.03 (so capped budget is re-allocated to other motives). Module 0 excitability x2.5; same W; 2 seeds."""
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs
import topo_endo as te
from tick88 import E_others
N = 1000; mods = np.arange(N) // 100; tgt = mods == 0

def sim(W, alpha, seed, T=3000, cap=None, hold=False):
    rng = np.random.default_rng(seed); theta = np.full(10, te.THETA); off = 0.0
    d = rng.uniform(0, .3, N); u = rng.uniform(.2, .6, N); s = np.zeros(N); refr = np.zeros(N); out = np.zeros((T, N), bool)
    for t in range(T):
        inp = W @ s
        u = np.clip(u + te.AGE*(1-u) + te.BETA_U*inp*(1-u) - te.RESOLVE*u*s, 0, 1)
        d = np.clip((1-te.RHO)*d + alpha*u + inp + te.SIGMA*rng.standard_normal(N) - .8*s, 0, 1)
        s = ((d > theta[mods] + off) & (refr <= 0)).astype(float); refr = np.where(s > 0, 5, refr-1); out[t] = s > 0
        if cap is not None and (t + 1) % 50 == 0:
            w = out[t-49:t+1]; tot = w.sum()
            if tot:
                share = np.array([w[:, mods == m].sum() for m in range(10)]) / tot
                theta = np.clip(theta + (share - cap), te.THETA - 0.3, 0.95)
            if hold:
                off = float(np.clip(off + 2.0 * (w.mean() - 0.03), -0.3, 0.3))
    return out[500:]

print(f"{'condition':<22}{'gen share':>10}{'indep':>7}{'E others':>10}{'rate':>7}")
for name, cap, hold in (("no governor", None, False), ("cap 0.15", 0.15, False), ("cap 0.15 + hold rate", 0.15, True)):
    rows = []
    for seed in (1, 2):
        g = nx.stochastic_block_model([100]*10, [[5*0.9/99 if i == j else 5*0.1/900 for j in range(10)] for i in range(10)], seed=seed, sparse=True)
        A = nx.to_scipy_sparse_array(g, nodelist=range(N), format="csr", dtype=float); A1 = A / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0])
        alpha = np.full(N, te.ALPHA); alpha[tgt] *= 2.5
        lo, hi = 0.3, 1.5
        for _ in range(9):
            mid = (lo+hi)/2; lo, hi = (mid, hi) if sim(sps.csr_matrix(A1*mid), alpha, seed, 1500).mean() < 0.03 else (lo, mid)
        W = sps.csr_matrix(A1*(lo+hi)/2); base = sim(W, alpha, seed, cap=cap, hold=hold)
        Wc = W.toarray(); Wc[np.ix_(tgt, ~tgt)] = 0
        indep = sim(sps.csr_matrix(Wc), alpha, seed, cap=cap, hold=hold)[:, tgt].mean() / base[:, tgt].mean()
        rows.append((base[:, tgt].sum() / base.sum(), indep, E_others(base, W), base.mean()))
    m = np.mean(rows, 0); print(f"{name:<22}{m[0]:>10.2f}{m[1]:>7.2f}{m[2]:>10.2f}{m[3]:>7.3f}", flush=True)

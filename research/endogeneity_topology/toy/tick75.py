"""Tick 75: hierarchy of timescales. SBM 10x100 (mu 0.1); modules 0-4 fast (drive decay rho 0.30),
modules 5-9 slow (rho 0.05); control: all rho 0.12. alpha scaled with rho (alpha*rho/0.12) so the drive
equilibrium is unchanged and only the timescale differs (first run without this: fast modules could not reach threshold). Rate-matched 0.03, 3 seeds.
Metrics: per-group E_norm (true W, module partition); cross-module trigger flow (attributed by W from units that
fired at t-1): share of cross-group triggering fast->slow vs slow->fast, normalised by source activity."""
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs
import topo_endo as te
N = 1000
mods = np.arange(N) // 100; slow = mods >= 5

def sim(W, rho, seed, T):
    rng = np.random.default_rng(seed)
    d = rng.uniform(0, .3, N); u = rng.uniform(.2, .6, N); s = np.zeros(N); refr = np.zeros(N); out = np.zeros((T, N), bool)
    for t in range(T):
        inp = W @ s
        u = np.clip(u + te.AGE*(1-u) + te.BETA_U*inp*(1-u) - te.RESOLVE*u*s, 0, 1)
        d = np.clip((1-rho)*d + te.ALPHA*(rho/te.RHO)*u + inp + te.SIGMA*rng.standard_normal(N) - .8*s, 0, 1)
        s = ((d > te.THETA) & (refr <= 0)).astype(float); refr = np.where(s > 0, 5, refr-1); out[t] = s > 0
    return out

def analyse(sp, W):
    P = sps.csr_matrix(sp[:-1].astype(float)); Sn = sp[1:]
    Wc = W.tocoo()
    def part(mask_row, mask_col):
        k = mask_row[Wc.row] & mask_col[Wc.col]
        return sps.csr_matrix((Wc.data[k], (Wc.row[k], Wc.col[k])), shape=W.shape)
    tot = (P @ W.T).toarray()
    same = part(np.ones(N, bool), np.ones(N, bool)).tocoo(); k = mods[same.row] == mods[same.col]
    Win = sps.csr_matrix((same.data[k], (same.row[k], same.col[k])), shape=W.shape)
    ins = (P @ Win.T).toarray(); endo = (tot <= 1e-12) | (ins >= 0.5 * tot)
    e = {g: endo[Sn[:, m]][:, None].mean() if False else endo[:, m][Sn[:, m]].mean() for g, m in (("fast", ~slow), ("slow", slow))}
    f2s = (P @ part(slow, ~slow).T).toarray()[Sn].sum(); s2f = (P @ part(~slow, slow).T).toarray()[Sn].sum()
    act_f, act_s = sp[:, ~slow].sum(), sp[:, slow].sum()
    return e, f2s / max(act_f, 1), s2f / max(act_s, 1), act_s / max(act_f, 1)

print(f"{'condition':<12}{'E fast':>8}{'E slow':>8}{'fast->slow':>12}{'slow->fast':>12}{'slow/fast activity':>20}")
for cond in ("uniform", "hierarchy"):
    rows = []
    for seed in (1, 2, 3):
        g = nx.stochastic_block_model([100]*10, [[5*0.9/99 if i == j else 5*0.1/900 for j in range(10)] for i in range(10)], seed=seed, sparse=True)
        A = nx.to_scipy_sparse_array(g, nodelist=range(N), format="csr", dtype=float)
        A1 = A / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0])
        rho = np.full(N, 0.12) if cond == "uniform" else np.where(slow, 0.05, 0.30)
        lo, hi = 0.5, 1.6
        for _ in range(10):
            mid = (lo+hi)/2; lo, hi = (mid, hi) if sim(A1*mid, rho, seed, 1000)[500:].mean() < 0.03 else (lo, mid)
        W = sps.csr_matrix(A1*(lo+hi)/2); sp = sim(W, rho, seed, 4500)[500:]
        e, fs, sf, ratio = analyse(sp, W); rows.append((e["fast"], e["slow"], fs, sf, ratio))
    m = np.mean(rows, 0); print(f"{cond:<12}{m[0]:>8.2f}{m[1]:>8.2f}{m[2]:>12.3f}{m[3]:>12.3f}{m[4]:>20.2f}", flush=True)

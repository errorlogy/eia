"""Tick 139: blind sub-agent detection under conduction delays. SBM 10x100 (mu 0.1), each edge gets a random delay 0..9 ticks.
Detectors on spike trains (Louvain on inferred graph): (a) lag-1 conditional attribution (tick 35), (b) multi-lag: parents =
spike counts summed over lags 1..10. ARI of found parts vs true modules; no-delay control. Rate-matched, 2 seeds."""
import io, contextlib, runpy
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs
import topo_endo as te
with contextlib.redirect_stdout(io.StringIO()):
    ari = runpy.run_path("tick12.py")["ari"]
import tick35_lib as t35
N = 1000; mods = np.arange(N) // 100

def sim(mats, seed, T):
    rng = np.random.default_rng(seed); D = max(k for k, _ in mats) + 1
    d = rng.uniform(0, .3, N); u = rng.uniform(.2, .6, N); s = np.zeros(N); refr = np.zeros(N); hist = np.zeros((D, N)); out = np.zeros((T, N), bool)
    for t in range(T):
        hist[t % D] = s; inp = sum(M @ hist[(t - k) % D] for k, M in mats)
        u = np.clip(u + te.AGE*(1-u) + te.BETA_U*inp*(1-u) - te.RESOLVE*u*s, 0, 1)
        d = np.clip((1-te.RHO)*d + te.ALPHA*u + inp + te.SIGMA*rng.standard_normal(N) - .8*s, 0, 1)
        s = ((d > te.THETA) & (refr <= 0)).astype(float); refr = np.where(s > 0, 5, refr-1); out[t] = s > 0
    return out[500:]

def split(W, delays):
    Wc = W.tocoo(); return [(k, sps.csr_matrix((Wc.data[delays == k], (Wc.row[delays == k], Wc.col[delays == k])), shape=W.shape)) for k in np.unique(delays)]

def detect(Wh, seed):
    G = nx.from_scipy_sparse_array(Wh + Wh.T); best = None
    for res in [0.5, 1, 2, 4]:
        lab = np.empty(N, int)
        for k, c in enumerate(nx.community.louvain_communities(G, weight="weight", resolution=res, seed=seed)): lab[list(c)] = k
        a = ari(lab, mods); best = a if best is None or a > best else best      # oracle resolution: upper bound per detector
    return best

def multilag(sp, L=10):
    X = sum(np.vstack([np.zeros((l, N)), sp[:-l]]).astype(float) for l in range(1, L + 1))
    return X

print(f"{'delays':<8}{'lag-1 detector ARI':>19}{'multi-lag detector ARI':>24}")
for cond in ("none", "0-9"):
    r1, rm = [], []
    for seed in (1, 2):
        g = nx.stochastic_block_model([100]*10, [[5*0.9/99 if i == j else 5*0.1/900 for j in range(10)] for i in range(10)], seed=seed, sparse=True)
        A = nx.to_scipy_sparse_array(g, nodelist=range(N), format="csr", dtype=float); A1 = A / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0])
        delays = np.zeros(A1.nnz, int) if cond == "none" else np.random.default_rng(seed).integers(0, 10, A1.tocoo().nnz)
        lo, hi = 0.5, 2.0
        for _ in range(9):
            mid = (lo+hi)/2; lo, hi = (mid, hi) if sim(split(sps.csr_matrix(A1*mid), delays), seed, 1500).mean() < 0.03 else (lo, mid)
        sp = sim(split(sps.csr_matrix(A1*(lo+hi)/2), delays), seed, 4500)[:2000]
        r1.append(detect(t35.top10(t35.conditional(sp, t35.pairwise(sp))), seed))
        X = multilag(sp); Kp = (sps.csr_matrix(X[:-1]).T @ sps.csr_matrix(sp[1:].astype(float))).toarray().T - np.outer(sp.mean(0), X.mean(0)) * (len(sp) - 1)
        np.fill_diagonal(Kp, 0); Kp = np.clip(Kp, 0, None)
        B = np.zeros((N, N)); Y = sp[1:].astype(float); Xp = X[:-1]
        for i in range(N):
            js = np.argsort(Kp[i])[-20:]; js = js[Kp[i, js] > 0]
            if len(js) == 0 or Y[:, i].sum() < 3: continue
            Xi = np.column_stack([np.ones(len(Xp)), Xp[:, i], Xp[:, js]]); B[i, js] = np.clip(np.linalg.lstsq(Xi, Y[:, i], rcond=None)[0][2:], 0, None)
        rm.append(detect(t35.top10(B), seed))
    print(f"{cond:<8}{np.mean(r1):>19.2f}{np.mean(rm):>24.2f}", flush=True)

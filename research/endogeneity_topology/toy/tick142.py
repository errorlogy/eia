"""Tick 142: attention-like dynamic routing. Fixed edge set (SBM 10x100, mu 0.2), but each edge weight is gated by the recent
co-activity of its endpoints: g_ij = 1 + beta * (z_i z_j - 1) clipped >= 0, z = standardised activity trace (tau 20 ticks).
beta = 0 is static. Rate-matched. Question: does dynamic routing by itself produce metastable/degenerate boundaries like the
brain (B9: split-half ARI ~0.04 with held-out E_norm ~0.4)? Blind detection per half (conditional detector, tick 35),
split-half ARI and held-out E_norm (true mean W). 2 seeds."""
import io, contextlib, runpy
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs
import topo_endo as te
with contextlib.redirect_stdout(io.StringIO()):
    ns = runpy.run_path("tick12.py")
E_of, ari, N = ns["E_of"], ns["ari"], ns["N"]
import tick35_lib as t35

def sim(W, seed, beta, T):
    rng = np.random.default_rng(seed); Wc = W.tocoo(); r, c, w0 = Wc.row, Wc.col, Wc.data
    d = rng.uniform(0, .3, N); u = rng.uniform(.2, .6, N); s = np.zeros(N); refr = np.zeros(N); tr = np.full(N, 0.03)
    out = np.zeros((T, N), bool); gsum = np.zeros_like(w0)
    for t in range(T):
        if beta:
            z = (tr - tr.mean()) / (tr.std() + 1e-9); g = np.clip(1 + beta * (z[r] * z[c] - 1), 0, None); gsum += g
            inp = np.bincount(r, weights=w0 * g * s[c], minlength=N)
        else:
            inp = W @ s
        u = np.clip(u + te.AGE*(1-u) + te.BETA_U*inp*(1-u) - te.RESOLVE*u*s, 0, 1)
        d = np.clip((1-te.RHO)*d + te.ALPHA*u + inp + te.SIGMA*rng.standard_normal(N) - .8*s, 0, 1)
        s = ((d > te.THETA) & (refr <= 0)).astype(float); refr = np.where(s > 0, 5, refr-1); tr += (s - tr) / 20; out[t] = s > 0
    Wmean = sps.csr_matrix((w0 * (gsum / T if beta else 1), (r, c)), shape=W.shape)
    return out[500:], Wmean

def detect(sp, seed):
    tr, tst = sp[:len(sp)//2], sp[len(sp)//2:]; Wh = t35.top10(t35.conditional(tr, t35.pairwise(tr))); G = nx.from_scipy_sparse_array(Wh + Wh.T)
    rng = np.random.default_rng(seed); best = None
    for res in [0.5, 1, 2, 4]:
        lab = np.empty(N, int)
        for k, cc in enumerate(nx.community.louvain_communities(G, weight="weight", resolution=res, seed=seed)): lab[list(cc)] = k
        sc = E_of(tst, Wh, lab) - E_of(tst, Wh, lab[rng.permutation(N)])
        if best is None or sc > best[0]: best = (sc, lab)
    return best[1]

if __name__ == "__main__":
    print(f"{'beta':>5}{'split-half ARI':>15}{'ARI vs modules':>15}{'held-out E_norm':>16}")
    for beta in (0.0, 0.5, 1.0, 2.0):
        rows = []
        for seed in (1, 2):
            g = nx.stochastic_block_model([100]*10, [[5*0.8/99 if i == j else 5*0.2/900 for j in range(10)] for i in range(10)], seed=seed, sparse=True)
            A = nx.to_scipy_sparse_array(g, nodelist=range(N), format="csr", dtype=float); A1 = A / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0])
            lo, hi = 0.3, 2.0
            for _ in range(9):
                mid = (lo+hi)/2; lo, hi = (mid, hi) if sim(sps.csr_matrix(A1*mid), seed, beta, 1500)[0].mean() < 0.03 else (lo, mid)
            sp, Wm = sim(sps.csr_matrix(A1*(lo+hi)/2), seed, beta, 8500); h1, h2 = sp[:4000], sp[4000:]
            l1, l2 = detect(h1, seed), detect(h2, seed + 1); rng = np.random.default_rng(seed)
            en = np.mean([E_of(h2, Wm, l1[rng.permutation(N)]) for _ in range(5)]); e = (E_of(h2, Wm, l1) - en) / (1 - en)
            rows.append((ari(l1, l2), ari(l1, np.arange(N) // 100), e))
        m = np.mean(rows, 0); print(f"{beta:>5}{m[0]:>15.2f}{m[1]:>15.2f}{m[2]:>16.2f}", flush=True)
    print("brain (B9): split-half ARI ~0.02-0.08, held-out E_norm ~0.3-0.5")

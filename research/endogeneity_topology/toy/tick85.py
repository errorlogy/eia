"""Tick 85: generator vs isolated — can interventions separate what attribution cannot? SBM 10x100 (mu 0.1).
Target module 0 in three versions: normal; GENERATOR (alpha x1.8, normal coupling); ISOLATED (normal alpha, incoming
cross-module links x0.1). Measures for module 0:
  self   = attribution-based self-initiation (share of its initiatives with no/within-module inferred cause, true W)
  out    = relative drop of the REST's activity when module 0 is silenced   (drives others?)
  indep  = module 0 activity kept when its incoming cross-module links are cut (independent of others?)
Rate-matched 0.03, 4 seeds."""
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs
import topo_endo as te
N = 1000; mods = np.arange(N) // 100; tgt = mods == 0

def sim(W, alpha, seed, T=3000, silent=None):
    rng = np.random.default_rng(seed)
    d = rng.uniform(0, .3, N); u = rng.uniform(.2, .6, N); s = np.zeros(N); refr = np.zeros(N); out = np.zeros((T, N), bool)
    for t in range(T):
        inp = W @ s
        u = np.clip(u + te.AGE*(1-u) + te.BETA_U*inp*(1-u) - te.RESOLVE*u*s, 0, 1)
        d = np.clip((1-te.RHO)*d + alpha*u + inp + te.SIGMA*rng.standard_normal(N) - .8*s, 0, 1)
        s = ((d > te.THETA) & (refr <= 0)).astype(float)
        if silent is not None: s[silent] = 0
        refr = np.where(s > 0, 5, refr-1); out[t] = s > 0
    return out[500:]

def self_init(sp, W):
    P = sps.csr_matrix(sp[:-1].astype(float)); Sn = sp[1:]
    Wc = W.tocoo(); k = mods[Wc.row] == mods[Wc.col]
    Win = sps.csr_matrix((Wc.data[k], (Wc.row[k], Wc.col[k])), shape=W.shape)
    tot = (P @ W.T).toarray(); ins = (P @ Win.T).toarray(); endo = (tot <= 1e-12) | (ins >= 0.5 * tot)
    return endo[:, tgt][Sn[:, tgt]].mean()

if __name__ == "__main__":
    print(f"{'module 0':<11}{'self':>7}{'out (rest drop when silenced)':>31}{'indep (kept when input cut)':>29}")
    for kind in ("normal", "generator", "isolated"):
        rows = []
        for seed in (1, 2, 3, 4):
            g = nx.stochastic_block_model([100]*10, [[5*0.9/99 if i == j else 5*0.1/900 for j in range(10)] for i in range(10)], seed=seed, sparse=True)
            A = nx.to_scipy_sparse_array(g, nodelist=range(N), format="lil", dtype=float)
            alpha = np.full(N, te.ALPHA)
            if kind == "generator": alpha[tgt] *= 1.8
            if kind == "isolated":
                rows_t = np.flatnonzero(tgt)
                for i in rows_t:
                    for j in list(A.rows[i]):
                        if not tgt[j]: A[i, j] = A[i, j] * 0.1
            A = A.tocsr(); A1 = A / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0])
            lo, hi = 0.5, 1.5
            for _ in range(9):
                mid = (lo+hi)/2; lo, hi = (mid, hi) if sim(sps.csr_matrix(A1*mid), alpha, seed, 1500).mean() < 0.03 else (lo, mid)
            W = sps.csr_matrix(A1*(lo+hi)/2); base = sim(W, alpha, seed)
            sil = sim(W, alpha, seed, silent=tgt)
            out = 1 - sil[:, ~tgt].mean() / base[:, ~tgt].mean()
            Wc = W.tolil()
            for i in np.flatnonzero(tgt):
                for j in list(Wc.rows[i]):
                    if not tgt[j]: Wc[i, j] = 0
            cut = sim(Wc.tocsr(), alpha, seed)
            rows.append((self_init(base, W), out, cut[:, tgt].mean() / base[:, tgt].mean()))
        m = np.mean(rows, 0); print(f"{kind:<11}{m[0]:>7.2f}{m[1]:>31.3f}{m[2]:>29.2f}", flush=True)

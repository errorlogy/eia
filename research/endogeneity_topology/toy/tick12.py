"""Tick 12: boundary discovery from spike trains only.
Inferred coupling: lagged excess co-activation K_ij = #(j at t-1, i at t) - expected. Louvain on K
(sym, positive part) at several resolutions; pick the one maximising E(found) - E(random, same sizes).
Evaluate E with the true W (ground-truth attribution) and ARI vs structural partition."""
import io, contextlib, runpy
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs
import topo_endo as te
with contextlib.redirect_stdout(io.StringIO()):
    ns6 = runpy.run_path("tick6.py")
build, N = ns6["build"], ns6["N"]
TARGET = 0.03

def sim(W, seed, T):
    rng = np.random.default_rng(seed)
    d = rng.uniform(0, .3, N); u = rng.uniform(.2, .6, N); s = np.zeros(N); refr = np.zeros(N)
    out = np.zeros((T, N), bool)
    for t in range(T):
        xi = rng.standard_normal(N); inp = W @ s
        u = np.clip(u + te.AGE*(1-u) + te.BETA_U*inp*(1-u) - te.RESOLVE*u*s, 0, 1)
        d = np.clip((1-te.RHO)*d + te.ALPHA*u + inp + te.SIGMA*xi - .8*s, 0, 1)
        s = ((d > te.THETA) & (refr <= 0)).astype(float); refr = np.where(s > 0, 5, refr-1)
        out[t] = s > 0
    return out

def E_of(sp, W, labels):
    Sp = sps.csr_matrix(sp[:-1].astype(float)); Sn = sp[1:]
    Wc = W.tocoo(); keep = labels[Wc.row] == labels[Wc.col]
    Win = sps.csr_matrix((Wc.data[keep], (Wc.row[keep], Wc.col[keep])), shape=W.shape)
    tot = (Sp @ W.T).toarray(); ins = (Sp @ Win.T).toarray()
    return ((tot <= 1e-12) | (ins >= 0.5 * tot))[Sn].mean()

def ari(a, b):
    from math import comb
    _, ai = np.unique(a, return_inverse=True); _, bi = np.unique(b, return_inverse=True)
    M = np.zeros((ai.max()+1, bi.max()+1), int); np.add.at(M, (ai, bi), 1)
    s = sum(comb(int(x), 2) for x in M.ravel()); sa = sum(comb(int(x), 2) for x in M.sum(1)); sb = sum(comb(int(x), 2) for x in M.sum(0))
    e = sa * sb / comb(len(a), 2); return (s - e) / (0.5 * (sa + sb) - e)

def infer(sp):
    S = sps.csr_matrix(sp.astype(float)); r = sp.mean(0)
    K = (S[:-1].T @ S[1:]).toarray().T - np.outer(r, r) * (len(sp) - 1)   # K[i,j]: j(t-1) -> i(t)
    K = np.clip(K + K.T, 0, None); np.fill_diagonal(K, 0)
    thr = np.percentile(K[K > 0], 90) if (K > 0).any() else 0   # keep strongest 10% of positive pairs
    return nx.from_numpy_array(np.where(K >= thr, K, 0))

def rand_same_sizes(labels, rng):
    return labels[rng.permutation(len(labels))]

if __name__ == "__main__":
    print(f"{'topology':<13}{'res':>5}{'#parts':>7}{'med size':>9}{'E_found':>8}{'E_null':>7}{'gain':>6}{'ARI_mod':>8}{'ARI_super':>10}")
    for name in ["small_world", "erdos_renyi", "modular_sbm", "hier_modular"]:
        for seed in [1, 2]:
            rng = np.random.default_rng(seed)
            g = nx.watts_strogatz_graph(N, 4, 0.1, seed=seed) if name == "small_world" else build(name, seed)[0]
            A = nx.to_scipy_sparse_array(g, nodelist=range(N), format="csr", dtype=float)
            A1 = A / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0])
            lo, hi = 0.8, 1.2
            for _ in range(10):
                mid = (lo + hi) / 2
                lo, hi = (mid, hi) if sim(A1*mid, seed, 1000)[500:].mean() < TARGET else (lo, mid)
            W = sps.csr_matrix(A1 * (lo + hi) / 2)
            sp = sim(W, seed, 4500)[500:]
            train, test = sp[:2000], sp[2000:]            # infer on train, score E on held-out test
            G = infer(train)
            best = None
            for res in [0.5, 1, 2, 4, 8]:
                comms = nx.community.louvain_communities(G, weight="weight", resolution=res, seed=seed)
                lab = np.empty(N, int)
                for k, c in enumerate(comms): lab[list(c)] = k
                ef = E_of(test, W, lab); en = E_of(test, W, rand_same_sizes(lab, rng))
                if best is None or ef - en > best[4] - best[5]:
                    best = (res, len(comms), int(np.median([len(c) for c in comms])), lab, ef, en)
            res, npart, med, lab, ef, en = best
            mod10, mod50 = np.arange(N) // (10 if name == "hier_modular" else 50), np.arange(N) // 50
            print(f"{name:<13}{res:>5}{npart:>7}{med:>9}{ef:>8.2f}{en:>7.2f}{ef-en:>6.2f}{ari(lab, mod10):>8.2f}{ari(lab, mod50):>10.2f}")

"""Tick 35: better blind attribution. Pairwise lagged excess (tick 13) is inflated by shared drive.
Conditional version: for each node i, least-squares regression of s_i(t+1) on s_j(t) over its top-20
pairwise candidates j (incl. own past); keep positive coefficients, top 10% overall.
Compare pairwise vs conditional: edge precision/recall vs true W, and blind E vs true E
for the true structural partition and a random partition. Held-out E; 2 seeds.
Enorm = (E(struct) - E(random)) / (1 - E(random)): null-normalised endogeneity."""
import io, contextlib, runpy
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs
with contextlib.redirect_stdout(io.StringIO()):
    ns = runpy.run_path("tick12.py")
sim, E_of, build, N = ns["sim"], ns["E_of"], ns["build"], ns["N"]

def pairwise(sp):
    S = sps.csr_matrix(sp.astype(float)); r = sp.mean(0)
    K = (S[:-1].T @ S[1:]).toarray().T - np.outer(r, r) * (len(sp) - 1)
    np.fill_diagonal(K, 0); return np.clip(K, 0, None)

def top10(K):
    thr = np.percentile(K[K > 0], 90); return sps.csr_matrix(np.where(K >= thr, K, 0))

def conditional(sp, K, cand=20):
    X = sp[:-1].astype(float); Y = sp[1:].astype(float); B = np.zeros((N, N))
    for i in range(N):
        if Y[:, i].sum() < 3: continue
        js = np.argsort(K[i])[-cand:]; js = js[K[i, js] > 0]
        cols = np.concatenate([[i], js]); Xi = np.column_stack([np.ones(len(X)), X[:, cols]])
        coef = np.linalg.lstsq(Xi, Y[:, i], rcond=None)[0][2:]
        B[i, js] = np.clip(coef, 0, None)
    return B

def pr(Wh, W):
    t = (W.toarray() > 0); p = Wh.toarray() > 0
    tp = (t & p).sum(); return tp / max(p.sum(), 1), tp / max(t.sum(), 1)

print(f"{'topology':<13}{'method':<12}{'prec':>6}{'rec':>6}{'E_true(struct)':>15}{'E_blind(struct)':>16}{'E_blind(rand)':>14}{'gap':>6}{'Enorm_true':>11}{'Enorm_blind':>12}")
for name in ["small_world", "erdos_renyi", "modular_sbm", "hier_modular"]:
    acc = {"pairwise": [], "conditional": []}
    for seed in [1, 2]:
        rng = np.random.default_rng(seed)
        g = nx.watts_strogatz_graph(N, 4, 0.1, seed=seed) if name == "small_world" else build(name, seed)[0]
        A = nx.to_scipy_sparse_array(g, nodelist=range(N), format="csr", dtype=float)
        A1 = A / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0])
        lo, hi = 0.8, 1.2
        for _ in range(10):
            mid = (lo+hi)/2; lo, hi = (mid, hi) if sim(A1*mid, seed, 1000)[500:].mean() < 0.03 else (lo, mid)
        W = sps.csr_matrix(A1*(lo+hi)/2); sp = sim(W, seed, 4500)[500:]; tr, tst = sp[:2000], sp[2000:]
        struct = np.arange(N) // (10 if name == "small_world" else 50); rnd = struct[rng.permutation(N)]
        K = pairwise(tr)
        for meth, Wh in [("pairwise", top10(K)), ("conditional", top10(conditional(tr, K)))]:
            p, r = pr(Wh, W); et = E_of(tst, W, struct); eb = E_of(tst, Wh, struct); er = E_of(tst, Wh, rnd)
            etr = E_of(tst, W, rnd)
            acc[meth].append((p, r, et, eb, er, (et-etr)/(1-etr), (eb-er)/(1-er)))
    for meth, rows in acc.items():
        m = np.mean(rows, 0)
        print(f"{name:<13}{meth:<12}{m[0]:>6.2f}{m[1]:>6.2f}{m[2]:>15.2f}{m[3]:>16.2f}{m[4]:>14.2f}{m[2]-m[3]:>6.2f}{m[5]:>11.2f}{m[6]:>12.2f}", flush=True)

"""Tick 42: are degenerate self-boundaries (human B9: split-half ARI 0.09, held-out E_norm ~0.45) a generic
property of near-critical networks, or specific to the brain? Toy networks at rate 0.03; split the activity
in halves, detect partitions on each (blind, tick 12 detector), score with conditional attribution +
E_norm (tick 35). Fixed vs metastable (switching SBM partitions, dwell 400 ticks)."""
import io, contextlib, runpy
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs
import topo_endo as te
with contextlib.redirect_stdout(io.StringIO()):
    ns12 = runpy.run_path("tick12.py")
E_of, infer, ari, build, N = ns12["E_of"], ns12["infer"], ns12["ari"], ns12["build"], ns12["N"]
import tick35_lib as t35  # noqa: E402

def sim(Ws, seed, T, dwell=None):
    rng = np.random.default_rng(seed); sw = np.random.default_rng(seed + 1); k = 0
    d = rng.uniform(0, .3, N); u = rng.uniform(.2, .6, N); s = np.zeros(N); refr = np.zeros(N); out = np.zeros((T, N), bool)
    for t in range(T):
        if dwell and sw.random() < 1 / dwell: k = (k + 1) % len(Ws)
        xi = rng.standard_normal(N); inp = Ws[k] @ s
        u = np.clip(u + te.AGE*(1-u) + te.BETA_U*inp*(1-u) - te.RESOLVE*u*s, 0, 1)
        d = np.clip((1-te.RHO)*d + te.ALPHA*u + inp + te.SIGMA*xi - .8*s, 0, 1)
        s = ((d > te.THETA) & (refr <= 0)).astype(float); refr = np.where(s > 0, 5, refr-1); out[t] = s > 0
    return out

def detect(sp, seed):
    tr, tst = sp[:len(sp)//2], sp[len(sp)//2:]; G = infer(tr); rng = np.random.default_rng(seed); best = None
    Wh = t35.top10(t35.conditional(tr, t35.pairwise(tr)))
    for res in [0.5, 1, 2, 4]:
        lab = np.empty(N, int)
        for k, c in enumerate(nx.community.louvain_communities(G, weight="weight", resolution=res, seed=seed)): lab[list(c)] = k
        sc = E_of(tst, Wh, lab) - E_of(tst, Wh, lab[rng.permutation(N)])
        if best is None or sc > best[0]: best = (sc, lab)
    return best[1]

def enorm(sp, Wh, lab, rng):
    en = np.mean([E_of(sp, Wh, lab[rng.permutation(N)]) for _ in range(5)]); return (E_of(sp, Wh, lab) - en) / (1 - en)

def sbm_W(seed, mu, perm=None):
    g = nx.stochastic_block_model([100]*10, [[5*(1-mu)/99 if i == j else 5*mu/900 for j in range(10)] for i in range(10)], seed=seed, sparse=True)
    A = nx.to_scipy_sparse_array(g, nodelist=range(N), format="csr", dtype=float)
    if perm is not None: A = A[perm][:, perm]
    return A / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0])

print(f"{'network':<22}{'split-half ARI':>15}{'E_norm(l1) on h2':>17}{'E_norm(l2)':>11}")
cases = {"SBM mu=0.10 fixed": dict(mu=0.10, dwell=None), "SBM mu=0.05 fixed": dict(mu=0.05, dwell=None),
         "hier fixed": dict(hier=True, dwell=None), "SBM mu=0.05 metastable": dict(mu=0.05, dwell=400)}
for name, c in cases.items():
    rows = []
    for seed in (1, 2):
        rng = np.random.default_rng(seed)
        if c.get("hier"):
            A = nx.to_scipy_sparse_array(build("hier_modular", seed)[0], nodelist=range(N), format="csr", dtype=float)
            Ws1 = [A / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0])]
        else:
            Ws1 = [sbm_W(seed, c["mu"])] + ([sbm_W(seed + 50, c["mu"], rng.permutation(N)) for _ in range(2)] if c["dwell"] else [])
        lo, hi = 0.8, 1.3
        for _ in range(9):
            mid = (lo+hi)/2; lo, hi = (mid, hi) if sim([W*mid for W in Ws1], seed, 1000, c["dwell"])[500:].mean() < 0.03 else (lo, mid)
        Ws = [sps.csr_matrix(W*(lo+hi)/2) for W in Ws1]
        sp = sim(Ws, seed, 8500, c["dwell"])[500:]; h1, h2 = sp[:4000], sp[4000:]
        l1, l2 = detect(h1, seed), detect(h2, seed + 1)
        Wh = t35.top10(t35.conditional(h1, t35.pairwise(h1)))
        rows.append((ari(l1, l2), enorm(h2, Wh, l1, rng), enorm(h2, Wh, l2, rng)))
    m = np.mean(rows, 0); print(f"{name:<22}{m[0]:>15.2f}{m[1]:>17.2f}{m[2]:>11.2f}", flush=True)
print("human empirical (tick 39): ARI 0.09, E_norm(l1) 0.49, E_norm(l2) 0.42")

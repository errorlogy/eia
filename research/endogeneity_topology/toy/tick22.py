"""Tick 22: hyperbolic and p-adic (ultrametric) topologies (Kairologos link).
  hyperbolic   Krioukov random hyperbolic graph (alpha 0.75 -> degree exponent ~2.5), mean deg ~6
  padic_a1.0   ultrametric p=10, 3 levels, P(d) = 0.35 * 10^(-1.0 (d-1))  (each level equal weight)
  padic_a1.5   same, alpha 1.5 (steeper hierarchy)
  refs: hier_modular (tick 3), scale_free (BA m=3)
Metrics: (1) transition smoothness over gain 0.85-1.25 (max step jump of rate x base), rich width;
(2) blind boundary detector (tick 12) -> true E of found parts, median part size."""
import io, contextlib, runpy
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs
import topo_endo as te
with contextlib.redirect_stdout(io.StringIO()):
    ns = runpy.run_path("tick12.py")
sim, E_of, infer, build, N = ns["sim"], ns["E_of"], ns["infer"], ns["build"], ns["N"]

def hyperbolic(seed, alpha=0.75, target_deg=6):
    rng = np.random.default_rng(seed)
    th = rng.uniform(0, 2*np.pi, N); u = rng.random(N)
    def graph(R):
        r = np.arccosh(1 + u*(np.cosh(alpha*R) - 1)) / alpha
        dth = np.pi - np.abs(np.pi - np.abs(th[:, None] - th[None, :]))
        ch = np.cosh(r)[:, None]*np.cosh(r)[None, :] - np.sinh(r)[:, None]*np.sinh(r)[None, :]*np.cos(dth)
        A = (np.arccosh(np.maximum(ch, 1)) < R).astype(float); np.fill_diagonal(A, 0); return A
    lo, hi = 5.0, 25.0
    for _ in range(25):
        mid = (lo+hi)/2; k = graph(mid).sum()/N
        lo, hi = (mid, hi) if k > target_deg else (lo, mid)
    return nx.from_numpy_array(graph((lo+hi)/2))

def padic(seed, a, p=10):
    rng = np.random.default_rng(seed); i = np.arange(N)
    d = np.where(i[:, None]//p == i[None, :]//p, 1, np.where(i[:, None]//p**2 == i[None, :]//p**2, 2, 3))
    P = 0.35 * 10.0**(-a*(d-1)); A = np.triu(rng.random((N, N)) < P, 1); A = A | A.T
    return nx.from_numpy_array(A.astype(float))

def topos(seed):
    return {"hyperbolic": hyperbolic(seed), "padic_a1.0": padic(seed, 1.0), "padic_a1.5": padic(seed, 1.5),
            "hier_modular": build("hier_modular", seed)[0], "scale_free": nx.barabasi_albert_graph(N, 3, seed=seed)}

gains = [round(0.85 + 0.05*i, 2) for i in range(9)]
names = ["hyperbolic", "padic_a1.0", "padic_a1.5", "hier_modular", "scale_free"]
sweep, blind, info = {}, {n: [] for n in names}, {n: [] for n in names}
for seed in [1, 2, 3]:
    b0 = sim(sps.csr_matrix((N, N)), seed, 1500)[500:].mean()
    for name, g in topos(seed).items():
        A = nx.to_scipy_sparse_array(g, nodelist=range(N), format="csr", dtype=float)
        A1 = A / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0])
        cc = nx.average_clustering(g); info[name].append((A.sum()/N, cc))
        for gn in gains:
            sp = sim(A1*gn, seed, 1500)[500:]; m = te.metrics(np.vstack([np.zeros((500, N), bool), sp]), b0)
            sweep.setdefault((name, gn), []).append(m)
        lo, hi = 0.7, 1.4
        for _ in range(10):
            mid = (lo+hi)/2; lo, hi = (mid, hi) if sim(A1*mid, seed, 1000)[500:].mean() < 0.03 else (lo, mid)
        W = sps.csr_matrix(A1*(lo+hi)/2); sp = sim(W, seed, 4500)[500:]; tr, tst = sp[:2000], sp[2000:]
        G = infer(tr); rng = np.random.default_rng(seed); best = None
        for res in [0.5, 1, 2, 4]:
            lab = np.empty(N, int)
            for k, c in enumerate(nx.community.louvain_communities(G, weight="weight", resolution=res, seed=seed)): lab[list(c)] = k
            sc = E_of(tst, W, lab) - E_of(tst, W, lab[rng.permutation(N)])
            if best is None or sc > best[0]: best = (sc, lab)
        lab = best[1]; sizes = np.bincount(lab)
        blind[name].append((E_of(tst, W, lab), E_of(tst, W, lab[rng.permutation(N)]), np.median(sizes), (lo+hi)/2))

def rich(m): return m["rate_x_base"] > 1.5 and 0.7 <= m["cv_isi"] <= 2.5
print(f"{'topology':<13}{'deg':>5}{'clust':>6} | rate x base over gains {gains}")
for n in names:
    r = [np.mean([m["rate_x_base"] for m in sweep[(n, g)]]) for g in gains]
    w = sum(np.mean([rich(m) for m in sweep[(n, g)]]) >= 0.6 for g in gains)
    dg, cc = np.mean(info[n], 0)
    print(f"{n:<13}{dg:>5.1f}{cc:>6.2f} | " + " ".join(f"{x:5.1f}" for x in r) + f" | jump {max(np.diff(r)):.1f} width {w}")
print(f"\n{'topology':<13}{'op gain':>8}{'E found':>8}{'E null':>7}{'median part':>12}")
for n in names:
    a = np.array(blind[n]); print(f"{n:<13}{a[:,3].mean():>8.3f}{a[:,0].mean():>8.2f}{a[:,1].mean():>7.2f}{a[:,2].mean():>12.0f}")

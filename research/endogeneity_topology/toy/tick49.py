"""Tick 49: directed graphs — does endogeneity need cycles? Directed random graphs (N=1000, mean out-degree 4)
with reciprocity r in {0 (DAG-like? no: random directed), 0.5, 1.0 (undirected)} and a strict DAG (edges only
i->j for i<j: no cycles at all). W normalised so the mean row sum = g (mean branching ratio, since
spectral radius of a DAG is 0). Metrics over g: rate x base; persist = activity kept after noise is
switched off (self-sustainment); spectral radius of W (loop gain)."""
import numpy as np, scipy.sparse as sps
from scipy.sparse.linalg import eigs
import topo_endo as te
N = te.N = 1000

def graph(kind, seed, k=4):
    rng = np.random.default_rng(seed); A = np.zeros((N, N))
    if kind == "DAG":
        m = rng.random((N, N)) < 2*k/N; A = np.triu(m, 1).astype(float)
    else:
        r = {"directed r=0": 0.0, "directed r=0.5": 0.5, "undirected": 1.0}[kind]
        m = rng.random((N, N)) < k/N; np.fill_diagonal(m, False); A = m.astype(float)
        recip = (rng.random((N, N)) < r) & (A.T > 0); A = np.maximum(A, recip.astype(float))
        if r == 1.0: A = np.maximum(A, A.T)
    return A

def run(W, seed, noise_off=None, T=3000):
    rng = np.random.default_rng(seed)
    d = rng.uniform(0, .3, N); u = rng.uniform(.2, .6, N); s = np.zeros(N); refr = np.zeros(N); out = np.zeros(T)
    for t in range(T):
        sig = 0.0 if (noise_off is not None and t >= noise_off) else te.SIGMA
        inp = W @ s
        u = np.clip(u + te.AGE*(1-u) + te.BETA_U*inp*(1-u) - te.RESOLVE*u*s, 0, 1)
        d = np.clip((1-te.RHO)*d + te.ALPHA*u + inp + sig*rng.standard_normal(N) - .8*s, 0, 1)
        s = ((d > te.THETA) & (refr <= 0)).astype(float); refr = np.where(s > 0, 5, refr-1); out[t] = s.mean()
    return out

gs = [0.6, 0.8, 1.0, 1.2, 1.5]
base = run(sps.csr_matrix((N, N)), 1)[500:].mean()
print(f"{'graph':<16}{'rho(W)/g':>9} | " + " ".join(f"{'g='+str(g):>13}" for g in gs) + "   (rate x base / persist)")
for kind in ["DAG", "directed r=0", "directed r=0.5", "undirected"]:
    cells, rhos = [], []
    for g in gs:
        r = []
        for seed in (1, 2):
            A = graph(kind, seed); W = sps.csr_matrix(A * (g / A.sum(1).mean()))
            if g == gs[0]:
                rhos.append(np.max(np.abs(np.linalg.eigvals(W.toarray()))) / g)
            on = run(W, seed)[500:].mean() / base
            pr = run(W, seed, noise_off=1500); persist = pr[2500:].mean() / max(pr[1000:1500].mean(), 1e-9)
            r.append((on, persist))
        m = np.mean(r, 0); cells.append(f"{m[0]:5.1f}/{m[1]:.2f}")
    print(f"{kind:<16}{np.mean(rhos):>9.2f} | " + " ".join(f"{c:>13}" for c in cells), flush=True)

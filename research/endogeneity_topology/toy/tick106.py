"""Tick 106: noise-driven vs self-sustained endogeneity. At the rate-matched gain (0.03), switch noise off after warm-up and
measure (i) activity kept, (ii) burst CV before/after (does deterministic dynamics stay irregular or lock into a cycle?).
Topologies: ER, SBM, hier-modular, BA, EDR (lambda 0.05). 2 seeds."""
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs
import topo_endo as te
from tick104 import graph as g104
from tick73 import edr
N = 1000

def run(W, seed, T=4000, off=2000):
    rng = np.random.default_rng(seed)
    d = rng.uniform(0, .3, N); u = rng.uniform(.2, .6, N); s = np.zeros(N); refr = np.zeros(N); out = np.zeros(T)
    for t in range(T):
        sig = te.SIGMA if t < off else 0.0; inp = W @ s
        u = np.clip(u + te.AGE*(1-u) + te.BETA_U*inp*(1-u) - te.RESOLVE*u*s, 0, 1)
        d = np.clip((1-te.RHO)*d + te.ALPHA*u + inp + sig*rng.standard_normal(N) - .8*s, 0, 1)
        s = ((d > te.THETA) & (refr <= 0)).astype(float); refr = np.where(s > 0, 5, refr-1); out[t] = s.mean()
    return out

def cv(x):
    ev = np.flatnonzero(x > np.percentile(x, 90)); isi = np.diff(ev); isi = isi[isi > 1]
    return isi.std() / isi.mean() if len(isi) > 2 else float("nan")

if __name__ == "__main__":
    print(f"{'topology':<9}{'kept (noise off)':>17}{'CV noisy':>10}{'CV no-noise':>12}")
    for kind in ("ER", "SBM", "hier", "BA", "EDR"):
        rows = []
        for seed in (1, 2):
            A = edr(seed, 0.05)[0] if kind == "EDR" else nx.to_scipy_sparse_array(g104(kind, seed), nodelist=range(N), format="csr", dtype=float)
            A1 = A / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0])
            lo, hi = 0.5, 1.5
            for _ in range(9):
                mid = (lo+hi)/2; lo, hi = (mid, hi) if run(sps.csr_matrix(A1*mid), seed, 1500, off=10**9)[500:].mean() < 0.03 else (lo, mid)
            o = run(sps.csr_matrix(A1*(lo+hi)/2), seed)
            rows.append((o[2500:].mean() / o[500:2000].mean(), cv(o[500:2000]), cv(o[2500:])))
        m = np.nanmean(rows, 0); print(f"{kind:<9}{m[0]:>17.2f}{m[1]:>10.2f}{m[2]:>12.2f}", flush=True)

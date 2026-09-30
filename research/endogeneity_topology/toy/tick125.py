"""Tick 125: carrier resonance. Weak modulation A = 0.05; carrier period P in {6, 12, 24, 48, 96, 192} ticks; hier-modular
and ER. PLV of burst onsets to the carrier. Intrinsic timescales: refractory 5 ticks, drive decay 1/rho ~ 8 ticks. 2 seeds."""
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs
from tick124 import sim, plv_cv, build, N

Ps = [6, 12, 24, 48, 96, 192]
print(f"{'topology':<7}" + "".join(f"{'P='+str(p):>8}" for p in Ps) + "   (PLV at A = 0.05)")
for kind in ("hier", "ER"):
    row = []
    for P in Ps:
        v = []
        for seed in (1, 2):
            g = build("hier_modular", seed)[0] if kind == "hier" else nx.erdos_renyi_graph(N, 5/N, seed=seed)
            Aa = nx.to_scipy_sparse_array(g, nodelist=range(N), format="csr", dtype=float); A1 = Aa / abs(eigs(Aa, k=1, which="LM", return_eigenvectors=False)[0])
            lo, hi = 0.7, 1.4
            for _ in range(9):
                mid = (lo+hi)/2; lo, hi = (mid, hi) if sim(sps.csr_matrix(A1*mid), seed, 0.0, 1500).mean() < 0.03 else (lo, mid)
            sp = sim(sps.csr_matrix(A1*(lo+hi)/2), seed, 0.05, P=P); v.append(plv_cv(sp, P=P)[0])
        row.append(np.mean(v))
    print(f"{kind:<7}" + "".join(f"{x:>8.2f}" for x in row), flush=True)

"""Tick 43: re-check the design rule mu_c ~0.1 (A12) with endogeneity itself instead of detectability (ARI).
SBM 10x100 and 20x50, degree 5, rate 0.03. For the TRUE module partition: E_norm with true W (ground truth)
and blind conditional attribution (tick 35). A sub-agent 'exists' when E_norm is high."""
import io, contextlib, runpy
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs
with contextlib.redirect_stdout(io.StringIO()):
    ns = runpy.run_path("tick12.py")
sim, E_of, N = ns["sim"], ns["E_of"], ns["N"]
import tick35_lib as t35

def enorm(sp, W, lab, rng):
    en = np.mean([E_of(sp, W, lab[rng.permutation(N)]) for _ in range(5)]); return (E_of(sp, W, lab) - en) / (1 - en)

mus = [0.3, 0.2, 0.15, 0.1, 0.07, 0.05, 0.03]
print(f"{'family':<11}" + "".join(f"{'mu='+str(m):>12}" for m in mus) + "   (true / blind E_norm)")
for size in (100, 50):
    cells = []
    for mu in mus:
        r = []
        for seed in (1, 2):
            k = N // size
            g = nx.stochastic_block_model([size]*k, [[5*(1-mu)/(size-1) if i == j else 5*mu/(N-size) for j in range(k)] for i in range(k)], seed=seed, sparse=True)
            A = nx.to_scipy_sparse_array(g, nodelist=range(N), format="csr", dtype=float)
            A1 = A / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0])
            lo, hi = 0.7, 1.4
            for _ in range(10):
                mid = (lo+hi)/2; lo, hi = (mid, hi) if sim(A1*mid, seed, 1000)[500:].mean() < 0.03 else (lo, mid)
            W = sps.csr_matrix(A1*(lo+hi)/2); sp = sim(W, seed, 4500)[500:]; tr, tst = sp[:2000], sp[2000:]
            lab = np.arange(N) // size; rng = np.random.default_rng(seed)
            Wh = t35.top10(t35.conditional(tr, t35.pairwise(tr)))
            r.append((enorm(tst, W, lab, rng), enorm(tst, Wh, lab, rng)))
        m = np.mean(r, 0); cells.append(f"{m[0]:.2f}/{m[1]:.2f}")
    print(f"SBM x{size:<6}" + "".join(f"{c:>12}" for c in cells), flush=True)

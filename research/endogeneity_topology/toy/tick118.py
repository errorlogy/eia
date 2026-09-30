"""Tick 118: the recommended architecture as a whole — hierarchical-modular motives + thin workspace layer (w 0.4).
Compare hier alone vs hier + workspace: block-level integration / TSE, module E_norm (100-unit blocks), and per-motive
controllability (u-only do(Z) on block 5 and 8, exact twin, 600 ticks). Rate-matched, 3 seeds."""
import io, contextlib, runpy
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs
import topo_endo as te
with contextlib.redirect_stdout(io.StringIO()):
    ns12 = runpy.run_path("tick12.py"); build = runpy.run_path("tick6.py")["build"]
sim, E_of, N = ns12["sim"], ns12["E_of"], ns12["N"]
from tick67 import layers
from tick116 import tse, mods
T, T0 = 1600, 1000

def sim_boost(W, seed, S=None):
    rng = np.random.default_rng(seed)
    d = rng.uniform(0, .3, N); u = rng.uniform(.2, .6, N); s = np.zeros(N); refr = np.zeros(N); out = np.zeros((T, N), bool)
    for t in range(T):
        if S is not None and t == T0: u[S] = 1.0
        inp = W @ s
        u = np.clip(u + te.AGE*(1-u) + te.BETA_U*inp*(1-u) - te.RESOLVE*u*s, 0, 1)
        d = np.clip((1-te.RHO)*d + te.ALPHA*u + inp + te.SIGMA*rng.standard_normal(N) - .8*s, 0, 1)
        s = ((d > te.THETA) & (refr <= 0)).astype(float); refr = np.where(s > 0, 5, refr-1); out[t] = s > 0
    return out

z = lambda x: x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))
print(f"{'architecture':<18}{'integration':>12}{'TSE':>7}{'module E_norm':>15}{'d self':>8}{'z':>6}")
for name, w in (("hier alone", 0.0), ("hier + workspace", 0.4)):
    rows, dself = [], []
    for seed in (1, 2, 3):
        H = nx.to_scipy_sparse_array(build("hier_modular", seed)[0], nodelist=range(N), format="csr", dtype=float)
        H = H / abs(eigs(H, k=1, which="LM", return_eigenvectors=False)[0]); _, B = layers(seed)
        lo, hi = 0.3, 1.4
        for _ in range(10):
            mid = (lo+hi)/2; lo, hi = (mid, hi) if sim(H*mid + B*w, seed, 1000)[500:].mean() < 0.03 else (lo, mid)
        W = sps.csr_matrix(H*(lo+hi)/2 + B*w); sp = sim(W, seed, 6500)[500:]
        X = np.stack([sp[:, mods == m].reshape(-1, 10, 100).mean((1, 2)) for m in range(10)])
        rng = np.random.default_rng(seed); I, C = tse(X, rng)
        en = np.mean([E_of(sp, W, mods[rng.permutation(N)]) for _ in range(5)]); e = (E_of(sp, W, mods) - en) / (1 - en)
        rows.append((I, C, e))
        tw = sim_boost(W, seed)
        for m in (5, 8):
            ins = mods == m; pe = sim_boost(W, seed, np.flatnonzero(ins)); dself.append(int(pe[T0:, ins].sum()) - int(tw[T0:, ins].sum()))
    m = np.mean(rows, 0); d = np.array(dself)
    print(f"{name:<18}{m[0]:>12.2f}{m[1]:>7.2f}{m[2]:>15.2f}{d.mean():>8.1f}{z(d):>6.2f}", flush=True)

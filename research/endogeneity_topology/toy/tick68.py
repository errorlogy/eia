"""Tick 68: does the workspace layer let one motive recruit the whole agent? u-only do(Z) on one module
(exact twin), w in {0, 0.4}; 8 seeds x 3 modules. Metrics over 600 ticks: extra initiatives in target (z),
spill-over to the rest (z), extra global ignitions (>=5 modules bursting) (z)."""
import numpy as np, scipy.sparse as sps
import topo_endo as te
from tick67 import layers, mods, N

T, T0 = 1600, 1000
def sim(W, seed, S=None):
    rng = np.random.default_rng(seed)
    d = rng.uniform(0, .3, N); u = rng.uniform(.2, .6, N); s = np.zeros(N); refr = np.zeros(N); out = np.zeros((T, N), bool)
    for t in range(T):
        if S is not None and t == T0: u[S] = 1.0
        xi = rng.standard_normal(N); inp = W @ s
        u = np.clip(u + te.AGE*(1-u) + te.BETA_U*inp*(1-u) - te.RESOLVE*u*s, 0, 1)
        d = np.clip((1-te.RHO)*d + te.ALPHA*u + inp + te.SIGMA*xi - .8*s, 0, 1)
        s = ((d > te.THETA) & (refr <= 0)).astype(float); refr = np.where(s > 0, 5, refr-1); out[t] = s > 0
    return out

def ign(sp):
    return int((np.stack([sp[:, mods == m].mean(1) >= 0.10 for m in range(10)], 1).sum(1) >= 5).sum())

z = lambda x: x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))
print(f"{'w':>4}{'d self':>9}{'z':>7}{'d rest':>9}{'z':>7}{'d ignitions':>12}{'z':>7}")
for w in (0.0, 0.4):
    a, b, c = [], [], []
    for seed in range(1, 9):
        A, B = layers(seed)
        lo, hi = 0.5, 1.4
        for _ in range(10):
            mid = (lo+hi)/2; lo, hi = (mid, hi) if sim(A*mid + B*w, seed)[500:1000].mean() < 0.03 else (lo, mid)
        W = sps.csr_matrix(A*(lo+hi)/2 + B*w); tw = sim(W, seed)
        for m in (0, 4, 8):
            ins = mods == m; pe = sim(W, seed, np.flatnonzero(ins))
            a.append(int(pe[T0:, ins].sum()) - int(tw[T0:, ins].sum()))
            b.append(int(pe[T0:, ~ins].sum()) - int(tw[T0:, ~ins].sum()))
            c.append(ign(pe[T0:]) - ign(tw[T0:]))
    a, b, c = map(np.array, (a, b, c))
    print(f"{w:>4}{a.mean():>9.1f}{z(a):>7.2f}{b.mean():>9.1f}{z(b):>7.2f}{c.mean():>12.2f}{z(c):>7.2f}", flush=True)

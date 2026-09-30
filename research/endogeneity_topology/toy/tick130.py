"""Tick 130: adaptation (a slow 'boredom' current) and the risk of an internal clock. Each unit gets an adaptation variable
w_i: w += (b*s - w)/tau_w (tau_w = 100 ticks), subtracted from the drive. b in {0, 0.1, 0.3}. Rate-matched per b.
Measures: population burst CV, periodicity (height of the first non-zero autocorrelation peak of population activity) and
its period, module E_norm (true W). Hier-modular and ER; 2 seeds."""
import io, contextlib, runpy
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs
import topo_endo as te
with contextlib.redirect_stdout(io.StringIO()):
    ns = runpy.run_path("tick12.py"); build = runpy.run_path("tick6.py")["build"]
E_of, N = ns["E_of"], ns["N"]; mods = np.arange(N) // 100

def sim(W, seed, bad, T=5000, tau=100.0):
    rng = np.random.default_rng(seed)
    d = rng.uniform(0, .3, N); u = rng.uniform(.2, .6, N); s = np.zeros(N); refr = np.zeros(N); a = np.zeros(N); out = np.zeros((T, N), bool)
    for t in range(T):
        inp = W @ s
        u = np.clip(u + te.AGE*(1-u) + te.BETA_U*inp*(1-u) - te.RESOLVE*u*s, 0, 1)
        d = np.clip((1-te.RHO)*d + te.ALPHA*u + inp + te.SIGMA*rng.standard_normal(N) - .8*s - a, 0, 1)
        s = ((d > te.THETA) & (refr <= 0)).astype(float); refr = np.where(s > 0, 5, refr-1); a += (bad * s - a) / tau; out[t] = s > 0
    return out[500:]

def rhythm(x):
    x = x - x.mean(); ac = np.correlate(x, x, "full")[len(x)-1:]; ac /= ac[0]
    lag = np.argmax(ac[20:600]) + 20; return ac[lag], lag

def cv(x):
    ev = np.flatnonzero((x[1:] > np.percentile(x, 90)) & (x[:-1] <= np.percentile(x, 90))); isi = np.diff(ev)
    return isi.std() / isi.mean() if len(isi) > 2 else np.nan

print(f"{'topology':<7}{'b':>5}{'burst CV':>10}{'autocorr peak':>15}{'period':>8}{'module E_norm':>15}")
for kind in ("hier", "ER"):
    for bad in (0.0, 0.1, 0.3):
        rows = []
        for seed in (1, 2):
            g = build("hier_modular", seed)[0] if kind == "hier" else nx.erdos_renyi_graph(N, 5/N, seed=seed)
            A = nx.to_scipy_sparse_array(g, nodelist=range(N), format="csr", dtype=float); A1 = A / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0])
            lo, hi = 0.5, 2.5
            for _ in range(10):
                mid = (lo+hi)/2; lo, hi = (mid, hi) if sim(sps.csr_matrix(A1*mid), seed, bad, 1500).mean() < 0.03 else (lo, mid)
            W = sps.csr_matrix(A1*(lo+hi)/2); sp = sim(W, seed, bad); x = sp.mean(1)
            pk, per = rhythm(x); rng = np.random.default_rng(seed)
            en = np.mean([E_of(sp, W, mods[rng.permutation(N)]) for _ in range(5)])
            rows.append((cv(x), pk, per, (E_of(sp, W, mods) - en) / (1 - en)))
        m = np.nanmean(rows, 0); print(f"{kind:<7}{bad:>5}{m[0]:>10.2f}{m[1]:>15.2f}{m[2]:>8.0f}{m[3]:>15.2f}", flush=True)

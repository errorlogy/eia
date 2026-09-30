"""Tick 124: a global carrier rhythm (Kairologos '42 Hz' as a test assumption). Global gain modulated as
g(t) = g0 * (1 + A sin(2 pi t / P)), P = 24 ticks (~42 Hz if a tick is 1 ms), A in {0, 0.05, 0.15, 0.3}.
Measures: phase-locking value (PLV) of population burst onsets to the carrier, burst CV, module E_norm; hier-modular vs ER.
Rate-matched at A = 0. 2 seeds."""
import io, contextlib, runpy
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs
import topo_endo as te
with contextlib.redirect_stdout(io.StringIO()):
    ns = runpy.run_path("tick12.py"); build = runpy.run_path("tick6.py")["build"]
E_of, N = ns["E_of"], ns["N"]
mods = np.arange(N) // 100; P = 24

def sim(W, seed, A, T=5000):
    rng = np.random.default_rng(seed)
    d = rng.uniform(0, .3, N); u = rng.uniform(.2, .6, N); s = np.zeros(N); refr = np.zeros(N); out = np.zeros((T, N), bool)
    for t in range(T):
        g = 1 + A * np.sin(2 * np.pi * t / P); inp = g * (W @ s)
        u = np.clip(u + te.AGE*(1-u) + te.BETA_U*inp*(1-u) - te.RESOLVE*u*s, 0, 1)
        d = np.clip((1-te.RHO)*d + te.ALPHA*u + inp + te.SIGMA*rng.standard_normal(N) - .8*s, 0, 1)
        s = ((d > te.THETA) & (refr <= 0)).astype(float); refr = np.where(s > 0, 5, refr-1); out[t] = s > 0
    return out[500:]

def plv_cv(sp):
    x = sp.mean(1); on = np.flatnonzero((x[1:] > np.percentile(x, 90)) & (x[:-1] <= np.percentile(x, 90))) + 1
    ph = 2 * np.pi * ((on + 500) % P) / P; plv = np.abs(np.exp(1j * ph).mean()) if len(on) else 0
    isi = np.diff(on); cv = isi.std() / isi.mean() if len(isi) > 2 else np.nan
    return plv, cv

print(f"{'topology':<7}{'A':>6}{'rate':>7}{'PLV to carrier':>16}{'burst CV':>10}{'module E_norm':>15}")
for kind in ("hier", "ER"):
    for A in (0.0, 0.05, 0.15, 0.3):
        rows = []
        for seed in (1, 2):
            g = build("hier_modular", seed)[0] if kind == "hier" else nx.erdos_renyi_graph(N, 5/N, seed=seed)
            Aa = nx.to_scipy_sparse_array(g, nodelist=range(N), format="csr", dtype=float); A1 = Aa / abs(eigs(Aa, k=1, which="LM", return_eigenvectors=False)[0])
            lo, hi = 0.7, 1.4
            for _ in range(9):
                mid = (lo+hi)/2; lo, hi = (mid, hi) if sim(sps.csr_matrix(A1*mid), seed, 0.0, 1500).mean() < 0.03 else (lo, mid)
            W = sps.csr_matrix(A1*(lo+hi)/2); sp = sim(W, seed, A); rng = np.random.default_rng(seed)
            plv, cv = plv_cv(sp); en = np.mean([E_of(sp, W, mods[rng.permutation(N)]) for _ in range(5)])
            rows.append((sp.mean(), plv, cv, (E_of(sp, W, mods) - en) / (1 - en)))
        m = np.nanmean(rows, 0); print(f"{kind:<7}{A:>6}{m[0]:>7.3f}{m[1]:>16.2f}{m[2]:>10.2f}{m[3]:>15.2f}", flush=True)

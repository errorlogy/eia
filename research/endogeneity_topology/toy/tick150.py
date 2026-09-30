"""Tick 150: noise colour. Hier-modular network; noise = white (baseline) / independent pink (1/f per unit) / half-shared pink
(50 % of the noise power is one common 1/f process). Same total noise variance. Rate-matched. Measures: burst CV, envelope
autocorrelation peak, module E_norm (true W). 2 seeds, 5000 ticks."""
import io, contextlib, runpy
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs
import topo_endo as te
with contextlib.redirect_stdout(io.StringIO()):
    ns = runpy.run_path("tick12.py"); build = runpy.run_path("tick6.py")["build"]
E_of, N = ns["E_of"], ns["N"]; mods = np.arange(N) // 100

def pink(rng, T, n):
    X = np.fft.rfft(rng.standard_normal((n, T)), axis=1); f = np.fft.rfftfreq(T); f[0] = f[1]
    x = np.fft.irfft(X / np.sqrt(f), n=T, axis=1); return (x / x.std(axis=1, keepdims=True)).T   # (T, n)

def noise(kind, seed, T):
    rng = np.random.default_rng(seed + 500)
    if kind == "white": return rng.standard_normal((T, N))
    ind = pink(rng, T, N)
    if kind == "pink": return ind
    return np.sqrt(0.5) * ind + np.sqrt(0.5) * pink(rng, T, 1)

def sim(W, seed, xi):
    rng = np.random.default_rng(seed); T = len(xi)
    d = rng.uniform(0, .3, N); u = rng.uniform(.2, .6, N); s = np.zeros(N); refr = np.zeros(N); out = np.zeros((T, N), bool)
    for t in range(T):
        inp = W @ s
        u = np.clip(u + te.AGE*(1-u) + te.BETA_U*inp*(1-u) - te.RESOLVE*u*s, 0, 1)
        d = np.clip((1-te.RHO)*d + te.ALPHA*u + inp + te.SIGMA*xi[t] - .8*s, 0, 1)
        s = ((d > te.THETA) & (refr <= 0)).astype(float); refr = np.where(s > 0, 5, refr-1); out[t] = s > 0
    return out[500:]

def stats(sp):
    x = sp.mean(1); xc = x - x.mean(); ac = np.correlate(xc, xc, "full")[len(xc)-1:]; ac /= ac[0]; pk = ac[20:800].max()
    th = np.percentile(x, 90); ev = np.flatnonzero((x[1:] > th) & (x[:-1] <= th)); isi = np.diff(ev)
    return (isi.std() / isi.mean() if len(isi) > 2 else np.nan), pk

print(f"{'noise':<16}{'burst CV':>9}{'envelope ac':>12}{'module E_norm':>15}")
for kind in ("white", "pink", "half-shared pink"):
    rows = []
    for seed in (1, 2):
        A = nx.to_scipy_sparse_array(build("hier_modular", seed)[0], nodelist=range(N), format="csr", dtype=float); A1 = A / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0])
        xs = noise(kind, seed, 1500); lo, hi = 0.5, 1.5
        for _ in range(9):
            mid = (lo+hi)/2; lo, hi = (mid, hi) if sim(sps.csr_matrix(A1*mid), seed, xs).mean() < 0.03 else (lo, mid)
        W = sps.csr_matrix(A1*(lo+hi)/2); sp = sim(W, seed, noise(kind, seed, 5000)); cv, pk = stats(sp); rng = np.random.default_rng(seed)
        en = np.mean([E_of(sp, W, mods[rng.permutation(N)]) for _ in range(5)]); rows.append((cv, pk, (E_of(sp, W, mods) - en) / (1 - en)))
    m = np.nanmean(rows, 0); print(f"{kind:<16}{m[0]:>9.2f}{m[1]:>12.2f}{m[2]:>15.2f}", flush=True)

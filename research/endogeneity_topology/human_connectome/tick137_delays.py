"""Tick 137: conduction delays from real tract lengths. Drive-units on SC (94 regions x 10 units); between-region links
delayed by round(length_mm / v) ticks (1 tick = 1 ms; v in {inf (no delay), 10, 3} m/s -> median delays 0 / 13 / 44 ticks),
binned into 8 delay classes. Within-region links undelayed. Rate-matched. Measures: burst CV, envelope autocorrelation peak
and period, module E_norm (EIA module map, true W). 2 subjects x 2 seeds."""
import numpy as np, scipy.sparse as sps, scipy.io as sio
import brain_eia as b
from tick47_units_on_sc import unit_matrix, R, UPR, N, te
reg = np.repeat(np.arange(R), UPR)
import runpy, io, contextlib, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "toy"))
MOD = np.full(R, -1)
for k, (m, idx) in enumerate(b.IDX.items()): MOD[idx] = k
lab_units = np.where(MOD[reg] >= 0, MOD[reg], 100 + reg)

def delay_mats(W, Lmm, v):
    Wc = W.tocoo(); same = reg[Wc.row] == reg[Wc.col]
    if v is None: return [(0, W)]
    d = np.where(same, 0, np.round(Lmm[reg[Wc.row], reg[Wc.col]] / v)).astype(int)
    bins = np.unique(np.concatenate([[0], np.quantile(d[~same], np.linspace(0, 1, 9)[1:]).round().astype(int)]))
    dq = bins[np.clip(np.searchsorted(bins, d), 0, len(bins) - 1)]
    return [(k, sps.csr_matrix((Wc.data[dq == k], (Wc.row[dq == k], Wc.col[dq == k])), shape=W.shape)) for k in np.unique(dq)]

def sim(mats, seed, T=4000):
    rng = np.random.default_rng(seed); D = max(k for k, _ in mats) + 1
    d = rng.uniform(0, .3, N); u = rng.uniform(.2, .6, N); s = np.zeros(N); refr = np.zeros(N)
    hist = np.zeros((D, N)); out = np.zeros((T, N), bool)
    for t in range(T):
        hist[t % D] = s
        inp = sum(M @ hist[(t - k) % D] for k, M in mats)
        u = np.clip(u + te.AGE*(1-u) + te.BETA_U*inp*(1-u) - te.RESOLVE*u*s, 0, 1)
        d = np.clip((1-te.RHO)*d + te.ALPHA*u + inp + te.SIGMA*rng.standard_normal(N) - .8*s, 0, 1)
        s = ((d > te.THETA) & (refr <= 0)).astype(float); refr = np.where(s > 0, 5, refr-1); out[t] = s > 0
    return out[500:]

def env_stats(sp):
    x = sp.mean(1); xc = x - x.mean(); ac = np.correlate(xc, xc, "full")[len(xc)-1:]; ac /= ac[0]; lag = np.argmax(ac[10:800]) + 10
    th = np.percentile(x, 90); ev = np.flatnonzero((x[1:] > th) & (x[:-1] <= th)); isi = np.diff(ev)
    return (isi.std() / isi.mean() if len(isi) > 2 else np.nan), ac[lag], lag

def E_norm(sp, W, lab, rng):
    P = sps.csr_matrix(sp[:-1].astype(float)); Sn = sp[1:]; Wc = W.tocoo()
    def E(l):
        k = l[Wc.row] == l[Wc.col]; Win = sps.csr_matrix((Wc.data[k], (Wc.row[k], Wc.col[k])), shape=W.shape)
        tot = (P @ W.T).toarray(); ins = (P @ Win.T).toarray(); return ((tot <= 1e-12) | (ins >= 0.5 * tot))[Sn].mean()
    en = np.mean([E(lab[rng.permutation(N)]) for _ in range(3)]); return (E(lab) - en) / (1 - en)

print(f"{'velocity':<10}{'median delay':>13}{'burst CV':>9}{'envelope ac':>12}{'period':>8}{'EIA-module E_norm':>19}")
for v in (None, 10.0, 3.0):
    rows = []
    for s_ in b.SUBJECTS[:2]:
        C, _ = b.load(s_); Lmm = sio.loadmat(b.DATA / f"{s_}_DTI_LEN.mat")["len"].astype(float)
        for seed in (1, 2):
            W1 = sps.csr_matrix(unit_matrix(C, seed)); lo, hi = 0.5, 2.5
            for _ in range(9):
                mid = (lo+hi)/2; lo, hi = (mid, hi) if sim(delay_mats(W1*mid, Lmm, v), seed, 1500).mean() < 0.03 else (lo, mid)
            W = W1*(lo+hi)/2; sp = sim(delay_mats(W, Lmm, v), seed); cv, ac, per = env_stats(sp)
            rows.append((cv, ac, per, E_norm(sp, W, lab_units, np.random.default_rng(seed))))
    m = np.nanmean(rows, 0); med = 0 if v is None else np.median(Lmm[Lmm > 0]) / v
    print(f"{'none' if v is None else str(v)+' m/s':<10}{med:>13.0f}{m[0]:>9.2f}{m[1]:>12.2f}{m[2]:>8.0f}{m[3]:>19.2f}", flush=True)

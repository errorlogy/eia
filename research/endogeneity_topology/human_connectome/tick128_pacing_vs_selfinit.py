"""Tick 128: region-level link between global-rhythm pacing (tick 127, leave-own-module-out PLV) and residual
self-initiation (tick 81: self-initiation regressed on SC strength, inferred in-degree, event count). Spearman per subject,
7 subjects; also partial on event count (PLV estimates depend on it)."""
import numpy as np
from scipy.signal import hilbert
from scipy.stats import spearmanr, rankdata
import brain_eia as b
from tick15_empirical import events
from tick36_calibrated import infer_cond, parents
from tick81_initiators_7subj import SUBJ, load

MOD = np.full(94, -1)
for k, (m, idx) in enumerate(b.IDX.items()): MOD[idx] = k
rs, rp = [], []
for s in SUBJ:
    C, tc = load(s); ev = events(tc); tr, te = ev[:len(ev)//2], ev[len(ev)//2:]
    Wh = infer_cond(tr); tot = parents(te) @ Wh.T
    y = np.array([((tot[:, i] <= 1e-12) & te[:, i]).sum() / max(te[:, i].sum(), 1) for i in range(94)])
    X = np.column_stack([np.ones(94), C.sum(1), (Wh > 0).sum(1), te.sum(0)]); resid = y - X @ np.linalg.lstsq(X, y, rcond=None)[0]
    plv = np.empty(94)
    for i in range(94):
        keep = (MOD != MOD[i]) if MOD[i] >= 0 else (np.arange(94) != i)
        ph = np.angle(hilbert(b.bandpass(tc[keep].mean(0, keepdims=True), 0.01, 0.03)[0][1:]))
        plv[i] = np.abs(np.exp(1j * ph[ev[:, i]]).mean()) if ev[:, i].sum() > 3 else np.nan
    ok = ~np.isnan(plv); rs.append(spearmanr(plv[ok], resid[ok])[0])
    n = ev.sum(0)[ok]; rz = rankdata(n)
    ex = rankdata(plv[ok]) - np.polyval(np.polyfit(rz, rankdata(plv[ok]), 1), rz); ey = rankdata(resid[ok]) - np.polyval(np.polyfit(rz, rankdata(resid[ok]), 1), rz)
    rp.append(np.corrcoef(ex, ey)[0, 1])
    print(f"{s}: rho(pacing, residual self-init) {rs[-1]:+.2f}   partial | event count {rp[-1]:+.2f}", flush=True)
print(f"mean rho {np.mean(rs):+.2f} (negative in {sum(r < 0 for r in rs)}/7), mean partial {np.mean(rp):+.2f}")

"""Tick 80: tick 79 with confounds regressed out. Per region & subject: self-initiated share, SC strength,
inferred in-degree (non-zero parents in W_hat), event count (proxy for signal quality). Residualise self-initiation
on these (OLS, per subject), then average residuals per module. 4 subjects."""
import numpy as np
from scipy.stats import spearmanr
import brain_eia as b
from tick15_empirical import events
from tick36_calibrated import infer_cond, parents

res = []
for s in b.SUBJECTS:
    C, tc = b.load(s); ev = events(tc); tr, te = ev[:len(ev)//2], ev[len(ev)//2:]
    Wh = infer_cond(tr); P = parents(te); tot = P @ Wh.T
    y = np.array([((tot[:, i] <= 1e-12) & te[:, i]).sum() / max(te[:, i].sum(), 1) for i in range(94)])
    X = np.column_stack([np.ones(94), C.sum(1), (Wh > 0).sum(1), te.sum(0)])
    beta = np.linalg.lstsq(X, y, rcond=None)[0]; r = y - X @ beta
    res.append(r)
    print(f"{s}: R^2 of confounds = {1 - r.var() / y.var():.2f}")
R = np.mean(res, 0)
print("residual self-initiation by module (positive = more self-initiating than connectivity/indegree/event-count predict):")
for m, idx in sorted(b.IDX.items(), key=lambda kv: -R[kv[1]].mean()):
    z = R[idx].mean() / (R.std() / np.sqrt(len(idx)))
    print(f"  {m:<4} {R[idx].mean():+.3f}  (z vs region spread {z:+.2f}, n={len(idx)})")
rr = [spearmanr(res[i], res[j])[0] for i in range(4) for j in range(i + 1, 4)]
print(f"cross-subject consistency of residual profile: {np.mean(rr):.2f}")

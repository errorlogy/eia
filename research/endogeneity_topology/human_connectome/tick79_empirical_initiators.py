"""Tick 79: which regions self-initiate in REAL resting-state data? Per region: share of its BOLD events (tick 15
point process) with no inferred parent activity in the previous 1-3 TR (conditional attribution, tick 36; inferred on
the first half, scored on the second). Averaged per EIA module and correlated with SC strength. 4 subjects."""
import numpy as np
from scipy.stats import spearmanr
import brain_eia as b
from tick15_empirical import events
from tick36_calibrated import infer_cond, parents

rows, strength = [], []
for s in b.SUBJECTS:
    C, tc = b.load(s); ev = events(tc); tr, te = ev[:len(ev)//2], ev[len(ev)//2:]
    Wh = infer_cond(tr); P = parents(te); tot = P @ Wh.T
    spont = np.array([((tot[:, i] <= 1e-12) & te[:, i]).sum() / max(te[:, i].sum(), 1) for i in range(94)])
    rows.append(spont); strength.append(C.sum(1))
sp = np.mean(rows, 0); st = np.mean(strength, 0)
print("self-initiated share of events, by module (mean over regions, 4 subjects):")
for m, idx in b.IDX.items():
    print(f"  {m:<4} {sp[idx].mean():.3f}  (n={len(idx)})")
other = np.setdiff1d(np.arange(94), np.concatenate(list(b.IDX.values())))
print(f"  other {sp[other].mean():.3f}")
print(f"Spearman(self-initiation, SC strength) = {spearmanr(sp, st)[0]:+.2f}")
top = np.argsort(sp)[-10:][::-1]
print("top-10 self-initiating regions:", [b.LABELS[i] for i in top])
# split-half-free reliability across subjects
r = [spearmanr(rows[i], rows[j])[0] for i in range(4) for j in range(i + 1, 4)]
print(f"cross-subject consistency of the regional profile: mean Spearman {np.mean(r):.2f}")

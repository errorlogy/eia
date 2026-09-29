"""Tick 81: B14 on all 7 neurolib HCP subjects, with across-subject statistics. Same residualisation as tick 80
(self-initiated share ~ SC strength + inferred in-degree + event count, per subject); module means per subject;
one-sample t across subjects."""
import numpy as np
from scipy.stats import ttest_1samp
import scipy.io as sio
import brain_eia as b
from tick15_empirical import events
from tick36_calibrated import infer_cond, parents

SUBJ = ["101309", "102311", "102816", "131217", "211619", "213522", "377451"]
def load(s):
    sc = sio.loadmat(b.DATA / f"{s}_DTI_CM.mat")["sc"].astype(float); np.fill_diagonal(sc, 0); sc = (sc + sc.T) / 2
    return sc / sc.max() * 0.2, sio.loadmat(b.DATA / f"{s}_TC_rsfMRI_REST1_LR.mat")["tc"].astype(float)

if __name__ == "__main__":
    per = {m: [] for m in b.IDX}
    for s in SUBJ:
        C, tc = load(s); ev = events(tc); tr, te = ev[:len(ev)//2], ev[len(ev)//2:]
        Wh = infer_cond(tr); P = parents(te); tot = P @ Wh.T
        y = np.array([((tot[:, i] <= 1e-12) & te[:, i]).sum() / max(te[:, i].sum(), 1) for i in range(94)])
        X = np.column_stack([np.ones(94), C.sum(1), (Wh > 0).sum(1), te.sum(0)])
        r = y - X @ np.linalg.lstsq(X, y, rcond=None)[0]
        for m, idx in b.IDX.items(): per[m].append(r[idx].mean())
    print(f"{'module':<6}{'mean residual':>14}{'sd':>7}{'t':>7}{'p':>8}{'subjects >0':>13}")
    for m, v in sorted(per.items(), key=lambda kv: -np.mean(kv[1])):
        v = np.array(v); t, p = ttest_1samp(v, 0)
        print(f"{m:<6}{v.mean():>+14.3f}{v.std(ddof=1):>7.3f}{t:>7.2f}{p:>8.3f}{(v > 0).sum():>9}/{len(v)}")

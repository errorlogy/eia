"""Tick 27: why does lateral inhibition kill per-motive controllability (tick 26)?
Hypothesis: winner-take-most -> effect depends on who holds the floor at t0; mean effect exists but
variance swamps it. For every module as target (10 seeds x 10 modules), classify by the target's share
of initiatives in [t0-20, t0): 'holder' (top module) vs 'others'. Report mean/sd of the local effect,
and a WTA index = mean share of the top module per 20-tick window."""
import numpy as np, scipy.sparse as sps
from tick25_lib import sbm, signed
from tick26 import sim, T0, N

z = lambda x: x.mean() / (x.std(ddof=1)/np.sqrt(len(x))) if len(x) > 1 else float("nan")
print(f"{'condition':<11}{'WTA':>6}{'n hold':>7}{'dI_in hold':>11}{'dI_in other':>12}{'sd all':>8}{'mean all':>9}{'z all':>7}{'z other':>8}")
for cond in ["exc", "cross_inh"]:
    hold, other, wta = [], [], []
    for seed in range(1, 11):
        A, truth = sbm(seed, 0.2); S1, _ = signed(A, truth, cond, seed)
        lo, hi = 0.5, 3.0
        for _ in range(11):
            m_ = (lo+hi)/2; lo, hi = (m_, hi) if sim(S1*m_, seed, T=1000)[500:].mean() < 0.03 else (lo, m_)
        W = sps.csr_matrix(S1*(lo+hi)/2); tw = sim(W, seed)
        per_mod = np.stack([tw[:, truth == k].sum(1) for k in range(10)], 1)        # (T, 10)
        win = per_mod[500:].reshape(-1, 20, 10).sum(1); tot = win.sum(1)
        wta.append(np.mean(win.max(1)[tot > 0] / tot[tot > 0]))
        pre = per_mod[T0-20:T0].sum(0); top = int(np.argmax(pre)) if pre.sum() > 0 else -1
        for k in range(10):
            ins = truth == k; pe = sim(W, seed, np.flatnonzero(ins))
            d = int(pe[T0:, ins].sum()) - int(tw[T0:, ins].sum())
            (hold if k == top else other).append(d)
    hold, other = np.array(hold), np.array(other); allv = np.concatenate([hold, other])
    print(f"{cond:<11}{np.mean(wta):>6.2f}{len(hold):>7}{hold.mean() if len(hold) else float('nan'):>11.1f}{other.mean():>12.1f}{allv.std():>8.1f}{allv.mean():>9.1f}{z(allv):>7.2f}{z(other):>8.2f}", flush=True)

"""Tick 102: does the connectome model (no SNR issues) reproduce the empirical negative correlation between region
strength and self-initiation (tick 79: rho = -0.55)? Drive-units on SC (tick 47 model), homogeneous timescales, rate-matched.
Per region: share of its unit-initiatives that are cascade starts (no active in-neighbour at t-1), activity share,
and SC strength. 4 subjects."""
import numpy as np, scipy.sparse as sps
from scipy.stats import spearmanr
import brain_eia as b
from tick47_units_on_sc import unit_matrix, R, UPR, N, te
from tick76_timescale_brain import sim, reg

rs, ra = [], []
for s_ in b.SUBJECTS:
    C, _ = b.load(s_); rho = np.full(N, 0.12); W1 = unit_matrix(C, 1); lo, hi = 0.5, 1.6
    for _ in range(9):
        mid = (lo+hi)/2; lo, hi = (mid, hi) if sim(sps.csr_matrix(W1*mid), rho, 1, 1500).mean() < 0.03 else (lo, mid)
    W = sps.csr_matrix(W1*(lo+hi)/2); sp = sim(W, rho, 1)
    prev_in = np.vstack([np.zeros((1, N)), (sps.csr_matrix(sp[:-1].astype(float)) @ (W > 0).T.astype(float)).toarray()])
    starts = sp & (prev_in == 0)
    start_share = np.array([starts[:, reg == r].sum() / max(sp[:, reg == r].sum(), 1) for r in range(R)])
    act = np.array([sp[:, reg == r].mean() for r in range(R)])
    st = C.sum(1)
    rs.append(spearmanr(st, start_share)[0]); ra.append(spearmanr(st, act)[0])
    print(f"{s_}: rho(strength, cascade-start share) = {rs[-1]:+.2f}   rho(strength, activity) = {ra[-1]:+.2f}", flush=True)
print(f"mean: start-share {np.mean(rs):+.2f} (empirical self-initiation vs strength: -0.55), activity {np.mean(ra):+.2f}")

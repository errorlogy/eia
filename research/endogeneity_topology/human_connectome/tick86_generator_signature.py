"""Tick 86: A26 generator signature for each EIA block on the human connectome (drive-units on SC, timescale
hierarchy as in tick 76). For block M: out = relative drop of all other units' activity when M is silenced;
indep = M's activity kept when all its incoming links from outside M are cut. 2 subjects x 1 seed, rate-matched."""
import numpy as np, scipy.sparse as sps
import brain_eia as b
from tick47_units_on_sc import unit_matrix, R, N, te
from tick76_timescale_brain import sim, reg

print(f"{'block':<5}{'out':>8}{'indep':>8}   (generator = high out & high indep; isolated = low out & high indep)")
res = {m: [] for m in b.IDX}
for s_ in b.SUBJECTS[:2]:
    C, _ = b.load(s_)
    rho_reg = np.full(R, 0.12); rho_reg[np.concatenate([b.IDX["DMN"], b.IDX["VAL"]])] = 0.05; rho_reg[b.IDX["SEN"]] = 0.30
    rho = rho_reg[reg]; W1 = unit_matrix(C, 1); lo, hi = 0.5, 1.6
    for _ in range(9):
        mid = (lo+hi)/2; lo, hi = (mid, hi) if sim(sps.csr_matrix(W1*mid), rho, 1, 1500).mean() < 0.03 else (lo, mid)
    W = W1*(lo+hi)/2; Ws = sps.csr_matrix(W); base = sim(Ws, rho, 1)
    for m, idx in b.IDX.items():
        inside = np.isin(reg, idx)
        sil = sim(Ws, rho, 1, silent=inside)
        out = 1 - sil[:, ~inside].mean() / base[:, ~inside].mean()
        Wc = W.copy(); Wc[np.ix_(inside, ~inside)] = 0
        indep = sim(sps.csr_matrix(Wc), rho, 1)[:, inside].mean() / base[:, inside].mean()
        res[m].append((out / inside.mean(), indep))   # out normalised per share of units silenced
for m, v in res.items():
    o, i = np.mean(v, 0); print(f"{m:<5}{o:>8.2f}{i:>8.2f}", flush=True)

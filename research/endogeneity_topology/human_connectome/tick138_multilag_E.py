"""Tick 138: multi-lag endogeneity under conduction delays. For each delay class k (matrix M_k), the cause of an initiative
at t is spiking at t-1-k (the sim adds M_k @ s(t-1-k)). E(B) = share of initiatives whose delayed input is >= 50 % from
inside B (or none); E_norm vs 3 permutations. Compare lag-1 E_norm (tick 137) and multi-lag E_norm. 2 subjects x 1 seed."""
import numpy as np, scipy.sparse as sps, scipy.io as sio
import brain_eia as b
from tick137_delays import delay_mats, sim, E_norm as E_norm_lag1, lab_units, unit_matrix, N

def E_multilag(sp, mats, lab, rng):
    T = len(sp); S = sp.astype(float)
    def E(l):
        tot = np.zeros((T, N)); ins = np.zeros((T, N))
        for k, M in mats:
            sh = np.vstack([np.zeros((k + 1, N)), S[:T - k - 1]]); Mc = M.tocoo(); same = l[Mc.row] == l[Mc.col]
            Min = sps.csr_matrix((Mc.data[same], (Mc.row[same], Mc.col[same])), shape=M.shape)
            P = sps.csr_matrix(sh); tot += (P @ M.T).toarray(); ins += (P @ Min.T).toarray()
        return ((tot <= 1e-12) | (ins >= 0.5 * tot))[sp].mean()
    en = np.mean([E(lab[rng.permutation(N)]) for _ in range(3)]); return (E(lab) - en) / (1 - en)

print(f"{'velocity':<10}{'E_norm lag-1':>13}{'E_norm multi-lag':>18}")
for v in (None, 10.0, 3.0):
    r1, rm = [], []
    for s_ in b.SUBJECTS[:2]:
        C, _ = b.load(s_); Lmm = sio.loadmat(b.DATA / f"{s_}_DTI_LEN.mat")["len"].astype(float)
        W1 = sps.csr_matrix(unit_matrix(C, 1)); lo, hi = 0.5, 2.5
        for _ in range(9):
            mid = (lo+hi)/2; lo, hi = (mid, hi) if sim(delay_mats(W1*mid, Lmm, v), 1, 1500).mean() < 0.03 else (lo, mid)
        W = W1*(lo+hi)/2; mats = delay_mats(W, Lmm, v); sp = sim(mats, 1, 3000)
        r1.append(E_norm_lag1(sp, W, lab_units, np.random.default_rng(1))); rm.append(E_multilag(sp, mats, lab_units, np.random.default_rng(1)))
    print(f"{'none' if v is None else str(v)+' m/s':<10}{np.mean(r1):>13.2f}{np.mean(rm):>18.2f}", flush=True)

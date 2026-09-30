"""Tick 129: does the Hopf connectome model reproduce B18 (events phase-locked to the slow global signal; SEN/SMA most,
BG/VAL least)? Same analysis (leave-own-module-out PLV, 0.01-0.03 Hz) on model 'BOLD' for all 7 subjects, plain SC."""
import numpy as np
from scipy.signal import hilbert
from scipy.stats import pearsonr
import brain_eia as b
from tick15_empirical import events
from tick81_initiators_7subj import SUBJ, load
from tick82_model_initiators import sim

EMP = {"DMN": 0.337, "SAL": 0.437, "BG": 0.256, "SMA": 0.507, "VAL": 0.258, "FPN": 0.400, "SEN": 0.446}
MOD = np.full(94, -1)
for k, (m, idx) in enumerate(b.IDX.items()): MOD[idx] = k
out = {m: [] for m in b.IDX}; allv = []
for i_s, s in enumerate(SUBJ):
    C, _ = load(s); x = sim(C, np.full(94, -0.02), 1300 + i_s); ev = events(x)
    for i in range(94):
        keep = (MOD != MOD[i]) if MOD[i] >= 0 else (np.arange(94) != i)
        ph = np.angle(hilbert(b.bandpass(x[keep].mean(0, keepdims=True), 0.01, 0.03)[0][1:]))
        if ev[:, i].sum() > 3:
            v = np.abs(np.exp(1j * ph[ev[:, i]]).mean()); allv.append(v)
            for m, idx in b.IDX.items():
                if i in idx: out[m].append(v)
mods = list(EMP); mv = [np.mean(out[m]) for m in mods]
print(f"model PLV all regions {np.mean(allv):.3f} (empirical 0.379)")
for m, v in zip(mods, mv): print(f"  {m:<4} model {v:.3f}  empirical {EMP[m]:.3f}")
print(f"module-profile correlation with empirical: r = {pearsonr(mv, [EMP[m] for m in mods])[0]:+.2f}")

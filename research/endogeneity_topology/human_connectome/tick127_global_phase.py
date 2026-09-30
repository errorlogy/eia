"""Tick 127: are empirical 'spontaneous' BOLD events paced by the slow global signal (A36 in data)?
Global signal = mean over 94 regions; slow band 0.01-0.03 Hz, Hilbert phase. Events = tick-15 point process.
PLV of each region's events to the global slow phase, averaged over regions and by EIA module; null = circularly shifted
event trains (200 shifts). 7 subjects."""
import numpy as np
from scipy.signal import hilbert
import brain_eia as b
from tick15_empirical import events
from tick81_initiators_7subj import SUBJ, load

rng = np.random.default_rng(127)
res = {"all": [], **{m: [] for m in b.IDX}}; null_all = []
for s in SUBJ:
    _, tc = load(s); ev = events(tc)                                     # (T-1, 94)
    g = b.bandpass(tc.mean(0, keepdims=True), 0.01, 0.03)[0][1:]; ph = np.angle(hilbert(g))
    plv = np.array([np.abs(np.exp(1j * ph[ev[:, i]]).mean()) if ev[:, i].sum() > 3 else np.nan for i in range(94)])
    shifts = rng.integers(50, len(ph) - 50, 200)
    null = np.nanmean([[np.abs(np.exp(1j * np.roll(ph, k)[ev[:, i]]).mean()) for i in range(94)] for k in shifts], 1)
    res["all"].append(np.nanmean(plv)); null_all.append((null.mean(), np.percentile(null, 95)))
    for m, idx in b.IDX.items(): res[m].append(np.nanmean(plv[idx]))
nm = np.mean(null_all, 0)
print(f"mean PLV of regional events to global slow phase: {np.mean(res['all']):.3f}  (null mean {nm[0]:.3f}, null 95% {nm[1]:.3f})")
for m in b.IDX: print(f"  {m:<4} {np.mean(res[m]):.3f}")

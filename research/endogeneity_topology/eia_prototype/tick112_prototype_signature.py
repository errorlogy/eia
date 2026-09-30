"""Tick 112: A26 signature of the three drives in the calibrated prototype engine (tick 60 targets + tick 62 subcritical,
gain 0.4, burst 0.15) vs the uncalibrated near-critical engine (gain 1.0). Fixed moderate tension on all drives (0.5).
out = drop of the other drives' activity when a drive is silenced; indep = the drive's activity kept when the other drives'
input to it is cut. 5 seeds, 3000 steps."""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))
from population_drives import DRIVES, PopulationParams
from tick60_target_uncertainty import TargetEngine

def run(eng, T=3000, silent=None, cut_to=None):
    if cut_to is not None:
        m = eng.label == cut_to; W = eng.W.copy(); W[np.ix_(m, ~m)] = 0; eng.W = W
    acts = []
    for _ in range(T):
        per = eng.step(np.array([0.5, 0.5, 0.5]))
        if silent is not None:
            k = eng.label == silent; eng.state.s[k] = 0; eng.state.d[k] = 0; per[silent] = 0
        acts.append(per)
    return np.array(acts)[500:]

TargetEngine.aging_k = 0.05
print(f"{'engine':<18}{'drive':<11}{'out':>7}{'indep':>7}{'activity':>10}")
for name, gain in (("calibrated (0.4)", 0.4), ("near-critical (1.0)", 1.0)):
    for i, dk in enumerate(DRIVES):
        rows = []
        for seed in range(1, 6):
            mk = lambda: TargetEngine(PopulationParams(seed=seed, mu=0.05, alpha=0.2, gain=gain, burst_frac=0.15))
            base = run(mk()); sil = run(mk(), silent=i); cut = run(mk(), cut_to=i)
            others = [j for j in range(3) if j != i]
            rows.append((1 - sil[:, others].mean() / max(base[:, others].mean(), 1e-9), cut[:, i].mean() / max(base[:, i].mean(), 1e-9), base[:, i].mean()))
        m = np.mean(rows, 0); print(f"{name:<18}{dk.value:<11}{m[0]:>7.2f}{m[1]:>7.2f}{m[2]:>10.3f}", flush=True)

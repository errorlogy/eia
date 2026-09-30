"""Tick 131: does the recommended prototype engine (v3: tension-set targets, gain 0.4, mu 0.15) have a slow internal
envelope (A37)? Fixed tension 0.5 on all drives, 20000 steps; per-drive and total activity: burst CV and autocorrelation
peak (lag 20-2000). Also near-critical gain 1.0 for comparison. 3 seeds."""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))
from population_drives import PopulationParams
from tick60_target_uncertainty import TargetEngine

def rhythm(x):
    x = x - x.mean(); ac = np.correlate(x, x, "full")[len(x)-1:]; ac /= ac[0]; lag = np.argmax(ac[20:2000]) + 20
    return ac[lag], lag

def cv(x):
    th = np.percentile(x, 90); ev = np.flatnonzero((x[1:] > th) & (x[:-1] <= th)); isi = np.diff(ev)
    return isi.std() / isi.mean() if len(isi) > 2 else np.nan

TargetEngine.aging_k = 0.05
print(f"{'engine':<20}{'burst CV':>9}{'autocorr peak':>15}{'period':>8}")
for name, gain in (("v3 (gain 0.4)", 0.4), ("near-critical (1.0)", 1.0)):
    rows = []
    for seed in (1, 2, 3):
        eng = TargetEngine(PopulationParams(seed=seed, mu=0.15, alpha=0.2, gain=gain, burst_frac=0.15))
        x = np.array([eng.step(np.array([0.5, 0.5, 0.5])) for _ in range(20000)])[1000:].sum(1)
        x = np.convolve(x, np.ones(10) / 10, "valid")          # 10-step smoothing (inner-step scale)
        pk, per = rhythm(x); rows.append((cv(x), pk, per))
    m = np.mean(rows, 0); print(f"{name:<20}{m[0]:>9.2f}{m[1]:>15.2f}{m[2]:>8.0f}", flush=True)

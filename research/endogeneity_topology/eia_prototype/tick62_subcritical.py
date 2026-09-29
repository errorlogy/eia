"""Tick 62: restore between-drive discriminability by making each motive subcritical (lower recurrent gain),
so activity follows the motive's own uncertainty target instead of recurrent amplification.
TargetEngine (tick 60, aging_k 0.05, alpha 0.2); gain in {1.0, 0.7, 0.4}. Metrics: within-scenario Spearman
between drive tension and intensity (averaged over scenarios), first-initiative agreement, silent burst CV."""
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr
import tick30_pipeline as h
from population_drives import PopulationParams
from tick60_target_uncertainty import TargetAdapter, TargetEngine

TargetEngine.aging_k = 0.05
h.use_population(False)
ref = {}
for sp in h.SCENARIOS:
    r = h.pl.run_scenario(sp, traces_dir=Path("_traces"), seed=100)
    ref[sp.stem] = (r["initiative"].candidate.kind.value, r["initiative"].candidate.target_belief_id)
print(f"{'gain':>5}{'burst_frac':>11}{'within-scen rho':>16}{'1st same':>10}{'silent CV':>10}{'events':>8}")
for gain in (1.0, 0.7, 0.4):
    for bf in (0.05, 0.15):
        rhos, same = [], []
        for sp in h.SCENARIOS:
            for seed in (1, 2, 3):
                h.use_population(True); h.pl.DriveEngine = TargetAdapter
                TargetAdapter.params = PopulationParams(seed=seed, mu=0.05, alpha=0.2, gain=gain, burst_frac=bf)
                r = h.pl.run_scenario(sp, traces_dir=Path("_traces"), seed=100)
                t = [s.error_term for s in r["motivation"].signals]; i = [s.intensity for s in r["motivation"].signals]
                if len(set(t)) > 1 and len(set(i)) > 1:
                    rhos.append(spearmanr(t, i)[0])
                same.append((r["initiative"].candidate.kind.value, r["initiative"].candidate.target_belief_id) == ref[sp.stem])
        h.use_population(False)
        eng = TargetEngine(PopulationParams(seed=7, mu=0.05, alpha=0.2, gain=gain, burst_frac=bf)); ev = []
        for tt in range(3000):
            if (eng.step(np.array([0.5, 0.5, 0.5])) >= bf).any(): ev.append(tt)
        isi = np.diff(ev); cv = isi.std() / isi.mean() if len(isi) > 2 else float("nan")
        print(f"{gain:>5}{bf:>11}{np.mean(rhos):>16.2f}{np.mean(same):>10.2f}{cv:>10.2f}{len(ev):>8}", flush=True)

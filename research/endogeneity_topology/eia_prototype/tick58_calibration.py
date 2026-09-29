"""Tick 58: why the proposed system changes eval initiatives (tick 57, twin_world_003): population drive intensity
is dominated by intrinsic dynamics, weakly tied to BeliefField tension (e.g. commitment tension 0.14 -> intensity
0.73-0.84, crossing the 0.2 gate). Sweep ext_gain; measure Spearman corr(tension, intensity) across drives and
agreement of the first initiative with the current pipeline. 7 scenarios x 3 seeds."""
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr
import tick30_pipeline as h
from population_drives import PopulationParams

ref = {}
h.use_population(False)
for sp in h.SCENARIOS:
    r = h.pl.run_scenario(sp, traces_dir=Path("_traces"), seed=100)
    ref[sp.stem] = (r["initiative"].candidate.kind.value, r["initiative"].candidate.target_belief_id)
print(f"{'ext_gain':>9}{'corr(tension,intensity)':>25}{'1st initiative same':>21}{'mean intensity':>16}")
for g in (0.02, 0.1, 0.3, 1.0):
    ten, inten, same = [], [], []
    for sp in h.SCENARIOS:
        for seed in (1, 2, 3):
            h.use_population(True); h.PopDriveAdapter.params = PopulationParams(seed=seed, mu=0.05, ext_gain=g)
            r = h.pl.run_scenario(sp, traces_dir=Path("_traces"), seed=100)
            for s in r["motivation"].signals:
                ten.append(s.error_term); inten.append(s.intensity)
            same.append((r["initiative"].candidate.kind.value, r["initiative"].candidate.target_belief_id) == ref[sp.stem])
    h.use_population(False)
    print(f"{g:>9}{spearmanr(ten, inten)[0]:>25.2f}{np.mean(same):>21.2f}{np.mean(inten):>16.2f}", flush=True)

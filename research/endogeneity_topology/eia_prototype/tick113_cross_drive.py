"""Tick 113: inter-motive interaction in the calibrated prototype. Cross-drive mixing mu in {0.05, 0.15, 0.30}.
(1) interaction: raise ONLY coherence tension 0.2 -> 0.8 (others 0.2); change in epistemic activity (should be ~0 at mu 0.05).
(2) eval compatibility: first-initiative agreement with the current pipeline over 7 scenarios x 3 seeds (tick 62 setup)."""
from pathlib import Path
import numpy as np
import tick30_pipeline as h
from population_drives import PopulationParams
from tick60_target_uncertainty import TargetAdapter, TargetEngine

TargetEngine.aging_k = 0.05
def epi_response(mu, seed):
    act = []
    for coh in (0.2, 0.8):
        eng = TargetEngine(PopulationParams(seed=seed, mu=mu, alpha=0.2, gain=0.4, burst_frac=0.15))
        a = np.array([eng.step(np.array([0.2, coh, 0.2])) for _ in range(3000)])[500:]
        act.append(a[:, 0].mean())
    return (act[1] - act[0]) / act[0]

h.use_population(False); ref = {}
for sp in h.SCENARIOS:
    r = h.pl.run_scenario(sp, traces_dir=Path("_traces"), seed=100); ref[sp.stem] = (r["initiative"].candidate.kind.value, r["initiative"].candidate.target_belief_id)
print(f"{'mu':>5}{'epistemic response to coherence tension':>42}{'1st initiative same':>21}")
for mu in (0.05, 0.15, 0.30):
    resp = np.mean([epi_response(mu, s) for s in range(1, 6)])
    same = []
    for sp in h.SCENARIOS:
        for seed in (1, 2, 3):
            h.use_population(True); h.pl.DriveEngine = TargetAdapter
            TargetAdapter.params = PopulationParams(seed=seed, mu=mu, alpha=0.2, gain=0.4, burst_frac=0.15)
            r = h.pl.run_scenario(sp, traces_dir=Path("_traces"), seed=100)
            same.append((r["initiative"].candidate.kind.value, r["initiative"].candidate.target_belief_id) == ref[sp.stem])
    h.use_population(False)
    print(f"{mu:>5}{resp:>+42.2f}{np.mean(same):>21.2f}", flush=True)

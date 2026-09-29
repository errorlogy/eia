"""Tick 59: evoked-minus-spontaneous readout for the population engine.
At construction, each motive's spontaneous activity is measured on a copy of the engine with zero tension
(1000 steps). Intensity = clip((recent activity - spontaneous) / (scale * spontaneous), 0, 1). Intrinsic dynamics
still set *timing*, tension sets *level*. Sweep scale and ext_gain; metrics as tick 58."""

from __future__ import annotations

import copy
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

import tick30_pipeline as h
from population_drives import PopulationParams


class RelAdapter(h.PopDriveAdapter):
    scale = 2.0

    def __init__(self) -> None:
        super().__init__()
        probe = copy.deepcopy(self.engine)
        hist = np.array([probe.step(np.zeros(3)) for _ in range(1000)])
        self.spont = np.maximum(hist[200:].mean(0), 1e-4)

    def compute(self, field, *, novelty_events=None, satisfaction=None, motivation_id="mot-0"):
        m = super().compute(field, novelty_events=novelty_events, satisfaction=satisfaction, motivation_id=motivation_id)
        recent = np.array(self.engine.state.history[-self.engine.p.window:]).mean(0)
        rel = np.clip((recent - self.spont) / (self.scale * self.spont), 0, 1)
        sigs = [s.model_copy(update={"intensity": float(rel[i]),
                                     "explanation": s.explanation + f"; evoked-minus-spontaneous {rel[i]:.2f}"})
                for i, s in enumerate(m.signals)]
        dom = max(sigs, key=lambda s_: s_.intensity)
        self.state.epistemic, self.state.coherence, self.state.commitment = (s.intensity for s in sigs)
        return m.model_copy(update={"signals": sigs, "dominant_drive": dom.drive if dom.intensity > 0 else None})


if __name__ == "__main__":
    ref = {}
    h.use_population(False)
    for sp in h.SCENARIOS:
        r = h.pl.run_scenario(sp, traces_dir=Path("_traces"), seed=100)
        ref[sp.stem] = (r["initiative"].candidate.kind.value, r["initiative"].candidate.target_belief_id)
    print(f"{'ext_gain':>9}{'scale':>7}{'corr':>7}{'1st same':>10}{'mean int.':>10}")
    for g in (0.1, 0.3):
        for sc in (1.0, 3.0, 10.0):
            ten, inten, same = [], [], []
            for sp in h.SCENARIOS:
                for seed in (1, 2, 3):
                    h.use_population(True)
                    h.pl.DriveEngine = RelAdapter
                    RelAdapter.params = PopulationParams(seed=seed, mu=0.05, ext_gain=g); RelAdapter.scale = sc
                    r = h.pl.run_scenario(sp, traces_dir=Path("_traces"), seed=100)
                    for s in r["motivation"].signals:
                        ten.append(s.error_term); inten.append(s.intensity)
                    same.append((r["initiative"].candidate.kind.value, r["initiative"].candidate.target_belief_id) == ref[sp.stem])
            h.use_population(False)
            print(f"{g:>9}{sc:>7}{spearmanr(ten, inten)[0]:>7.2f}{np.mean(same):>10.2f}{np.mean(inten):>10.2f}", flush=True)

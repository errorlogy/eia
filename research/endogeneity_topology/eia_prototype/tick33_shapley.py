"""Tick 33: Shapley attribution of the initiative to drives, all scenarios, three intervention modes.
v(S) = P(initiative signature changes | do(silence drives in S)), from the post-cognition snapshot.
  baseline-weak    zero DriveState scalars (tick 31/32; compute re-derives from gradient)
  baseline-strong  zero scalars AND block the field gradient into silenced drives during compute
  population       silence motive populations for the whole compute (4 noise draws)
Exact Shapley for 3 players; v(all) = total causal dependence of the initiative on drive state."""

from __future__ import annotations

import copy
import itertools
from math import factorial
from pathlib import Path

import numpy as np

import tick30_pipeline as h
from eia.beliefs import BeliefField
from eia.intention import IntentionGenesis
from population_drives import DRIVES, PopulationParams

DRAWS = 4
KEY = {"epistemic": "epistemic", "coherence": "coherence", "commitment": "commitment"}


def signature(ini):
    c = ini.candidate
    return (ini.abstained, c.kind.value if c else None, c.target_belief_id if c else None)


def compute_silenced(drives, field, ks, mode, draw):
    eng = copy.deepcopy(drives)
    names = {k.value for k in ks}
    if mode == "population":
        eng.engine.rng = np.random.default_rng(1000 + draw)
        sil = [DRIVES.index(k) for k in ks]; e = eng.engine
        for i in sil:
            m = e.label == i; e.state.u[m] = 0; e.state.d[m] = 0
        e.state.history = [np.where(np.isin(np.arange(3), sil), 0.0, x) for x in e.state.history]
        orig = type(e).step

        def st(self, ext=None, boost=None):
            per = orig(self, ext, boost)
            for i in sil:
                m = self.label == i; self.state.u[m] = 0; self.state.d[m] = 0; self.state.s[m] = 0; per[i] = 0
            self.state.history[-1] = per
            return per
        e.step = st.__get__(e)
        return eng.compute(field, motivation_id="mot-do")
    for n in names:
        setattr(eng.state, n, 0.0)
    if mode == "baseline-strong" and names:
        orig_g = BeliefField.gradient_snapshot
        BeliefField.gradient_snapshot = lambda self: {k: (0.0 if k in names else v) for k, v in orig_g(self).items()}
        try:
            return eng.compute(field, motivation_id="mot-do")
        finally:
            BeliefField.gradient_snapshot = orig_g
    return eng.compute(field, motivation_id="mot-do")


def value_fn(loop, mode):
    drives = loop._drives_at_snapshot if mode == "population" else loop.drives
    draws = range(DRAWS) if mode == "population" else range(1)
    ig = IntentionGenesis(abstain_threshold=0.30, min_evsi=0.12)

    def sig(ks, d):
        f = BeliefField.model_validate(loop._snapshot_field.model_dump())
        return signature(ig.best_or_abstain(compute_silenced(drives, f, ks, mode, d), f))
    ref = {d: sig([], d) for d in draws}
    return {S: float(np.mean([sig(list(S), d) != ref[d] for d in draws]))
            for n in range(4) for S in itertools.combinations(DRIVES, n)}


def shapley(v):
    n = 3; phi = {}
    for i in DRIVES:
        tot = 0.0
        for r in range(n):
            for S in itertools.combinations([d for d in DRIVES if d != i], r):
                S_i = tuple(sorted(S + (i,), key=DRIVES.index))
                tot += factorial(r) * factorial(n - r - 1) / factorial(n) * (v[S_i] - v[tuple(sorted(S, key=DRIVES.index))])
        phi[i.value] = tot
    return phi


if __name__ == "__main__":
    print(f"{'scenario':<21}{'mode':<17}{'src':<11}{'phi_e':>7}{'phi_c':>7}{'phi_m':>7}{'v(all)':>8}")
    summary = {m: [] for m in ("baseline-weak", "baseline-strong", "population")}
    for sp in h.SCENARIOS:
        for mode in summary:
            pop = mode == "population"
            h.use_population(pop)
            if pop:
                h.PopDriveAdapter.params = PopulationParams(seed=0, mu=0.05, ext_gain=0.02)
            r = h.pl.run_scenario(sp, traces_dir=Path(h.__file__).parent / "_traces", seed=100)
            ini = r["initiative"]; src = ",".join(d.value[:4] for d in (ini.candidate.source_drives if ini.candidate else []))
            v = value_fn(r["loop"], mode); phi = shapley(v); vall = v[tuple(DRIVES)]
            summary[mode].append((vall, phi))
            print(f"{sp.stem:<21}{mode:<17}{src:<11}{phi['epistemic']:>7.2f}{phi['coherence']:>7.2f}{phi['commitment']:>7.2f}{vall:>8.2f}")
    h.use_population(False)
    print("\nmean v(all) (initiative depends on drive state at all):")
    for m, rows in summary.items():
        print(f"  {m:<16} {np.mean([x[0] for x in rows]):.2f}   scenarios with v(all)>0: {sum(x[0] > 0 for x in rows)}/{len(rows)}")

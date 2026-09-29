"""Tick 31: a causal replacement for AuthenticReason's lexical 'structural drive' check.

Test: from the post-cognition snapshot (drive engine + belief field), re-run MotiveFormation →
IntentionGenesis with do(Z_k) = silence drive k's internal state, for each drive k. A drive is
*causally structural* for the initiative if silencing it changes the initiative (kind / target /
abstain) — and specificity requires that silencing drives NOT in source_drives changes it less.
Population engine: 8 noise re-draws per condition → P(change). Baseline DriveEngine: deterministic.
"""

from __future__ import annotations

import copy
from pathlib import Path

import numpy as np

import tick30_pipeline as h  # sets sys.path, provides adapter + patching
from eia.intention import IntentionGenesis
from eia.schemas.motivation import DriveKind
from population_drives import DRIVES, PopulationParams

DRAWS = 8


def signature(ini):
    c = ini.candidate
    return (ini.abstained, c.kind.value if c else None, c.target_belief_id if c else None)


def silence(eng, k: DriveKind, population: bool):
    if population:
        e = eng.engine; m = e.label == DRIVES.index(k)
        e.state.u[m] = 0.0; e.state.d[m] = 0.0; e.p = copy.copy(e.p)
        e.state.history = [np.where(np.arange(3) == DRIVES.index(k), 0.0, x) for x in e.state.history]
        # keep motive silent for this compute: block its uncertainty input
        e._silenced = DRIVES.index(k)
    else:
        setattr(eng.state, k.value, 0.0)


def run_once(drives, field, k, population, draw):
    eng = copy.deepcopy(drives)
    if population:
        eng.engine.rng = np.random.default_rng(1000 + draw)
    if k is not None:
        silence(eng, k, population)
    f = h.pl.BeliefField.model_validate(field.model_dump())
    m = eng.compute(f, motivation_id="mot-do")
    return signature(IntentionGenesis(abstain_threshold=0.30, min_evsi=0.12).best_or_abstain(m, f)), m


def gate(loop, population):
    drives = loop._drives_at_snapshot if population else loop.drives
    field = loop._snapshot_field
    draws = range(DRAWS) if population else range(1)
    refs = [run_once(drives, field, None, population, d) for d in draws]
    ref_sig = [r[0] for r in refs]
    out = {}
    for k in DRIVES:
        ch = [run_once(drives, field, k, population, d)[0] != ref_sig[i] for i, d in enumerate(draws)]
        out[k.value] = float(np.mean(ch))
    return out


# PopulationDriveEngine: honour the silenced motive during the do() compute
_orig_step = h.PopulationDriveEngine.step


def _step(self, ext=None, boost=None):
    per = _orig_step(self, ext, boost)
    k = getattr(self, "_silenced", None)
    if k is not None:
        m = self.label == k
        self.state.u[m] = 0.0; self.state.d[m] = 0.0; self.state.s[m] = 0.0
        per[k] = 0.0; self.state.history[-1] = per
    return per


h.PopulationDriveEngine.step = _step

if __name__ == "__main__":
    print(f"{'scenario':<22}{'engine':<11}{'source_drives':<26}" + "".join(f"{'do('+k.value[:5]+')':>11}" for k in DRIVES) + "   verdict")
    for sp in h.SCENARIOS:
        for population in (False, True):
            h.use_population(population)
            if population:
                h.PopDriveAdapter.params = PopulationParams(seed=0, mu=0.05, ext_gain=0.02)
            r = h.pl.run_scenario(sp, traces_dir=Path(h.__file__).parent / "_traces", seed=100)
            loop, ini = r["loop"], r["initiative"]
            src = [d.value for d in (ini.candidate.source_drives if ini.candidate else [])]
            ch = gate(loop, population)
            s_eff = max((ch[d] for d in src), default=0.0)
            n_eff = max((v for k_, v in ch.items() if k_ not in src), default=0.0)
            verdict = "causal+specific" if s_eff >= 0.5 and s_eff > n_eff else ("causal, unspecific" if s_eff >= 0.5 else "NOT causal")
            print(f"{sp.stem:<22}{'population' if population else 'baseline':<11}{','.join(src):<26}"
                  + "".join(f"{ch[k.value]:>11.2f}" for k in DRIVES) + f"   {verdict}")
    h.use_population(False)

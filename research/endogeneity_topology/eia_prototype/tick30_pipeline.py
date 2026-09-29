"""Tick 30: PopulationDriveEngine inside the MVP-0 pipeline (no src/ changes — monkeypatched harness).

Adapter: each pipeline cognition tick = INNER internal steps of the population engine; readout is the
standard Motivation; `.state` mirrors DriveState scalars for AgentState / shadow code.
Twin: exact deep copy of the population engine (incl. RNG) at twin time, mirroring the original
semantics (twin re-runs one compute on the snapshot field).
Compare on 7 scenarios: baseline DriveEngine vs population engine (5 engine seeds each).
"""

from __future__ import annotations

import copy
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import eia.pipeline as pl  # noqa: E402
from eia.drives import DriveEngine, DriveState  # noqa: E402
from population_drives import PopulationDriveEngine, PopulationParams  # noqa: E402

INNER = 40
_ORIG_DRIVE_ENGINE = pl.DriveEngine
_ORIG_RUN_TWIN = pl.CognitiveLoop.run_twin


class PopDriveAdapter:
    params = PopulationParams()

    def __init__(self) -> None:
        self.engine = PopulationDriveEngine(copy.deepcopy(self.params))
        self.state = DriveState()

    def compute(self, field, *, novelty_events=None, satisfaction=None, motivation_id="mot-0"):
        for _ in range(INNER - 1):
            grads = field.gradient_snapshot()
            self.engine.step(np.array([grads["epistemic"], grads["coherence"], grads["commitment"]]))
        m = self.engine.compute(field, motivation_id=motivation_id)
        self.state.epistemic, self.state.coherence, self.state.commitment = (s.intensity for s in m.signals)
        self.state.tick += 1
        return m


def _pop_run_twin(self, removed_event_ids, sim):
    twin_field = pl.BeliefField.model_validate(self._snapshot_field.model_dump())
    twin_drives = copy.deepcopy(self._drives_at_snapshot)
    twin_intention = pl.IntentionGenesis(abstain_threshold=0.30, min_evsi=0.12)
    twin_gov = pl.ContactGovernor()
    twin_gov.state = pl.GovernorState(current_tick=sim.clock.tick, hour=sim.clock.hour)
    motivation = twin_drives.compute(twin_field, motivation_id="mot-twin")
    initiative = twin_intention.best_or_abstain(motivation, twin_field)
    return motivation, initiative, twin_gov.evaluate(initiative)


_ORIG_TICK = pl.CognitiveLoop.tick_cognition


def _tick_with_snapshot(self, **kw):
    out = _ORIG_TICK(self, **kw)
    self._drives_at_snapshot = copy.deepcopy(self.drives)
    return out


def use_population(on: bool) -> None:
    pl.DriveEngine = PopDriveAdapter if on else _ORIG_DRIVE_ENGINE
    pl.CognitiveLoop.run_twin = _pop_run_twin if on else _ORIG_RUN_TWIN
    pl.CognitiveLoop.tick_cognition = _tick_with_snapshot if on else _ORIG_TICK


SCENARIOS = sorted((ROOT / "evals").glob("twin_world_*.yaml")) + [
    ROOT / "scenarios" / "twin_world_001.yaml", ROOT / "scenarios" / "autonomous_question.yaml"]


def run(path, seed):
    r = pl.run_scenario(path, traces_dir=Path(__file__).parent / "_traces", seed=seed)
    ini = r["initiative"]
    return dict(eoi=r["twin_result"].eoi, kind=ini.candidate.kind.value if ini.candidate else None,
                abstained=ini.abstained, contact=r["decision"].outcome.value,
                cls=r["authentic_verdict"].initiative_class,
                intens=[round(s.intensity, 2) for s in r["motivation"].signals] if r.get("motivation") else None)


if __name__ == "__main__":
    rows = []
    print(f"{'scenario':<22}{'engine':<12}{'EOI':>6}  {'kind (counts)':<34}{'contact':<22}{'class':<22}")
    for sp in SCENARIOS:
        use_population(False)
        b = run(sp, 100)
        print(f"{sp.stem:<22}{'baseline':<12}{b['eoi']:>6.2f}  {str(b['kind']):<34}{b['contact']:<22}{b['cls']:<22}")
        use_population(True)
        pops = []
        for s in range(5):
            PopDriveAdapter.params = PopulationParams(seed=s, mu=0.05, ext_gain=0.02)
            pops.append(run(sp, 100))
        kinds = Counter(p["kind"] if not p["abstained"] else "abstain" for p in pops)
        contacts = Counter(p["contact"] for p in pops); classes = Counter(p["cls"] for p in pops)
        print(f"{'':<22}{'population':<12}{np.mean([p['eoi'] for p in pops]):>6.2f}  {str(dict(kinds)):<34}{str(dict(contacts)):<22}{str(dict(classes)):<22}")
        rows.append((sp.stem, b, pops))
    use_population(False)
    be = np.mean([b["eoi"] for _, b, _ in rows]); pe = np.mean([p["eoi"] for _, _, ps in rows for p in ps])
    bend = np.mean([b["cls"] == "endogenous" for _, b, _ in rows]); pend = np.mean([p["cls"] == "endogenous" for _, _, ps in rows for p in ps])
    div = np.mean([len({(p["kind"], p["abstained"]) for p in ps}) > 1 for _, _, ps in rows])
    print(f"\nmean EOI baseline {be:.2f} | population {pe:.2f};  endogenous class baseline {bend:.2f} | population {pend:.2f}")
    print(f"scenarios where population engine seeds disagree on initiative: {div:.0%}")

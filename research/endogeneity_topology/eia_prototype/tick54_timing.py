"""Tick 54: timing of initiative in the full closed architecture. 200 silent episodes with the tick-53 environment
(closed loop + aging) and IOR, for baseline DriveEngine vs PopulationDriveEngine. Is the sequence of 'ask'
episodes clock-like (CV of intervals ~0) or endogenous-bursty (CV ~1 or more)? Also: how many distinct targets
over the run, and whether the agent ever falls silent (abstain) on its own."""

from __future__ import annotations

from pathlib import Path

import numpy as np

import tick30_pipeline as h
from eia.intention import IntentionGenesis
from population_drives import PopulationParams
from tick52_closed_loop import age, sharpen
from tick53_intention_loop import _ORIG_BEST, make_best

EP = 200


def run(scenario, engine, seed):
    h.use_population(engine == "population")
    if engine == "population":
        h.PopDriveAdapter.params = PopulationParams(seed=seed, mu=0.05, ext_gain=0.02)
    IntentionGenesis.best_or_abstain = _ORIG_BEST
    r = h.pl.run_scenario(scenario, traces_dir=Path(h.__file__).parent / "_traces", seed=100)
    loop = r["loop"]; rng = np.random.default_rng(seed); state = {"penalty": {}}
    IntentionGenesis.best_or_abstain = make_best(state, "IOR", rng)
    asks, targets, abstain = [], set(), 0
    for e in range(EP):
        _, ini, dec, _ = loop.tick_cognition(tick=100 + e, hour=14, finalize=True)
        tgt = ini.candidate.target_belief_id if (ini.candidate and not ini.abstained and ini.candidate.kind.value == "ask_question") else None
        abstain += int(ini.abstained)
        state["penalty"] = {k: v * 0.8 for k, v in state["penalty"].items()}
        if tgt:
            asks.append(e); targets.add(tgt); state["penalty"][tgt] = state["penalty"].get(tgt, 0.0) + 1.0
        if dec is not None and dec.outcome.value == "send_now" and tgt and rng.random() < 0.7:
            b = loop.field.beliefs.get(tgt)
            if b is not None:
                sharpen(b, 0.4)
        age(loop.field)
    IntentionGenesis.best_or_abstain = _ORIG_BEST
    h.use_population(False)
    isi = np.diff(asks)
    return dict(asks=len(asks), cv=float(isi.std() / isi.mean()) if len(isi) > 2 else float("nan"),
                distinct=len(targets), abstain=abstain / EP)


if __name__ == "__main__":
    scen = [s for s in h.SCENARIOS if s.stem in ("twin_world_001", "twin_world_003", "twin_world_005", "autonomous_question")]
    print(f"{'scenario':<21}{'engine':<11}{'asks':>6}{'ISI CV':>8}{'distinct':>9}{'abstain':>8}")
    agg = {}
    for sp in scen:
        for eng in ("baseline", "population"):
            rs = [run(sp, eng, s) for s in (1, 2)]
            m = {k: float(np.nanmean([x[k] for x in rs])) for k in rs[0]}
            agg.setdefault(eng, []).append(m)
            print(f"{sp.stem:<21}{eng:<11}{m['asks']:>6.0f}{m['cv']:>8.2f}{m['distinct']:>9.1f}{m['abstain']:>8.2f}", flush=True)
    print("\nmeans:")
    for eng, rows in agg.items():
        print(f"  {eng:<11}" + "  ".join(f"{k} {np.nanmean([r[k] for r in rows]):.2f}" for k in rows[0]))

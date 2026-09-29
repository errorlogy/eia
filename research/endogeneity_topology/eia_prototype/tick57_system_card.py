"""Tick 57: system card — current MVP-0 vs the proposed combination (harness only):
  current   DriveEngine, open loop, no IOR
  proposed  PopulationDriveEngine + closed loop (answers sharpen target) + state-dependent IOR, stochastic staleness
Per scenario: first (eval-scored) initiative, EOI, causal dependence of the initiative on drive state (v(all),
state-only interventions), and 200-episode silent behaviour (asks, longest same-question run, ISI CV). 3 seeds."""

from __future__ import annotations

from pathlib import Path

import numpy as np

import tick30_pipeline as h
from eia.intention import IntentionGenesis
from population_drives import PopulationParams
from tick33_shapley import value_fn
from tick52_closed_loop import age, sharpen
from tick53_intention_loop import _ORIG_BEST
from tick55_state_ior import H, make_state_best

EP = 200


def card(scenario, system, seed):
    pop = system == "proposed"
    h.use_population(pop)
    if pop:
        h.PopDriveAdapter.params = PopulationParams(seed=seed, mu=0.05, ext_gain=0.02)
    IntentionGenesis.best_or_abstain = _ORIG_BEST
    r = h.pl.run_scenario(scenario, traces_dir=Path(h.__file__).parent / "_traces", seed=100)
    first = (r["initiative"].candidate.kind.value, r["initiative"].candidate.target_belief_id)
    eoi = r["twin_result"].eoi
    v = value_fn(r["loop"], "population" if pop else "baseline-weak")
    vall = max(v.values())
    loop = r["loop"]; rng = np.random.default_rng(seed); asked = {}
    if pop:
        IntentionGenesis.best_or_abstain = make_state_best(asked, rng)
    asks, targets = [], []
    for e in range(EP):
        _, ini, dec, _ = loop.tick_cognition(tick=100 + e, hour=14, finalize=True)
        tgt = ini.candidate.target_belief_id if (ini.candidate and not ini.abstained and ini.candidate.kind.value == "ask_question") else None
        targets.append(tgt)
        if tgt:
            asks.append(e)
            if pop and dec is not None and dec.outcome.value == "send_now" and rng.random() < 0.7 and tgt in loop.field.beliefs:
                sharpen(loop.field.beliefs[tgt], 0.4)
            if tgt in loop.field.beliefs:
                asked[tgt] = H(loop.field.beliefs[tgt])
        if pop and rng.random() < 0.1:
            age(loop.field, 0.3)
    IntentionGenesis.best_or_abstain = _ORIG_BEST
    h.use_population(False)
    run, best, prev = 0, 0, object()
    for t in targets:
        run = run + 1 if (t is not None and t == prev) else (1 if t else 0); prev = t; best = max(best, run)
    isi = np.diff(asks)
    return dict(first=first, eoi=eoi, vall=vall, asks=len(asks), max_run=best,
                cv=float(isi.std() / isi.mean()) if len(isi) > 2 else float("nan"))


if __name__ == "__main__":
    print(f"{'scenario':<21}{'system':<10}{'1st same':>9}{'EOI':>6}{'v(all)':>8}{'asks/200':>9}{'max run':>8}{'ISI CV':>8}")
    agg = {"current": [], "proposed": []}
    for sp in h.SCENARIOS:
        ref = None
        for system in ("current", "proposed"):
            rs = [card(sp, system, s) for s in (1, 2, 3)]
            if system == "current":
                ref = rs[0]["first"]
            m = dict(same=np.mean([x["first"] == ref for x in rs]), eoi=np.mean([x["eoi"] for x in rs]),
                     vall=np.mean([x["vall"] for x in rs]), asks=np.mean([x["asks"] for x in rs]),
                     max_run=np.mean([x["max_run"] for x in rs]), cv=np.nanmean([x["cv"] for x in rs]))
            agg[system].append(m)
            print(f"{sp.stem:<21}{system:<10}{m['same']:>9.2f}{m['eoi']:>6.2f}{m['vall']:>8.2f}{m['asks']:>9.1f}{m['max_run']:>8.1f}{m['cv']:>8.2f}", flush=True)
    print("\nmeans:")
    for system, rows in agg.items():
        print(f"  {system:<9}" + "  ".join(f"{k} {np.nanmean([r[k] for r in rows]):.2f}" for k in rows[0]))

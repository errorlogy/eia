"""Tick 52: proposal 9 demonstrated in a harness (no src/ changes) — close the cognitive loop.
Runs 30 consecutive cognition episodes after a scenario's events, with NO new user input.
  open         current MVP-0 behaviour (DAG per episode)
  closed       after a sent contact, the environment answers with p = 0.7: the targeted belief is sharpened
               (resolution, as RESOLVE in the toy) and the source drive receives satisfaction next tick
  closed+aging closed + slow uncertainty aging of every categorical belief (knowledge goes stale)
Metrics: contacts sent, distinct targets asked, longest run of the same question (perseveration), abstain share."""

from __future__ import annotations

from pathlib import Path

import numpy as np

import tick30_pipeline as h  # sys.path + pipeline module
from eia.schemas.belief import BeliefKind

EPISODES = 30


def sharpen(belief, factor):
    d = belief.distribution
    if not d:
        belief.uncertainty *= factor
        return
    top = max(d, key=d.get)
    rest = 1 - d[top]
    new_rest = rest * factor
    scale = new_rest / rest if rest > 0 else 0
    belief.distribution = {k: (1 - new_rest if k == top else v * scale) for k, v in d.items()}
    belief.uncertainty = max(0.0, belief.uncertainty * factor)


def age(field, rate=0.03):
    for b in field.beliefs.values():
        if b.kind == BeliefKind.CATEGORICAL and b.distribution:
            n = len(b.distribution)
            b.distribution = {k: v * (1 - rate) + rate / n for k, v in b.distribution.items()}
            b.uncertainty = min(1.0, b.uncertainty + rate * (1 - b.uncertainty))


def episode_run(scenario, mode, seed):
    h.use_population(False)
    r = h.pl.run_scenario(scenario, traces_dir=Path(h.__file__).parent / "_traces", seed=seed)
    loop = r["loop"]; rng = np.random.default_rng(seed)
    pending_sat = {}
    orig_compute = loop.drives.compute

    def compute(field, *, novelty_events=None, satisfaction=None, motivation_id="mot-0"):
        sat = dict(pending_sat); pending_sat.clear()
        return orig_compute(field, novelty_events=novelty_events, satisfaction=sat or satisfaction, motivation_id=motivation_id)
    loop.drives.compute = compute

    targets, contacts, abstains = [], 0, 0
    tick0 = 100
    for e in range(EPISODES):
        _, ini, dec, _ = loop.tick_cognition(tick=tick0 + e, hour=14, finalize=True)
        sent = dec is not None and dec.outcome.value == "send_now"
        if ini.abstained or ini.candidate is None or ini.candidate.kind.value in ("abstain", "observe"):
            abstains += 1; targets.append(None)
        else:
            targets.append(ini.candidate.target_belief_id)
        if sent:
            contacts += 1
            if mode != "open" and rng.random() < 0.7:
                b = loop.field.beliefs.get(ini.candidate.target_belief_id)
                if b is not None:
                    sharpen(b, 0.4)
                    if b.metadata.get("status") == "open" and b.kind == BeliefKind.COMMITMENT:
                        b.metadata["status"] = "progressed" if rng.random() < 0.5 else "open"
                for d in ini.candidate.source_drives:
                    pending_sat[d] = 1.0
        if mode == "closed+aging":
            age(loop.field)
    runs, cur, prev = [], 0, object()
    for t in targets:
        cur = cur + 1 if (t == prev and t is not None) else 1
        prev = t; runs.append(cur if t is not None else 0)
    return dict(contacts=contacts, distinct=len({t for t in targets if t}), max_run=max(runs), abstain=abstains / EPISODES)


if __name__ == "__main__":
    scen = [s for s in h.SCENARIOS if s.stem in ("twin_world_001", "twin_world_002", "autonomous_question", "twin_world_004")]
    print(f"{'scenario':<21}{'mode':<14}{'contacts':>9}{'distinct':>9}{'max run':>8}{'abstain':>8}")
    agg = {}
    for sp in scen:
        for mode in ("open", "closed", "closed+aging"):
            rs = [episode_run(sp, mode, s) for s in (100, 101, 102)]
            m = {k: float(np.mean([x[k] for x in rs])) for k in rs[0]}
            agg.setdefault(mode, []).append(m)
            print(f"{sp.stem:<21}{mode:<14}{m['contacts']:>9.1f}{m['distinct']:>9.1f}{m['max_run']:>8.1f}{m['abstain']:>8.2f}", flush=True)
    print("\nmeans:")
    for mode, rows in agg.items():
        print(f"  {mode:<14}" + "  ".join(f"{k} {np.mean([r[k] for r in rows]):.2f}" for k in rows[0]))

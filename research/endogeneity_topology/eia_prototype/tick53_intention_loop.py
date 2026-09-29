"""Tick 53: close the loop *through intention selection* (harness, no src/ changes) — fixes for C9.
  IOR       inhibition of return: a target that was denied or asked gets a penalty that decays (x0.8/episode);
            candidates whose penalty > 0.5 are skipped
  IOR+drive IOR + drive-weighted choice among remaining candidates (softmax over intensity x info, T = 0.1)
Combined with the tick-52 'closed+aging' environment. Metrics as tick 52 + first-episode agreement with the
unmodified pipeline (the G2 eval initiative must stay the same)."""

from __future__ import annotations

from pathlib import Path

import numpy as np

import tick30_pipeline as h
from eia.intention import IntentionGenesis
from eia.schemas.initiative import InitiativeKind
from tick52_closed_loop import EPISODES, age, sharpen
from eia.schemas.belief import BeliefKind

_ORIG_BEST = IntentionGenesis.best_or_abstain


def make_best(state, mode, rng):
    def best(self, motivation, field):
        base = _ORIG_BEST(self, motivation, field)
        if base.abstained or base.candidate is None:
            return base
        cands = [c for c in self.generate_candidates(motivation, field)
                 if c.kind not in (InitiativeKind.ABSTAIN, InitiativeKind.OBSERVE)]
        ok = [c for c in cands if state["penalty"].get(c.target_belief_id, 0.0) <= 0.5]
        if not ok:
            obs = next(c for c in self.generate_candidates(motivation, field) if c.kind == InitiativeKind.OBSERVE)
            return base.model_copy(update={"candidate": obs, "abstained": False})
        if mode == "IOR":
            pick = max(ok, key=lambda c: c.lex_score)
        else:
            inten = {s.drive: s.intensity for s in motivation.signals}
            score = np.array([max(inten.get(d, 0) for d in c.source_drives or [None]) * (c.expected_info_gain + 1e-3) for c in ok])
            p = np.exp((score - score.max()) / 0.1); p /= p.sum()
            pick = ok[int(rng.choice(len(ok), p=p))]
        return base.model_copy(update={"candidate": pick})
    return best


def run(scenario, mode, seed):
    h.use_population(False)
    IntentionGenesis.best_or_abstain = _ORIG_BEST
    r = h.pl.run_scenario(scenario, traces_dir=Path(h.__file__).parent / "_traces", seed=seed)
    first_ref = (r["initiative"].candidate.kind.value, r["initiative"].candidate.target_belief_id)
    loop = r["loop"]; rng = np.random.default_rng(seed); state = {"penalty": {}}
    if mode != "baseline":
        IntentionGenesis.best_or_abstain = make_best(state, mode, rng)
    targets, contacts, first = [], 0, None
    for e in range(EPISODES):
        _, ini, dec, _ = loop.tick_cognition(tick=100 + e, hour=14, finalize=True)
        tgt = ini.candidate.target_belief_id if (ini.candidate and not ini.abstained and ini.candidate.kind.value == "ask_question") else None
        if e == 0:
            first = (ini.candidate.kind.value, ini.candidate.target_belief_id)
        targets.append(tgt)
        state["penalty"] = {k: v * 0.8 for k, v in state["penalty"].items()}
        if tgt:
            state["penalty"][tgt] = state["penalty"].get(tgt, 0.0) + 1.0
        if dec is not None and dec.outcome.value == "send_now":
            contacts += 1
            if rng.random() < 0.7 and tgt:
                b = loop.field.beliefs.get(tgt)
                if b is not None:
                    sharpen(b, 0.4)
        age(loop.field)
    IntentionGenesis.best_or_abstain = _ORIG_BEST
    runs, cur, prev = [], 0, object()
    for t in targets:
        cur = cur + 1 if (t == prev and t is not None) else 1
        prev = t; runs.append(cur if t else 0)
    return dict(contacts=contacts, distinct=len({t for t in targets if t}), max_run=max(runs),
                asked=sum(t is not None for t in targets) / EPISODES, first_same=float(first == first_ref))


if __name__ == "__main__":
    print(f"{'scenario':<21}{'mode':<11}{'contacts':>9}{'distinct':>9}{'max run':>8}{'asked':>7}{'1st=ref':>8}")
    agg = {}
    for sp in h.SCENARIOS:
        for mode in ("baseline", "IOR", "IOR+drive"):
            rs = [run(sp, mode, s) for s in (100, 101, 102)]
            m = {k: float(np.mean([x[k] for x in rs])) for k in rs[0]}
            agg.setdefault(mode, []).append(m)
            print(f"{sp.stem:<21}{mode:<11}{m['contacts']:>9.1f}{m['distinct']:>9.1f}{m['max_run']:>8.1f}{m['asked']:>7.2f}{m['first_same']:>8.2f}", flush=True)
    print("\nmeans over 7 scenarios x 3 seeds:")
    for mode, rows in agg.items():
        print(f"  {mode:<10}" + "  ".join(f"{k} {np.mean([r[k] for r in rows]):.2f}" for k in rows[0]))

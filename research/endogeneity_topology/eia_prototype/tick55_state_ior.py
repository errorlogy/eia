"""Tick 55: state-dependent IOR release. A target asked at uncertainty H0 is re-admitted only when its belief's
normalised entropy exceeds H0 + delta (knowledge went stale / new conflicting evidence).
World staleness: deterministic aging (rate 0.03 every episode) vs stochastic aging (same mean: with p = 0.1 an
event ages the belief by 0.3). 200 silent episodes, 4 scenarios x 2 seeds, baseline DriveEngine.
Question: is re-asking still clock-like? (ISI CV)"""

from __future__ import annotations

from pathlib import Path

import numpy as np

import tick30_pipeline as h
from eia.beliefs import shannon_entropy
from eia.intention import IntentionGenesis
from eia.schemas.initiative import InitiativeKind
from tick52_closed_loop import age, sharpen
from tick53_intention_loop import _ORIG_BEST, make_best

EP, DELTA = 200, 0.05


def H(b):
    return shannon_entropy(b.distribution) if b.distribution else b.uncertainty


def make_state_best(asked, rng):
    def best(self, motivation, field):
        base = _ORIG_BEST(self, motivation, field)
        if base.abstained or base.candidate is None:
            return base
        cands = [c for c in self.generate_candidates(motivation, field) if c.kind not in (InitiativeKind.ABSTAIN, InitiativeKind.OBSERVE)]
        ok = [c for c in cands if c.target_belief_id not in asked or
              (c.target_belief_id in field.beliefs and H(field.beliefs[c.target_belief_id]) > asked[c.target_belief_id] + DELTA)]
        if not ok:
            obs = next(c for c in self.generate_candidates(motivation, field) if c.kind == InitiativeKind.OBSERVE)
            return base.model_copy(update={"candidate": obs, "abstained": False})
        return base.model_copy(update={"candidate": max(ok, key=lambda c: c.lex_score)})
    return best


def run(scenario, ior, aging, seed):
    h.use_population(False)
    IntentionGenesis.best_or_abstain = _ORIG_BEST
    r = h.pl.run_scenario(scenario, traces_dir=Path(h.__file__).parent / "_traces", seed=100)
    loop = r["loop"]; rng = np.random.default_rng(seed); state = {"penalty": {}}; asked = {}
    IntentionGenesis.best_or_abstain = make_best(state, "IOR", rng) if ior == "fixed" else make_state_best(asked, rng)
    asks = []
    for e in range(EP):
        _, ini, dec, _ = loop.tick_cognition(tick=100 + e, hour=14, finalize=True)
        tgt = ini.candidate.target_belief_id if (ini.candidate and not ini.abstained and ini.candidate.kind.value == "ask_question") else None
        state["penalty"] = {k: v * 0.8 for k, v in state["penalty"].items()}
        if tgt:
            asks.append(e); state["penalty"][tgt] = state["penalty"].get(tgt, 0.0) + 1.0
            if dec is not None and dec.outcome.value == "send_now" and rng.random() < 0.7 and tgt in loop.field.beliefs:
                sharpen(loop.field.beliefs[tgt], 0.4)
            if tgt in loop.field.beliefs:
                asked[tgt] = H(loop.field.beliefs[tgt])
        if aging == "deterministic":
            age(loop.field, 0.03)
        elif rng.random() < 0.1:
            age(loop.field, 0.3)
    IntentionGenesis.best_or_abstain = _ORIG_BEST
    isi = np.diff(asks)
    return len(asks), (float(isi.std() / isi.mean()) if len(isi) > 2 else float("nan"))


if __name__ == "__main__":
    scen = [s for s in h.SCENARIOS if s.stem in ("twin_world_001", "twin_world_003", "twin_world_005", "autonomous_question")]
    conds = [("fixed", "deterministic"), ("state", "deterministic"), ("fixed", "stochastic"), ("state", "stochastic")]
    print(f"{'scenario':<21}" + "".join(f"{i+'/'+a[:5]:>18}" for i, a in conds) + "   (asks / ISI CV)")
    agg = {c: [] for c in conds}
    for sp in scen:
        cells = []
        for c in conds:
            rs = [run(sp, *c, s) for s in (1, 2)]
            m = np.nanmean(rs, 0); agg[c].append(m); cells.append(f"{m[0]:.0f}/{m[1]:.2f}")
        print(f"{sp.stem:<21}" + "".join(f"{x:>18}" for x in cells), flush=True)
    print(f"{'mean':<21}" + "".join(f"{np.nanmean([m[0] for m in agg[c]]):.0f}/{np.nanmean([m[1] for m in agg[c]]):.2f}".rjust(18) for c in conds))

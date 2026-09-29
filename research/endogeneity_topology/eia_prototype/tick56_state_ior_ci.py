"""Tick 56: tick 55 with 10 seeds and pooled inter-ask intervals (less noisy CV).
Conditions: fixed-decay IOR, state IOR + deterministic aging, state IOR + stochastic aging."""
import numpy as np
from pathlib import Path
import tick30_pipeline as h
from eia.intention import IntentionGenesis
from tick52_closed_loop import age, sharpen
from tick53_intention_loop import _ORIG_BEST, make_best
from tick55_state_ior import make_state_best, H, EP

def isis(scenario, ior, aging, seed):
    h.use_population(False); IntentionGenesis.best_or_abstain = _ORIG_BEST
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
            if tgt in loop.field.beliefs: asked[tgt] = H(loop.field.beliefs[tgt])
        if aging == "deterministic": age(loop.field, 0.03)
        elif rng.random() < 0.1: age(loop.field, 0.3)
    IntentionGenesis.best_or_abstain = _ORIG_BEST
    return len(asks), list(np.diff(asks))

scen = [s for s in h.SCENARIOS if s.stem in ("twin_world_001", "twin_world_003", "twin_world_005", "autonomous_question")]
conds = [("fixed", "stochastic"), ("state", "deterministic"), ("state", "stochastic")]
print(f"{'condition':<24}{'asks/run':>9}{'pooled ISIs':>12}{'pooled CV':>10}{'CV 95% boot':>16}")
for c in conds:
    n, pool = [], []
    for sp in scen:
        for seed in range(1, 11):
            k, d = isis(sp, *c, seed); n.append(k); pool += d
    pool = np.array(pool, float); rng = np.random.default_rng(0)
    boots = [ (lambda x: x.std()/x.mean())(rng.choice(pool, len(pool))) for _ in range(1000)]
    print(f"{c[0]+' / '+c[1]:<24}{np.mean(n):>9.1f}{len(pool):>12}{pool.std()/pool.mean():>10.2f}{np.percentile(boots,2.5):>8.2f}-{np.percentile(boots,97.5):.2f}", flush=True)

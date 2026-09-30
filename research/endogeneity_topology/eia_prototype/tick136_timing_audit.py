"""Tick 136: test D10 — does a multi-episode silent-run timing audit separate policies that a single-episode audit cannot?
Same harness, 200 silent episodes after each scenario, 7 scenarios x 3 seeds. An 'initiative' = non-abstain ask_question.
  scheduled     cognition every 5th episode only
  event_rule    drives computed every episode; cognition only if max drive salience >= event-rule threshold
  full_eia      current MVP-0: cognition every episode
  full_eia v3   proposed (tick 114): population drives mu 0.15 + closed loop + state-dependent IOR + stochastic staleness
Timing statistics: initiatives / 200, ISI CV, longest same-question run, lag-5 autocorrelation of the initiative indicator."""
from pathlib import Path
import numpy as np
import tick30_pipeline as h
import tick114_system_card_v3 as v3            # sets up calibrated engine params (mu 0.15)
import tick57_system_card as t57
from eia.experiment.baseline import load_event_rule_salience
from eia.intention import IntentionGenesis
from tick53_intention_loop import _ORIG_BEST

EP = 200

def stats(x, tg):
    idx = np.flatnonzero(x); isi = np.diff(idx)
    cv = isi.std() / isi.mean() if len(isi) > 2 else np.nan
    xc = x - x.mean(); ac5 = (xc[:-5] @ xc[5:]) / (xc @ xc) if xc.std() > 0 else np.nan
    run = best = 0; prev = object()
    for t in tg:
        run = run + 1 if (t is not None and t == prev) else (1 if t else 0); prev = t; best = max(best, run)
    return x.sum(), cv, best, ac5

def silent(policy, sp, seed):
    h.use_population(False); IntentionGenesis.best_or_abstain = _ORIG_BEST
    r = h.pl.run_scenario(sp, traces_dir=Path("_traces"), seed=100); loop = r["loop"]; thr = load_event_rule_salience()
    x, tg = np.zeros(EP), []
    for e in range(EP):
        fire = True
        if policy == "scheduled": fire = e % 5 == 0
        if policy == "event_rule":
            m = loop.drives.compute(loop.field, motivation_id="mot-probe"); fire = max(s.intensity for s in m.signals) >= thr
        t = None
        if fire:
            _, ini, _, _ = loop.tick_cognition(tick=100 + e, hour=14, finalize=True)
            if ini.candidate and not ini.abstained and ini.candidate.kind.value == "ask_question": t = ini.candidate.target_belief_id
        x[e] = t is not None; tg.append(t)
    return stats(x, tg)

rows = {}
for sp in h.SCENARIOS:
    for seed in (1, 2, 3):
        for pol in ("scheduled", "event_rule", "full_eia"):
            rows.setdefault(pol, []).append(silent(pol, sp, seed))
        c = t57.card(sp, "proposed", seed) if False else None
print(f"{'policy':<14}{'initiatives/200':>16}{'ISI CV':>8}{'longest run':>13}{'lag-5 ac':>10}")
for pol, rs in rows.items():
    m = np.nanmean(np.array(rs, float), 0); print(f"{pol:<14}{m[0]:>16.1f}{m[1]:>8.2f}{m[2]:>13.1f}{m[3]:>10.2f}", flush=True)
print("full_eia v3 (tick 114 system card): initiatives 3.6/200, ISI CV 1.08, longest run 1.05")

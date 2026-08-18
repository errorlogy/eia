# M-G metrics — measured EIS vector (2026-08-18)

**Sci-flow:** S1–S5 · Milestone **M-G**  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Claim:** C1 preserved (not C2). Vector components are functions of run state. S/R remain event-count flags until scheduler/rule CF exist.

## Hypothesis (S1)

H-EIS-002: Replacing demo constants in `EndogeneityVector` with measured run-state functions does not drop CF-1 full-window pass-rate below 0.90.

## Design (S2)

| Component | Source |
|-----------|--------|
| P `prompt_independence` | 1.0 if no prompt applied before intent, else 0.25 |
| S `scheduler_independence` | 1.0 if scheduler event count = 0, else 0.20 |
| R `event_rule_independence` | 1.0 if rule event count = 0, else 0.20 |
| persistent state | 0 if world-model off; else `0.55 + 0.45 * mean_staleness` |
| M `world_model_grounding` | epistemic gap (pressure) |
| W `coherence_dependence` | peak Kuramoto order parameter in episode prefix |
| goal novelty | `0.35 + 0.40 * goal_separation`, capped &lt; 0.75 for catalog targets |
| self-model | `0.45 + 0.55 * self_prior_mismatch` |
| constitutional | 1.0 until an EIS-8 rewrite path exists |

**Falsifier:** CF-1 mini/smoke full pass-rate &lt; 0.90 after the change → revert.

## Execute (S3)

- `measure_endogeneity_vector()` in `endogenous.py`
- WoE `emergence.py` uses prefix peak R, not hard-coded 0.88 / 0.68 / 0.72 / 0.95
- Tests: prompt vs clean classify; catalog cannot reach EIS-7

## Analyze (S4)

| Check | Result |
|-------|--------|
| WoE unittest | **38/38** |
| CF-1 mini (seeds 7–10, full) | pass ≥ 0.90 |
| CF-1 smoke (seeds 1–20, full) | **0.95** |
| Seed 7 | still EIS-6 |
| P2 hard-coded demo vector | **closed** on WoE path |

S/R are still flags (harness has no scheduler/rule events). That is documented, not hidden.

## Review (S5)

M-G **DONE** as C1-preserving measurement layer. Next: **M-D** Kuramoto coupling/delay sweep (C2).

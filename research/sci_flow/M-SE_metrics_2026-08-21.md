# M-SE / Stable endogeneity stack ablation — 2026-08-21

**Status:** toy sim executed — **CONJECTURE** / engineering ablation only  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Claim ceiling:** unchanged (**C2** scoped ATT-E only); **not C3**, **not AGI***  
**Author:** Roman Kuznetsov — research@anthemium.tech  
**Theory:** [`STABLE_ENDOGENEITY.md`](STABLE_ENDOGENEITY.md)  
**Script:** [`endogeneity_stack_sim.py`](../../endogeneity_stack_sim.py)

## Hypothesis

H-MSE-STACK: a **stable endogeneity stack** (multi-term drive + Noisy-TV suppressor + hierarchical goals + bounded drive dynamics) allocates less action mass to irreducible noisy traps and matches or improves competence / diversity vs LP-only, while naive prediction-error drive collapses to traps.

## Pre-registered design

| Item | Value |
|------|-------|
| Seeds | 10 |
| Steps / run | 2500 |
| External reward | 0 (intrinsic selection only) |
| Modes | `prediction_error`, `learning_progress`, `stable_stack` |
| Goal space | 5 levels x 5 goals; level-0 index 0 = noisy trap |

## Ablation table (batch means)

| mode | mastered_goals | unlocked_goals | noisy_trap_fraction | goal_entropy | max_goal_share | switching_rate | drive_norm_min | drive_norm_max |
|------|----------------|----------------|---------------------|--------------|----------------|----------------|----------------|----------------|
| prediction_error | 0.0 | 5.0 | **0.994** | 0.014 | **0.994** | 0.008 | — | — |
| learning_progress | 7.5 | 9.4 | 0.017 | 0.621 | 0.176 | 0.705 | — | — |
| stable_stack | 7.5 | 9.4 | **0.009** | 0.613 | 0.199 | 0.611 | 0.583 | 1.099 |

Notes: `mastered_goals` = learnable goals with competence >= 0.80; `noisy_trap_fraction` = share of steps on procedurally marked noisy goals; drive norms only for `stable_stack`.

## Interpretation (scoped)

- **prediction_error** — Noisy-TV failure (~99.4% trap allocation); not stable endogeneity.
- **learning_progress** — escapes traps; higher switching; no explicit drive homeostasis.
- **stable_stack** — lowest trap fraction (~0.9%), comparable mastery/entropy to LP, bounded drive band.

## Artifacts

| Item | Path |
|------|------|
| Script | `endogeneity_stack_sim.py` |
| CSV | `endogeneity_stack_results.csv` |
| Figure | `endogeneity_ablation.png` |

## ATT mapping

| Cell | Status |
|------|--------|
| ATT-E | Unchanged — C2 CF-4 partial; sim does not substitute for do(Z) |
| ATT-G / ATT-P | Informs Q_L, P_G, lambda_G proxies only |
| ATT-R | Related recurrence narrative; not CognitiveLoop closure |
| M-SE | Documented stable stack; **no C-level raise** |

## Next

Optional daemon carryover (shadow-first) or T_NAMM soft witness; wire continuous E_C when theta_E pre-registered.

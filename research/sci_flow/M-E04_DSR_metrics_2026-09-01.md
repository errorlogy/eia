# M-E04 / D05 — Drive Sustainability (DSR) on shadow carryover — 2026-09-01

**Status:** harness executed · OPERATIONAL explore proxy (shadow carryover)  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Claim ceiling:** architecture / M-SE `B_D` explore — **not C3**, **not AGI\***, C2 unchanged  
**Author:** Roman Kuznetsov — research@anthemium.tech  
**Hermes tasks:** **E04** (longitudinal 50 ticks) · **D05** (DSR `d>0.3` persistence)

## Hypothesis

H-DSR-CARRYOVER: on the Phase 2 shadow carryover path (`run_shadow_carryover_tick`), the three-channel drive vector \(d_t = [d^{\mathrm{epi}}, d^{\mathrm{coh}}, d^{\mathrm{com}}]^\top\) stays **bounded** (Tier B `B_D`) and **above** the D05 persistence floor over 50 cognitive ticks with **no user prompt**.

## Pre-registered design

| Item | Value |
|------|-------|
| Session length | 50 cognitive ticks (`session_tick`) |
| Bootstrap | `CLOSED_LOOP` shadow episode (seed 0) |
| Continuation | `run_shadow_carryover_tick` × 24 (ambient obs only) |
| User prompts | 0 |
| `emit_m0` | always `false` |
| Governor thresholds | Default `GovernorConfig` — **not** lowered |
| D05 floor | \(\|d_t\| > 0.3\) on every sample |
| `B_D` envelope | \(0 \le \|d_t\| \le \sqrt{3}\) |

## Results (seed 0)

| Metric | Value | D05 / E04 target |
|--------|-------|------------------|
| Cognitive ticks reached | **50** | E04: ≥ 50 |
| Carryover episodes | 24 | — |
| Drive samples | 25 (2-tick episode boundaries) | — |
| `dsr_min` | **0.822** | D05: > 0.3 |
| `dsr_max` | **0.912** | `B_D` bounded |
| `dsr_mean` | **0.903** | — |
| `persistence_fraction` | **1.0** | D05: all samples > 0.3 |
| `b_d_bounded` | **true** | `B_D` engineering guard |
| **D05 pass** | **true** | — |
| **E04 pass** | **true** | — |

## ATT / pool mapping

| Cell | Status |
|------|--------|
| **M-SE** `B_D` | Tier B — bounded drives; shadow carryover evidence (not toy sim) |
| **E04** | Longitudinal 50-tick no-user session — **done** on shadow path |
| **D05** | DSR persistence floor — **pass** (explore; not production daemon) |
| ATT-E / C-ladder | Unchanged — no C-level raise |

## Gap vs live daemon

DSR is measured on `ShadowSessionCarryover` + `run_shadow_carryover_tick`. Production `run_daemon_tick` still constructs a fresh `CognitiveLoop` each APScheduler interval; StateStore BeliefField hydration **deferred**.

## Artifacts

| Item | Path |
|------|------|
| Harness API | `src/eia/runtime/shadow_multitick.py` (`run_dsr_longitudinal_session`) |
| Runner | `python research/sci_flow/run_dsr_carryover.py` |
| JSON | `research/sci_flow/dsr_carryover_results.json` |
| Tests | `tests/test_shadow_multitick.py::test_dsr_longitudinal_50_tick_carryover_session` |
| Pool | `ENDOGENEITY_METRICS_POOL.md` Tier B `B_D` |

## Next

Live daemon StateStore carryover **or** Hermes **D01** / metrics pool Tier A tick; no C-level raise.

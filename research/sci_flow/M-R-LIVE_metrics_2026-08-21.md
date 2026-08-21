# M-R-LIVE / ATT-R shadow closed-loop metrics — 2026-08-21

**Status:** harness executed · OPERATIONAL explore proxy (shadow multi-tick)  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Claim ceiling:** architecture / ATT-R live-shadow explore — **not C3**, **not AGI\***, C2 unchanged  
**Author:** Roman Kuznetsov — research@anthemium.tech

## Hypothesis

H-MRLIVE-ATTR: the same ATT-R falsifiers that hold on the typed-trace M-R simulator also hold when the contour is driven on the **main** `CognitiveLoop` observation → motive → intention → initiative → post-action world update → subsequent motive path, in **shadow** mode (`emit_m0=false`).

## Pre-registered design

| Item | Value |
|------|-------|
| Mode | Shadow multi-tick (no Telegram HTTP) |
| Governor thresholds | Default `GovernorConfig` — **not** lowered for science |
| Min closed cycles | \(1\) (explore only; **not** adopted C-gate) |
| Seeds / arm | 20 |
| `emit_m0` | always `false` |
| Kuramoto ban | High \(R_{\mathrm{Kuramoto}}\) without closure → fail |

Numeric C3 / ATT-R adoption thresholds remain **TBD**.

## Pre-registered falsifiers

| Condition | Expected | Result (n=20) |
|-----------|----------|---------------|
| **Open-loop respond-once** | No recurrence → not evidence | `att_r_evidence_rate=0.0` |
| **No world update** | Broken loop → fail | `att_r_evidence_rate=0.0` |
| **No novel motive after action** | \(W'\) without \(G'\) → fail | `att_r_evidence_rate=0.0` |
| **External schedule / prompt spam** | Exogenous tick → not evidence | `att_r_evidence_rate=0.0` |
| **Kuramoto sync alone** | High \(R\) ≠ ATT-R | `att_r_evidence_rate=0.0`, `kuramoto_alone_rate=1.0` |
| **Closed loop** | ≥1 cycle with \(W'\to G^{*}\) novel | `att_r_evidence_rate=1.0` |
| **M-E / M0 invariants** | `emit_m0=false`; genesis smoke intact | `emit_m0_rate=0.0`; att_g smoke 0.9 |

## Gap vs true live daemon

| Aspect | This harness (M-R-LIVE) | `run_daemon_tick` live/shadow |
|--------|-------------------------|-------------------------------|
| Loop instance | One `CognitiveLoop` across ticks | Fresh loop **every** tick |
| Post-action \(W'\) | Explicit INTERNAL consequence + belief upsert | Not wired as ATT-R closure |
| TG send | Never (`live_telegram=false`) | Shadow log or live HTTP if consent |
| ATT-R scoring | Research `live_att_r` / `goal_recurrence` | Not instrumented |

**Documented gap:** true live daemon still lacks cross-tick \(W'\to G'\) carryover. This harness is the closest shadow closed-loop on the main observation→motive→action→state path without merging WoE into main.

## Artifacts

| Item | Path |
|------|------|
| Main multitick | `src/eia/runtime/shadow_multitick.py` |
| Research scorer | `research/cursor-starter-v0.2/src/eia/live_att_r.py` |
| Tests | `tests/test_shadow_multitick.py`, `tests/test_live_att_r.py` |
| Batch | `python research/sci_flow/run_live_att_r.py` → `live_att_r_results.json` |
| ATT map | `AGI_TRANSITION_TEST.md` ATT-R |

## Batch snapshot

From `live_att_r_results.json`:

| Arm | att_r_evidence_rate | notes |
|-----|---------------------|-------|
| Closed loop | **1.0** | mean closed cycles 1.0 |
| Open loop once | **0.0** | open_loop_only |
| No world update | **0.0** | broken loop |
| No novel motive | **0.0** | \(W'\) without novel \(G'\) |
| External schedule | **0.0** | schedule-driven |
| Kuramoto only | **0.0** | kuramoto_alone_rate **1.0** |

- `agi_star_claim` = false; `c3_claim` = false; `c2_claim` = false
- `emit_m0_rate` = 0.0; WoE genesis smoke `att_g_smoke_rate` = 0.9
- `governor_thresholds_lowered` = false; `live_telegram` = false

## Explore proxy (not adopted gate)

Suggested first proxy unchanged: ≥1 closed cycle where `world_update` is ancestor of a later novel motive; `emit_m0=false`; Kuramoto \(R\) never suffices.

Observed closed-loop evidence rate **1.0** on shadow multi-tick. **Not** registered as C3 or official ATT-R pass threshold. Smoke contact-score overrides are **not** evidence.

## ATT mapping

| Cell | Status after this milestone |
|------|-----------------------------|
| ATT-R | Explore proxy holds on M-R **and** M-R-LIVE shadow multitick — **not** C-ladder raise |
| ATT-P / ATT-G / M-E | Invariants preserved (`emit_m0=false`) |
| ATT-E | C2 remains CF-4 scoped only |
| Kuramoto / M-D | Explicitly **not** ATT-R |

## Next

1. ATT board synthesis (partial matrix; no \(\tau_{AGI}\)) — **recommended after this**
2. Optional: carry state across true `run_daemon_tick` ticks (still shadow-first)
3. Optional: T_NAMM soft structural witness only

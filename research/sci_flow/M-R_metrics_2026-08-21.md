# M-R / ATT-R endogenous cognitive recurrence metrics — 2026-08-21

**Status:** harness executed · OPERATIONAL explore proxy  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Claim ceiling:** architecture / ATT-R explore — **not C3**, **not AGI\***, C2 unchanged (CF-4 scoped \(E_{\mathrm{endo}}\) only)  
**Author:** Roman Kuznetsov — research@anthemium.tech

## Hypothesis

H-MR-ATTR: a closed goal-formation loop \(W\to M\to G\to\Pi\to A\to X'\to W'\to G'\) is detectable as runtime endogenous causal closure when a post-action `world_update` is ancestral parent of a later *novel* motive. Kuramoto synchrony \(R\) alone does **not** satisfy ATT-R.

## Pre-registered design

| Item | Value |
|------|-------|
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

## Distinction enforced

| Arm | Meaning | ATT-R evidence? |
|-----|---------|-----------------|
| **Closed loop** | \(A\to X'\to W'\to G'\) novel with typed parents | Yes (explore) |
| **Open loop once** | Respond-once; no \(W'\) | No |
| **No world update** | Action without \(W'\) | No |
| **No novel motive** | \(W'\) but same / non-novel \(G\) | No |
| **External schedule** | Cron / prompt spam parents only | No |
| **Kuramoto only** | High sync, no closure | No (**ban**) |

## Artifacts

| Item | Path |
|------|------|
| Module | `research/cursor-starter-v0.2/src/eia/goal_recurrence.py` |
| Tests | `tests/test_goal_recurrence.py` |
| Batch | `python research/sci_flow/run_goal_recurrence.py` → `goal_recurrence_results.json` |
| ATT map | `AGI_TRANSITION_TEST.md` ATT-R |

## Batch snapshot

From `goal_recurrence_results.json`:

| Arm | att_r_evidence_rate | notes |
|-----|---------------------|-------|
| Closed loop | **1.0** | mean closed cycles 1.0 |
| Open loop once | **0.0** | open_loop_only |
| No world update | **0.0** | broken loop |
| No novel motive | **0.0** | \(W'\) without novel \(G'\) |
| External schedule | **0.0** | schedule-driven |
| Kuramoto only | **0.0** | kuramoto_alone_rate **1.0** |

- `agi_star_claim` = false; `c3_claim` = false; `c2_claim` = false (unchanged ceiling)
- `emit_m0_rate` = 0.0; WoE genesis smoke `att_g_smoke_rate` = 0.9

## Explore proxy (not adopted gate)

Suggested first proxy: ≥1 closed cycle where `world_update` is ancestor of a later novel motive; `emit_m0=false`; Kuramoto \(R\) never suffices.

Observed closed-loop evidence rate **1.0**. **Not** registered as C3 or official ATT-R pass threshold.

## ATT mapping

| Cell | Status after this milestone |
|------|-----------------------------|
| ATT-R | Explore proxy holds on research typed-trace simulator — **not** C-ladder raise |
| ATT-P / ATT-G / M-E | Invariants preserved (`emit_m0=false`) |
| ATT-E | C2 remains CF-4 scoped only |
| Kuramoto / M-D | Explicitly **not** ATT-R |

## Next

1. Optional live closed-loop instrumentation on WoE / T_LIVE traces (same falsifiers)  
2. ATT-N only after encoding budget \(B\) pre-registration  
3. ATT-D after ATT-E stable in a second domain  

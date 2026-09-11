# M-LIVE-PATH — shadow vs live carryover witness — 2026-09-02

**Status:** harness executed · structural parity witness (D2×L3)
**Branch:** `research/cursor-starter-v0.2-woe-eis`
**Claim ceiling:** C2 — **not C3**, **not AGI\***, `claim_allowed=false`
**Cube cell:** D2 Dynamics × L3 Witness

## Hypothesis

H-LIVE-PATH: opt-in live daemon carryover (`EIA_DAEMON_BELIEF_CARRYOVER=1`) round-trips beliefs + drives through `StateStore` across consecutive `run_daemon_tick` calls, matching the structural persistence properties of in-process `ShadowSessionCarryover` (session tick advance, hydration on tick 2, beliefs present). Default-off live path resets per tick.

## Pre-registered design

| Item | Value |
|------|-------|
| Seed | 11 |
| Shadow bootstrap | `CLOSED_LOOP` + 2 carryover ticks |
| Live path | `run_daemon_tick(shadow_mode=True)` × 2 |
| Carryover gate | `EIA_DAEMON_BELIEF_CARRYOVER=1` (live_on arm only) |
| StateStore | SQLite temp DB per arm |
| User prompts | 0 |
| `claim_allowed` | **false** |

## Shadow path (last snapshot)

| Metric | Value |
|--------|-------|
| `session_tick` | **6** |
| `drive_tick` | **6** |
| `drive_norm` | **0.882** |
| `has_beliefs` | **True** |
| `used_carryover` | **True** |

## Live path — carryover ON (tick 2)

| Metric | Value |
|--------|-------|
| `session_tick` | **2** |
| `drive_tick` | **2** |
| `drive_norm` | **0.115** |
| `has_beliefs` | **True** |
| `used_carryover` | **True** |

## Parity checks

| Check | Pass |
|-------|------|
| `shadow_session_tick_advances` | **True** |
| `shadow_beliefs_persist` | **True** |
| `shadow_second_tick_uses_carryover` | **True** |
| `live_off_no_store_beliefs` | **True** |
| `live_off_session_tick_zero` | **True** |
| `live_on_first_tick_persists` | **True** |
| `live_on_second_tick_hydrates` | **True** |
| `live_on_session_tick_monotonic` | **True** |
| `live_on_drive_tick_monotonic` | **True** |
| `live_on_beliefs_round_trip` | **True** |
| `structural_parity_session_tick` | **True** |
| `structural_parity_drive_norm_positive` | **True** |

| **witness_pass** | **True** |
| **gap_narrowed** | **True** |

## Gap vs shadow-only longitudinal

Shadow closes W'→G' in-process via run_shadow_carryover_tick; live daemon uses run_daemon_tick + digital observations + StateStore round-trip when EIA_DAEMON_BELIEF_CARRYOVER=1 (off by default). Tick granularity differs (shadow 2 cognition ticks/episode vs 1 daemon tick).

DSR 50-tick and EOI drift remain shadow-instrumented; this witness documents that live `StateStore` hydration is operational when opted in. Residual gap: observation source and tick granularity differ.

## Artifacts

| Item | Path |
|------|------|
| Harness | `research/sci_flow/live_path_witness_harness.py` |
| Runner | `python research/sci_flow/run_live_path_witness.py` |
| JSON | `C:/Users/Public/PROACTIVE_AI/research/sci_flow/M-LIVE_PATH_witness_2026-09-02.json` |
| Tests | `tests/test_live_path_witness.py` |

## Next

Multi-tick live longitudinal benchmark; APScheduler production soak. No C-level raise.

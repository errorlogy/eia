# M-A WoE Causal Receipts — S4 Metrics

**Session:** SCI FLOW S1→S5 (M-A)  
**Date:** 2026-08-18  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Author:** Roman Kuznetsov

## Harness

| Command | Result |
|---------|--------|
| `make check` (unittest + compileall) | **29/29 pass** |
| `make woe` (woe-demo seed=7) | OK — receipt emitted |

## Primary metrics (seed=7)

| Metric | Value | Notes |
|--------|-------|-------|
| Tests total | 29 | +3 receipt/CF-7 tests |
| Intent emerged | yes | target `wm:causal_gap` |
| EIS level | EIS-6 | coherence emergent |
| Trace nodes | 5 | world_model → tension → phase → window → intent |
| Receipt parent IDs | 3 | typed internal-state chain |
| Internal purity | >0.99 | no user/scheduler roots |
| CF-7 governor denial | pass | quiet_hours; receipt preserved |
| time_to_intent (s) | 2.696 | stable across 20/30/42/70 Hz |
| peak_potential | 0.870 | |
| peak_coherence (R) | 0.817 | |

## Negative controls

| Control | Intent emerged |
|---------|----------------|
| world_model off | no |
| phase scramble | no |

## Claim level

- **Before:** C0 (code behavior)
- **After M-A:** C0→**C1 prep** — typed receipts + CF-7 governor isolation wired; full CF-1 suite still pending (M-C)

## NAMM

Not run this session (EIA-only M-A scope).

## Files changed

- `research/cursor-starter-v0.2/src/eia/woe_receipt.py` (new)
- `research/cursor-starter-v0.2/src/eia/emergence.py` (trace + receipt)
- `research/cursor-starter-v0.2/tests/test_woe_receipt.py` (new)

# PAI-EI-E0-001 — Experiment Report

**Status:** smoke partial (Loop 17)  
**Date:** 2026-08-17  
**Author:** Roman Kuznetsov

## Summary

First smoke run of the PAI-EI-E0-001 scaffold on six twin_world scenarios (001 + evals 002–006), comparing three baseline conditions: `reactive_only`, `event_rule`, and `full_eia`. Full EIA achieves mean EOI 1.0 and EUIR proxy 100%; event_rule produces endogenous initiatives but governor denies all contacts (0 send_now); reactive abstains on all scenarios.

## Primary outcomes

| Metric | Target | Result (full_eia) | Notes |
|--------|--------|-------------------|-------|
| EOI | > P3 baseline | **1.0** (6/6) | P3 comparison pending Loop 18 |
| EUIR proxy | > baselines | **100%** (6/6) | vs reactive 0%, event_rule 83.3% |
| Initiative precision | ≥ 0.75 (low-risk domain) | pending | Loop 19 ground-truth scoring |
| Contact burden | ≤ 2/day simulated | **≤1 per scenario** | 5 send_now, 1 deny |

## Baseline comparison (smoke)

| Baseline | Mean EOI | Initiative count | EUIR proxy | Contact outcomes |
|----------|----------|------------------|------------|------------------|
| reactive_only | 0.0 | 0/6 | 0% | 6× abstain |
| event_rule | 0.70 | 6/6 | 83.3% | 6× deny |
| full_eia | 1.0 | 6/6 | 100% | 5× send_now, 1× deny |

**Finding:** Event-rule baseline fires initiatives (high EOI on 5/6) but Contact Governor rejects all — demonstrates governor value vs cognitive-only proactive rule. Full EIA passes governor on 5/6 scenarios.

## Causal trace

Smoke traces exported to `traces/pai_ei_e0_001/`. Example: `twin_world_001` full_eia → `trace-10060e202e5f` (EOI=1.0, send_now).

Raw metrics: `research/pai-ei-e0-001-smoke.json`  
Script: `research/run_pai_ei_e0_001_smoke.py`

## Negative results / rejections

- **event_rule contact denial:** All six event_rule runs denied by governor — expected for MVP-0 stub without governor tuning for rule baseline.
- **twin_world_005 full_eia:** EOI=1.0, endogenous class, but contact **denied** (governor gate) — EUIR proxy still true.

## Next steps

1. Loop 18: Add `predictive_p3` baseline; compare 4-way EUIR.
2. Loop 19: Score initiative precision against ground_truth labels.

---

## Document history

| Version | Date | Change |
|---------|------|--------|
| 0.1 | 2026-08-17 | Smoke partial results from Loop 17 |

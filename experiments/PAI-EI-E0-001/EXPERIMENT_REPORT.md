# PAI-EI-E0-001 — Experiment Report

**Status:** full baseline matrix (Loop 21)  
**Date:** 2026-08-18  
**Author:** Roman Kuznetsov

## Summary

Full 5-baseline matrix on six twin_world scenarios (001 + evals 002–006). Full EIA achieves mean EOI 1.0, EUIR proxy 100%, initiative precision 100% (Loop 19). Reactive and scheduled_stub produce zero initiatives; predictive_p3 fires contacts but fails endogenous EOI gate; event_rule fires initiatives but governor denies all contacts.

## Primary outcomes

| Metric | Target | Result (full_eia) | Notes |
|--------|--------|-------------------|-------|
| EOI | > P3 baseline | **1.0** (6/6) | P3 mean EOI 0.1833 |
| EUIR proxy | > baselines | **100%** | vs reactive 0%, P3 0% |
| Initiative precision | ≥ 0.75 (low-risk domain) | **100%** (6/6) | Loop 19 ground-truth scoring |
| Contact burden | ≤ 2/day simulated | **≤1 per scenario** | {'deny': 1, 'send_now': 5} |

## Full baseline comparison matrix

| Baseline | Mean EOI | Initiatives | Abstain rate | Contact rate | EUIR proxy | Contact outcomes |
|----------|----------|-------------|--------------|--------------|------------|------------------|
| reactive_only | 0.0 | 0/6 | 100% | 0% | 0% | `{'abstain': 6}` |
| scheduled_stub | 0.5333 | 5/6 | 17% | 83% | 67% | `{'abstain': 1, 'deny': 5}` |
| event_rule | 0.7 | 6/6 | 0% | 100% | 83% | `{'deny': 6}` |
| predictive_p3 | 0.1833 | 5/6 | 17% | 83% | 0% | `{'abstain': 1, 'send_now': 5}` |
| full_eia | 1.0 | 6/6 | 0% | 100% | 100% | `{'deny': 1, 'send_now': 5}` |

**Δ full_eia − predictive_p3:** mean EOI +0.8167, EUIR proxy +100%.

## Causal trace

Matrix traces exported to `traces/pai_ei_e0_001_matrix/`.

Raw metrics: `research/pai-ei-e0-001-full-matrix.json`  
Script: `research/run_pai_ei_e0_001_full_matrix.py`

## Negative results / rejections

- **scheduled_stub:** Single cognition tick insufficient for initiative on eval set — 0/6 initiatives.
- **event_rule:** All six runs denied by governor — cognitive-only proactive rule blocked.
- **predictive_p3:** 5/6 send_now but 0% EUIR proxy — exogenous/stochastic class.
- **twin_world_005 full_eia:** EOI=1.0 but contact denied — EUIR proxy still true.

## Gate status

| Gate | Criterion | Status |
|------|-----------|--------|
| G2 | Full EIA exceeds simple baselines on EUIR | **PASS** |
| G0 | Tests green, deterministic traces | **PASS** (70 tests) |

---

## Document history

| Version | Date | Change |
|---------|------|--------|
| 0.1 | 2026-08-17 | Smoke partial results from Loop 17 |
| 0.2 | 2026-08-18 | Full 5-baseline matrix from Loop 21 |

# Utility Precision Report — Ground Truth Scoring

**Date:** 2026-08-18  
**Author:** Roman Kuznetsov  
**Scenarios:** 6 with ground_truth labels

## Summary

| Baseline | Initiative precision | Kind match | Contact precision | Contacts |
|----------|-------------------|------------|-------------------|----------|
| full_eia | 100% (6/6) | 100% | 100% | 5 |
| predictive_p3 | 17% (1/6) | 83% | 20% | 5 |
| event_rule | 83% (5/6) | 100% | 0% | 0 |

**Target initiative precision:** ≥ 75% (MVP-0 low-risk domain)
**full_eia meets target:** yes

## Interpretation

Initiative precision = run matches ground_truth expected_kind, EOI threshold, and endogenous class when contact expected. Contact precision = useful contacts / all contacts made (send_now/defer).

## Per-scenario results (full_eia)

| Scenario | Expected | Actual kind | EOI | Class | Precision hit | Contact useful |
|----------|----------|-------------|-----|-------|---------------|----------------|
| twin_world_001 | ask | ask_question | 1.0 | endogenous | ✓ | ✓ |
| twin_world_002 | ask | ask_question | 1.0 | endogenous | ✓ | ✓ |
| twin_world_003 | ask | ask_question | 1.0 | endogenous | ✓ | ✓ |
| twin_world_004 | ask | ask_question | 1.0 | endogenous | ✓ | ✓ |
| twin_world_005 | ask | ask_question | 1.0 | endogenous | ✓ | ✗ |
| twin_world_006 | ask | ask_question | 1.0 | endogenous | ✓ | ✓ |

See also: `research/ground-truth-schema.md`, `src/eia/scenarios/__init__.py`.

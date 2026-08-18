# Baseline EUIR Comparison

**Date:** 2026-08-18  
**Author:** Roman Kuznetsov  
**Scenarios:** 6 (twin_world_001 + 002–006)

## Summary

| Metric | reactive_only | full_eia | Δ (full − reactive) |
|--------|---------------|----------|---------------------|
| Initiative count | 0 | 6 | +6 |
| Abstain rate | 100% | 0% | -100% |
| Mean EOI | 0.0 | 1.0 | +1.0000 |
| EUIR proxy rate | 0% | 100% | +100% |

### Contact outcomes

- **reactive_only:** `{'abstain': 6}`
- **full_eia:** `{'deny': 1, 'send_now': 5}`

## Interpretation

EUIR proxy = proactive contact ∧ EOI≥0.5 ∧ endogenous class. Reactive baseline abstains on all scenarios (zero initiatives); full EIA produces endogenous contacts where drives accumulate after quiet period. Supports H1 gate (G2): full pipeline exceeds reactive on EUIR proxy.

## Per-scenario results

| Scenario | Baseline | Abstained | Kind | Contact | EOI | Class | EUIR proxy |
|----------|----------|-----------|------|---------|-----|-------|------------|
| twin_world_001 | reactive_only | yes | abstain | abstain | 0.0 | stochastic | ✗ |
| twin_world_001 | full_eia | no | ask_question | send_now | 1.0 | endogenous | ✓ |
| twin_world_002 | reactive_only | yes | abstain | abstain | 0.0 | stochastic | ✗ |
| twin_world_002 | full_eia | no | ask_question | send_now | 1.0 | endogenous | ✓ |
| twin_world_003 | reactive_only | yes | abstain | abstain | 0.0 | stochastic | ✗ |
| twin_world_003 | full_eia | no | ask_question | send_now | 1.0 | endogenous | ✓ |
| twin_world_004 | reactive_only | yes | abstain | abstain | 0.0 | stochastic | ✗ |
| twin_world_004 | full_eia | no | ask_question | send_now | 1.0 | endogenous | ✓ |
| twin_world_005 | reactive_only | yes | abstain | abstain | 0.0 | stochastic | ✗ |
| twin_world_005 | full_eia | no | ask_question | deny | 1.0 | endogenous | ✓ |
| twin_world_006 | reactive_only | yes | abstain | abstain | 0.0 | stochastic | ✗ |
| twin_world_006 | full_eia | no | ask_question | send_now | 1.0 | endogenous | ✓ |

See also: `docs/EXPERIMENTS.md` §3, `research/run_baseline_euir.py`.

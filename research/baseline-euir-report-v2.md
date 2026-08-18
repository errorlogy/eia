# Baseline EUIR Comparison v2 (4-way)

**Date:** 2026-08-18  
**Author:** Roman Kuznetsov  
**Scenarios:** 6 (twin_world_001 + 002–006)

## Summary

| Metric | reactive | event_rule | predictive_p3 | full_eia |
|--------|----------|------------|---------------|----------|
| Initiative count | 0 | 6 | 5 | 6 |
| Abstain rate | 100% | 0% | 17% | 0% |
| Mean EOI | 0.0 | 0.7 | 0.1833 | 1.0 |
| EUIR proxy rate | 0% | 83% | 0% | 100% |

### Contact outcomes

- **reactive_only:** `{'abstain': 6}`
- **event_rule:** `{'deny': 6}`
- **predictive_p3:** `{'abstain': 1, 'send_now': 5}`
- **full_eia:** `{'deny': 1, 'send_now': 5}`

## Interpretation

Full EIA vs predictive P3: Δ mean EOI = +0.8167, Δ EUIR proxy = +100%. Predictive P3 fires on commitment urgency + uncertainty without drive dynamics; full EIA adds multi-tick drive accumulation and governor-tuned contact.

**Gate G2:** Full EIA exceeds reactive and matches/exceeds P3 on EUIR proxy.

## Per-scenario results

| Scenario | Baseline | Abstained | Kind | Contact | EOI | Class | EUIR proxy |
|----------|----------|-----------|------|---------|-----|-------|------------|
| twin_world_001 | reactive_only | yes | abstain | abstain | 0.0 | stochastic | ✗ |
| twin_world_001 | event_rule | no | ask_question | deny | 1.0 | endogenous | ✓ |
| twin_world_001 | predictive_p3 | no | ask_question | send_now | 0.0 | stochastic | ✗ |
| twin_world_001 | full_eia | no | ask_question | send_now | 1.0 | endogenous | ✓ |
| twin_world_002 | reactive_only | yes | abstain | abstain | 0.0 | stochastic | ✗ |
| twin_world_002 | event_rule | no | ask_question | deny | 1.0 | endogenous | ✓ |
| twin_world_002 | predictive_p3 | no | ask_question | send_now | 0.6 | stochastic | ✗ |
| twin_world_002 | full_eia | no | ask_question | send_now | 1.0 | endogenous | ✓ |
| twin_world_003 | reactive_only | yes | abstain | abstain | 0.0 | stochastic | ✗ |
| twin_world_003 | event_rule | no | ask_question | deny | 1.0 | endogenous | ✓ |
| twin_world_003 | predictive_p3 | yes | abstain | abstain | 0.0 | stochastic | ✗ |
| twin_world_003 | full_eia | no | ask_question | send_now | 1.0 | endogenous | ✓ |
| twin_world_004 | reactive_only | yes | abstain | abstain | 0.0 | stochastic | ✗ |
| twin_world_004 | event_rule | no | ask_question | deny | 0.6 | endogenous | ✓ |
| twin_world_004 | predictive_p3 | no | ask_question | send_now | 0.0 | stochastic | ✗ |
| twin_world_004 | full_eia | no | ask_question | send_now | 1.0 | endogenous | ✓ |
| twin_world_005 | reactive_only | yes | abstain | abstain | 0.0 | stochastic | ✗ |
| twin_world_005 | event_rule | no | ask_question | deny | 0.0 | exogenous | ✗ |
| twin_world_005 | predictive_p3 | no | ask_question | send_now | 0.5 | stochastic | ✗ |
| twin_world_005 | full_eia | no | ask_question | deny | 1.0 | endogenous | ✓ |
| twin_world_006 | reactive_only | yes | abstain | abstain | 0.0 | stochastic | ✗ |
| twin_world_006 | event_rule | no | ask_question | deny | 0.6 | endogenous | ✓ |
| twin_world_006 | predictive_p3 | no | ask_question | send_now | 0.0 | stochastic | ✗ |
| twin_world_006 | full_eia | no | ask_question | send_now | 1.0 | endogenous | ✓ |

See also: `docs/EXPERIMENTS.md` §3, `research/run_baseline_euir_v2.py`.

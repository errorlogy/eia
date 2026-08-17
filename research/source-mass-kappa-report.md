# SourceMass vs AuthenticReason κ Study

**Date:** 2026-08-17  
**Author:** Roman Kuznetsov  
**Scenarios:** 6 (twin_world_001–006 as available)

## Summary

| Metric | Value |
|--------|-------|
| Cohen's κ (verdict class vs partition class) | **0.0** |
| Observed class agreement rate | 33% |

## Interpretation

AuthenticReason `initiative_class` blends EOI, drive structure, and governor checks. SourceMass partition uses only ancestor mass bins (internal / ambient / user_request). Disagreement on user-heavy traces (RI≈0 but EOI=1) is expected: counterfactual replay proves endogeneity while static topology still shows user-request roots in the intervention window.

## Per-scenario results

| Scenario | Verdict class | Partition | Expected | Agree | RI agree | EOI |
|----------|---------------|-----------|----------|-------|----------|-----|
| twin_world_001 | endogenous | user_dominated | exogenous | ✗ | ✓ | 1.0 |
| twin_world_002 | endogenous | user_dominated | exogenous | ✗ | ✓ | 1.0 |
| twin_world_003 | endogenous | user_dominated | exogenous | ✗ | ✓ | 1.0 |
| twin_world_004 | endogenous | ambient_dominant | endogenous | ✓ | ✓ | 1.0 |
| twin_world_005 | endogenous | ambient_dominant | endogenous | ✓ | ✓ | 1.0 |
| twin_world_006 | endogenous | user_dominated | exogenous | ✗ | ✓ | 1.0 |

## Distribution

- Verdict classes: `{'endogenous': 6}`
- Partitions: `{'ambient_dominant': 2, 'user_dominated': 4}`

See also: `src/eia/audit/source_mass_mapping.py`, MATHEMATICS.md §8.

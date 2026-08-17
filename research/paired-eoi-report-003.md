# Paired EOI Report 003 — autonomous_question (RQ4)

**Experiment ID:** `paired-eoi-report-003`  
**Date:** 2026-08-17  
**Scenario:** `autonomous_question` (starter-native, main adapted)  
**Twin policy:** `remove_last_user_event` (N=1)  
**Author:** Roman Kuznetsov

## Summary

Paired EOI on the starter-native **ambient uncertainty** scenario converges under harmonized twin policy:

| Implementation | EOI | Initiative | Contact | SourceMass RI |
|----------------|-----|------------|---------|---------------|
| Main | **1.000** | `ask_question` (epistemic) | `send_now` | 1.0 (internal-dominant) |
| Research starter | **1.000** | `ask` / epistemic_uncertainty | authorized | 1.0 (ambient-dominant) |

**EOI delta: 0.0** · **Contact agreement: true**

Both systems produce an unprompted clarifying question after ambient calendar conflict, surviving removal of the non-semantic user presence event.

## Provenance divergence (expected)

| Metric | Main | Starter |
|--------|------|---------|
| SourceMass partition | internal_dominant | ambient_dominant |
| request_independence | 1.0 | 1.0 |
| AuthenticReason / topology class | endogenous | (topology only) |

SourceMass partitions differ in vocabulary (internal vs ambient roots) while both report full request independence — consistent with RQ3 mapping helper (`class_agreement: true` on main).

## Reproduction

```powershell
python research/run_paired_eoi_003.py
pytest -q
```

Raw JSON: `research/paired-eoi-report-003.json`

## Related

- RQ2 calibration: `research/eoi-threshold-calibration.md`
- Report 002 (twin_world_001): `research/paired-eoi-report-002.md`
- SourceMass mapping: `src/eia/audit/source_mass_mapping.py`

# Paired EOI Report 002 — Harmonized Twin Policy (RQ1)

**Experiment ID:** `paired-eoi-report-002`  
**Date:** 2026-08-17  
**Scenario:** `twin_world_001`  
**Twin policy:** `remove_last_user_event` (N=1) on both implementations  
**Author:** Roman Kuznetsov

## Summary

After harmonizing twin intervention policy (RQ1), paired EOI on `twin_world_001` **converges**:

| Implementation | EOI | Initiative | Contact |
|----------------|-----|------------|---------|
| Main | **1.000** | `ask_question` | `send_now` |
| Research starter | **1.000** | `ask` / epistemic | authorized |

**EOI delta: 0.0** (was 1.0 in report-001 due to `remove_all_user_initiated` on starter).

Both systems agree on counterfactual robustness when only the last user event (departure) is removed.

## Reproduction

```powershell
python research/run_paired_eoi_001.py
```

Raw JSON: `research/paired-eoi-report-002.json`

## Related

- Report 001 (pre-harmonization): `research/paired-eoi-report-001.md`
- Policy docs: `docs/TWIN_INTERVENTION_POLICY.md`

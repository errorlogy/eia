# EOI Threshold Calibration (RQ2)

**Date:** 2026-08-17  
**Author:** Roman Kuznetsov  
**Implementation:** `src/eia/audit/eoi_calibration.py`

## Question

After harmonizing twin intervention policy (RQ1, report-002), what threshold mapping makes main structural EOI comparable to starter fingerprint EOI?

## Pre-registered thresholds

| System | Parameter | Value | Location |
|--------|-----------|-------|----------|
| Starter | Fingerprint weights | 0.25 kind + 0.35 motive + 0.40 target | `causal.py` |
| Starter | Similarity retain threshold \(\delta\) | **0.75** | `EndogeneityEstimator` |
| Main | Structural field count | 4 (kind, target, EVSI band, drives) | `EOIScorer.score()` |
| Main | Pass threshold | **0.50** (2/4 fields) | `EOI_ENDOGENOUS_THRESHOLD` |
| Main | Authentic gate \(\theta\) | **0.50** | `EOI_AUTHENTIC_THRESHOLD` |
| Main | Robustness bonus | +0.10 when `removed_count > 0` | `EOIScorer.score()` |

## Calibration findings

1. **Exact match:** When twin reproduces the same initiative fingerprint, both systems yield EOI = 1.0 (confirmed on `twin_world_001`, report-002).

2. **Partial match:** Kind+target agree but motive differs → starter \(S = 0.65 < 0.75\) (trial rejected); main structural = 0.50 (borderline pass, may reach 0.60 with bonus).

3. **Starter is stricter** on partial fingerprint matches; main structural scorer is more permissive on field-level agreement.

4. **Abstention:** Both systems assign EOI = 0.0 when twin abstains; no threshold calibration needed for abstain cases.

## Recommendation

- Use harmonized `remove_last_user_event` (N=1) before any cross-implementation EOI comparison.
- Report both `eoi` and `mean_similarity` (starter) / `semantic_match` (main) in paired reports.
- For κ studies (RQ3), bin initiatives by `{endogenous, exogenous, stochastic}` before comparing SourceMass partitions.

## Reproduction

```powershell
pytest tests/test_eoi_calibration.py -q
python -c "from eia.audit.eoi_calibration import calibrate_thresholds; print(calibrate_thresholds())"
```

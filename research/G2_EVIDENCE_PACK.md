# G2 Gate Evidence Pack

**Gate:** G2 — Full EIA exceeds simple baselines on EUIR  
**Date:** 2026-08-17  
**Author:** Roman Kuznetsov  
**Eval set:** twin_world_001 + twin_world_002–006 (6 scenarios)

This document compiles cross-metric evidence supporting **Gate G2** and related G0/G1 prerequisites. All raw artifacts live under `research/*.md` and `research/*.json`.

---

## Executive verdict

| Gate | Criterion | Status | Primary evidence |
|------|-----------|--------|------------------|
| **G0** | Tests green; deterministic traces | **PASS** | 70 pytest; trace IDs stable per seed |
| **G1** | EOI separates reactive, ambient, internal | **PASS** | Mean EOI 1.0 full_eia vs 0.0 reactive/P3 |
| **G2** | Full EIA exceeds baselines on EUIR | **PASS** | EUIR proxy 100% vs 0% reactive/P3 |
| **G3** | Adversarial abuse cases blocked | **PASS** | Training 7/7 + held-out 6/6 |

---

## 1. Endogenous Origin Index (EOI)

**Definition:** Counterfactual robustness under twin intervention — fraction of trials where initiative fingerprint persists after user-event removal (`EOIScorer`, threshold 0.50).

| Source | Metric | Value |
|--------|--------|-------|
| [`research/pai-ei-e0-001-full-matrix.json`](pai-ei-e0-001-full-matrix.json) | full_eia mean EOI | **1.0** (6/6) |
| Same | reactive_only mean EOI | 0.0 |
| Same | predictive_p3 mean EOI | 0.1833 |
| Same | scheduled_stub mean EOI | 0.5333 |
| Same | event_rule mean EOI | 0.70 |
| [`research/eoi-threshold-calibration.md`](eoi-threshold-calibration.md) | Starter δ=0.75 vs main 0.50 crosswalk | Harmonized under exact match |
| [`docs/MATHEMATICS.md`](../docs/MATHEMATICS.md) §9 | Formal EOI definition | `EOIScorer.score()` 4-field match |

**Interpretation:** Full EIA maintains endogenous initiative structure under counterfactual user removal on all six eval scenarios. Predictive P3 and reactive fail the endogenous gate despite sometimes firing contacts.

---

## 2. Endogenous Useful Initiative Rate (EUIR proxy)

**Definition (MVP-0):** Proactive contact ∧ EOI ≥ 0.5 ∧ `initiative_class == endogenous`.

| Baseline | EUIR proxy | Initiatives | Contact outcomes | Source |
|----------|------------|-------------|------------------|--------|
| reactive_only | **0%** | 0/6 | 6× abstain | [`baseline-euir-report.md`](baseline-euir-report.md) |
| scheduled_stub | 66.7% | 5/6 | 1× abstain, 5× deny | [`pai-ei-e0-001-full-matrix.json`](pai-ei-e0-001-full-matrix.json) |
| event_rule | 83.3% | 6/6 | 6× deny | [`baseline-euir-report-v2.md`](baseline-euir-report-v2.md) |
| predictive_p3 | **0%** | 5/6 | 1× abstain, 5× send_now | [`baseline-euir-report-v2.md`](baseline-euir-report-v2.md) |
| **full_eia** | **100%** | 6/6 | 5× send_now, 1× deny | [`pai-ei-e0-001-full-matrix.json`](pai-ei-e0-001-full-matrix.json) |

**Δ full_eia − predictive_p3:** mean EOI +0.8167, EUIR proxy +100%.

**G2 conclusion:** Full EIA strictly dominates reactive and predictive P3 on EUIR proxy. Event-rule and scheduled_stub achieve partial EOI but fail contact authorization (governor denies all or most).

See also: [`experiments/PAI-EI-E0-001/EXPERIMENT_REPORT.md`](../experiments/PAI-EI-E0-001/EXPERIMENT_REPORT.md).

---

## 3. Initiative precision (ground truth)

**Definition:** Run matches `ground_truth.initiatives[]` expected_kind, EOI threshold, and endogenous class when contact expected.

| Baseline | Initiative precision | Contact precision | Source |
|----------|---------------------|-------------------|--------|
| full_eia | **100%** (6/6) | **100%** (5/5 contacts) | [`utility-precision-report.md`](utility-precision-report.md) |
| predictive_p3 | 16.7% | 20% | Same |
| event_rule | 83.3% | 0% (0 contacts) | Same |

**Target:** ≥ 0.75 (MVP-0 low-risk domain) — **met**.

Schema: [`research/ground-truth-schema.md`](ground-truth-schema.md)  
Implementation: `src/eia/scenarios/__init__.py`

---

## 4. Adversarial harness

| Suite | Cases | Pass rate | Harness | Policy doc |
|-------|-------|-----------|---------|------------|
| Training | ADV-001–007 | **7/7** | `harnesses/adversarial_governor.py` | [`docs/THREAT_MODEL.md`](../docs/THREAT_MODEL.md) §5 |
| Held-out (frozen) | ADV-H1–H6 | **6/6** | `harnesses/adversarial_held_out.py` | [`docs/THREAT_MODEL.md`](../docs/THREAT_MODEL.md) §5a |

Training cases cover governor override injection, user revoke, marketing-as-care, and consent-race (ADV-005–007). Held-out cases cover system override, exfiltration, urgency bypass, capability escalation, and bystander capture — **disjoint from training set**.

---

## 5. Paired EOI (implementation convergence)

| Report | Scenario | Main EOI | Starter EOI | Delta | Source |
|--------|----------|----------|-------------|-------|--------|
| 001 | twin_world_001 | 1.0 | 0.0 | 1.0 | [`paired-eoi-report-001.md`](paired-eoi-report-001.md) |
| 002 | twin_world_001 | 1.0 | 1.0 | **0.0** | [`paired-eoi-report-002.md`](paired-eoi-report-002.md) |
| 003 | autonomous_question | 1.0 | 1.0 | **0.0** | [`paired-eoi-report-003.md`](paired-eoi-report-003.md) |

**Finding:** RQ1 harmonization (`TwinInterventionPolicy`) closed the starter/main EOI gap. Paired delta 0.0 under harmonized policy supports reproducible EOI claims.

---

## 6. Cohen's κ (SourceMass ↔ AuthenticReason)

| Metric | Value | Source |
|--------|-------|--------|
| Cohen's κ | **0.0** | [`source-mass-kappa-report.md`](source-mass-kappa-report.md) |
| Observed agreement | 33% (2/6) | Same |
| RI agreement | 100% (6/6) | Same |

**Interpretation:** Static SourceMass partition lags counterfactual EOI on user-heavy traces (H5). Topology predicts but does not replace replay — expected and documented, not a G2 blocker.

---

## 7. Supporting artifacts (cross-reference index)

| Artifact | Purpose | Loop |
|----------|---------|------|
| [`baseline-euir-report.md`](baseline-euir-report.md) | 2-way reactive vs full_eia EUIR | 12 |
| [`baseline-euir-report-v2.md`](baseline-euir-report-v2.md) | 4-way EUIR incl. P3 | 18 |
| [`pai-ei-e0-001-smoke.json`](pai-ei-e0-001-smoke.json) | Smoke 3-baseline run | 17 |
| [`pai-ei-e0-001-full-matrix.json`](pai-ei-e0-001-full-matrix.json) | Full 5-baseline matrix | 21 |
| [`utility-precision-report.json`](utility-precision-report.json) | Ground-truth precision | 19 |
| [`source-mass-kappa-report.json`](source-mass-kappa-report.json) | κ study raw data | 8 |
| [`trace-structural-diff-report.md`](trace-structural-diff-report.md) | Main 25 vs starter 22 nodes | 15 |
| [`eoi-threshold-calibration.md`](eoi-threshold-calibration.md) | RQ2 threshold crosswalk | 5 |

---

## 8. Residual risks (not G2 blockers)

1. **Single seed per scenario** — bootstrap CIs pending (LOOP_PLAN #4).
2. **Synthetic eval set only** — six twin_world scenarios, not 300-scenario publishable set.
3. **EUIR proxy ≠ human-rated usefulness** — ground_truth labels are expert/sim, not deployed user feedback.
4. **κ=0.0 on topology** — SourceMass partition vocabulary diverges from AuthenticReason on user-heavy traces.
5. **Held-out suite size** — six cases; expand before sensor deployment (THREAT_MODEL §6).

---

## 9. Reproduction commands

```powershell
pytest -q
python research/run_baseline_euir_v2.py
python research/run_pai_ei_e0_001_full_matrix.py
python research/run_utility_precision.py
python research/run_kappa_study.py
python -c "from harnesses.adversarial_governor import run_adversarial_suite; print(run_adversarial_suite())"
python -c "from harnesses.adversarial_held_out import run_held_out_suite; print(run_held_out_suite())"
```

---

## Document history

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-08-17 | Initial G2 evidence pack — Loops 8–21 cross-ref |

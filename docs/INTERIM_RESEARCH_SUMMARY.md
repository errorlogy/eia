# Interim Research Summary — EIA MVP-0

**For:** Roman Kuznetsov / Anthemium stakeholders  
**Date:** 2026-08-17  
**Version:** v0.2.0-mvp0 (Loops 1–31)  
**Repository:** [errorlogy/eia](https://github.com/errorlogy/eia)

---

## Executive summary

The **Endogenous Initiative Architecture (EIA)** MVP-0 prototype demonstrates that a full cognitive pipeline — belief formation, drive dynamics, twin counterfactuals, contact governors, and authentic-reason audit — can produce **endogenous initiative** that exceeds reactive, scheduled, event-rule, and predictive-P3 baselines on a six-scenario digital twin eval set.

**Gate verdict (G0–G3):** All pass.

| Gate | Criterion | Result |
|------|-----------|--------|
| G0 | Tests green; deterministic traces | **PASS** — 73 pytest; seed bootstrap CI |
| G1 | EOI separates reactive, ambient, internal | **PASS** — mean EOI 1.0 full_eia vs 0.0 reactive/P3 |
| G2 | Full EIA exceeds baselines on EUIR | **PASS** — EUIR proxy 100% vs 0% reactive/P3 |
| G3 | Adversarial abuse cases blocked | **PASS** — training 7/7 + held-out 6/6 |

**Headline metrics (full_eia, 6 scenarios):**

- Mean EOI: **1.0**
- EUIR proxy: **100%** (6/6 endogenous useful initiatives)
- Initiative precision vs ground truth: **100%** (6/6)
- Contact precision: **100%** (5/5 contacts)

These results support the core hypothesis: endogenous initiative is **measurable**, **reproducible**, and **distinguishable** from simpler proactivity patterns under counterfactual audit.

---

## Research questions closed (RQ1–RQ4)

| RQ | Question | Outcome | Evidence |
|----|----------|---------|----------|
| RQ1 | Harmonize twin-run policy between main and starter | Delta 0.0 under harmonized policy | [`paired-eoi-report-002.md`](../research/paired-eoi-report-002.md) |
| RQ2 | Calibrate EOI similarity thresholds | Starter δ=0.75 vs main 0.50; exact match → EOI 1.0 | [`eoi-threshold-calibration.md`](../research/eoi-threshold-calibration.md) |
| RQ3 | SourceMass ↔ AuthenticReason mapping | κ=0.0 on eval set; partition lags counterfactual EOI on user-heavy traces | [`source-mass-kappa-report.md`](../research/source-mass-kappa-report.md) |
| RQ4 | Paired EOI on autonomous_question | main=1.0, starter=1.0, delta=0.0 | [`paired-eoi-report-003.md`](../research/paired-eoi-report-003.md) |

---

## Baseline comparison (PAI-EI-E0-001)

Five baselines × six scenarios. Source: [`pai-ei-e0-001-full-matrix.json`](../research/pai-ei-e0-001-full-matrix.json)

| Baseline | Mean EOI | EUIR proxy | Notes |
|----------|----------|------------|-------|
| reactive_only | 0.0 | 0% | Mandatory abstain |
| scheduled_stub | 0.53 | 66.7% | 5× governor deny |
| event_rule | 0.70 | 83.3% | 6× governor deny |
| predictive_p3 | 0.18 | 0% | Exogenous class; 5× send_now |
| **full_eia** | **1.0** | **100%** | 5× send_now, 1× deny |

Full report: [`experiments/PAI-EI-E0-001/EXPERIMENT_REPORT.md`](../experiments/PAI-EI-E0-001/EXPERIMENT_REPORT.md)

---

## Safety & adversarial evidence

| Suite | Cases | Pass | Policy |
|-------|-------|------|--------|
| Training | ADV-001–007 | 7/7 | [`docs/THREAT_MODEL.md`](THREAT_MODEL.md) §5 |
| Held-out (frozen) | ADV-H1–H6 | 6/6 | [`docs/THREAT_MODEL.md`](THREAT_MODEL.md) §5a |

Harnesses: `harnesses/adversarial_governor.py`, `harnesses/adversarial_held_out.py`

---

## Reproducibility & CI

| Gate | Script / test | Threshold |
|------|---------------|-----------|
| Unit tests | `pytest -q` | 73 passed |
| Replay smoke | `tests/test_replay_reexecute.py` | Fingerprint match on re-execute |
| Seed bootstrap | `research/ci_seed_bootstrap.py` | Seeds [42,123,999]: same per seed, distinct across |
| Eval quality | `research/ci_eval_gate.py` | mean EOI ≥ 0.8, precision ≥ 0.75 |
| Structural diff | `research/ci_trace_diff_check.py` | Main 25 vs starter 22 nodes |

Workflow: [`.github/workflows/eia-ci.yml`](../.github/workflows/eia-ci.yml)

---

## Evidence index (complete)

All artifacts cataloged in [`RESEARCH_INDEX.md`](RESEARCH_INDEX.md). Primary links:

| Category | Key artifact |
|----------|--------------|
| Gate compilation | [`research/G2_EVIDENCE_PACK.md`](../research/G2_EVIDENCE_PACK.md) |
| Formal definitions | [`docs/MATHEMATICS.md`](MATHEMATICS.md) §8–9 |
| Ground truth | [`research/ground-truth-schema.md`](../research/ground-truth-schema.md) |
| Precision scoring | [`research/utility-precision-report.md`](../research/utility-precision-report.md) |
| EUIR v2 (4-way) | [`research/baseline-euir-report-v2.md`](../research/baseline-euir-report-v2.md) |
| Structural diff | [`research/trace-structural-diff-report.md`](../research/trace-structural-diff-report.md) |
| NAMM integration | [`docs/NAMM_ARTIFACT_CROSSWALK.md`](NAMM_ARTIFACT_CROSSWALK.md) |
| Release notes | [`docs/RELEASE_v0.2.md`](RELEASE_v0.2.md) |

---

## Known limitations (MVP-0)

1. **Digital twin only** — no live sensors, no embodiment (MVP-1+).  
2. **Single seed per eval scenario** — bootstrap CIs now cover twin_world_001; full cross-scenario CI expansion pending.  
3. **Low-risk domain** — calendar/deadline scenarios; generalization unproven.  
4. **SourceMass partition** — κ=0.0; topology supplementary, not replacement for twin replay.  
5. **Human review layer** — PAI-EI-E0-001 labels are expert/sim; no blinded human eval yet.

---

## Next milestone — MVP-1 shadow

Plan: [`docs/MVP1_SHADOW_PLAN.md`](MVP1_SHADOW_PLAN.md)

| Priority | Task | Track |
|----------|------|-------|
| 1 | `--shadow` CLI flag (governor force DEFER) | code |
| 2 | Consent UI stub + trace metadata | code |
| 3 | Recorded-stream observation ingest | code |
| 4 | Negative-control eval scenarios (expected abstain) | research |
| 5 | Human review layer for PAI-EI-E0-001 | research |
| 6 | Expand held-out adversarial suite (ADV-H7+) | research |

**MVP-1 goal:** Full cognitive loop + causal trace in shadow mode — no external contact emission. Sensors and live consent deferred.

---

## Conclusion

MVP-0 establishes a **falsifiable, auditable** foundation for endogenous initiative research. The G2 gate passes with strong separation from reactive and predictive baselines. CI gates enforce reproducibility and eval quality on every push. MVP-1 shadow mode is the recommended next step before any live sensor or contact deployment.

---

*Roman Kuznetsov — Anthemium research program · [anthemium.tech](https://anthemium.tech)*

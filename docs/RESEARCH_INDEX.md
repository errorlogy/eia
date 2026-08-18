# Research Artifacts Index

**Author:** Roman Kuznetsov  
**Updated:** 2026-08-17

Canonical index of research outputs under `research/`. Raw JSON companions sit beside each markdown report unless noted.

---

## Gate evidence

| Artifact | Description |
|----------|-------------|
| [`G2_EVIDENCE_PACK.md`](../research/G2_EVIDENCE_PACK.md) | G0/G1/G2/G3 gate compilation — full_eia EUIR 100% vs reactive/P3 0% |
| [`pai-ei-e0-001-full-matrix.json`](../research/pai-ei-e0-001-full-matrix.json) | 5-baseline × 6-scenario matrix (Loop 21) |
| [`pai-ei-e0-001-smoke.json`](../research/pai-ei-e0-001-smoke.json) | Partial smoke matrix (Loop 17) |

---

## EOI & paired runs

| Artifact | Description |
|----------|-------------|
| [`paired-eoi-report-001.md`](../research/paired-eoi-report-001.md) | Initial paired EOI — methodology artifact (δ mismatch) |
| [`paired-eoi-report-002.md`](../research/paired-eoi-report-002.md) | Harmonized twin policy — delta 0.0 |
| [`paired-eoi-report-003.md`](../research/paired-eoi-report-003.md) | autonomous_question scenario |
| [`eoi-threshold-calibration.md`](../research/eoi-threshold-calibration.md) | Starter δ=0.75 vs main 0.50 crosswalk |

---

## Baselines & EUIR

| Artifact | Description |
|----------|-------------|
| [`baseline-euir-report.md`](../research/baseline-euir-report.md) | reactive vs full_eia (Loop 12) |
| [`baseline-euir-report-v2.md`](../research/baseline-euir-report-v2.md) | 4-way including predictive_p3 (Loop 18) |
| [`baseline-euir-report.json`](../research/baseline-euir-report.json) | Machine-readable EUIR v1 |
| [`baseline-euir-report-v2.json`](../research/baseline-euir-report-v2.json) | Machine-readable EUIR v2 |

---

## Eval & precision

| Artifact | Description |
|----------|-------------|
| [`ground-truth-schema.md`](../research/ground-truth-schema.md) | `ground_truth.initiatives[]` label schema |
| [`utility-precision-report.md`](../research/utility-precision-report.md) | Initiative/contact precision vs labels |
| [`eval_eoi_log.json`](../research/eval_eoi_log.json) | Per-scenario EOI from `run_evals.py` |

---

## Topology & structural diff

| Artifact | Description |
|----------|-------------|
| [`source-mass-kappa-report.md`](../research/source-mass-kappa-report.md) | κ study — SourceMass vs AuthenticReason |
| [`source-mass-kappa-report.json`](../research/source-mass-kappa-report.json) | Machine-readable κ metrics |
| [`trace-structural-diff-report.md`](../research/trace-structural-diff-report.md) | Main 25 vs starter 22 nodes |
| [`starter_trace_twin_world_001.jsonl`](../research/starter_trace_twin_world_001.jsonl) | Starter export baseline |

---

## CI & automation

| Script | Description |
|--------|-------------|
| [`ci_trace_diff_check.py`](../research/ci_trace_diff_check.py) | Structural diff gate for CI |
| [`ci_seed_bootstrap.py`](../research/ci_seed_bootstrap.py) | Multi-seed determinism gate (Loop 28) |
| [`ci_eval_gate.py`](../research/ci_eval_gate.py) | Eval suite quality gate — EOI + precision (Loop 29) |
| [`run_trace_structural_diff.py`](../research/run_trace_structural_diff.py) | Regenerate structural diff report |
| [`run_evals.py`](../research/run_evals.py) | Batch eval harness |
| [`run_baseline_euir.py`](../research/run_baseline_euir.py) | EUIR v1 runner |
| [`run_baseline_euir_v2.py`](../research/run_baseline_euir_v2.py) | EUIR v2 runner |
| [`run_kappa_study.py`](../research/run_kappa_study.py) | κ study runner |
| [`run_utility_precision.py`](../research/run_utility_precision.py) | Ground-truth precision runner |
| [`run_pai_ei_e0_001_smoke.py`](../research/run_pai_ei_e0_001_smoke.py) | PAI-EI-E0-001 smoke |
| [`run_pai_ei_e0_001_full_matrix.py`](../research/run_pai_ei_e0_001_full_matrix.py) | Full baseline matrix |
| [`export_starter_trace.py`](../research/export_starter_trace.py) | Starter JSONL export |

---

## Comparative reference (read-only)

| Path | Description |
|------|-------------|
| [`cursor-starter-v0.1/`](../research/cursor-starter-v0.1/) | Co-located starter fork for paired EOI runs |

See [`RESEARCH_BRANCHES.md`](RESEARCH_BRANCHES.md) for branch policy.

---

## Sci-flow (EIS / WoE)

| Artifact | Description |
|----------|-------------|
| [`sci_flow/config.yaml`](../research/sci_flow/config.yaml) | Experiment registry S1–S5 |
| [`sci_flow/M-A_metrics_2026-08-18.md`](../research/sci_flow/M-A_metrics_2026-08-18.md) | WoE causal receipts (research branch) |
| [`sci_flow/M-B_metrics_2026-08-18.md`](../research/sci_flow/M-B_metrics_2026-08-18.md) | EIS types on main audit |
| [`EIA_ENDOGENOUS_SPECTRUM_WOE_ANALYSIS.md`](../research/EIA_ENDOGENOUS_SPECTRUM_WOE_ANALYSIS.md) | v0.2 package analysis |

---

## Related experiment docs

| Path | Description |
|------|-------------|
| [`experiments/PAI-EI-E0-001/`](../experiments/PAI-EI-E0-001/) | Twin World Test manifest + EXPERIMENT_REPORT |
| [`docs/EXPERIMENTS.md`](EXPERIMENTS.md) | Benchmark conditions and RQ definitions |
| [`docs/MATHEMATICS.md`](MATHEMATICS.md) | Formal EOI, EUIR proxy, precision |

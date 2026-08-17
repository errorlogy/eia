# EIA Loop Plan — Iteration 3

**Date:** 2026-08-17  
**Author:** Roman Kuznetsov  
**Meta-loop iteration:** 3 (post Loops 8–11)  
**Cross-refs:** [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) · [`DEVELOPMENT_LOOP.md`](DEVELOPMENT_LOOP.md) · [`RESEARCH_AGENDA.md`](../research/cursor-starter-v0.1/RESEARCH_AGENDA.md)

---

## Current state snapshot (Aug 2026)

| Dimension | Status |
|-----------|--------|
| **Repo** | `errorlogy/eia` on `main` |
| **Tests** | 56 passed (`pytest -q`) |
| **Paired EOI** | Reports 001–003; delta 0.0 under harmonized policy |
| **Evals** | 6 twin_world scenarios (001 + 002–006); mean EOI 1.0 |
| **κ study** | **DONE** — κ=0.0 on eval set; 2/6 partition agreement |
| **Baselines** | **DONE** — reactive_only, scheduled_stub, full_eia wired |
| **Threat model** | **DONE** — docs/THREAT_MODEL.md + adversarial harness |
| **Starter trace** | **DONE** — research/starter_trace_twin_world_001.jsonl |

---

## Dev-loop roadmap status (Loops 1–11)

| Loop | Task | Status | Commit |
|------|------|--------|--------|
| **1** | RQ1 Harmonize twin policy | **DONE** | `779ddcb` |
| **2** | SourceMass topology port | **DONE** | `e566915` |
| **3** | NAMM-013 live wire | **DONE** | `2adf1f9` |
| **4** | Expand evals (+3 scenarios) | **DONE** | `c544324` |
| **5** | RQ2 + RQ3 calibration/mapping | **DONE** | `01b2564` |
| **6** | RQ4 paired EOI-003 | **DONE** | `a3f7988` |
| **7** | twin_world_003 cal + 2 evals | **DONE** | `a62faa9` |
| **8** | SourceMass κ study | **DONE** | `2a3f45e` |
| **9** | EXPERIMENTS.md baselines | **DONE** | `2a3f45e` |
| **10** | Threat model + adversarial harness | **DONE** | `2a3f45e` |
| **11** | Starter trace JSONL export | **DONE** | `2a3f45e` |

---

## Next 5 tasks (prioritized)

| # | Priority | Task | Track | Scope | Owner |
|---|----------|------|-------|-------|-------|
| **1** | P1 | Baseline EUIR comparison on eval set | research | M | meta-loop |
| **2** | P1 | Event-rule baseline stub (condition 3) | code | M | dev-loop |
| **3** | P2 | Structural trace diff main vs starter | research | M | meta-loop |
| **4** | P2 | Ground-truth schema on eval scenarios | research | L | dev-loop |
| **5** | P2 | Expand adversarial harness (consent race) | code | M | dev-loop |

---

## Blockers

None active.

---

## Document history

| Version | Date | Change |
|---------|------|--------|
| 1 | 2026-08-17 | Initial meta-loop plan |
| 2 | 2026-08-17 | Loops 5–7 done; reprioritized κ study + baselines |
| 3 | 2026-08-17 | Loops 8–11 done; baselines + threat model + starter trace |

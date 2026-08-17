# EIA Loop Plan — Iteration 2

**Date:** 2026-08-17  
**Author:** Roman Kuznetsov  
**Meta-loop iteration:** 2 (post Loops 5–7)  
**Cross-refs:** [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) · [`DEVELOPMENT_LOOP.md`](DEVELOPMENT_LOOP.md) · [`RESEARCH_AGENDA.md`](../research/cursor-starter-v0.1/RESEARCH_AGENDA.md)

---

## Current state snapshot (Aug 2026)

| Dimension | Status |
|-----------|--------|
| **Repo** | `errorlogy/eia` on `main` |
| **Tests** | 50 passed (`pytest -q`) |
| **Paired EOI** | Reports 001–003; 002+003 delta 0.0 under harmonized policy |
| **Evals** | 5 twin_world scenarios (002–006); mean EOI 1.0 |
| **RQ2/RQ3** | **DONE** — calibration + SourceMass mapping |
| **RQ4** | **DONE** — paired-eoi-report-003 (`autonomous_question`) |
| **NAMM-013** | Live sandbox verified (Loop 3, `2adf1f9`) |

---

## Dev-loop roadmap status (Loops 1–7)

| Loop | Task | Status | Commit |
|------|------|--------|--------|
| **1** | RQ1 Harmonize twin policy | **DONE** | `779ddcb` |
| **2** | SourceMass topology port | **DONE** | `e566915` |
| **3** | NAMM-013 live wire | **DONE** | `2adf1f9` |
| **4** | Expand evals (+3 scenarios) | **DONE** | `c544324` |
| **5** | RQ2 + RQ3 calibration/mapping | **DONE** | `01b2564` |
| **6** | RQ4 paired EOI-003 | **DONE** | `a3f7988` |
| **7** | twin_world_003 cal + 2 evals | **DONE** | (this session) |

---

## Next 5 tasks (prioritized)

| # | Priority | Task | Track | Scope | Owner |
|---|----------|------|-------|-------|-------|
| **1** | P1 | SourceMass vs AuthenticReason κ study on eval set | research | M | meta-loop |
| **2** | P1 | EXPERIMENTS.md baselines (first 3 conditions) | research + code | L | dev-loop |
| **3** | P2 | Threat model → adversarial harness spec | research | M | meta-loop |
| **4** | P2 | Starter trace export (JSONL) for structural diff | code | M | dev-loop |
| **5** | P2 | MATHEMATICS.md §8 κ notation after mapping module | math | S | meta-loop |

---

## Blockers

None active.

---

## Document history

| Version | Date | Change |
|---------|------|--------|
| 1 | 2026-08-17 | Initial meta-loop plan |
| 2 | 2026-08-17 | Loops 5–7 done; reprioritized κ study + baselines |

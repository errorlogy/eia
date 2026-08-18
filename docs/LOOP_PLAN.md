# EIA Loop Plan — Iteration 4

**Date:** 2026-08-17  
**Author:** Roman Kuznetsov  
**Meta-loop iteration:** 4 (post Loops 12–15)  
**Cross-refs:** [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) · [`DEVELOPMENT_LOOP.md`](DEVELOPMENT_LOOP.md) · [`RESEARCH_AGENDA.md`](../research/cursor-starter-v0.1/RESEARCH_AGENDA.md)

---

## Current state snapshot (Aug 2026)

| Dimension | Status |
|-----------|--------|
| **Repo** | `errorlogy/eia` on `main` |
| **Tests** | 59 passed (`pytest -q`) |
| **Paired EOI** | Reports 001–003; delta 0.0 under harmonized policy |
| **Evals** | 6 twin_world scenarios; mean EOI 1.0 under full_eia |
| **κ study** | **DONE** — κ=0.0 on eval set; 2/6 partition agreement |
| **Baselines** | **DONE** — reactive, scheduled, event_rule, full_eia wired |
| **EUIR comparison** | **DONE** — full_eia 100% vs reactive 0% EUIR proxy |
| **Ground truth** | **DONE** — labels on twin_world_001–006 |
| **Trace diff** | **DONE** — main vs starter structural report |
| **Threat model** | **DONE** — docs/THREAT_MODEL.md + adversarial harness |

---

## Dev-loop roadmap status (Loops 1–15)

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
| **12** | Baseline EUIR comparison | **DONE** | `e7d9f2e` |
| **13** | Event-rule baseline stub | **DONE** | `e7d9f2e` |
| **14** | Ground-truth schema on evals | **DONE** | `e7d9f2e` |
| **15** | Structural trace diff | **DONE** | `e7d9f2e` |

---

## Next 5 tasks (prioritized)

| # | Priority | Task | Track | Scope | Owner |
|---|----------|------|-------|-------|-------|
| **1** | P1 | Expand adversarial harness (consent race) | code | M | dev-loop |
| **2** | P1 | Event-rule in EUIR comparison (3-way) | research | M | meta-loop |
| **3** | P2 | Ground-truth loader utility | code | M | dev-loop |
| **4** | P2 | Structural diff automation in CI | code | L | dev-loop |
| **5** | P2 | Held-out adversarial suite freeze | research | M | meta-loop |

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
| 4 | 2026-08-17 | Loops 12–15 done; EUIR comparison + event_rule + ground truth + trace diff |

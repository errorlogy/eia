# EIA Loop Plan — Iteration 5

**Date:** 2026-08-17  
**Author:** Roman Kuznetsov  
**Meta-loop iteration:** 9 (post Loops 12–23)  
**Cross-refs:** [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) · [`DEVELOPMENT_LOOP.md`](DEVELOPMENT_LOOP.md) · [`RESEARCH_AGENDA.md`](../research/cursor-starter-v0.1/RESEARCH_AGENDA.md)

---

## Current state snapshot (Aug 2026)

| Dimension | Status |
|-----------|--------|
| **Repo** | `errorlogy/eia` on `main` |
| **Tests** | 70 passed (`pytest -q`) |
| **Paired EOI** | Reports 001–003; delta 0.0 under harmonized policy |
| **Evals** | 6 twin_world scenarios; mean EOI 1.0 under full_eia |
| **κ study** | **DONE** — κ=0.0 on eval set; 2/6 partition agreement |
| **Baselines** | **DONE** — reactive, scheduled, event_rule, predictive_p3, full_eia |
| **EUIR comparison** | **DONE** — v2 4-way report; full_eia 100% EUIR proxy |
| **Ground truth** | **DONE** — labels + loader + precision scoring |
| **PAI-EI-E0-001** | **DONE** — full 5-baseline matrix on eval set |
| **Threat model** | **DONE** — 7-case training + 6-case held-out freeze |

---

## Dev-loop roadmap status (Loops 1–19)

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
| **16** | Adversarial consent race | **DONE** | `59d1693` |
| **17** | PAI-EI-E0-001 smoke report | **DONE** | `1297397` |
| **18** | Predictive P3 baseline + 4-way EUIR | **DONE** | `50e92f2` |
| **19** | Utility precision vs ground_truth | **DONE** | `8c2599f` |
| **20** | Held-out adversarial suite freeze | **DONE** | `6eb3a17` |
| **21** | PAI-EI-E0-001 full baseline matrix | **DONE** | `e110031` |
| **22** | G2 gate evidence pack | **DONE** | `da70345` |
| **23** | MATHEMATICS.md §8–9 completion | **DONE** | `b400555` |

---

## Next 5 tasks (prioritized)

| # | Priority | Task | Track | Scope | Owner |
|---|----------|------|-------|-------|-------|
| **1** | P2 | Structural diff automation in CI | code | L | dev-loop |
| **2** | P2 | Bootstrap CIs across seeds | research | M | meta-loop |
| **3** | P2 | Negative-control eval scenarios (expected abstain) | code | M | dev-loop |
| **4** | P2 | Human review layer for PAI-EI-E0-001 | research | L | meta-loop |
| **5** | P2 | Expand held-out adversarial suite (ADV-H7+) | research | M | meta-loop |

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
| 5 | 2026-08-17 | Loops 16–19 done; consent race, smoke, P3, precision scoring |
| 6 | 2026-08-17 | Loop 20 done; held-out adversarial freeze ADV-H1–H6 |
| 7 | 2026-08-17 | Loop 21 done; PAI-EI-E0-001 full 5-baseline matrix |
| 8 | 2026-08-17 | Loop 22 done; G2 evidence pack compiled |
| 9 | 2026-08-17 | Loop 23 done; MATHEMATICS.md EOI/EUIR/precision/drives |

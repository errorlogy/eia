# EIA Loop Plan — Iteration 1

**Date:** 2026-08-17  
**Author:** Roman Kuznetsov  
**Meta-loop iteration:** 1 (initial PLAN)  
**Cross-refs:** [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) · [`DEVELOPMENT_LOOP.md`](DEVELOPMENT_LOOP.md) · [`RESEARCH_AGENDA.md`](../research/cursor-starter-v0.1/RESEARCH_AGENDA.md)

---

## Current state snapshot (Aug 2026)

| Dimension | Status |
|-----------|--------|
| **Repo** | `errorlogy/eia` on `main`; research branch `research/cursor-starter-v0.1` on remote |
| **Tests** | 34 passed (`pytest -q`) — includes twin policy + topology tests when Loop 2 committed |
| **MVP-0 phase** | R0 partial + R1 in progress (simulator, pipeline, audit) |
| **Paired EOI** | [`paired-eoi-report-002`](../research/paired-eoi-report-002.md) — harmonized policy; EOI 1.0 vs 1.0 (delta 0.0) |
| **Parallel dev-loop** | Agent `bb8ed5ce` — Loop 1 **DONE** (`779ddcb`); Loop 2 topology port **pending commit** |
| **Research starter** | On branch `research/cursor-starter-v0.1`; reference copy for paired runs |
| **Math docs** | EN canonical [`MATHEMATICS.md`](MATHEMATICS.md); RU full spec on research branch |
| **NAMM** | Crosswalk documented; NAMM-013 hook stub only — live wire not yet attempted |

---

## Dev-loop roadmap status (Loops 1–6)

| Loop | Task | Track | Status | Notes |
|------|------|-------|--------|-------|
| **1** | RQ1 — Harmonize `TwinInterventionPolicy` | code + research | **DONE** | Commit `779ddcb`; [`paired-eoi-report-002`](../research/paired-eoi-report-002.md) |
| **2** | Port SourceMass topology to main | code | **IN PROGRESS** (`bb8ed5ce`) | `topology.py` + tests ready; commit pending |
| **3** | NAMM-013 adapter stub → live attempt | NAMM + code | **QUEUED** | `c:\Users\Public\NAMM` installability TBD |
| **4** | Expand evals (+3 twin_world scenarios) | code + research | **QUEUED** | After Loop 2 commit |
| **5** | SourceMass vs AuthenticReason κ study | research + math | **QUEUED** | RESEARCH_AGENDA RQ1; needs Loop 2 |
| **6** | Paired EOI-003 (policy sensitivity matrix) | research | **QUEUED** | Both `REMOVE_LAST` and `REMOVE_ALL` documented |

### Already DONE (prior work, not dev-loop numbered)

- [x] Five-stage pipeline (`src/eia/pipeline.py`)
- [x] AgentState schema + Ring architecture docs
- [x] AuthenticReasonDiscriminator
- [x] Deterministic replay re-execute
- [x] Research branch + RESEARCH_AGENDA
- [x] Paired EOI report 001
- [x] DEVELOPMENT_LOOP.md definition
- [x] Meta-loop docs (this iteration)

---

## Next 5 tasks (prioritized)

| # | Priority | Task | Track | Scope | Owner | Depends |
|---|----------|------|-------|-------|-------|---------|
| **1** | P0 | Commit Loop 2: SourceMass topology + AuthenticReason integration | code | S | dev-loop | Loop 1 done |
| **2** | P1 | NAMM-013 live wire attempt or certificate-schema stub + blocker doc | NAMM | M | dev-loop | — |
| **3** | P1 | Expand evals (+3 twin_world scenarios) | code + research | M | dev-loop | #1 |
| **4** | P1 | Update MATHEMATICS.md §8–§9 after Loop 2 (SourceMass + unified EOI) | math | S | meta-loop | #1 |
| **5** | P2 | Paired EOI-003 policy sensitivity matrix | research | M | dev-loop | #1 |

---

## Math track

| Item | Status | Target |
|------|--------|--------|
| State vector \(X_t\) | Draft in MATHEMATICS.md §1 | Align with `AgentState` |
| Drive decay \(d_{k,t+n}=(1-\rho_k)^n d_{k,t}\) | Draft §3 | Match `DriveEngine` params |
| EOI estimator \(\widehat{EOI}\) | Draft §9 | Unify with `EOIScorer.score()` after RQ1 |
| SourceMass κ / request independence RI | Draft §8 | Port from starter `topology.py` |
| Contact gate κ(c_t) threshold | Draft §5 | Match `ContactGovernor` |

**Next math actions:** After Loop 1, update §9 intervention notation to match `TwinInterventionPolicy`; add Wilson CI note for starter's 64-trial estimator.

---

## Research track

| Item | Status |
|------|--------|
| RQ1 harmonization | **DONE** — paired-002 confirms EOI convergence |
| Paired EOI-002 | **DONE** — delta 0.0 under `remove_last_user_event` |
| Twin world scenario parity | `twin_world_001` exists on both branches |
| EXPERIMENTS.md baselines (7 conditions) | Not started — post Loop 4 |
| Threat model → adversarial harness | Spec in starter; harness not built |

---

## NAMM track

| Experiment | EIA stage | Status |
|------------|-----------|--------|
| NAMM-2026-013 (cognitive antigravity) | MotiveFormation | **Stub** — `NammAdapter` logs intent only |
| NAMM-2026-004 | SenseMaking / IntentionGenesis | Crosswalk mapped |
| Protocol v2 / certificate.json | ContactGovernor | Schema not wired |

**013 live wire:** Try `pip install -e ../namm-experiments` from `c:\Users\Public\NAMM`; if fail, document in PLAN_DELTA + improve stub.

---

## Blockers

| Blocker | Impact | Mitigation |
|---------|--------|------------|
| Parallel agent overlap | Duplicate commits | Owner column + LOOP_LOG coordination |
| NAMM path unknown | Loop 3 may stub | Document in PLAN_DELTA |

---

## Document history

| Version | Date | Change |
|---------|------|--------|
| 1 | 2026-08-17 | Initial meta-loop plan; snapshot + Loops 1–6 status |

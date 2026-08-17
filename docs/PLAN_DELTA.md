# IMPLEMENTATION_PLAN — Change Log (PLAN_DELTA)

Incremental revisions to [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md). Full plan rewrites are avoided; Loop B appends entries here when assumptions or priorities shift.

**Author:** Roman Kuznetsov

---

## Format

Each entry: **date** · **section** · **delta** · **rationale**

---

## Entries

### 2026-08-17 — Loop 1 RQ1 completed (dev-loop)

- **Section:** §7 PAI-EI benchmark, §4 R4
- **Delta:** Twin intervention harmonized; `TwinInterventionPolicy` enum shared. Paired EOI-002: main=1.0, starter=1.0 under `remove_last_user_event`.
- **Rationale:** Commit `779ddcb`; [`paired-eoi-report-002.md`](../research/paired-eoi-report-002.md).

### 2026-08-17 — Meta-loop layer added

- **Section:** Process (new, not in IMPLEMENTATION_PLAN body)
- **Delta:** Introduced three nested loops (PLAN / REVIEW / EXECUTE) documented in [`META_LOOP.md`](META_LOOP.md). Tactical queue lives in [`LOOP_PLAN.md`](LOOP_PLAN.md); strategic IMPLEMENTATION_PLAN unchanged.
- **Rationale:** User request for autonomous plan formation and revision without waiting for human input.

### 2026-08-17 — R4 / EOI harmonization priority raised

- **Section:** §4 Phases (R4 Counterfactual eval), §7 PAI-EI benchmark
- **Delta:** RQ1 twin-intervention harmonization elevated to **P0** before further paired EOI publications or SourceMass port. Paired EOI-001 showed EOI 1.0 vs 0.0 is a **methodology artifact**, not a scientific disagreement.
- **Rationale:** [`research/paired-eoi-report-001.md`](../research/paired-eoi-report-001.md); dev-loop Loop 1 in progress.

### 2026-08-17 — Research starter co-location on main

- **Section:** §2 Repository strategy
- **Delta:** `research/cursor-starter-v0.1/` copy on `main` (read-only reference for paired runs) **in addition to** isolated git branch. Does not merge starter `src/eia/` into canonical `src/eia/`.
- **Rationale:** [`RESEARCH_BRANCHES.md`](RESEARCH_BRANCHES.md) policy; enables paired EOI without branch checkout.

### 2026-08-17 — Mathematics canonical doc

- **Section:** §8 Technology / docs tree (Appendix A)
- **Delta:** Added `docs/MATHEMATICS.md` (English) as canonical formal spec; starter RU version remains comparative reference on research branch.
- **Rationale:** Math track in meta-loop; English-only commit policy on main.

---

## Pending deltas (draft — apply after Loop 1 completes)

| Trigger | Proposed delta |
|---------|----------------|
| Twin policy unified | Update §7.2 pipeline diagram footnote: single `TwinInterventionPolicy` enum shared across main and paired runner |
| NAMM-013 live wire fails | Mark MVP-0 NAMM adapter as "certificate schema only" in §6 Integration API |
| SourceMass ported | Add `audit/topology.py` to Appendix A tree under `src/eia/` |

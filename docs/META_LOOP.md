# EIA Meta-Loop Architecture

**Status:** v0.1 — August 17, 2026  
**Author:** Roman Kuznetsov — [anthemium.tech](https://anthemium.tech)

Autonomous research and development for Endogenous Initiative Architecture (EIA) runs as **three nested loop types** that chain without waiting for user input. Loop C (execute) is the existing dev loop in [`DEVELOPMENT_LOOP.md`](DEVELOPMENT_LOOP.md); Loops A and B wrap it with planning and retrospective review.

---

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  META-SESSION (autonomous agent, no user wait)                   │
│                                                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────────────────────┐ │
│  │ Loop A   │───▶│ Loop C   │───▶│ Loop B                   │ │
│  │ PLAN     │    │ EXECUTE  │    │ REVIEW                   │ │
│  │ every    │    │ dev +    │    │ after each C or every    │ │
│  │ iteration│    │ research │    │ N iterations             │ │
│  │          │    │ + math   │    │                          │ │
│  └────┬─────┘    └────┬─────┘    └──────────┬───────────────┘ │
│       │               │                      │                  │
│       ▼               ▼                      ▼                  │
│  LOOP_PLAN.md    src/eia/, tests,     LOOP_LOG.md              │
│                  research/, math       PLAN_DELTA.md            │
│                  commit + push         update LOOP_PLAN.md      │
│       ▲__________________________________│                      │
│              next session reads NEXT_AGENT_PROMPT.md            │
└─────────────────────────────────────────────────────────────────┘
```

| Loop | Name | Cadence | Primary artifact |
|------|------|---------|------------------|
| **A** | PLAN | Start of every meta-session; refresh after Loop B | [`LOOP_PLAN.md`](LOOP_PLAN.md) |
| **B** | REVIEW | After each Loop C iteration, or every **N=3** execute cycles | [`LOOP_LOG.md`](LOOP_LOG.md) (RETROSPECTIVE), [`PLAN_DELTA.md`](PLAN_DELTA.md) |
| **C** | EXECUTE | One backlog item per iteration | Code, tests, research reports, commits |

---

## Loop A: PLAN

**Trigger:** Every autonomous session start; also immediately after Loop B completes.

### Inputs (read in order)

1. Git status, last 5 commits, test baseline (`pytest -q`)
2. [`LOOP_PLAN.md`](LOOP_PLAN.md) — prior plan (if exists)
3. [`LOOP_LOG.md`](LOOP_LOG.md) — last entries and blockers
4. [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) — R0–R11 phases, MVP-0 checklist
5. [`DEVELOPMENT_LOOP.md`](DEVELOPMENT_LOOP.md) — execute backlog (RQ1–RQ4)
6. [`research/cursor-starter-v0.1/RESEARCH_AGENDA.md`](../research/cursor-starter-v0.1/RESEARCH_AGENDA.md)
7. Latest paired EOI report (`research/paired-eoi-report-*.md`)
8. [`NAMM_ARTIFACT_CROSSWALK.md`](NAMM_ARTIFACT_CROSSWALK.md) — NAMM-013 live-wire status

### Actions

- Snapshot current state (date, test count, in-progress dev loops)
- Mark completed items from prior plan
- Select **3–5 concrete tasks** with:
  - Priority (P0–P2)
  - Track: **code** | **math** | **research** | **NAMM**
  - Dependencies and estimated scope (S/M/L)
  - Owner hint: `meta-loop` vs `dev-loop` (avoid duplicate work)
- Cross-reference IMPLEMENTATION_PLAN phase gates where relevant
- Write or overwrite [`LOOP_PLAN.md`](LOOP_PLAN.md)

### Stop conditions (Loop A only)

- No git repo / read-only sandbox → write plan locally, skip push
- Conflicting in-progress work detected → document in plan as **IN PROGRESS (parallel agent)**; do not duplicate

---

## Loop B: REVIEW

**Trigger:** After each Loop C commit+push, or every **N=3** execute iterations without user input.

### Actions

1. Re-read completed work vs [`LOOP_PLAN.md`](LOOP_PLAN.md)
2. Mark tasks **DONE** / **DROPPED** / **BLOCKED**
3. Append to [`LOOP_LOG.md`](LOOP_LOG.md):
   - Timestamp, commit SHA(s), test count
   - **RETROSPECTIVE** section: what worked, what drifted, metric deltas (EOI, κ if measured)
4. If [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) assumptions changed → record in [`PLAN_DELTA.md`](PLAN_DELTA.md) (do not rewrite full plan)
5. Reprioritize next 3–5 tasks in LOOP_PLAN
6. Update [`NEXT_AGENT_PROMPT.md`](NEXT_AGENT_PROMPT.md) for handoff

### PLAN_DELTA rules

- One entry per material change (scope, priority, new blocker, completed phase gate)
- Format: date, section affected, delta, rationale
- Full IMPLEMENTATION_PLAN rewrite only on explicit user request

---

## Loop C: EXECUTE

**Trigger:** Top-priority task from LOOP_PLAN that is not blocked or owned by parallel dev-loop.

This loop **is** the dev loop defined in [`DEVELOPMENT_LOOP.md`](DEVELOPMENT_LOOP.md):

```
OBSERVE → PLAN → IMPLEMENT → TEST → COMMIT → PUSH → RESEARCH NOTE
```

### Execute tracks

| Track | Location | Examples |
|-------|----------|----------|
| **Code** | `src/eia/` | TwinRunner policy, SourceMass port, NAMM adapter |
| **Math** | [`MATHEMATICS.md`](MATHEMATICS.md), `docs/math/` | EOI formalization, drive decay, SourceMass κ |
| **Research** | `research/` | Paired EOI-002, RQ1 harmonization report |
| **NAMM** | `src/eia/namm/`, crosswalk | NAMM-2026-013 live wire |

### Requirements

- All tests pass before commit
- English only in committed files
- Author: Roman Kuznetsov
- Push to `origin/main` after each Loop C iteration (unless comparative work on research branch)
- Append brief note to LOOP_LOG (Loop B may expand into full RETROSPECTIVE)

---

## Chaining without user input

1. **Session start:** Read [`NEXT_AGENT_PROMPT.md`](NEXT_AGENT_PROMPT.md) → run Loop A → run Loop C (1 item) → run Loop B if due
2. **Cursor `/loop`:** Schedule recurring prompt: `Continue EIA meta-loop A→C→B from docs/NEXT_AGENT_PROMPT.md`
3. **Parallel agents:** Check LOOP_PLAN **Owner** column; meta-loop owns docs/math; dev-loop owns RQ1–RQ4 code unless plan says otherwise
4. **Handoff:** NEXT_AGENT_PROMPT always points to latest LOOP_PLAN priority #1

---

## Stop conditions (global)

| Condition | Action |
|-----------|--------|
| Tests fail after 2 fix attempts | Log blocker in LOOP_LOG; skip commit; Loop B reprioritizes |
| Git push fails | Log blocker; stop session |
| NAMM unavailable | Stub + document in PLAN_DELTA; continue non-NAMM tasks |
| EOI regression on paired scenario | Loop B flags; Loop A adds harmonization task P0 |
| All P0 tasks blocked | Loop B only; update NEXT_AGENT_PROMPT with blocker summary |

---

## Cadence summary

| Event | Loops run |
|-------|-----------|
| New autonomous session | A → C → (B if last C was ≥N ago) |
| After each dev commit | C note in LOOP_LOG; B if configured |
| Every 3 execute iterations | Full B with RETROSPECTIVE |
| User message | Optional A refresh; do not reset LOOP_LOG |

---

## Related documents

| Document | Role |
|----------|------|
| [`LOOP_PLAN.md`](LOOP_PLAN.md) | Living 3–5 task queue |
| [`LOOP_LOG.md`](LOOP_LOG.md) | Iteration journal + retrospectives |
| [`PLAN_DELTA.md`](PLAN_DELTA.md) | IMPLEMENTATION_PLAN changelog |
| [`DEVELOPMENT_LOOP.md`](DEVELOPMENT_LOOP.md) | Loop C execute protocol |
| [`NEXT_AGENT_PROMPT.md`](NEXT_AGENT_PROMPT.md) | Session handoff template |
| [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) | Strategic R0–R11 roadmap |
| [`MATHEMATICS.md`](MATHEMATICS.md) | Formal model (canonical English) |

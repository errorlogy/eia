# EIA Development Loop

Repeatable autonomous iteration cycle for research and implementation on the EIA codebase.

**Author:** Roman Kuznetsov

## Cycle

```
OBSERVE → PLAN → IMPLEMENT → TEST → COMMIT → PUSH → RESEARCH NOTE → next iteration
```

| Phase | Action |
|-------|--------|
| **OBSERVE** | Read backlog (`docs/LOOP_LOG.md`), git status, test baseline, prior research notes |
| **PLAN** | Pick next backlog item; define acceptance criteria and stop conditions |
| **IMPLEMENT** | Minimal focused diff; English only in committed files |
| **TEST** | `pytest` — all tests must pass before commit |
| **COMMIT** | One commit per loop iteration on `main`; author Roman Kuznetsov |
| **PUSH** | `git push origin main` after each iteration |
| **RESEARCH NOTE** | Append entry to `docs/LOOP_LOG.md` with timestamp, metrics, blockers |

## Stop conditions

| Condition | Action |
|-----------|--------|
| Tests fail | Fix before continue; do not commit broken state |
| Git push fails | Report blocker in `LOOP_LOG.md`; stop iteration |
| External dependency unavailable | Document blocker; ship stub + tests; continue next item |

## Backlog (ordered)

1. **RQ1** — Harmonize twin-run policy (`TwinInterventionPolicy`)
2. **RQ2** — Port SourceMass topology to main
3. **RQ3** — NAMM-013 adapter stub → live attempt
4. **RQ4** — Expand evals (twin_world scenarios)

## Metrics to record

- Test count and pass/fail
- Paired EOI results (main vs starter)
- Commit SHA
- Blockers for next iteration

## Meta-loop nesting

Loop C (this document) runs inside the larger **A → C → B** cycle:

| Loop | Doc | Role |
|------|-----|------|
| A — PLAN | [`LOOP_PLAN.md`](LOOP_PLAN.md) | 3–5 prioritized tasks each session |
| B — REVIEW | [`LOOP_LOG.md`](LOOP_LOG.md), [`PLAN_DELTA.md`](PLAN_DELTA.md) | Retrospective + plan amendments |
| C — EXECUTE | This file | OBSERVE → … → PUSH |

See [`META_LOOP.md`](META_LOOP.md) for full architecture and handoff via [`NEXT_AGENT_PROMPT.md`](NEXT_AGENT_PROMPT.md).

## Related docs

- [`META_LOOP.md`](META_LOOP.md) — PLAN / REVIEW / EXECUTE nesting
- [`LOOP_PLAN.md`](LOOP_PLAN.md) — current task queue
- [`LOOP_LOG.md`](LOOP_LOG.md) — iteration journal
- [`PLAN_DELTA.md`](PLAN_DELTA.md) — IMPLEMENTATION_PLAN changelog
- [`MATHEMATICS.md`](MATHEMATICS.md) — formal model (math track)
- [`RESEARCH_BRANCHES.md`](RESEARCH_BRANCHES.md) — comparative branches
- [`research/paired-eoi-report-001.md`](../research/paired-eoi-report-001.md) — baseline paired EOI

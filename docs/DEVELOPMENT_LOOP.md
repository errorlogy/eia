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

## Related docs

- [`LOOP_LOG.md`](LOOP_LOG.md) — iteration journal
- [`RESEARCH_BRANCHES.md`](RESEARCH_BRANCHES.md) — comparative branches
- [`research/paired-eoi-report-001.md`](../research/paired-eoi-report-001.md) — baseline paired EOI

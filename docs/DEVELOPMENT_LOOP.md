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

## CI automation (Loop 24+)

GitHub Actions workflow [`.github/workflows/eia-ci.yml`](../.github/workflows/eia-ci.yml):

| Step | Command | Purpose |
|------|---------|---------|
| Full test suite | `pytest -q` | G0 gate — all unit/integration tests |
| Replay smoke | `pytest tests/test_replay_reexecute.py -q` | Deterministic re-execute fingerprint match |
| Seed bootstrap (Loop 28) | `python research/ci_seed_bootstrap.py` | Multi-seed determinism on twin_world_001 |
| Eval gate (Loop 29) | `python research/ci_eval_gate.py` | Mean EOI ≥ 0.8, precision ≥ 0.75 on 6 scenarios |
| Structural diff (optional) | `python research/ci_trace_diff_check.py` | Main 25 vs starter 22 nodes on twin_world_001 |

Disable gates locally or in fork CI with `EIA_CI_TRACE_DIFF=0`, `EIA_CI_SEED_BOOTSTRAP=0`, or `EIA_CI_EVAL_GATE=0`.

Regenerate the human-readable diff report with `python research/run_trace_structural_diff.py`.

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
- [`RESEARCH_INDEX.md`](RESEARCH_INDEX.md) — research artifact catalog
- [`RESEARCH_BRANCHES.md`](RESEARCH_BRANCHES.md) — comparative branches
- [`research/paired-eoi-report-001.md`](../research/paired-eoi-report-001.md) — baseline paired EOI

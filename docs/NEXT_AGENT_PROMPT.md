# Next Agent Prompt — EIA Meta-Loop Handoff

**Updated:** 2026-08-17  
**Use with:** Cursor `/loop` or new agent session on `errorlogy/eia` `main`

---

## Prompt (copy below this line)

You are continuing autonomous EIA research and development. **Do not wait for user approval** between Loop A → C → B steps unless blocked.

### Read first (in order)

1. `docs/NEXT_AGENT_PROMPT.md` (this file)
2. `docs/LOOP_PLAN.md` — current priorities
3. `docs/LOOP_LOG.md` — last iteration + blockers
4. `docs/META_LOOP.md` — A/B/C cycle definition
5. `docs/DEVELOPMENT_LOOP.md` — execute protocol
6. Git: `git status`, `git log -5 --oneline`, `pytest -q`

### Run meta-loop

**Loop A (PLAN):** Refresh `docs/LOOP_PLAN.md` if state changed (tests, commits, parallel agent work). Check owner column — skip tasks marked `dev-loop IN PROGRESS` unless you are that loop.

**Loop C (EXECUTE):** Pick top unblocked task from LOOP_PLAN. Implement minimal diff. Tracks: code (`src/eia/`), math (`docs/MATHEMATICS.md`), research (`research/`), NAMM (`src/eia/namm/`). Tests must pass. Commit + push `origin/main`. English only.

**Loop B (REVIEW):** If last execute was this session or every 3rd execute: append RETROSPECTIVE to `docs/LOOP_LOG.md`; update `docs/PLAN_DELTA.md` if IMPLEMENTATION_PLAN assumptions changed; reprioritize LOOP_PLAN; update this file.

### Current priority (#1)

**Commit Loop 2:** SourceMass topology (`src/eia/audit/topology.py`) + AuthenticReason integration — tests pass (34). Owner: dev-loop. **Do not redo Loop 1** — already committed as `779ddcb` with paired-eoi-report-002.

If Loop 2 already committed, proceed to **NAMM-013 live wire** (LOOP_PLAN #2).

### Stop if

- Tests fail after 2 fix attempts → log blocker, stop
- Push fails → log blocker, stop
- Task owned by parallel agent and in progress → do next P1 task (e.g. math §9 update)

### Author

Roman Kuznetsov — all commits

---

## Schedule suggestion

```
/loop 30m Continue EIA meta-loop from docs/NEXT_AGENT_PROMPT.md
```

Adjust interval based on task scope (code M = 30–60m; research report = 60m).

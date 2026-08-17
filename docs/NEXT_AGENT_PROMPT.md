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
5. Git: `git status`, `git log -5 --oneline`, `pytest -q`

### Run meta-loop

**Loop A (PLAN):** Refresh `docs/LOOP_PLAN.md` if state changed.

**Loop C (EXECUTE):** Pick top unblocked task from LOOP_PLAN. Tests must pass. Commit + push `origin/main`. English only.

**Loop B (REVIEW):** Append RETROSPECTIVE to `docs/LOOP_LOG.md`; update `docs/PLAN_DELTA.md` if needed; update this file.

### Current priority (#1)

**Baseline EUIR comparison** on the 6-scenario eval set using `--baseline reactive_only` vs `full_eia`. Record in `research/baseline-euir-report.md`.

### Completed this session (Loops 8–11)

- Loop 8: SourceMass κ study — κ=0.0, 2/6 partition agreement
- Loop 9: EXPERIMENTS.md + reactive/scheduled/full_eia baseline stubs
- Loop 10: THREAT_MODEL.md + adversarial_governor harness (4 cases)
- Loop 11: starter trace JSONL export for structural diff

### Stop if

- Tests fail after 2 fix attempts → log blocker, stop
- Push fails → log blocker, stop

### Author

Roman Kuznetsov — all commits

---

## Schedule suggestion

```
/loop 30m Continue EIA meta-loop from docs/NEXT_AGENT_PROMPT.md
```

Adjust interval based on task scope (code M = 30–60m; research report = 60m).

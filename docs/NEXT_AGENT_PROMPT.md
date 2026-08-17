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

**SourceMass vs AuthenticReason κ study** on the 5-scenario eval set using `kappa_bin_agreement()` from `src/eia/audit/source_mass_mapping.py`. Record results in `research/source-mass-kappa-report.md`.

### Completed this session (Loops 5–7)

- Loop 5 (`01b2564`): EOI threshold calibration + SourceMass mapping
- Loop 6 (`a3f7988`): paired-eoi-report-003 on `autonomous_question`
- Loop 7: twin_world_003 calibrated + twin_world_005–006 evals

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

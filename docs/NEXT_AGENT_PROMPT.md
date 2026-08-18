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

**Negative-control eval scenarios** — expected abstain cases for eval set expansion.

### Completed this session (Loops 12–31)

- Loop 12: Baseline EUIR comparison — full_eia 100% vs reactive 0% EUIR proxy
- Loop 13: Event-rule baseline stub (`--baseline event_rule`, salience 0.30)
- Loop 14: Ground-truth labels on twin_world_001–006 + schema doc
- Loop 15: Structural trace diff main vs starter (25 vs 22 nodes)
- Loop 16: Adversarial consent-race cases ADV-005–007 (7-case suite)
- Loop 17: PAI-EI-E0-001 smoke — full_eia EOI 1.0, partial EXPERIMENT_REPORT
- Loop 18: Predictive P3 baseline + 4-way EUIR v2 report
- Loop 19: Ground-truth loader + initiative precision 100% on eval set
- Loop 20: Held-out adversarial suite ADV-H1–H6 + freeze policy in THREAT_MODEL §5a
- Loop 21: PAI-EI-E0-001 full 5-baseline matrix — full_eia EUIR 100%, scheduled_stub 66.7%
- Loop 22: G2 evidence pack — G2/G0/G3 PASS; cross-ref all research reports
- Loop 23: MATHEMATICS.md §9 — formal EOI, EUIR proxy, precision; §3 DriveEngine params
- Loop 24: CI workflow — pytest + replay smoke + structural diff gate
- Loop 25: README G2 badge + RESEARCH_INDEX.md
- Loop 26: MVP1_SHADOW_PLAN.md + PLAN_DELTA iteration 6
- Loop 27: NAMM crosswalk 008–010 + AuthenticReason NAMM cert wire
- Loop 28: Seed determinism bootstrap — ci_seed_bootstrap.py + test_seed_determinism.py
- Loop 29: Eval suite CI gate — ci_eval_gate.py (mean EOI ≥ 0.8, precision ≥ 0.75)
- Loop 30: RELEASE_v0.2.md + tag v0.2.0-mvp0
- Loop 31: INTERIM_RESEARCH_SUMMARY.md for Anthemium stakeholders

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

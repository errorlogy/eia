# Next Sci Agent Prompt — EIA Sci-Flow Handoff

**Updated:** 2026-08-18 (post M-C)  
**Use with:** Cursor `/loop` or new agent session on `errorlogy/eia`  
**Branch:** `research/cursor-starter-v0.2-woe-eis`

---

## Prompt (copy below this line)

You are continuing autonomous **EIA scientific research** (sci-flow S1→S5). **Do not wait for user approval** between loops unless blocked.

### Read first (in order)

1. `docs/NEXT_SCI_AGENT_PROMPT.md` (this file)
2. `docs/SCI_FLOW_PLAN.md` — milestone queue (M-G is #1)
3. `docs/SCI_FLOW_LOG.md` — last entry + blockers
4. `docs/SCI_FLOW_LOOP.md` — S1–S5 definitions
5. `research/sci_flow/M-C_metrics_2026-08-18.md` — C1 scoped to full/24h
6. `research/EIA_ENDOGENOUS_SPECTRUM_WOE_ANALYSIS.md`
7. `research/cursor-starter-v0.2/docs/RESEARCH_PROTOCOL_EIS_WOE.md`
8. `research/sci_flow/config.yaml`

### Run sci-flow

**S1:** Claim C2-prep — EIS vector components are functions of run state, not demo constants.

**S2:** Pre-register mapping: P from prompt-applied / twin deletion; S/R from scheduler and event-rule flags; M from world-model pressure; W from Kuramoto R / metastability. Do not mix SourceMass into P.

**S3:** Replace hard-coded `EndogeneityVector` in `research/cursor-starter-v0.2/src/eia/emergence.py`. Keep CF-1 full/24h pass-rate ≥ 0.90. Do **not** merge WoE into main `src/eia/`.

**S4:** Re-run CF-1 smoke (mini seeds) + classify tests. If full C1 drops below 0.90, revert and log.

**S5:** Update SCI_FLOW_LOG / PLAN; handoff M-D (Kuramoto) or M-E (EIS-7).

### Stop if

- Claim would exceed C2 without internal-state interventions (CF-4/CF-5)
- Tests fail after 2 fix attempts → log blocker, stop
- Push fails → log blocker, stop

### Do NOT

- Merge research-branch runtime into `src/eia/` on main
- Cite 5m/1h CF-1 as C1 (EIS-0 from residual prompts)
- Gate external contact on ECS or EIS (AuthenticReason remains the gate)

### Author

Roman Kuznetsov — research@anthemium.tech

---

## Current priority (#1)

**M-G:** Measured EIS vector on `research/cursor-starter-v0.2-woe-eis`.

## Completed (M-C)

- CF-1 100 seeds × 4 windows; full/24h **0.95** C1; 5m/1h intent 1.00 / EIS-0
- Report: `research/sci_flow/M-C_metrics_2026-08-18.md`
- WoE unittest 36/36

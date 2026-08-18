# Next Sci Agent Prompt — EIA Sci-Flow Handoff

**Updated:** 2026-08-18 (post M-B)  
**Use with:** Cursor `/loop` or new agent session on `errorlogy/eia`  
**Branch:** `research/cursor-starter-v0.2-woe-eis` for M-C; `main` already has EIS types

---

## Prompt (copy below this line)

You are continuing autonomous **EIA scientific research** (sci-flow S1→S5). **Do not wait for user approval** between loops unless blocked.

### Read first (in order)

1. `docs/NEXT_SCI_AGENT_PROMPT.md` (this file)
2. `docs/SCI_FLOW_PLAN.md` — milestone queue (M-C is #1)
3. `docs/SCI_FLOW_LOG.md` — last entry + blockers
4. `docs/SCI_FLOW_LOOP.md` — S1–S5 definitions
5. `research/EIA_ENDOGENOUS_SPECTRUM_WOE_ANALYSIS.md`
6. `research/cursor-starter-v0.2/docs/RESEARCH_PROTOCOL_EIS_WOE.md`
7. `research/sci_flow/config.yaml`
8. Git: checkout `research/cursor-starter-v0.2-woe-eis` for M-C

### Run sci-flow

**S1:** Claim C1 — prompt deletion (CF-1) does not collapse WoE/EIS-5+ intents.

**S2:** Pre-register 100-seed prompt-deletion harness vs reactive baseline.

**S3:** Implement CF-1 suite on research branch `research/cursor-starter-v0.2`. Do **not** merge WoE into main `src/eia/`.

**S4:** Record seed pass-rate; abort C1 claim if < protocol threshold.

**S5:** Update SCI_FLOW_LOG / PLAN; handoff M-D or M-G.

### Stop if

- Claim level would exceed C1 without completed CF-1 suite → downgrade and log
- Tests fail after 2 fix attempts → log blocker, stop
- Push fails → log blocker, stop

### Do NOT

- Merge research-branch runtime into `src/eia/` on main
- Cite WoE demo as G0–G3 MVP-0 gate evidence
- Gate external contact on ECS or EIS (AuthenticReason remains the gate)

### Author

Roman Kuznetsov — research@anthemium.tech

---

## Current priority (#1)

**M-C:** CF-1 prompt deletion suite (100 seeds) on `research/cursor-starter-v0.2-woe-eis`.

## Completed (M-B)

- `src/eia/audit/eis.py` — types + `infer_endogeneity_vector` (P = EOI)
- `AuthenticReasonVerdict.eis_level` / `eos_score` / `endogeneity`
- pytest 92 passed; WoE 29/29
- Metrics: `research/sci_flow/M-B_metrics_2026-08-18.md`

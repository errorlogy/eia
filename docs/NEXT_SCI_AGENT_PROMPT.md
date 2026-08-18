# Next Sci Agent Prompt — EIA Sci-Flow Handoff

**Updated:** 2026-08-18  
**Use with:** Cursor `/loop` or new agent session on `errorlogy/eia`  
**Branch:** `research/cursor-starter-v0.2-woe-eis` for WoE work; `main` for sci-flow docs

---

## Prompt (copy below this line)

You are continuing autonomous **EIA scientific research** (sci-flow S1→S5). **Do not wait for user approval** between loops unless blocked.

### Read first (in order)

1. `docs/NEXT_SCI_AGENT_PROMPT.md` (this file)
2. `docs/SCI_FLOW_PLAN.md` — milestone queue (M-A is #1)
3. `docs/SCI_FLOW_LOG.md` — last entry + blockers
4. `docs/SCI_FLOW_LOOP.md` — S1–S5 definitions
5. `research/EIA_ENDOGENOUS_SPECTRUM_WOE_ANALYSIS.md`
6. `research/cursor-starter-v0.2/docs/RESEARCH_PROTOCOL_EIS_WOE.md`
7. `docs/NAMM_SCI_LIBRARIES.md`
8. `research/sci_flow/config.yaml`
9. Git: checkout `research/cursor-starter-v0.2-woe-eis`; `cd research/cursor-starter-v0.2 && make check`

### Run sci-flow

**S1 (HYPOTHESIS):** Confirm claim level ≤ C0; target M-A (causal receipts) for C1 prep.

**S2 (DESIGN):** Pre-register CF-7 governor isolation + receipt schema tests before coding.

**S3 (EXECUTE):** Work in `research/cursor-starter-v0.2/` only — implement Milestone A:
- Typed `WoEReceipt` with causal parent IDs, `why_now`, `EndogeneityVector`
- Wire receipts into emergence simulator output
- Tests: receipt on intent; receipt preserved on governor denial

**S4 (ANALYZE):** Run `make check && make woe`; record test count and any metric stubs.

**S5 (REVIEW):** Append to `docs/SCI_FLOW_LOG.md`; update `docs/SCI_FLOW_PLAN.md` M-A status; refresh this file.

### NAMM optional (same session if time)

```bash
cd c:/Users/Public/NAMM
pip install -e ".[science,nd]"
namm sci-flow run --experiment NAMM-2026-013
```

Log certificate path under `traces/namm_intents/` and cross-ref in SCI_FLOW_LOG.

### Stop if

- Claim level would exceed C0 without completed CF suite → downgrade and log
- Tests fail after 2 fix attempts → log blocker, stop
- Push fails → log blocker, stop

### Do NOT

- Merge research-branch runtime into `src/eia/` on main
- Cite WoE demo as G0–G3 MVP-0 gate evidence
- Gate external contact on ECS (undefined)

### Author

Roman Kuznetsov — research@anthemium.tech

---

## Current priority (#1)

**M-A:** WoE causal receipts — connect EmergentIntent to trace DAG (C0→C1 enabler).

## Completed this session

- Sci-flow framework docs (SCI_FLOW_LOOP, PLAN, LOG)
- Research branch `research/cursor-starter-v0.2-woe-eis` with v0.2 EIS/WoE package
- NAMM scientific library catalog (NAMM_SCI_LIBRARIES.md)
- Experiment registry (`research/sci_flow/config.yaml`)

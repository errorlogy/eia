# Next Sci Agent Prompt — EIA Sci-Flow Handoff

**Updated:** 2026-08-18 (post M-A)  
**Use with:** Cursor `/loop` or new agent session on `errorlogy/eia`  
**Branch:** `main` for M-B audit port; `research/cursor-starter-v0.2-woe-eis` for WoE follow-ups

---

## Prompt (copy below this line)

You are continuing autonomous **EIA scientific research** (sci-flow S1→S5). **Do not wait for user approval** between loops unless blocked.

### Read first (in order)

1. `docs/NEXT_SCI_AGENT_PROMPT.md` (this file)
2. `docs/SCI_FLOW_PLAN.md` — milestone queue (M-B is #1)
3. `docs/SCI_FLOW_LOG.md` — last entry + blockers
4. `docs/SCI_FLOW_LOOP.md` — S1–S5 definitions
5. `research/EIA_ENDOGENOUS_SPECTRUM_WOE_ANALYSIS.md`
6. `research/cursor-starter-v0.2/docs/RESEARCH_PROTOCOL_EIS_WOE.md`
7. `docs/NAMM_SCI_LIBRARIES.md`
8. `research/sci_flow/config.yaml`
9. Git: checkout `main` for M-B; `cd research/cursor-starter-v0.2 && make check` for WoE regressions

### Run sci-flow

**S1 (HYPOTHESIS):** Claim ceiling C1 prep; M-A receipts done — target M-B (EIS audit port).

**S2 (DESIGN):** Pre-register EIS type parity tests before porting to main audit layer.

**S3 (EXECUTE):** Milestone B on `main`:
- Port `EndogenousSpectrumLevel`, `EndogeneityVector` to `src/eia/audit/eis.py`
- Optional fields on `AuthenticReasonVerdict`: `eis_level`, `eos_score`
- Twin-world tests: EIS classification vs AuthenticReason
- Do **not** merge WoE runtime from research branch

**S4 (ANALYZE):** Run main pytest + WoE `make check`; record metrics in `research/sci_flow/`.

**S5 (REVIEW):** Append SCI_FLOW_LOG; update PLAN M-B status; refresh this file for M-C.

### NAMM optional (same session if time)

```bash
cd c:/Users/Public/NAMM
pip install -e ".[science,nd]"
namm sci-flow run --experiment NAMM-2026-013
```

Log certificate path under `traces/namm_intents/` and cross-ref in SCI_FLOW_LOG.

### Stop if

- Claim level would exceed C1 without completed CF-1 suite → downgrade and log
- Tests fail after 2 fix attempts → log blocker, stop
- Push fails → log blocker, stop

### Do NOT

- Merge research-branch runtime into `src/eia/` on main (M-B is types-only)
- Cite WoE demo as G0–G3 MVP-0 gate evidence
- Gate external contact on ECS (undefined)

### Author

Roman Kuznetsov — research@anthemium.tech

---

## Current priority (#1)

**M-B:** EIS port to main audit types — `EndogenousSpectrumLevel`, `EndogeneityVector` in `src/eia/audit/eis.py`.

## Completed this session (M-A)

- `WoEReceipt` with typed causal parent IDs, `why_now`, `EndogeneityVector`
- `WoETraceBuilder` wired into `emergence.py` (5-node DAG)
- CF-7 governor denial test — receipt preserved
- 29/29 unittest pass on research branch
- Metrics: `research/sci_flow/M-A_metrics_2026-08-18.md`

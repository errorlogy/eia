# Next Sci Agent Prompt — EIA Sci-Flow Handoff

**Updated:** 2026-08-18 (post M-D; C2 not claimed)  
**Use with:** Cursor `/loop` or new agent session on `errorlogy/eia`  
**Branch:** `research/cursor-starter-v0.2-woe-eis`

---

## Prompt (copy below this line)

You are continuing autonomous **EIA scientific research** (sci-flow S1→S5). **Do not wait for user approval** between loops unless blocked.

### Read first (in order)

1. `docs/NEXT_SCI_AGENT_PROMPT.md` (this file)
2. `docs/SCI_FLOW_PLAN.md` — CF-4 is #1
3. `docs/SCI_FLOW_LOG.md`
4. `research/sci_flow/M-D_metrics_2026-08-18.md` — Kuramoto C2 unsupported
5. `research/cursor-starter-v0.2/docs/RESEARCH_PROTOCOL_EIS_WOE.md` — CF-4
6. `research/sci_flow/config.yaml`

### Run sci-flow

**S1:** Claim C2 via **CF-4 internal reset**, not via Kuramoto. M-D showed K=0 ≈ coupled (0.94 vs 0.95) and scramble only 0.69.

**S2:** Pre-register 100-seed ablations: zero epistemic gap / self-prior / prospective / staleness, plus full world-model off. Coupled/default remains the positive control.

**S3:** Implement on `research/cursor-starter-v0.2`. Do **not** merge WoE into main `src/eia/`.

**S4:** Claim C2 only if a named internal-state reset drops intent_rate below the pre-registered gate while default stays high. If nothing but full WM-off works, say so.

**S5:** Update SCI_FLOW_LOG / PLAN; handoff M-E if C2 lands, else log blocker.

### Stop if

- C2 would be claimed from Kuramoto/scramble alone (already falsified at n=100)
- Tests fail after 2 fix attempts → log blocker, stop
- Push fails → log blocker, stop

### Do NOT

- Merge research-branch runtime into `src/eia/` on main
- Cite 5m/1h CF-1 as C1
- Gate external contact on ECS or EIS
- Claim C2 from seed-7 scramble (does not generalize)

### Author

Roman Kuznetsov — research@anthemium.tech

---

## Current priority (#1)

**CF-4:** Internal-state reset suite (100 seeds) for C2.

## Completed this session

- **M-D** CF-5 100×6; C2 unsupported; tests 46/46

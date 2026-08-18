# Next Sci Agent Prompt — EIA Sci-Flow Handoff

**Updated:** 2026-08-18 (post M-G)  
**Use with:** Cursor `/loop` or new agent session on `errorlogy/eia`  
**Branch:** `research/cursor-starter-v0.2-woe-eis`

---

## Prompt (copy below this line)

You are continuing autonomous **EIA scientific research** (sci-flow S1→S5). **Do not wait for user approval** between loops unless blocked.

### Read first (in order)

1. `docs/NEXT_SCI_AGENT_PROMPT.md` (this file)
2. `docs/SCI_FLOW_PLAN.md` — milestone queue (M-D is #1)
3. `docs/SCI_FLOW_LOG.md` — last entry + blockers
4. `docs/SCI_FLOW_LOOP.md`
5. `research/sci_flow/M-C_metrics_2026-08-18.md`
6. `research/sci_flow/M-G_metrics_2026-08-18.md`
7. `research/cursor-starter-v0.2/docs/RESEARCH_PROTOCOL_EIS_WOE.md`
8. `research/sci_flow/config.yaml`

### Run sci-flow

**S1:** Claim C2 — internal-state causation via phase organization (CF-5 / Kuramoto).

**S2:** Pre-register delay/coupling sweep vs scramble and K=0 negative controls. Carrier 42 Hz remains a computational parameter, not a biological claim.

**S3:** Implement M-D on `research/cursor-starter-v0.2`. Optional NAMM-2026-013 correlation. Do **not** merge WoE into main `src/eia/`.

**S4:** If scramble/K=0 does not change intent rate vs coupled, do not claim C2.

**S5:** Update SCI_FLOW_LOG / PLAN; handoff M-E or M-F.

### Stop if

- C2 would be claimed without a negative control
- Tests fail after 2 fix attempts → log blocker, stop
- Push fails → log blocker, stop

### Do NOT

- Merge research-branch runtime into `src/eia/` on main
- Cite 5m/1h CF-1 as C1
- Gate external contact on ECS or EIS

### Author

Roman Kuznetsov — research@anthemium.tech

---

## Current priority (#1)

**M-D:** Kuramoto coupling graph + delay sweep (C2).

## Completed this session

- **M-C** CF-1 100 seeds; full/24h C1 0.95
- **M-G** measured EIS vector; CF-1 smoke 0.95; tests 38/38

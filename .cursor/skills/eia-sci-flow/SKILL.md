---
name: eia-sci-flow
description: >-
  Autonomous EIA scientific research (sci-flow S1→S5) on branch
  research/cursor-starter-v0.2-woe-eis. Tier 0 default (no LLM for ATT
  evidence). Claim ceiling C2; no AGI*; no WoE→main merge. Use when continuing
  ATT/M-CLI work, endogeneity harnesses, or sci-flow loops on this repo.
---

# EIA Sci-Flow

Continue **EIA scientific research** across multiple topologies. Do not wait for user approval between loops unless blocked.

## Branch and scope

| Item | Value |
|------|-------|
| **Branch** | `research/cursor-starter-v0.2-woe-eis` |
| **Repo** | `C:\Users\Public\PROACTIVE_AI` |
| **Claim ceiling** | **C2** — scoped \(E_{\mathrm{endo}}\) / ATT-E partial only |
| **M-CLI default tier** | **0** (sim + CF-4 + ATT stubs; no LLM for ATT scoring) |
| **Hard stop** | Do **not** merge WoE research runtime into `main/src/eia/` |

## Read first (in order)

1. `docs/NEXT_SCI_AGENT_PROMPT.md`
2. `docs/ENDOGENEITY_IMPLEMENTATION_PLAN.md` — M-CLI Phases 0–6
3. `research/sci_flow/AGI_PHASE_TRANSITION.md`
4. `research/sci_flow/CAUSAL_ENDOGENEITY.md`
5. `research/sci_flow/STABLE_ENDOGENEITY.md`
6. `research/sci_flow/AGI_TRANSITION_TEST.md`
7. `research/sci_flow/AGI_STAR_CRITERION.md`
8. `docs/MULTI_TOPOLOGY_LOOPS.md`
9. `docs/SCI_FLOW_PLAN.md` / `docs/SCI_FLOW_LOG.md`
10. Metrics files listed in `NEXT_SCI_AGENT_PROMPT.md` (M-CF4 through M-D2)
11. `research/sci_flow/config.yaml`
12. **Main-stack backlog (not sci-flow merge):** [`docs/CURSOR_TASKS.md`](../../docs/CURSOR_TASKS.md) · [`docs/CURSOR_TASKS_SCI_FLOW_CROSSWALK.md`](../../docs/CURSOR_TASKS_SCI_FLOW_CROSSWALK.md) — use for Governor/Drive/EOI/G2 on `main`; sci-flow P0 picks **B05**, **D01**, **D05** per crosswalk

Also read `research/cursor-starter-v0.2/AGENTS.md` and `.cursor/rules/eia.mdc` under that tree for coding invariants.

## Tier 0 verification (run after substantive changes)

```powershell
cd C:\Users\Public\PROACTIVE_AI
git checkout research/cursor-starter-v0.2-woe-eis
make check-sci-tier0
```

Equivalent: `python scripts/check_sci_tier0.py` — runs `endogeneity_stack_sim.py`, shadow/live ATT-R, and pytest suites (root + `research/cursor-starter-v0.2`).

Individual checks (see `docs/ENDOGENEITY_IMPLEMENTATION_PLAN.md` §7):

- `python endogeneity_stack_sim.py`
- `python research/sci_flow/run_shadow_att_r.py`
- `python research/sci_flow/run_live_att_r.py`
- `pytest tests/test_shadow_multitick.py`
- `cd research/cursor-starter-v0.2 && pytest tests/test_agi_transition.py tests/test_live_att_r.py`

## Sci-flow phases (S1→S5)

| Phase | Action |
|-------|--------|
| **S1–S3** | Read docs; implement per implementation plan; add falsifier tests |
| **S4** | No new C-level without pre-registered gates; never claim AGI* |
| **S5** | Update `SCI_FLOW_LOG.md`; run tier-0 lock; optional T_LIVE / T_NAMM |

**Current priority:** optional daemon cross-tick \(W'\to G'\) carryover (shadow-first) **or** T_NAMM soft witness **or** Hermes P0 overlap (**B05**, **D01**, **D05**) per [`docs/CURSOR_TASKS_SCI_FLOW_CROSSWALK.md`](../../docs/CURSOR_TASKS_SCI_FLOW_CROSSWALK.md).

## Stop immediately if

- C2 re-attributed to Kuramoto
- AGI* / consciousness / \(\tau_{AGI}\) claimed from partial ATT or Telegram
- Strong \(N_H\) from opacity or ATT-N explore alone
- C5 from ATT-D explore alone
- Live SEND faked by unlabeled threshold gutting
- Tests fail after **2** fix attempts → log blocker, stop
- Merge WoE into main `src/eia/` attempted

## Do NOT

- Merge research-branch runtime into `src/eia/` on main
- Lower `min_contact_score` without labeling smoke
- Treat Kuramoto \(R\) as ATT-R endogeneity
- Raise C3 from ATT-G/P/R explore alone; C5 from ATT-D explore alone
- Use LLM every tick for goals (`att_evidence.llm_allowed: false` for Tier 0)

## Related skills

| Skill | When |
|-------|------|
| **sci-loop** (`.cursor/skills/sci-loop/`) | Recurring autonomous sci-flow ticks |
| **loop** (Cursor built-in) | `/loop [interval] <prompt>` timer |
| **loop-library** (user: `~/.agents/skills/loop-library/`) | Design/audit bounded loops |
| **babysit** (Cursor built-in) | Keep research PR merge-ready |
| **split-to-prs** (Cursor built-in) | Split large sci changes into reviewable PRs |

## M-CLI phase map (quick)

| Phase | Goal |
|-------|------|
| 0 | Tier 0 regression lock (`make check-sci-tier0`) |
| 1 | `ModelRoleAdapter` stub, `tier: 0` |
| 2 | Daemon carryover (shadow-first) |
| 3 | Consolidated theory TZ |
| 4–6 | Tier 1 CLI genesis, metrics report, Telegram witness (optional; last) |

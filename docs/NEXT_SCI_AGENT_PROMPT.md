# Next Sci Agent Prompt — EIA Sci-Flow Handoff

**Updated:** 2026-09-01 (Hermes CURSOR_TASKS backlog integrated; M-EMP Endogeneity Metrics Pool; OMEGA_t in_progress; loop playbook)  
**Use with:** Cursor `/loop` or new agent session on `errorlogy/eia`  
**Branch:** `research/cursor-starter-v0.2-woe-eis`

### Cursor skills (load before autonomous loops)

| Skill | Path | Use |
|-------|------|-----|
| **eia-sci-flow** | `.cursor/skills/eia-sci-flow/SKILL.md` | Branch, read order, C2 ceiling, tier 0, stop rules |
| **sci-loop** | `.cursor/skills/sci-loop/SKILL.md` | Bounded `/loop` cadence + tier-0 verify each tick |
| **loop** | Cursor built-in (`/loop`) | Timer / recurring agent wake |
| **loop-library** | `~/.agents/skills/loop-library/` | Audit or design bounded loops |
| **babysit** | Cursor built-in | PR merge-ready (CI + comments) |
| **split-to-prs** | Cursor built-in | Split large sci diffs into reviewable PRs |

**Tier 0 lock:** `make check-sci-tier0` (or `python scripts/check_sci_tier0.py`) after substantive changes.

**Example loop prompt:** `/loop 45m Follow sci-loop + eia-sci-flow. Tick: one M-O/OMEGA evidence item. Read OMEGA_WAVE_METRIC.md, MIOC_EIA_BRIDGE.md. Tier 0 check_sci_tier0 after changes. Claim ceiling C2.`  
**OMEGA loop doc:** [`docs/SCI_LOOP_OMEGA_RESEARCH.md`](SCI_LOOP_OMEGA_RESEARCH.md)

Rule: `.cursor/rules/eia-sci-flow.mdc` (applies under `docs/`, `research/sci_flow/`, `research/cursor-starter-v0.2/`).  
**Implementation plan:** [`docs/ENDOGENEITY_IMPLEMENTATION_PLAN.md`](ENDOGENEITY_IMPLEMENTATION_PLAN.md)  
**Hermes CURSOR_TASKS backlog:** [`docs/CURSOR_TASKS.md`](CURSOR_TASKS.md) · [`docs/cursor_tasks.json`](cursor_tasks.json) · sci-flow crosswalk [`docs/CURSOR_TASKS_SCI_FLOW_CROSSWALK.md`](CURSOR_TASKS_SCI_FLOW_CROSSWALK.md)  
**Registry:** [`docs/MULTI_TOPOLOGY_LOOPS.md`](MULTI_TOPOLOGY_LOOPS.md)  
**AGI\* notes:** [`AGI_STAR_CRITERION.md`](../research/sci_flow/AGI_STAR_CRITERION.md) · [`AGI_PHASE_TRANSITION.md`](../research/sci_flow/AGI_PHASE_TRANSITION.md) · [`AGI_TRANSITION_TEST.md`](../research/sci_flow/AGI_TRANSITION_TEST.md) · [`CAUSAL_ENDOGENEITY.md`](../research/sci_flow/CAUSAL_ENDOGENEITY.md)

---

## Prompt (copy below this line)

You are continuing autonomous **EIA scientific research** (sci-flow S1→S5) across **multiple topologies**. **Do not wait for user approval** between loops unless blocked.

### Read first (in order)

1. `docs/NEXT_SCI_AGENT_PROMPT.md` (this file)
2. `docs/ENDOGENEITY_IMPLEMENTATION_PLAN.md` — M-CLI Phases 0–6 roadmap
3. `research/sci_flow/AGI_PHASE_TRANSITION.md` — order parameters \(E,N_H,P,R,D\), \(\tau_{AGI}\), regimes
3. `research/sci_flow/CAUSAL_ENDOGENEITY.md` — causal \(E_{\mathrm{endo}}\) bar (declaration/simulation ≠ endogeneity)
4. `research/sci_flow/STABLE_ENDOGENEITY.md` — M-SE multi-loop / drive field; toy `endogeneity_stack_sim.py`
5. `research/sci_flow/AGI_TRANSITION_TEST.md` — ATT-E…ATT-D harness map (thresholds TBD)
5. `research/sci_flow/AGI_STAR_CRITERION.md` — compact \(AGI^{*} = E_{\mathrm{endo}} \land C_{\mathrm{non\text{-}emb}(H)}\)
6. `docs/MULTI_TOPOLOGY_LOOPS.md`
7. `docs/SCI_FLOW_PLAN.md` / `docs/SCI_FLOW_LOG.md`
8. `research/sci_flow/M-CF4_metrics_2026-08-20.md` — **C2 claimed** (gap core) = scoped \(E_{\mathrm{endo}}\) / ATT-E partial only
9. `research/sci_flow/M0_TWIN_METRICS_2026-08-20.md` — T_AMAT_M0 harness falsifiers (architecture only)
10. `research/sci_flow/M-E_metrics_2026-08-20.md` — ATT-G explore proxy (no C3)
11. `research/sci_flow/M-P_metrics_2026-08-21.md` — ATT-P explore proxy (no C3)
12. `research/sci_flow/M-R_metrics_2026-08-21.md` — ATT-R explore proxy (no C3; not Kuramoto)
13. `research/sci_flow/M-R-LIVE_metrics_2026-08-21.md` — ATT-R shadow multitick on main CognitiveLoop (no C3)
14. `research/sci_flow/M-N_metrics_2026-08-21.md` — ATT-N explore proxy under \(B\) (no strong \(N_H\))
15. `research/sci_flow/M-D2_metrics_2026-08-21.md` — ATT-D explore proxy (no C5)
16. `research/sci_flow/NON_EMBEDDABILITY_MEASUREMENT.md` — M-N / ATT-N design
17. `research/sci_flow/M-D_metrics_2026-08-18.md` — Kuramoto still not a cause (not ATT-R)
18. `research/sci_flow/OMEGA_WAVE_METRIC.md` — OMEGA_t multi-band analog metric; MIT/MIOC bridges
19. `research/sci_flow/MIOC_EIA_BRIDGE.md` — FieldCard ↔ AttREvent crosswalk (D:\MIOC external)
20. `research/sci_flow/ENDOGENEITY_METRICS_POOL.md` — Tier A–E metric registry; ERI conjecture; YAML pool
21. `docs/CURSOR_TASKS_SCI_FLOW_CROSSWALK.md` — Hermes 75 tasks ↔ sci-flow / main vs research routing
22. `research/sci_flow/config.yaml`

### AGI\* / ATT framing (do not overclaim)

- **Primary transition metric:** \(E_{\mathrm{endo}}\) (ATT-E lead suite; [`CAUSAL_ENDOGENEITY.md`](../research/sci_flow/CAUSAL_ENDOGENEITY.md)); \(N_H\) secondary but necessary for full \(AGI^{*}\).
- C0–C5 are **empirical milestones toward** AGI\*, not AGI\*.
- **C2 / CF-4** ⇒ partial evidence for \(E_{\mathrm{endo}}\) / ATT-E only; **must** satisfy causal endogeneity bar (declaration/simulation ≠ \(E_{\mathrm{endo}}\)).
- **M-E / ATT-G** ⇒ explore proxy for goal genesis; **not C3**, not AGI\*.
- **M-P / ATT-P** ⇒ explore proxy for temporal \(P_G\); **not C3**, not AGI\*; corrigibility ≠ persistence.
- **M-R / ATT-R** ⇒ explore proxy for closed goal-formation recurrence; **not C3**, not AGI\*; Kuramoto \(R\) ≠ ATT-R.
- **M-R-LIVE** ⇒ shadow multi-tick on main CognitiveLoop under same falsifiers; **not C3**; gap vs true daemon carryover documented; **does not** replace ATT-E declaration falsifiers.
- **M-N / ATT-N** ⇒ explore proxy for \(D_H\) under pre-registered \(B\); **not** strong \(N_H\), not AGI\*; opacity ≠ non-embeddability.
- **M-O / O_t substrate** → explore adjunct only; oscillation as state/Phi_t source ≠ E_endo; F-SYNC / F-PHASE-ONLY / F-KURAMOTO-AS-E; parallel to ATT-G (M-E).
- **M-D2 / ATT-D** ⇒ explore proxy for cross-domain \(E_{\mathrm{endo}}\); **not C5**, not AGI\*; single-domain / schedule-prompt transfer falsified.
- \(AGI^{*}\) / \(\tau_{AGI}\) requires sustained \(E,N_H,P,R,D\) — **research horizon, not claimed**.
- Endogeneity ≠ Autonomy; description/simulation/declaration ≠ \(E_{\mathrm{endo}}\); opacity ≠ non-embeddability / causation; Trans-Human Cognition ≠ task SOTA; corrigibility ≠ persistence.
- **OMEGA_t** → supporting order parameter (Tier C in metrics pool; not Tier A); F-OMEGA-DECOR / F-OMEGA-EXT; MIT analog wave + MIOC Omega_G crosswalk; see `OMEGA_WAVE_METRIC.md`.
- **M-EMP / metrics pool** → `ENDOGENEITY_METRICS_POOL.md` + `endogeneity_metrics.yaml`; use `tier_a_metrics()` for harness; ERI is CONJECTURE only.
- **Hermes CURSOR_TASKS** → 75 open problems on `main` (production stack) vs `research/cursor-starter-v0.2-woe-eis` (ATT/M-CLI); see crosswalk; P0 sci-flow picks: **B05**, **D01**, **D05**, **B01**, **A04**.
- **AuthenticReason** = production gate; EIS/ECS/WoE/AGI\* = research-only.

### Topologies

| Id | Loop | Status |
|----|------|--------|
| **T_EIA_state** | `L_EIA_CF4` | **DONE** — C2 via `zero_epistemic_gap` 0.06 (\(E_{\mathrm{endo}}\) / ATT-E partial) |
| **T_AMAT_M0** | `L_AMAT_M0` | **DONE** — M0-twin harness; OFF collapse / ON differs; `emit_m0=false` |
| **T_LIVE_gate** | `L_LIVE_DIAG` | on demand — score ~−0.03; no unlabeled threshold cut |
| **T_LIVE_ATTR** | `L_LIVE_ATTR_SHADOW` | **DONE** — M-R-LIVE shadow multitick; falsifiers hold; gap vs daemon |
| **T_NAMM_cert** | `L_NAMM_013_030` | optional external witness (ATT-N soft only) |

### Run next (optional deepen)

**Preferred #1 — Optional daemon carryover:** Wire cross-tick state on true `run_daemon_tick` (still shadow-first; `emit_m0=false`). Do **not** lower governor thresholds for science claims.

**Alt A — T_NAMM_cert:** optional soft structural witness only (not strong \(N_H\)).

**Alt B — Hold:** ATT board is already synthesized in SCI_FLOW_LOG Entry 016; no further C-raises without pre-registered gates.

**S4:** No new C-level without pre-registered gates. Never claim AGI\*. Do not re-claim C2 via Kuramoto or M0 alone. Do not raise C3 from ATT-G/ATT-P/ATT-R explore alone. Do not claim strong \(N_H\) from ATT-N explore alone. Do not raise C5 from ATT-D explore alone.  
**S5:** Update logs; then T_LIVE / T_NAMM as needed.

### Stop if

- C2 re-attributed to Kuramoto
- AGI\* / consciousness / \(\tau_{AGI}\) claimed from C2, EIS, WoE, AMAT, ATT partials, or Telegram
- Strong \(N_H\) claimed from opacity or ATT-N explore alone
- C5 claimed from ATT-D explore alone
- Live SEND faked by unlabeled threshold gutting
- Tests fail after 2 fix attempts → log blocker, stop
- Merge WoE into main `src/eia/` attempted

### Do NOT

- Merge research-branch runtime into `src/eia/` on main
- Paste AMAT JSON as bot persona
- Lower `min_contact_score` without labeling smoke
- Claim AGI / AGI\* / consciousness from EIS/WoE/AMAT/C-ladder/ATT alone
- Treat self-description, roleplay, or declaration of agency as \(E_{\mathrm{endo}}\)
- Treat non-embeddability stubs / ATT-N explore as positive strong \(C_{\mathrm{non\text{-}emb}(H)}\)
- Treat Kuramoto \(R\) as Endogenous Cognitive Recurrence (\(R\) in ATT)
- Raise C3 solely from ATT-G, ATT-P, or ATT-R explore proxy
- Raise C5 solely from ATT-D explore proxy

### Author

Roman Kuznetsov — research@anthemium.tech

---

## Current priority (#1)

**Metrics pool loops:** Use [`ENDOGENEITY_METRICS_POOL.md`](../research/sci_flow/ENDOGENEITY_METRICS_POOL.md) — one Tier A/B metric tick per `/loop 45m`; tier-0 verify.  
**Hermes P0 overlap:** [`CURSOR_TASKS_SCI_FLOW_CROSSWALK.md`](CURSOR_TASKS_SCI_FLOW_CROSSWALK.md) — **B05** (no-LLM-mood / M-CLI Tier 0), **D01** (EOI-k / ATT-E), **D05** (DSR / M-SE), Phase 2 carryover via **E04**.  
**Alt:** OMEGA do(Omega) shadow arm; true daemon cross-tick \(W'\to G'\) carryover; T_NAMM soft witness.  
ATT board + pool synthesized (partial matrix; no \(\tau_{AGI}\)).

## Completed this session

- Multi-topology registry
- **M-CF4** 100×6; C2 claimed (`zero_epistemic_gap` 0.06); AGI\* fields on summarizer
- **AGI\*** compact criterion + **phase-transition** expansion + **ATT** draft
- **M-N** non-embeddability design + ATT-N explore under pre-registered \(B\) (`claim_allowed=False`, `n_h_claim=false`)
- **M-ATT** `eia.agi_transition` order-parameter stubs (`agi_star_claim=false`)
- **T_AMAT_M0** M0-twin harness expand + falsifiers
- **M-E / ATT-G** goal genesis + genealogy + falsifiers (n=50); `claim_allowed=False`
- **M-P / ATT-P** multi-tick \(P_G\) explore proxy + falsifiers (k∈{10,50,200}); `claim_allowed=False`
- **M-R / ATT-R** closed goal-formation loop scoring + falsifiers (incl. Kuramoto ban); `claim_allowed=False`
- **M-O / O_t substrate** → explore adjunct only; oscillation as state/Phi_t source ≠ E_endo; F-SYNC / F-PHASE-ONLY / F-KURAMOTO-AS-E; parallel to ATT-G (M-E).
- **M-D2 / ATT-D** cross-domain \(E_{\mathrm{endo}}\) (woe_catalog + twin_ops) + falsifiers; `claim_allowed=False` / no C5
- **M-R-LIVE** shadow multi-tick on main CognitiveLoop under ATT-R falsifiers; ATT board synthesis; `claim_allowed=False`
- **M-SE** stable endogeneity framework + stack sim (`STABLE_ENDOGENEITY.md`)
- **Causal endogeneity** criterion + ATT-E falsifiers + `e_endo_label_admissible` stub (`CAUSAL_ENDOGENEITY.md`)
- **M-O** oscillatory endogeneity substrate doc (adjunct; Kuramoto not E_endo)
- **OMEGA_t** metric + MIT/MIOC bridge (`OMEGA_WAVE_METRIC.md`, `MIOC_EIA_BRIDGE.md`, `oscillatory_state.py`)
- **M-EMP** Endogeneity Metrics Pool — Tier A–E registry, YAML, `endogeneity_metrics.py`, ERI conjecture

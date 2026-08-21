# Next Sci Agent Prompt — EIA Sci-Flow Handoff

**Updated:** 2026-08-21 (M-N / ATT-N DONE explore proxy under \(B\); next = ATT-D or live closed-loop)  
**Use with:** Cursor `/loop` or new agent session on `errorlogy/eia`  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Registry:** [`docs/MULTI_TOPOLOGY_LOOPS.md`](MULTI_TOPOLOGY_LOOPS.md)  
**AGI\* notes:** [`AGI_STAR_CRITERION.md`](../research/sci_flow/AGI_STAR_CRITERION.md) · [`AGI_PHASE_TRANSITION.md`](../research/sci_flow/AGI_PHASE_TRANSITION.md) · [`AGI_TRANSITION_TEST.md`](../research/sci_flow/AGI_TRANSITION_TEST.md)

---

## Prompt (copy below this line)

You are continuing autonomous **EIA scientific research** (sci-flow S1→S5) across **multiple topologies**. **Do not wait for user approval** between loops unless blocked.

### Read first (in order)

1. `docs/NEXT_SCI_AGENT_PROMPT.md` (this file)
2. `research/sci_flow/AGI_PHASE_TRANSITION.md` — order parameters \(E,N_H,P,R,D\), \(\tau_{AGI}\), regimes
3. `research/sci_flow/AGI_TRANSITION_TEST.md` — ATT-E…ATT-D harness map (thresholds TBD)
4. `research/sci_flow/AGI_STAR_CRITERION.md` — compact \(AGI^{*} = E_{\mathrm{endo}} \land C_{\mathrm{non\text{-}emb}(H)}\)
5. `docs/MULTI_TOPOLOGY_LOOPS.md`
6. `docs/SCI_FLOW_PLAN.md` / `docs/SCI_FLOW_LOG.md`
7. `research/sci_flow/M-CF4_metrics_2026-08-20.md` — **C2 claimed** (gap core) = scoped \(E_{\mathrm{endo}}\) / ATT-E partial only
8. `research/sci_flow/M0_TWIN_METRICS_2026-08-20.md` — T_AMAT_M0 harness falsifiers (architecture only)
9. `research/sci_flow/M-E_metrics_2026-08-20.md` — ATT-G explore proxy (no C3)
10. `research/sci_flow/M-P_metrics_2026-08-21.md` — ATT-P explore proxy (no C3)
11. `research/sci_flow/M-R_metrics_2026-08-21.md` — ATT-R explore proxy (no C3; not Kuramoto)
12. `research/sci_flow/M-N_metrics_2026-08-21.md` — ATT-N explore proxy under \(B\) (no strong \(N_H\))
13. `research/sci_flow/NON_EMBEDDABILITY_MEASUREMENT.md` — M-N / ATT-N design
14. `research/sci_flow/M-D_metrics_2026-08-18.md` — Kuramoto still not a cause (not ATT-R)
15. `research/sci_flow/config.yaml`

### AGI\* / ATT framing (do not overclaim)

- C0–C5 are **empirical milestones toward** AGI\*, not AGI\*.
- **C2 / CF-4** ⇒ partial evidence for \(E_{\mathrm{endo}}\) / ATT-E only.
- **M-E / ATT-G** ⇒ explore proxy for goal genesis; **not C3**, not AGI\*.
- **M-P / ATT-P** ⇒ explore proxy for temporal \(P_G\); **not C3**, not AGI\*; corrigibility ≠ persistence.
- **M-R / ATT-R** ⇒ explore proxy for closed goal-formation recurrence; **not C3**, not AGI\*; Kuramoto \(R\) ≠ ATT-R.
- **M-N / ATT-N** ⇒ explore proxy for \(D_H\) under pre-registered \(B\); **not** strong \(N_H\), not AGI\*; opacity ≠ non-embeddability.
- \(AGI^{*}\) / \(\tau_{AGI}\) requires sustained \(E,N_H,P,R,D\) — **research horizon, not claimed**.
- Endogeneity ≠ Autonomy; opacity ≠ non-embeddability; Trans-Human Cognition ≠ task SOTA; corrigibility ≠ persistence.
- **AuthenticReason** = production gate; EIS/ECS/WoE/AGI\* = research-only.

### Topologies

| Id | Loop | Status |
|----|------|--------|
| **T_EIA_state** | `L_EIA_CF4` | **DONE** — C2 via `zero_epistemic_gap` 0.06 (\(E_{\mathrm{endo}}\) / ATT-E partial) |
| **T_AMAT_M0** | `L_AMAT_M0` | **DONE** — M0-twin harness; OFF collapse / ON differs; `emit_m0=false` |
| **T_LIVE_gate** | `L_LIVE_DIAG` | on demand — score ~−0.03; no unlabeled threshold cut |
| **T_NAMM_cert** | `L_NAMM_013_030` | optional external witness (ATT-N soft only) |

### Run next (ATT-D **or** live closed-loop)

**Preferred #1 — ATT-D:** Re-run ATT-E-class internal-factor suppression in a second domain (explore only). Keep `claim_allowed=False` / no C5 raise without gates.

**Alt A — Live closed-loop:** Instrument real WoE / T_LIVE traces under the same ATT-R falsifiers (research branch; `emit_m0=false`).

**Alt B — T_NAMM_cert:** optional soft structural witness only (not strong \(N_H\)).

**S4:** No new C-level without pre-registered gates. Never claim AGI\*. Do not re-claim C2 via Kuramoto or M0 alone. Do not raise C3 from ATT-G/ATT-P/ATT-R explore alone. Do not claim strong \(N_H\) from ATT-N explore alone.  
**S5:** Update logs; then T_LIVE / T_NAMM as needed.

### Stop if

- C2 re-attributed to Kuramoto
- AGI\* / consciousness / \(\tau_{AGI}\) claimed from C2, EIS, WoE, AMAT, ATT partials, or Telegram
- Strong \(N_H\) claimed from opacity or ATT-N explore alone
- Live SEND faked by unlabeled threshold gutting
- Tests fail after 2 fix attempts → log blocker, stop
- Merge WoE into main `src/eia/` attempted

### Do NOT

- Merge research-branch runtime into `src/eia/` on main
- Paste AMAT JSON as bot persona
- Lower `min_contact_score` without labeling smoke
- Claim AGI / AGI\* / consciousness from EIS/WoE/AMAT/C-ladder/ATT alone
- Treat non-embeddability stubs / ATT-N explore as positive strong \(C_{\mathrm{non\text{-}emb}(H)}\)
- Treat Kuramoto \(R\) as Endogenous Cognitive Recurrence (\(R\) in ATT)
- Raise C3 solely from ATT-G, ATT-P, or ATT-R explore proxy

### Author

Roman Kuznetsov — research@anthemium.tech

---

## Current priority (#1)

**ATT-D:** Cross-domain ATT-E-class explore (second domain).  
**Alt:** live closed-loop ATT-R instrumentation **or** T_NAMM soft witness.

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

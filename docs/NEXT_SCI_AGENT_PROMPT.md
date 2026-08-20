# Next Sci Agent Prompt — EIA Sci-Flow Handoff

**Updated:** 2026-08-20 (M-E / ATT-G DONE explore proxy; next = ATT-P)  
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
10. `research/sci_flow/NON_EMBEDDABILITY_MEASUREMENT.md` — M-N / ATT-N design (no claim)
11. `research/sci_flow/M-D_metrics_2026-08-18.md` — Kuramoto still not a cause (not ATT-R)
12. `research/sci_flow/config.yaml`

### AGI\* / ATT framing (do not overclaim)

- C0–C5 are **empirical milestones toward** AGI\*, not AGI\*.
- **C2 / CF-4** ⇒ partial evidence for \(E_{\mathrm{endo}}\) / ATT-E only.
- **M-E / ATT-G** ⇒ explore proxy for goal genesis; **not C3**, not AGI\*.
- \(AGI^{*}\) / \(\tau_{AGI}\) requires sustained \(E,N_H,P,R,D\) — **research horizon, not claimed**.
- \(C_{\mathrm{non\text{-}emb}(H)}\) / ATT-N is **unmeasured**; stubs must keep `claim_allowed=False` / `agi_star_claim=false`.
- Endogeneity ≠ Autonomy; opacity ≠ non-embeddability; Trans-Human Cognition ≠ task SOTA; corrigibility ≠ persistence.
- **AuthenticReason** = production gate; EIS/ECS/WoE/AGI\* = research-only.

### Topologies

| Id | Loop | Status |
|----|------|--------|
| **T_EIA_state** | `L_EIA_CF4` | **DONE** — C2 via `zero_epistemic_gap` 0.06 (\(E_{\mathrm{endo}}\) / ATT-E partial) |
| **T_AMAT_M0** | `L_AMAT_M0` | **DONE** — M0-twin harness; OFF collapse / ON differs; `emit_m0=false` |
| **T_LIVE_gate** | `L_LIVE_DIAG` | on demand — score ~−0.03; no unlabeled threshold cut |
| **T_NAMM_cert** | `L_NAMM_013_030` | optional external witness (ATT-N soft only) |

### Run next (ATT-P)

**S1:** Pre-register multi-tick goal/motive persistence \(P_G\) (explore \(k \in \{10,50,200\}\)) with corrigibility separate.  
**S2:** Falsifiers: vanishes without re-prompt; or “persistence” = incorrigibility under correction.  
**S3:** Instrument `LoopScheduler` / multi-tick WoE runs on research branch only.  
**S4:** No new C-level without pre-registered gates. Never claim AGI\*. Do not re-claim C2 via Kuramoto or M0 alone. Do not raise C3 from ATT-G explore alone.  
**S5:** Update logs; then T_LIVE / T_NAMM / ATT-N as needed.

### Stop if

- C2 re-attributed to Kuramoto
- AGI\* / consciousness / \(\tau_{AGI}\) claimed from C2, EIS, WoE, AMAT, ATT partials, or Telegram
- Live SEND faked by unlabeled threshold gutting
- Tests fail after 2 fix attempts → log blocker, stop
- Merge WoE into main `src/eia/` attempted

### Do NOT

- Merge research-branch runtime into `src/eia/` on main
- Paste AMAT JSON as bot persona
- Lower `min_contact_score` without labeling smoke
- Claim AGI / AGI\* / consciousness from EIS/WoE/AMAT/C-ladder/ATT alone
- Treat non-embeddability stubs as positive \(C_{\mathrm{non\text{-}emb}(H)}\) evidence
- Treat Kuramoto \(R\) as Endogenous Cognitive Recurrence (\(R\) in ATT)
- Raise C3 solely from ATT-G explore proxy

### Author

Roman Kuznetsov — research@anthemium.tech

---

## Current priority (#1)

**ATT-P:** Multi-tick persistence pre-registration + harness.  
**M-N / ATT-N:** Execute only after encoding budget \(B\) is pre-registered.

## Completed this session

- Multi-topology registry
- **M-CF4** 100×6; C2 claimed (`zero_epistemic_gap` 0.06); AGI\* fields on summarizer
- **AGI\*** compact criterion + **phase-transition** expansion + **ATT** draft
- **M-N** non-embeddability design + `eia.non_embeddability` stub
- **M-ATT** `eia.agi_transition` order-parameter stubs (`agi_star_claim=false`)
- **T_AMAT_M0** M0-twin harness expand + falsifiers
- **M-E / ATT-G** goal genesis + genealogy + falsifiers (n=50); `claim_allowed=False`

# Next Sci Agent Prompt — EIA Sci-Flow Handoff

**Updated:** 2026-08-20 (AGI\* phase-transition + ATT drafted; M-CF4 = scoped \(E_{\mathrm{endo}}\); M-N scaffolded)  
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
8. `research/sci_flow/NON_EMBEDDABILITY_MEASUREMENT.md` — M-N / ATT-N design (no claim)
9. `research/sci_flow/M-D_metrics_2026-08-18.md` — Kuramoto still not a cause (not ATT-R)
10. `research/sci_flow/M0_TWIN_AMAT_DESIGN.md`
11. `research/sci_flow/config.yaml`

### AGI\* / ATT framing (do not overclaim)

- C0–C5 are **empirical milestones toward** AGI\*, not AGI\*.
- **C2 / CF-4** ⇒ partial evidence for \(E_{\mathrm{endo}}\) / ATT-E only.
- \(AGI^{*}\) / \(\tau_{AGI}\) requires sustained \(E,N_H,P,R,D\) — **research horizon, not claimed**.
- \(C_{\mathrm{non\text{-}emb}(H)}\) / ATT-N is **unmeasured**; stubs must keep `claim_allowed=False` / `agi_star_claim=false`.
- Endogeneity ≠ Autonomy; opacity ≠ non-embeddability; Trans-Human Cognition ≠ task SOTA; corrigibility ≠ persistence.
- **AuthenticReason** = production gate; EIS/ECS/WoE/AGI\* = research-only.

### Topologies

| Id | Loop | Status |
|----|------|--------|
| **T_EIA_state** | `L_EIA_CF4` | **DONE** — C2 via `zero_epistemic_gap` 0.06 (\(E_{\mathrm{endo}}\) / ATT-E partial) |
| **T_AMAT_M0** | `L_AMAT_M0` | **#1 next** — expand beyond `amat_m0` stub (ATT-R / motive-side \(E\)) |
| **T_LIVE_gate** | `L_LIVE_DIAG` | on demand — score ~−0.03; no unlabeled threshold cut |
| **T_NAMM_cert** | `L_NAMM_013_030` | optional external witness (ATT-N soft only) |

### Run next (T_AMAT_M0 / M-E)

**S1:** Motives from off-typical / M0-twin architecture (AMAT law), not prompt persona — strengthens \(E_{\mathrm{endo}}\) and ATT-R.  
**S2:** Keep `emit_m0=false`; wire audit sketch into receipts optional.  
**S3:** Implement on research branch only; NAMM certs stay in NAMM repo.  
**S4:** No new C-level without pre-registered gates. C2 already from CF-4 — do not re-claim via Kuramoto. Never claim AGI\*.  
**S5:** Update logs; optional live diagnose; if touching ATT cells, update evidence matrix only (no fake thresholds).

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

### Author

Roman Kuznetsov — research@anthemium.tech

---

## Current priority (#1)

**T_AMAT_M0:** Expand M0-twin harness; then M-E / ATT-G; ATT-P persistence pre-reg; T_NAMM_cert / T_LIVE_gate as needed.  
**M-N / ATT-N:** Execute only after encoding budget \(B\) is pre-registered.

## Completed this session

- Multi-topology registry
- **M-CF4** 100×6; C2 claimed (`zero_epistemic_gap` 0.06); AGI\* fields on summarizer
- **AGI\*** compact criterion + **phase-transition** expansion + **ATT** draft
- **M-N** non-embeddability design + `eia.non_embeddability` stub
- **M-ATT** `eia.agi_transition` order-parameter stubs (`agi_star_claim=false`)

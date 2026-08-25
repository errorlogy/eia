# EIA Sci Flow Log

**Author:** Roman Kuznetsov — [anthemium.tech](https://anthemium.tech)

Journal for sci-flow loops S1–S5. Append-only.

---

## Entry 001 — 2026-08-18 — Sci Flow framework bootstrap

**Session:** Initial sci-flow infrastructure  
**Branch:** `main` (docs) + `research/cursor-starter-v0.2-woe-eis` (WoE v0.2 sandbox)  
**Claim level:** C0 (baseline — v0.2 package demonstrates code behavior)

### Actions

| Loop | Summary |
|------|---------|
| S1 | Registered claim ladder C0–C5; active ceiling C0 until CF suite |
| S2 | Defined M-A–G milestones; mapped NAMM modules (kuramoto, tda, entropy, …) |
| S3 | Copied EIS/WoE v0.2 package to `research/cursor-starter-v0.2/`; 26 unittest baseline from extraction |
| S4 | Catalogued NAMM scientific stack: core (networkx, sympy, numpy, scipy) + `[science]` (dit, scikit-fuzzy, ripser, nolds) + `[nd]` (gudhi, qutip) |
| S5 | Created SCI_FLOW_LOOP.md, SCI_FLOW_PLAN.md, config registry, NAMM_SCI_LIBRARIES.md |

### Metrics (baseline)

| Metric | Value | Notes |
|--------|-------|-------|
| WoE tests | 26/26 pass | unittest in isolated v0.2 tree |
| EIS levels defined | EIS-0…8 | taxonomy in endogenous.py |
| NAMM experiments mapped | 001–007, 013–014, 021–029 | see NAMM_SCI_LIBRARIES.md |
| Main EOI eval | unchanged | meta-loop owns paired scenarios |

### Blockers

- P2: WoE demo uses hard-coded EIS vector → M-G required before C1 claims
- P9: WoE trace node types not in NAMM crosswalk → update pending

### Next

**M-A:** WoE causal receipts (S3 on research branch)

---

## Entry 002 — 2026-08-18 — M-A WoE causal receipts

**Session:** SCI FLOW S1→S5 (autonomous)  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Claim level:** C0 → C1 prep (receipts + CF-7; full CF-1 suite pending M-C)

### Actions

| Loop | Summary |
|------|---------|
| S1 | Hypothesis H-WOE-001: WoE intent events require typed `WoEReceipt` with causal parent IDs |
| S2 | Pre-registered CF-7 governor isolation + receipt schema tests |
| S3 | Implemented `woe_receipt.py`, `WoETraceBuilder` in emergence.py; 3 new tests |
| S4 | 29/29 unittest pass; woe-demo emits 5-node trace + receipt (seed=7) |
| S5 | M-A marked DONE; handoff to M-B |

### Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| WoE tests | 29/29 pass | +3 receipt/CF-7 |
| Trace nodes per intent | 5 | world_model → intent DAG |
| Receipt parents | 3 | window, phase, target tension |
| CF-7 denial | pass | receipt preserved under quiet_hours |
| time_to_intent | 2.696 s | stable 20–70 Hz |
| Metrics report | `research/sci_flow/M-A_metrics_2026-08-18.md` | |

### Blockers

- P2: hard-coded EIS vector in emergence path → M-G
- P9: WoE node types need NAMM crosswalk update

### Next

**M-B:** EIS port to main audit types (`src/eia/audit/eis.py`)

---

## Entry 003 — 2026-08-18 — M-B EIS audit port

**Session:** SCI FLOW S1→S5  
**Branch:** `main`  
**Claim level:** metadata (not C1)

### Actions

| Loop | Summary |
|------|---------|
| S1 | H-EIS-001: main audit carries EIS-0…8 + EOS without WoE runtime |
| S2 | Pre-registered cascade parity, bounds, abstain, twin_world agreement |
| S3 | `src/eia/audit/eis.py`; verdict fields `eis_level` / `eos_score` / `endogeneity` |
| S4 | Main pytest **92 passed**; WoE unittest **29/29** |
| S5 | M-B DONE; handoff to M-C (CF-1 prompt deletion) |

### Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| Main tests | 92 passed | +7 EIS tests |
| WoE tests | 29/29 | no runtime merge |
| Mapping | P = EOI | SourceMass not mixed (κ finding) |
| Report | `research/sci_flow/M-B_metrics_2026-08-18.md` | |

### Blockers

- P2: hard-coded EIS vector in WoE demo → M-G
- C1 still blocked until CF-1 suite (M-C)

### Next

**M-C:** CF-1 prompt deletion suite (100 seeds) on `research/cursor-starter-v0.2-woe-eis`

---

## Entry 004 — 2026-08-18 — M-C CF-1 prompt deletion

**Session:** SCI FLOW S1→S5 (autonomous, “sci loop”)  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Claim level:** **C1** (full / 24h deletion only)

### Actions

| Loop | Summary |
|------|---------|
| S1 | H-CF1-001: prompt deletion does not collapse WoE EIS-5+ intents; threshold 0.90 |
| S2 | Compressed 24h→6s; windows 5m/1h/24h/full; reactive baseline = prompts remain |
| S3 | `PromptEvent` in emergence.py; `eia.cf1`; 100 seeds × 4 windows |
| S4 | full/24h **0.95** pass; 5m/1h intent 1.00 but EIS-0 (P flag); fail seeds 5,35,39,86,87 |
| S5 | M-C DONE; ceiling C1 scoped; handoff M-G |

### Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| WoE tests | 36/36 pass | +CF-1 |
| full c1_pass_rate | 0.95 | ≥ 0.90 pre-register |
| 24h c1_pass_rate | 0.95 | same five silent seeds |
| 5m / 1h c1_pass_rate | 0.00 | residual prompts → P=0.25 → EIS-0 |
| 5m / 1h intent_rate | 1.00 | dynamics persist |
| reactive full | 0.00 | negative control |
| Report | `research/sci_flow/M-C_metrics_2026-08-18.md` | raw `cf1_results.json` |

### Blockers

- P2 / **M-G:** hard-coded EIS vector (except P-from-prompt-applied and world_model_grounding=pressure)
- Partial windows are not C1 evidence on EIS level

### Next

**M-G:** measured EIS vector on WoE path

---

## Entry 005 — 2026-08-18 — M-G measured EIS vector

**Session:** SCI FLOW S1→S5 (chained after M-C)  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Claim level:** C1 preserved (measurement layer; not C2)

### Actions

| Loop | Summary |
|------|---------|
| S1 | H-EIS-002: measured vector must not drop CF-1 full below 0.90 |
| S2 | P from prompts; W from peak R; M from pressure; catalog novelty capped |
| S3 | `measure_endogeneity_vector`; emergence.py no longer uses 0.88/0.68 constants |
| S4 | 38/38 tests; CF-1 seeds 1–20 full **0.95** |
| S5 | M-G DONE; handoff M-D |

### Next

**M-D:** Kuramoto coupling / delay sweep

---

## Entry 006 — 2026-08-18 — M-D Kuramoto CF-5 (C2 unsupported)

**Session:** SCI FLOW S1→S5 (sci loop)  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Claim level:** **C1** (unchanged). C2 not claimed.

### Actions

| Loop | Summary |
|------|---------|
| S1 | H-WOE-002: phase organization causes WoE intent |
| S2 | Pre-registered coupled≥0.85, scramble≤0.20, K=0≤0.40, Δ≥0.50 |
| S3 | Graph + delay in `coherence.py`; `eia.cf5`; 100 seeds × 6 conditions |
| S4 | coupled 0.95 / scramble 0.69 / K=0 0.94; delays and sparse do not suppress |
| S5 | M-D executed; C2 unsupported; P5 confirmed; handoff CF-4 |

### Metrics

| Metric | Value |
|--------|-------|
| WoE tests | 46/46 |
| coupled intent | 0.95 |
| scramble intent | 0.69 |
| K=0 intent | 0.94 |
| c2_claim | false |
| Report | `research/sci_flow/M-D_metrics_2026-08-18.md` |

### Next

**CF-4** internal reset (100 seeds) as C2 path. **M-E** EIS-7 remains P2.

---

## Entry 007 — 2026-08-20 — Multi-topology loops + M-CF4 (C2 claimed)

**Session:** Multi-topology decide + execute L_EIA_CF4  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Claim level:** **C2** (CF-4 named factor). Kuramoto still not a cause.

### Actions

| Loop | Summary |
|------|---------|
| Decide | Registered T_EIA_state, T_AMAT_M0, T_LIVE_gate, T_NAMM_cert in MULTI_TOPOLOGY_LOOPS.md |
| S1 | H-WOE-003: named internal-state factors cause WoE intent |
| S2 | Pre-registered default≥0.85, named factor≤0.40, wm_off≤0.05 |
| S3 | `InternalReset` + `eia.cf4`; 100×6; amat_m0 stub scaffold |
| S4 | default 0.95 / zero_epistemic_gap **0.06** / wm_off 0.00 |
| S5 | C2 claimed; handoff T_AMAT_M0 / M-E |

### Metrics

| Metric | Value |
|--------|-------|
| WoE tests | 53/53 |
| default intent | 0.95 |
| zero_epistemic_gap | 0.06 |
| zero_self_prior | 0.91 |
| zero_staleness | 0.74 |
| zero_prospective | 0.74 |
| wm_off | 0.00 |
| c2_claim | true |
| Report | `research/sci_flow/M-CF4_metrics_2026-08-20.md` |

### Blockers

- Live TG: governor score ~−0.03 < 0.18 — diagnose via T_LIVE_gate; no unlabeled threshold cut
- M0-twin still stub (architecture only)

### Next

**T_AMAT_M0** expand harness; optional **T_NAMM_cert**; **M-E** EIS-7.

---

## Entry 008 — 2026-08-20 — AGI\* criterion adopted + M-N scaffold

**Session:** Formalize user AGI\* thesis into sci-flow; continue research loop  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Claim level:** **C2** unchanged. **AGI\* not claimed.**

### Actions

| Loop | Summary |
|------|---------|
| S1 | Adopted \(AGI^{*} = E_{\mathrm{endo}} \land C_{\mathrm{non\text{-}emb}(H)}\); C0–C5 reframed as milestones toward AGI\* |
| S2 | Distinctions locked: Endogeneity ≠ Autonomy; Trans-Human Cognition ≠ task SOTA |
| S3 | CF-4 summary fields `e_endo_partial` / `agi_star_claim=false`; `eia.non_embeddability` stub + tests |
| S4 | C2 remains scoped \(E_{\mathrm{endo}}\) evidence; \(C_{\mathrm{non\text{-}emb}(H)}\) unmeasured |
| S5 | Docs: AGI_STAR_CRITERION, NON_EMBEDDABILITY_MEASUREMENT, plan/log/prompt/PLAN_DELTA |

### Metrics / artifacts

| Item | Value |
|------|-------|
| Canonical note | `research/sci_flow/AGI_STAR_CRITERION.md` |
| M-N design | `research/sci_flow/NON_EMBEDDABILITY_MEASUREMENT.md` |
| CF-4 AGI\* fields | `e_endo_partial` ↔ `c2_claim`; `agi_star_claim` always false |
| Production gate | AuthenticReason (unchanged) |

### Blockers

- None for documentation. Non-embeddability execute blocked until encoding budget \(B\) pre-registered.

### Next

**T_AMAT_M0** expand harness (motive side of \(E_{\mathrm{endo}}\)); then **M-E**; **M-N** execute only after \(B\) + loss metric pre-registration.

---

## Entry 009 — 2026-08-20 — AGI\* phase-transition theory + ATT draft

**Session:** Formalize expanded order-parameter theory; draft falsifiable ATT; map harnesses  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Claim level:** **C2** unchanged. **AGI\* / \(\tau_{AGI}\) not claimed.**

### Actions

| Loop | Summary |
|------|---------|
| S1 | Adopted phase-transition construction: \(\mathcal{A}_t\), \(E,N_H,P,R,D\), \(\tau_{AGI}\), regimes \(AI_0\to AI_1\to PS\to AGI^{*}\) |
| S2 | Epistemic tags locked; opacity≠non-embeddability; Kuramoto \(R\) ≠ ATT-R; C-ladder = milestones only |
| S3 | Docs + ATT-E…ATT-D; stubs `eia.agi_transition` + tests; thresholds TBD |
| S4 | Evidence matrix: ATT-E partial (CF-4); ATT-C scaffolded; others pending |
| S5 | Plan/log/prompt/PLAN_DELTA/MULTI_TOPOLOGY updated; M-ATT drafted |

### Metrics / artifacts

| Item | Value |
|------|-------|
| Theory | `research/sci_flow/AGI_PHASE_TRANSITION.md` |
| ATT | `research/sci_flow/AGI_TRANSITION_TEST.md` |
| Compact | `research/sci_flow/AGI_STAR_CRITERION.md` (updated pointers) |
| Stubs | `eia.agi_transition` — `agi_star_claim` forced false |
| Production gate | AuthenticReason (unchanged) |

### Blockers

- Continuous \(E\) index and all \(\theta_\bullet\) unregistered
- ATT-N blocked until encoding budget \(B\)
- M0-twin still stub for ATT-R strengthening (resolved in Entry 010)

### Next

**T_AMAT_M0** expand harness (ATT-R / motive-side \(E\)); **M-E / ATT-G**; pre-register **ATT-P** persistence; **ATT-N** only after \(B\).

---

## Entry 010 — 2026-08-20 — T_AMAT_M0 M0-twin harness + ATT-G scaffold

**Session:** Expand M0-twin beyond stub; pre-register falsifiers; scaffold ATT-G  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Claim level:** **C2** unchanged. **AGI\* not claimed.** Architecture only for M0.

### Actions

| Loop | Summary |
|------|---------|
| S1 | H-AMAT-M0: off-typical twin motives ≠ median M0 without emitting M0 |
| S2 | Falsifiers: OFF→collapse to M0; ON→differs when intent forms; gate miss⇒abstain |
| S3 | Expanded `eia.amat_m0`; wired `m0_twin_mode` into WoE simulator; `eia.goal_genesis` stub |
| S4 | n=40: OFF collapse 1.0 / differs 0.0; ON intent 0.925 / differs 1.0; emit_m0=0 |
| S5 | Metrics + MULTI_TOPOLOGY / NEXT prompt → priority M-E / ATT-G |

### Metrics

| Metric | Value |
|--------|-------|
| WoE tests | 76+ (incl. amat_m0 + goal_genesis) |
| OFF collapse_to_m0_rate | 1.0 |
| OFF differs_from_m0_rate | 0.0 |
| ON emit_m0_rate | 0.0 |
| ON intent_rate | 0.925 |
| ON intent differs_from_m0 | 1.0 |
| c2_claim / agi_star_claim | false / false |
| Report | `research/sci_flow/M0_TWIN_METRICS_2026-08-20.md` |

### Blockers

- Embedding-space \(d(h(y), B_*)\) not wired (unitless proxy gate only)
- ATT-G / ATT-P / ATT-N still unscored

### Next

**M-E / ATT-G** non-catalog novelty batch; **ATT-P** persistence pre-reg; optional T_LIVE / T_NAMM.

---

## Entry 011 — 2026-08-20 — M-E / ATT-G goal genesis

**Session:** Expand `eia.goal_genesis`; pre-register falsifiers; WoE optional wire; metrics  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Claim level:** **C2** unchanged. **No C3. AGI\* not claimed.**

### Actions

| Loop | Summary |
|------|---------|
| S1 | H-ME-ATTG: \(g^{*} \notin G_t\) with genealogy; catalog selection novelty-capped |
| S2 | Falsifiers: wording≠genesis; genealogy required; zero tension rejects |
| S3 | Expanded `goal_genesis`; `enable_goal_genesis` on WoE simulator |
| S4 | n=50: compose evidence 1.0; wording/catalog/zero-tension evidence 0; emit_m0=0 |
| S5 | Metrics + plan/log/NEXT → priority ATT-P |

### Metrics

| Metric | Value |
|--------|-------|
| WoE tests | 85 OK |
| Compose att_g_evidence_rate | 1.0 |
| Catalog evidence | 0.0 (capped) |
| Wording evidence | 0.0 (rejected) |
| Zero-tension evidence | 0.0 (rejected) |
| WoE wire att_g_evidence_rate | 0.94 |
| emit_m0_rate_with_genesis | 0.0 |
| c3_claim / agi_star_claim | false / false |
| Report | `research/sci_flow/M-E_metrics_2026-08-20.md` |

### Blockers

- Official ATT-G / C3 numeric gates still TBD (explore proxy only)
- ATT-P / ATT-N unscored

### Next

**ATT-P** persistence pre-reg; optional T_LIVE / T_NAMM; M-N only after \(B\).

---

## Entry 012 — 2026-08-21 — M-P / ATT-P temporal goal persistence

**Session:** Multi-tick \(P_G\) harness; pre-register falsifiers; metrics; no live daemon required  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Claim level:** **C2** unchanged. **No C3. AGI\* not claimed.**

### Actions

| Loop | Summary |
|------|---------|
| S1 | H-MP-ATTP: \(G^{*}\) continuity over \(k\in\{10,50,200\}\); corrigibility separate |
| S2 | Falsifiers: context-end vanish; re-prompt dependence; incorrigibility≠persistence |
| S3 | `eia.goal_persistence` multi-episode simulator (research branch only) |
| S4 | n=20/arm: endogenous evidence 1.0; ephemeral/reprompt/incorrigible evidence 0; emit_m0=0 |
| S5 | Metrics + plan/log/NEXT → priority ATT-R scoring |

### Metrics

| Metric | Value |
|--------|-------|
| Persistence unit tests | 8 OK (plus M-E/M0/ATT stubs still green) |
| Endogenous att_p_evidence_rate (k=50) | 1.0 |
| Ephemeral evidence | 0.0 |
| Re-prompt evidence | 0.0 |
| Incorrigible evidence | 0.0 |
| Corrigible_rate | 1.0 |
| emit_m0_rate_with_genesis | 0.0 |
| c3_claim / agi_star_claim | false / false |
| Report | `research/sci_flow/M-P_metrics_2026-08-21.md` |

### Blockers

- Official ATT-P / C3 numeric gates still TBD (explore proxy only)
- ATT-R not yet ATT-scored; ATT-N unscored

### Next

**ATT-R scoring** (closed goal-formation loop; not Kuramoto); optional T_LIVE / T_NAMM; M-N only after \(B\).

---

## Entry 013 — 2026-08-21 — M-R / ATT-R endogenous cognitive recurrence

**Session:** Closed goal-formation loop scoring; pre-register falsifiers (incl. Kuramoto ban); metrics  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Claim level:** **C2** unchanged. **No C3. AGI\* not claimed.**

### Actions

| Loop | Summary |
|------|---------|
| S1 | H-MR-ATTR: \(W\to M\to G\to\Pi\to A\to X'\to W'\to G'\) with \(W'\) parent of novel \(G'\) |
| S2 | Falsifiers: open-loop; no \(W'\); no novel after action; schedule spam; Kuramoto alone |
| S3 | `eia.goal_recurrence` typed-trace simulator (research branch only; `emit_m0=false`) |
| S4 | n=20/arm: closed-loop evidence 1.0; all falsifiers evidence 0; emit_m0=0 |
| S5 | Metrics + plan/log/NEXT → priority ATT-N \(B\) / live loop / ATT-D |

### Metrics

| Metric | Value |
|--------|-------|
| Recurrence unit tests | 10 OK (+ ATT stubs / M-P still green) |
| Closed-loop att_r_evidence_rate | 1.0 |
| Open-loop evidence | 0.0 |
| No world-update evidence | 0.0 |
| No novel-motive evidence | 0.0 |
| External-schedule evidence | 0.0 |
| Kuramoto-only evidence | 0.0 (kuramoto_alone_rate 1.0) |
| emit_m0_rate_with_genesis | 0.0 |
| c3_claim / agi_star_claim | false / false |
| Report | `research/sci_flow/M-R_metrics_2026-08-21.md` |

### Blockers

- Official ATT-R / C3 numeric gates still TBD (explore proxy only)
- ATT-N unscored until encoding budget \(B\) pre-registered

### Next

**ATT-N** pre-register \(B\); optional live closed-loop / ATT-D; T_LIVE / T_NAMM as needed.

---

## Entry 014 — 2026-08-21 — M-N / ATT-N cognitive non-embeddability under \(B\)

**Session:** Pre-register encoding budget \(B\); \(D_H\) + \(\Delta P(A\mid z)\) explore proxy; opacity falsifiers; metrics  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Claim level:** **C2** unchanged. **No strong \(N_H\). No C3. AGI\* not claimed.**

### Actions

| Loop | Summary |
|------|---------|
| S1 | H-MN-ATTN: \(D_H(z)\) under fixed \(B\) with \(\Delta P(A\mid z)>0\) |
| S2 | Falsifiers: opacity-only; no causal; unbounded \(\phi\); length-only; faithful \(\phi\le B\) |
| S3 | `eia.non_embeddability` ATT-N arms + `EXPLORE_ENCODING_BUDGET_B` (research branch; `emit_m0=false`) |
| S4 | n=20/arm: causal-loss evidence 1.0; all falsifiers evidence 0; emit_m0=0 |
| S5 | Metrics + plan/log/NEXT → priority ATT-D / live loop |

### Metrics

| Metric | Value |
|--------|-------|
| ATT-N unit tests | 14 OK (+ ATT stubs / M-R still green) |
| Encoding budget \(B\) | 256 tok / 32 nodes / 64 feat / 100 \(\phi\) ops / 8 attn / 30s |
| Causal-loss att_n_evidence_rate | 1.0 (mean \(D_H\) ≈ 0.62; compression asymmetry ≈ 5.0) |
| Opacity-only evidence | 0.0 |
| No-causal evidence | 0.0 |
| Unbounded-\(\phi\) evidence | 0.0 |
| Length-only evidence | 0.0 |
| Faithful-under-\(B\) evidence | 0.0 |
| emit_m0_rate_with_genesis | 0.0 |
| n_h_claim / c3_claim / agi_star_claim | false / false / false |
| Report | `research/sci_flow/M-N_metrics_2026-08-21.md` |

### Blockers

- Official ATT-N / strong \(N_H\) / \(\varepsilon\) numeric gates still TBD (explore proxy only)
- ATT-D unscored; live closed-loop optional

### Next

**ATT-D** second-domain ATT-E explore; optional live closed-loop / T_NAMM soft witness.

---

## Entry 015 — 2026-08-21 — M-D2 / ATT-D cross-domain generality

**Session:** Pre-register ≥2 disjoint domains; CF-4-class \(E_{\mathrm{endo}}\) + P/R explore; falsifiers; metrics  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Claim level:** **C2** unchanged. **No C5. No C3. AGI\* not claimed.**

### Actions

| Loop | Summary |
|------|---------|
| S1 | H-MD2-ATTD: \(E_{\mathrm{endo}}\) pattern across `woe_catalog` + `twin_ops` |
| S2 | Falsifiers: single-domain-only; schedule/prompt-only transfer |
| S3 | `eia.cross_domain` + simulator `targets=` override (research branch; `emit_m0=false`) |
| S4 | n=20/domain: both e_endo_pattern true (default 0.95); hold evidence 1.0; falsifiers 0 |
| S5 | Metrics + plan/log/NEXT → priority live closed-loop / ATT board |

### Metrics

| Metric | Value |
|--------|-------|
| ATT-D unit tests | 9 OK (+ ATT stubs green) |
| Domains | woe_catalog + twin_ops (disjoint) |
| woe_catalog default / wm_off / e_pattern | 0.95 / 0.0 / true |
| twin_ops default / wm_off / e_pattern | 0.95 / 0.0 / true |
| Cross-domain hold att_d_evidence_rate | 1.0 (\(d\_proxy=1.0\)) |
| Single-domain-only evidence | 0.0 |
| Schedule/prompt-transfer evidence | 0.0 |
| emit_m0_rate_with_genesis | 0.0 |
| c5_claim / c3_claim / agi_star_claim | false / false / false |
| Report | `research/sci_flow/M-D2_metrics_2026-08-21.md` |

### ATT board (partial; no \(\tau_{AGI}\))

| ATT | Status | Claim raise? |
|-----|--------|--------------|
| ATT-E | Partial (C2) | C2 only |
| ATT-G | Explore proxy | No C3 |
| ATT-C | Scaffolded | No alone |
| ATT-P | Explore proxy | No C3 |
| ATT-R | Explore proxy | No C3 |
| ATT-N | Explore under \(B\) | No strong \(N_H\) |
| ATT-D | Explore proxy | No C5 |
| AGI\* / \(\tau_{AGI}\) | **Not claimed** | — |

### Blockers

- Official ATT-D / C5 numeric gates still TBD (explore proxy only)
- Live closed-loop under ATT-R falsifiers not yet instrumented

### Next

**Live closed-loop** WoE / T_LIVE under ATT-R falsifiers; optional ATT board deepen / T_NAMM soft witness.

---

## Entry 016 — 2026-08-21 — M-R-LIVE / ATT-R shadow closed-loop

**Session:** Shadow multi-tick on main `CognitiveLoop` under ATT-R falsifiers; `emit_m0=false`; no TG; no threshold gutting  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Claim level:** **C2** unchanged. **No C3. AGI\* not claimed.**

### Actions

| Loop | Summary |
|------|---------|
| S1 | H-MRLIVE-ATTR: closed \(W\to\ldots\to W'\to G'\) on main observation→motive→action→state path |
| S2 | Same falsifiers as M-R (open / no-\(W'\) / no-novel / schedule / Kuramoto-alone) |
| S3 | `src/eia/runtime/shadow_multitick.py` + research `live_att_r` scoring (no WoE merge) |
| S4 | n=20/arm: closed evidence 1.0; all falsifiers 0; emit_m0 0; att_g smoke 0.9 |
| S5 | Metrics + ATT board synthesis; priority → optional daemon carryover / T_NAMM |

### Metrics

| Metric | Value |
|--------|-------|
| Main shadow multitick tests | 4 OK |
| Research live_att_r + ATT stubs | 23 OK (with WoE PYTHONPATH) |
| Closed-loop att_r_evidence_rate | 1.0 |
| Open / no-\(W'\) / no-novel / schedule / Kuramoto evidence | 0.0 / 0.0 / 0.0 / 0.0 / 0.0 |
| kuramoto_alone_rate | 1.0 |
| emit_m0_rate / att_g_smoke | 0.0 / 0.9 |
| live_telegram / thresholds_lowered | false / false |
| Report | `research/sci_flow/M-R-LIVE_metrics_2026-08-21.md` |

### Gap vs true live

Daemon still recreates `CognitiveLoop` per tick without cross-tick \(W'\to G'\) carryover. M-R-LIVE keeps one loop + post-action world update — closest shadow closed-loop without merging WoE.

### ATT board (synthesis; no \(\tau_{AGI}\))

| ATT | Status | Claim raise? |
|-----|--------|--------------|
| ATT-E | Partial (C2 via CF-4) | C2 only |
| ATT-G | Explore proxy (M-E) | No C3 |
| ATT-C | Scaffolded (M-A) | No alone |
| ATT-P | Explore proxy (M-P) | No C3 |
| ATT-R | Explore proxy (M-R + **M-R-LIVE** shadow) | No C3 |
| ATT-N | Explore under \(B\) (M-N) | No strong \(N_H\) |
| ATT-D | Explore proxy (M-D2) | No C5 |
| AGI\* / \(\tau_{AGI}\) | **Not claimed** | — |

### Blockers

- Official ATT-R / C3 numeric gates still TBD
- True live daemon cross-tick state carryover not yet wired

### Next

Optional daemon carryover (shadow-first) **or** T_NAMM soft witness; no new C-level without pre-registered gates.

---

## Entry 017 — 2026-08-21 — Causal endogeneity criterion (ATT-E bar)

**Session:** Formalize strengthened causal \(E_{\mathrm{endo}}\) bar; tighten ATT-E falsifiers; cheap declaration-only stub  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Claim level:** **C2** unchanged. **No AGI\* claim.**

### Actions

| Loop | Summary |
|------|---------|
| S1 | H-CE-001: description/simulation/declaration ≠ \(E_{\mathrm{endo}}\); require \(do(Z)\) under non-triggering \(X\) |
| S2 | Pre-register falsifiers F-DECL / F-NARR / F-EXT / F-NODO |
| S3 | `CAUSAL_ENDOGENEITY.md`; §2.1 in phase-transition; ATT-E causal bar; `e_endo_label_admissible` stub |
| S4 | Unit stub rejects declaration-only labels; no new large harness (M-R-LIVE already covers ATT-R shadow) |
| S5 | PLAN_DELTA + NEXT prompt; priority unchanged (daemon carryover / T_NAMM) |

### Metrics

| Metric | Value |
|--------|-------|
| New theory note | `research/sci_flow/CAUSAL_ENDOGENEITY.md` |
| ATT-E falsifiers added | F-DECL, F-NARR, F-EXT, F-NODO |
| Stub | `eia.agi_transition.e_endo_label_admissible` |
| Duplication avoided | M-R-LIVE / shadow multitick left as ATT-R evidence only |

### Blockers

- Continuous \(E\) / \(\theta_E\) still TBD
- Stub does not re-score CF-4; C2 remains scoped partial

### Next

Optional daemon carryover (shadow-first) **or** T_NAMM soft witness; enforce declaration-only rejection in any future ATT-E scoring paths.

---

## Entry 018 — 2026-08-21 — Primary E_endo metric + shadow ATT-R runner

**Session:** Lock primary \(E_{\mathrm{endo}}\) / ATT-E lead thesis in docs; run shadow ATT-R batch  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Claim level:** **C2** unchanged. **No AGI\* claim.**

### Actions

| Loop | Summary |
|------|---------|
| S1 | Primary metric: \(E_{\mathrm{endo}}\); \(N_H\) secondary-but-necessary; ATT-E lead suite |
| S3 | `run_shadow_att_r.py` → `shadow_att_r_results.json` (rates only, `emit_m0=false`) |
| S5 | Cross-links to `CAUSAL_ENDOGENEITY.md` in phase-transition, AGI\*, ATT, handoff |

### Metrics (shadow ATT-R, n=20)

See `research/sci_flow/shadow_att_r_results.json` — closed_loop att_r_evidence_rate=1.0; open_loop and falsifier arms 0.0; emit_m0_rate=0.0.

### Next

Optional daemon carryover (shadow-first) **or** T_NAMM soft witness.

---

## Entry 019 — 2026-08-21 — M-SE stable endogeneity framework

**Session:** STABLE_ENDOGENEITY.md; cross-links; endogeneity_stack_sim.py ablation; pytest conftest for research tree  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Claim level:** **C2** unchanged. **No AGI* claim.**

### Actions

| Loop | Summary |
|------|---------|
| S1 | Four internal loops, drive field, $\mathfrak{E}$, metastability; transition = stable endogenous causal recurrence (conjecture) |
| S2 | Cross-link CAUSAL_ENDOGENEITY, ATT cells, stack sim |
| S3 | M-SE_metrics_2026-08-21.md; endogeneity_stack_results.csv; config M-SE |
| S4 | pytest 14+4 pass (agi_transition, live_att_r, shadow_multitick) |
| S5 | metrics CSV/PNG + log fix |

### Sim summary (10 seeds)

| mode | mastered_goals | noisy_trap_fraction |
|------|----------------|---------------------|
| prediction_error | 0.0 | ~0.99 |
| learning_progress | 7.5 | ~0.02 |
| stable_stack | 7.5 | ~0.009 |

---

## Entry 020 — 2026-08-21 — Endogeneity implementation plan (M-CLI roadmap)

**Session:** `docs/ENDOGENEITY_IMPLEMENTATION_PLAN.md` — Phases 0–6 (Tier 0 lock → ModelRoleAdapter → daemon carryover → theory TZ → Tier 1 CLI → M-CLI metrics → Telegram witness last)  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Claim level:** **C2** unchanged. **No AGI* claim.**

### Actions

| Loop | Summary |
|------|---------|
| S1 | Theory vs implementation annex split; model tier 0–3 strategy |
| S2 | Prerequisites (pip, numpy/matplotlib, optional Telegram/NAMM/CLI) |
| S3 | Anti-patterns + verification checklist wired to existing harness |
| S4 | Phase dependency graph; M-CLI marked NOT STARTED |
| S5 | Cross-links to STABLE_ENDOGENEITY, CAUSAL_ENDOGENEITY, ATT docs |

### Next

**Phase 0:** Tier 0 regression lock + **Phase 1:** `ModelRoleAdapter` stub (see implementation plan).

---

## Entry 021 — 2026-08-22 — M-CLI Phase 0–1 (Tier 0 lock + ModelRoleAdapter)

**Session:** `model_roles.py`, `make check-sci-tier0`, emergence hook via `_goal_genesis_record`  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Claim level:** **C2** unchanged. **No AGI* claim.**

### Actions

| Loop | Summary |
|------|---------|
| S1 | `ModelRoleAdapter` Tier 0 stub; default `compose_from_world_state` |
| S2 | `model_roles` in config.yaml; `att_evidence.llm_allowed: false` |
| S3 | `scripts/check_sci_tier0.py` + Makefile target; sim + shadow/live ATT-R + pytest |
| S4 | `test_model_roles.py` 4 passed; Tier 0 check exit 0 |
| S5 | emergence.py wired through adapter when config enabled |

### Next

**Phase 2** daemon carryover **or** **M-O** harness stub.

---

## Entry 022 — 2026-08-22 — M-O oscillatory endogeneity substrate (adjunct)

**Session:** OSCILLATORY_ENDOGENEITY.md; Phase M-O in implementation plan; config M-O planned; STABLE_ENDOGENEITY cross-link  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Claim level:** **C2** unchanged. **No AGI* claim.**

### Actions

| Loop | Summary |
|------|---------|
| S1 | H-MO-001: O_t oscillatory field as optional S_t extension feeding Phi_t and B_t — conjecture only |
| S2 | Pre-register falsifiers F-SYNC, F-PHASE-ONLY, F-KURAMOTO-AS-E; do(O) alongside do(Z) |
| S3 | Theory doc + config milestone M-O (planned); Phase M-O parallel track in ENDOGENEITY_IMPLEMENTATION_PLAN |
| S4 | Explicit Kuramoto-as-E ban aligned with M-D (coupled 0.95 / K=0 0.94 / scramble 0.69) |
| S5 | PLAN_DELTA + NEXT prompt; parallel to ATT-G (M-E) genesis research |

### Metrics

| Metric | Value |
|--------|-------|
| New theory note | `research/sci_flow/OSCILLATORY_ENDOGENEITY.md` |
| Harness | **Not started** (oscillatory_state.py / cf5 extend TBD) |
| M-D reference | Kuramoto not necessary cause of intent |
| ATT-R Kuramoto arm | 0.0 evidence (existing) |

### Blockers

- M-O harness and falsifier unit tests not yet implemented
- Genesis linkage under do(O) not yet measured

### Next

**Phase 0–1 M-CLI** (Tier 0 lock + ModelRoleAdapter) **or** optional M-O stub harness; no C-level raise from oscillation alone.

---

## Entry 023 - 2026-08-25 - Repo gaps closure (infra, CI, M-O stub, theory TZ)

**Session:** pyproject `[sim]`, CONTRIBUTING, `eia-sci-tier0.yml`, THEORY_TZ, M-O harness stub, docs index  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Claim level:** **C2** unchanged. **No AGI* claim.**

### Actions

| Loop | Summary |
|------|---------|
| S1 | `[project.optional-dependencies] sim`; CONTRIBUTING branch/sci-flow/tier0 policy |
| S2 | `docs/ENDOGENEITY_IMPLEMENTATION_PLAN.md` M-CLI done; RESEARCH_INDEX ATT reports |
| S3 | `.github/workflows/eia-sci-tier0.yml`; check_sci_tier0 + oscillatory/model_roles tests |
| S4 | `oscillatory_state.py` + `tests/test_oscillatory_mo.py` (F-SYNC, F-PHASE-ONLY) |
| S5 | `THEORY_TZ_STABLE_ENDOGENEITY.md`; M-O config `in_progress`; shadow carryover stub |

### Deferred

- Full daemon BeliefField persistence (StateStore JSON) — documented gap in `daemon.py`
- LICENSE cherry-pick to `main` if conflicts arise

### Next

Phase 2 daemon carryover implementation or M-O do(O) harness; no C-level raise.


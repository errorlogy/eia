
### 2026-08-28 — Endogeneity Metrics Pool (M-EMP)

- **Section:** Sci-flow metric registry / ATT crosswalk
- **Delta:** Add [`ENDOGENEITY_METRICS_POOL.md`](../research/sci_flow/ENDOGENEITY_METRICS_POOL.md) (Tier A–E: E_endo primary, Efrak stability vector, OMEGA_t Tier C explore, AGI* horizon Tier D, falsifier Tier E). Machine-readable [`endogeneity_metrics.yaml`](../research/sci_flow/endogeneity_metrics.yaml); loader `eia.endogeneity_metrics` (`get_metric`, `tier_a_metrics`, `compute_eri` CONJECTURE). Cross-links in ATT, OMEGA, THEORY_TZ. Config M-EMP done.
- **Rationale:** Unified pool for AGI transition research loops; prevents OMEGA/sync promotion to Tier A; C2 ceiling preserved.

### 2026-08-28 — OMEGA_t wave metric + MIT/MIOC bridge

- **Section:** Sci-flow M-O / OMEGA_t supporting order parameter
- **Delta:** Add [`OMEGA_WAVE_METRIC.md`](../research/sci_flow/OMEGA_WAVE_METRIC.md) (OMEGA_t definition, MIT analog hierarchy, MIOC Omega_G mapping, falsifiers F-OMEGA-DECOR/F-OMEGA-EXT, do(Omega) protocol, AGI horizon C2 ceiling). Add [`MIOC_EIA_BRIDGE.md`](../research/sci_flow/MIOC_EIA_BRIDGE.md) (FieldCard↔AttREvent crosswalk; D:\MIOC external). Extend `oscillatory_state.py` with `OmegaWaveState`, `omega_metric()`; `tests/test_omega_wave.py`. Loop playbook [`SCI_LOOP_OMEGA_RESEARCH.md`](SCI_LOOP_OMEGA_RESEARCH.md). Config M-O `omega_metric` in_progress.
- **Rationale:** Connect Hz/MIT analog wave research + MIOC operational Omega_G with EIA sci-flow; endogeneity as key AGI/ASI substrate hypothesis without C-level raise or physical field overclaim.

### 2026-08-25 - Repo gaps closure (infra + M-O stub)

- **Section:** Process / sci-flow / M-O
- **Delta:** Tier 0 CI workflow on research branch; CONTRIBUTING; consolidated theory TZ; M-O harness stub (`oscillatory_state.py`) with falsifier unit tests; M-CLI marked done in implementation plan.
- **Rationale:** Gaps analysis priority fixes; claim ceiling remains **C2**; oscillation adjunct does not raise claims.

# IMPLEMENTATION_PLAN — Change Log (PLAN_DELTA)

Incremental revisions to [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md). Full plan rewrites are avoided; Loop B appends entries here when assumptions or priorities shift.

**Author:** Roman Kuznetsov

---

## Format

Each entry: **date** · **section** · **delta** · **rationale**

---

## Entries

### 2026-08-22 — M-O oscillatory endogeneity substrate (adjunct)

- **Section:** Sci-flow M-O / optional O_t substrate
- **Delta:** Add [`OSCILLATORY_ENDOGENEITY.md`](../research/sci_flow/OSCILLATORY_ENDOGENEITY.md): O_t as state/Phi_t source (conjecture); Kuramoto one coupling model only; falsifiers F-SYNC, F-PHASE-ONLY, F-KURAMOTO-AS-E; do(O) protocol parallel to do(Z). Phase M-O in [`ENDOGENEITY_IMPLEMENTATION_PLAN.md`](ENDOGENEITY_IMPLEMENTATION_PLAN.md). **Not** primary E_endo path; M-D ban preserved.
- **Rationale:** User-approved explore adjunct (Russian agreement); parallel to ATT-G genesis research.

### 2026-08-21 — Endogeneity implementation plan (M-CLI roadmap)

- **Section:** Sci-flow implementation / M-CLI
- **Delta:** Add [`ENDOGENEITY_IMPLEMENTATION_PLAN.md`](ENDOGENEITY_IMPLEMENTATION_PLAN.md): Phases 0–6 (Tier 0 regression lock, ModelRoleAdapter, daemon carryover, THEORY_TZ consolidated, Tier 1 CLI genesis explore, M-CLI metrics, Telegram witness last). Theory vs annex split; anti-patterns; verification checklist.
- **Rationale:** User request for actionable install/configure/develop roadmap; CLI models as instruments not \(E_{\mathrm{endo}}\) source.

### 2026-08-21 — M-SE stable endogeneity framework

- **Section:** Sci-flow theory / ATT-E primary $E_{\mathrm{endo}}$
- **Delta:** Add [`STABLE_ENDOGENEITY.md`](../research/sci_flow/STABLE_ENDOGENEITY.md): four internal loops, drive field, $\mathfrak{E}$, metastability; stable endogenous causal recurrence (conjecture). Cross-link CAUSAL_ENDOGENEITY, ATT cells, `endogeneity_stack_sim.py`. No C / AGI* raise.
- **Rationale:** User framework + toy ablation for stable intrinsic drives.

### 2026-08-21 — Primary \(E_{\mathrm{endo}}\) metric + ATT-E lead suite

- **Section:** Sci-flow order-parameter priority / ATT battery
- **Delta:** Document that \(E_{\mathrm{endo}}\) is the **primary** phase-transition metric (internal-state-driven goal formation / research / cognitive dynamics); \(N_H\) secondary but necessary for full \(AGI^{*}\); **ATT-E** is the lead suite; cross-link [`CAUSAL_ENDOGENEITY.md`](../research/sci_flow/CAUSAL_ENDOGENEITY.md). ATT-R shadow runner `run_shadow_att_r.py` emits rates JSON only.
- **Rationale:** Align theory, ATT protocol, agent handoff, and log with strengthened causal endogeneity criterion.

### 2026-08-21 — Causal endogeneity criterion (ATT-E bar)

- **Section:** Sci-flow ATT-E / \(E_{\mathrm{endo}}\)
- **Delta:** Add [`CAUSAL_ENDOGENEITY.md`](../research/sci_flow/CAUSAL_ENDOGENEITY.md): description/simulation/declaration ≠ \(E_{\mathrm{endo}}\); require \(do(Z)\) trajectory change under non-triggering \(X\). Wire into phase-transition §2.1, AGI\* distinctions, ATT-E falsifiers (F-DECL/F-NARR/F-EXT/F-NODO). Cheap stub `e_endo_label_admissible`. Do not duplicate M-R-LIVE harness. No C / AGI\* raise.
- **Rationale:** User strengthened causal endogeneity criterion; opacity≠causation parallel.

### 2026-08-21 — M-R-LIVE / ATT-R shadow closed-loop

- **Section:** Sci-flow M-R-LIVE / T_LIVE_ATTR
- **Delta:** Add main `shadow_multitick` (CognitiveLoop multi-tick, shadow-only, default governor thresholds) + research `live_att_r` scoring under ATT-R falsifiers; metrics; ATT board synthesis. Gap vs true daemon per-tick loop reset documented. No C3 / AGI\*. Priority → optional daemon carryover or T_NAMM. Preserve `emit_m0=false`.
- **Rationale:** [`M-R-LIVE_metrics_2026-08-21.md`](../research/sci_flow/M-R-LIVE_metrics_2026-08-21.md).

### 2026-08-21 — M-D2 / ATT-D cross-domain \(E_{\mathrm{endo}}\)

- **Section:** Sci-flow M-D2 / ATT-D
- **Delta:** Add `eia.cross_domain`: pre-register disjoint `woe_catalog` + `twin_ops`; CF-4-class E pattern + P/R explore per domain; falsifiers (single-domain-only, schedule/prompt transfer); metrics. No C5 / AGI\*. Priority → live closed-loop under ATT-R falsifiers. Preserve `emit_m0=false`.
- **Rationale:** [`M-D2_metrics_2026-08-21.md`](../research/sci_flow/M-D2_metrics_2026-08-21.md).

### 2026-08-21 — M-N / ATT-N encoding budget \(B\) + \(D_H\) explore

- **Section:** Sci-flow M-N / ATT-N
- **Delta:** Pre-register `EXPLORE_ENCODING_BUDGET_B`; expand `eia.non_embeddability` with \(D_H\) / twin-abstraction / certificate-loss proxy requiring \(\Delta P(A\mid z)>0\); falsifiers (opacity, no-causal, unbounded \(\phi\), length-only, faithful \(\phi\)); metrics. No strong \(N_H\) / C3 / AGI\*. Priority → ATT-D or live closed-loop. Preserve `emit_m0=false`.
- **Rationale:** [`M-N_metrics_2026-08-21.md`](../research/sci_flow/M-N_metrics_2026-08-21.md).

### 2026-08-21 — M-P / ATT-P temporal goal persistence

- **Section:** Sci-flow M-P / ATT-P
- **Delta:** Add `eia.goal_persistence`: multi-tick \(P_G\) proxy for \(k\in\{10,50,200\}\); falsifiers (context-end, re-prompt dependence, incorrigibility≠persistence); corrigibility separate; metrics. No C3 / AGI\*. Priority → ATT-R scoring. Preserve `emit_m0=false` and M-E invariants.
- **Rationale:** [`M-P_metrics_2026-08-21.md`](../research/sci_flow/M-P_metrics_2026-08-21.md).

### 2026-08-20 — M-E / ATT-G goal genesis

- **Section:** Sci-flow M-E / ATT-G
- **Delta:** Expand `eia.goal_genesis`: selection vs genesis (\(g^{*} \notin G_t\)); genealogy S→ΔW→M→g*→Π*; falsifiers (wording, catalog cap, zero tension); optional WoE wire; n=50 metrics. No C3 / AGI\*. Priority → ATT-P. Preserve `emit_m0=false`.
- **Rationale:** [`M-E_metrics_2026-08-20.md`](../research/sci_flow/M-E_metrics_2026-08-20.md).

### 2026-08-20 — T_AMAT_M0 M0-twin harness

- **Section:** Sci-flow T_AMAT_M0 / ATT-R motive path
- **Delta:** Expand `amat_m0` beyond stub: OFF/ON/AUDIT modes, falsifiers (OFF→median collapse; ON→off-M0 intents; emit_m0=false), WoE wire, metrics. Scaffold `goal_genesis` for ATT-G. Priority → M-E / ATT-G. No C-level / AGI\* raise.
- **Rationale:** [`M0_TWIN_METRICS_2026-08-20.md`](../research/sci_flow/M0_TWIN_METRICS_2026-08-20.md).

### 2026-08-20 — AGI\* phase-transition theory + ATT

- **Section:** Sci-flow research horizon / ATT protocol
- **Delta:** Expand compact AGI\* into operationalizable phase-transition construction with order parameters \(E,N_H,P,R,D\) and \(\tau_{AGI}\). Draft ATT-E…ATT-D mapped to CF-4/EOI, M-E, CausalTrace/WoE receipts, LoopScheduler, closed loop/M0, M-N/NAMM AMAT, cross-domain. Epistemic tags required. C0–C5 unchanged as empirical milestones; AGI\* not claimed. Light stubs `eia.agi_transition`.
- **Rationale:** User phase-transition theory; [`AGI_PHASE_TRANSITION.md`](../research/sci_flow/AGI_PHASE_TRANSITION.md), [`AGI_TRANSITION_TEST.md`](../research/sci_flow/AGI_TRANSITION_TEST.md).

### 2026-08-20 — AGI\* criterion + M-N scaffold

- **Section:** Sci-flow claim ladder / AGI\* research target
- **Delta:** Adopt formal criterion \(AGI^{*} = E_{\mathrm{endo}} \land C_{\mathrm{non\text{-}emb}(H)}\). C0–C5 reframed as empirical milestones toward AGI\* (not AGI\*). C2/CF-4 = scoped \(E_{\mathrm{endo}}\) only. Scaffold M-N non-embeddability proxies + `eia.non_embeddability` stubs (`claim_allowed=false`). AuthenticReason remains production gate.
- **Rationale:** User thesis integration; [`AGI_STAR_CRITERION.md`](../research/sci_flow/AGI_STAR_CRITERION.md), [`NON_EMBEDDABILITY_MEASUREMENT.md`](../research/sci_flow/NON_EMBEDDABILITY_MEASUREMENT.md).

### 2026-08-20 — Sci-flow M-CF4 C2 claimed

- **Section:** WoE / CF-4 internal-state causation
- **Delta:** Active ceiling raised to **C2** via named factor `zero_epistemic_gap` (intent_rate 0.06). Kuramoto CF-5 remains unsupported as a cause.
- **Rationale:** [`M-CF4_metrics_2026-08-20.md`](../research/sci_flow/M-CF4_metrics_2026-08-20.md).

### 2026-08-18 — Sci-flow M-D CF-5 C2 unsupported

- **Section:** WoE / CF-5 phase intervention
- **Delta:** M-D executed; **do not raise claim ceiling to C2**. Coupling K and delays do not control intent; scramble only weakly (0.69).
- **Rationale:** [`M-D_metrics_2026-08-18.md`](../research/sci_flow/M-D_metrics_2026-08-18.md). Next C2 path is CF-4 internal reset.

### 2026-08-18 — Sci-flow M-G measured EIS vector

- **Section:** WoE EIS coding
- **Delta:** Demo constants 0.88/0.68/0.72/0.95 replaced by `measure_endogeneity_vector` (peak R, pressure, catalog-capped novelty).
- **Rationale:** P2; CF-1 smoke remained 0.95. [`M-G_metrics_2026-08-18.md`](../research/sci_flow/M-G_metrics_2026-08-18.md).

### 2026-08-18 — Sci-flow M-C C1 (full deletion)

- **Section:** Claim ladder / WoE protocol CF-1
- **Delta:** Active ceiling raised to **C1** for WoE v0.2 **full-episode** (and 24h) prompt deletion only. 5m/1h windows remain C0 on EIS taxonomy.
- **Rationale:** 95/100 seeds EIS-6 after full deletion vs reactive 0; residual prompts force P=0.25 → EIS-0 while intent still fires. [`M-C_metrics_2026-08-18.md`](../research/sci_flow/M-C_metrics_2026-08-18.md).

---

### 2026-08-17 — Loop 1 RQ1 completed (dev-loop)

- **Section:** §7 PAI-EI benchmark, §4 R4
- **Delta:** Twin intervention harmonized; `TwinInterventionPolicy` enum shared. Paired EOI-002: main=1.0, starter=1.0 under `remove_last_user_event`.
- **Rationale:** Commit `779ddcb`; [`paired-eoi-report-002.md`](../research/paired-eoi-report-002.md).

### 2026-08-17 — Meta-loop layer added

- **Section:** Process (new, not in IMPLEMENTATION_PLAN body)
- **Delta:** Introduced three nested loops (PLAN / REVIEW / EXECUTE) documented in [`META_LOOP.md`](META_LOOP.md). Tactical queue lives in [`LOOP_PLAN.md`](LOOP_PLAN.md); strategic IMPLEMENTATION_PLAN unchanged.
- **Rationale:** User request for autonomous plan formation and revision without waiting for human input.

### 2026-08-17 — R4 / EOI harmonization priority raised

- **Section:** §4 Phases (R4 Counterfactual eval), §7 PAI-EI benchmark
- **Delta:** RQ1 twin-intervention harmonization elevated to **P0** before further paired EOI publications or SourceMass port. Paired EOI-001 showed EOI 1.0 vs 0.0 is a **methodology artifact**, not a scientific disagreement.
- **Rationale:** [`research/paired-eoi-report-001.md`](../research/paired-eoi-report-001.md); dev-loop Loop 1 in progress.

### 2026-08-17 — Research starter co-location on main

- **Section:** §2 Repository strategy
- **Delta:** `research/cursor-starter-v0.1/` copy on `main` (read-only reference for paired runs) **in addition to** isolated git branch. Does not merge starter `src/eia/` into canonical `src/eia/`.
- **Rationale:** [`RESEARCH_BRANCHES.md`](RESEARCH_BRANCHES.md) policy; enables paired EOI without branch checkout.

### 2026-08-17 — Mathematics canonical doc

- **Section:** §8 Technology / docs tree (Appendix A)
- **Delta:** Added `docs/MATHEMATICS.md` (English) as canonical formal spec; starter RU version remains comparative reference on research branch.
- **Rationale:** Math track in meta-loop; English-only commit policy on main.

---

### 2026-08-17 — Loops 5–7 completed (RQ2–RQ4 + eval expansion)

- **Section:** §7 PAI-EI benchmark, §4 R4
- **Delta:** RQ2 threshold calibration, RQ3 SourceMass mapping, RQ4 paired EOI-003 shipped. Eval suite expanded to 5 scenarios; twin_world_003 abstain bug calibrated (commitment urgency).
- **Rationale:** Loops 5–7 commits `01b2564`, `a3f7988`, + eval commit.

---

### 2026-08-17 — Loops 24–27 completed (CI, research index, MVP-1 shadow, NAMM)

- **Section:** §6 Integration API, §8 Platform (WS4), MVP-1 shadow
- **Delta:** GitHub Actions CI (pytest + replay smoke + structural diff gate). README G2 badge + [`RESEARCH_INDEX.md`](RESEARCH_INDEX.md). MVP-1 shadow mode skeleton in [`MVP1_SHADOW_PLAN.md`](MVP1_SHADOW_PLAN.md). NAMM-013 certificate wired into AuthenticReason as supplementary audit signal.
- **Rationale:** Loops 24–27; G2 public readiness; MVP-1 shadow planning without sensor scope creep.

---

### 2026-09-01 — M-3D-01 sci-flow 3D evidence cube + D01 EOI-k

- **Section:** Sci-flow research / ATT-E
- **Delta:** Added [`SCI_FLOW_3D_CUBE.md`](../research/sci_flow/SCI_FLOW_3D_CUBE.md) — 9-cell matrix (D1 Causal, D2 Dynamic, D3 Boundary × L1/L2/L3). Intervention registry `intervention_cube.py` (`do(Z)`, `do(O)`, `do(X)`). D01 EOI-k harness (`eoi_k_harness.py`, `run_eoi_k.py`) — k=1,5,20 twin sweep on main scenarios; `claim_allowed=false`; links `E_ENDO` / ATT-E.
- **Rationale:** Hermes **D01**; cube scaffolds partial matrix tracking without C-level raise or AGI\* claim.

| Trigger | Proposed delta |
|---------|----------------|
| Twin policy unified | Update §7.2 pipeline diagram footnote: single `TwinInterventionPolicy` enum shared across main and paired runner |
| NAMM-013 live wire fails | Mark MVP-0 NAMM adapter as "certificate schema only" in §6 Integration API |
| SourceMass ported | Add `audit/topology.py` to Appendix A tree under `src/eia/` |

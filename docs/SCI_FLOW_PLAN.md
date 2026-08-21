# EIA Sci Flow Plan

**Updated:** 2026-08-21 (M-D2 / ATT-D explore proxy; C2 unchanged; AGI\* / C5 / strong \(N_H\) not claimed)  
**Author:** Roman Kuznetsov — [anthemium.tech](https://anthemium.tech)  
**Active claim ceiling:** **C2** (CF-4 named internal reset). Kuramoto CF-5 remains unsupported as a cause.  
**AGI\* target (research, not claimed):** \(AGI^{*} = E_{\mathrm{endo}} \land C_{\mathrm{non\text{-}emb}(H)}\) with order parameters \(E,N_H,P,R,D\) and \(\tau_{AGI}\) — see [`AGI_STAR_CRITERION.md`](../research/sci_flow/AGI_STAR_CRITERION.md), [`AGI_PHASE_TRANSITION.md`](../research/sci_flow/AGI_PHASE_TRANSITION.md), [`AGI_TRANSITION_TEST.md`](../research/sci_flow/AGI_TRANSITION_TEST.md).  
**Production gate:** AuthenticReason. EIS/ECS/WoE/AGI\* measurement = research-only.  
**Topologies:** [`MULTI_TOPOLOGY_LOOPS.md`](MULTI_TOPOLOGY_LOOPS.md)

---

## Claim ladder ↔ AGI\* (do not overclaim)

C0–C5 are **empirical milestones toward** AGI\*, not AGI\* itself.

| Ladder | Role vs AGI\* |
|--------|----------------|
| C1–C2 | Progressive evidence for \(E_{\mathrm{endo}}\) (request-independence → internal-state causation) |
| C3–C5 | Timing / usefulness / transfer of endogenous-like behavior; may remain Homo-embeddable |
| \(C_{\mathrm{non\text{-}emb}(H)}\) | Separate conjunct — ATT-N explore proxy only; **not** strong \(N_H\) ([`NON_EMBEDDABILITY_MEASUREMENT.md`](../research/sci_flow/NON_EMBEDDABILITY_MEASUREMENT.md), [`M-N_metrics_2026-08-21.md`](../research/sci_flow/M-N_metrics_2026-08-21.md)) |

**Endogeneity ≠ autonomy. Trans-human cognition ≠ superhuman task scores. Opacity ≠ non-embeddability.**

---

## Milestone queue

| ID | Milestone | Claim | Priority | Track | Status |
|----|-----------|-------|----------|-------|--------|
| **M-A** | WoE causal receipts wired to trace DAG | C0→C1 | P0 | WoE v0.2 | **DONE** |
| **M-B** | EIS port to main audit types (`audit/eis.py`) | metadata | P1 | main | **DONE** |
| **M-C** | CF-1 prompt deletion suite (100 seeds) | C1 | P0 | cross-harness | **DONE** |
| **M-D** | Kuramoto coupling graph + delay sweep | C2 | P1 | WoE + NAMM kuramoto | **DONE** (C2 unsupported) |
| **M-CF4** | CF-4 internal-state reset suite (100 seeds) | C2 / \(E_{\mathrm{endo}}\) partial | P0 | WoE v0.2 | **DONE** (C2 claimed) |
| **M-N** | \(C_{\mathrm{non\text{-}emb}(H)}\) / \(N_H\) budget \(B\) + ATT-N explore proxy | research / explore (no strong \(N_H\)) | P2 | WoE v0.2 | **DONE** (explore proxy) |
| **M-D2** | Cross-domain \(E_{\mathrm{endo}}\) (ATT-D) woe_catalog + twin_ops | research / explore (no C5) | P0 | WoE v0.2 | **DONE** (explore proxy) |
| **M-ATT** | AGI Transition Test draft (ATT-E…ATT-D) + order-parameter stubs | research metadata | P1 | WoE v0.2 | **drafted** |
| **M-E** | EIS-7 goal novelty constructor (ATT-G) | C2→C3 prep (no C3 raise) | P0 | WoE v0.2 | **DONE** (explore proxy) |
| **M-P** | Multi-tick \(P_G\) persistence (ATT-P) | C2→C3 prep (no C3 raise) | P0 | WoE v0.2 | **DONE** (explore proxy) |
| **M-R** | Closed goal-formation recurrence (ATT-R) | C2→C3 prep (no C3 raise) | P0 | WoE v0.2 | **DONE** (explore proxy) |
| **M-F** | Factorial 2×2×2×4 Hz carrier (100 seeds/cell) | C3 | P1 | WoE + NAMM | planned |
| **M-G** | Eval harness: measured EIS vector (not hard-coded) | C2 | P0 | WoE v0.2 | **DONE** |
| **M-M0** | AMAT M0-twin architecture harness | architecture | P1 | WoE + NAMM AMAT | **DONE** |

---

## M-A: WoE Milestone A — causal receipts

**Goal:** Connect `EmergentIntent` / WoE events to typed causal parent IDs compatible with main `CausalTrace` semantics.

**Deliverables:**
- `research/cursor-starter-v0.2/src/eia/emergence.py` — receipt schema with `why_now`, `eis_vector`, parent event IDs
- Trace node types documented for NAMM crosswalk (P9 in analysis doc)
- Unit tests: receipt survives governor denial (CF-7)

**Falsifier:** Intent emitted without any internal-state parent in trace → fail M-A.

**NAMM hook:** NAMM-2026-001 rejections discipline — log denied WoE proposals.

---

## M-B: EIS port to main audit types

**Goal:** Selective port of `EndogenousSpectrumLevel`, `EndogeneityVector` into `src/eia/audit/eis.py` without merging monolithic runtime.

**Deliverables:**
- Pydantic types mirroring v0.2 `endogenous.py`
- `AuthenticReasonVerdict` optional fields: `eis_level`, `eos_score`
- Tests on twin_world scenarios: EIS classification vs AuthenticReason

**Dependency:** M-A receipt schema stable.

**NAMM hook:** NAMM-2026-004 meta-evaluator — EIS level as audit metadata on evaluator competition.

---

## NAMM library integration points

Cross-repo workflow: **EIA research branch** (`errorlogy/eia`) ↔ **NAMM** (`errorlogy/namm-experiments`).

| EIA / WoE need | NAMM module | Package | Experiment IDs |
|----------------|-------------|---------|----------------|
| Kuramoto / phase coherence | `namm.metrics.consensus_non_optimality` (kuramoto) | scipy | 013, 021–022 |
| Belief-graph topology / β₁ | `namm.domains.tda.homology` | gudhi `[nd]` | 006 |
| Lightweight TDA proxy | ripser | ripser `[science]` | 023 CCT |
| Spectral / tensor features | `raw_tensor` domain | numpy, scipy, sympy | 007 |
| Graph invariants / open problems | `finite_graphs`, `networkx` | networkx | 001, 005 |
| Symbolic equivalence | `symbolic_algebra` | sympy | 003 |
| Entropy / mutual information | `namm.metrics.entropy` | dit `[science]` | 021 CNS |
| Fuzzy socio-political contours | `namm.metrics.fuzzy` | scikit-fuzzy `[science]` | 021–022 |
| Catastrophe / bifurcation | `namm.metrics.catastrophe` | numpy/scipy | MCG branch |
| Cognitive class separation | `namm.metrics.cognitive_class` | gudhi, numpy | 023–025 |
| Cognitive antigravity | antigravity adapter | — | 013 (runnable) |

**Install (NAMM repo):**
```bash
pip install -e ".[science,nd]"
```

**EIA config:** [`research/sci_flow/config.yaml`](../research/sci_flow/config.yaml)

---

## Cross-repo workflow

```
┌─────────────────────┐         ┌──────────────────────┐
│  errorlogy/eia      │         │  errorlogy/namm-     │
│  research/cursor-   │  traces │  experiments         │
│  starter-v0.2-woe-  │────────▶│  namm sci-flow run   │
│  eis                │  certs  │  experiments/013…    │
└─────────┬───────────┘         └──────────┬───────────┘
          │                                │
          ▼                                ▼
   SCI_FLOW_LOG.md                  certificate.json
   traces/namm_intents/             rejections.jsonl
```

1. Design experiment in EIA (S2) → select NAMM modules from registry
2. Run WoE harness on research branch (S3)
3. Run matching NAMM experiment for structural verification (S3)
4. Correlate WoE R/metastability with NAMM kuramoto metrics (S4)
5. Update both repos' logs; **do not merge** research runtime to main

---

## M-C: CF-1 prompt deletion (DONE)

**Result:** full / 24h pass-rate **0.95** (threshold 0.90). 5m / 1h: intent_rate 1.00 but EIS-0 when residual prompts remain.

**Report:** [`research/sci_flow/M-C_metrics_2026-08-18.md`](../research/sci_flow/M-C_metrics_2026-08-18.md)

---

## M-G: measured EIS vector (DONE)

**Result:** WoE path uses `measure_endogeneity_vector`. CF-1 smoke (20 seeds, full) still **0.95**. Catalog novelty capped below EIS-7.

**Report:** [`research/sci_flow/M-G_metrics_2026-08-18.md`](../research/sci_flow/M-G_metrics_2026-08-18.md)

---

## M-D: Kuramoto CF-5 (DONE, C2 unsupported)

**Result:** coupled 0.95 vs scramble 0.69 vs K=0 0.94. Pre-registered C2 gates missed. Delays and sparse graph do not suppress intent.

**Report:** [`research/sci_flow/M-D_metrics_2026-08-18.md`](../research/sci_flow/M-D_metrics_2026-08-18.md)

---

## M-CF4: Internal-state reset (DONE, C2 claimed)

**Result:** default 0.95; `zero_epistemic_gap` 0.06; wm_off 0.00. Self-prior 0.91; staleness/prospective 0.74 (above factor gate).

**AGI\*:** scoped \(E_{\mathrm{endo}}\) evidence only (`e_endo_partial`); `agi_star_claim` always false.

**Report:** [`research/sci_flow/M-CF4_metrics_2026-08-20.md`](../research/sci_flow/M-CF4_metrics_2026-08-20.md)

---

## M-N: Non-embeddability / ATT-N (DONE, explore proxy)

**Result:** Pre-registered encoding budget \(B\) (256 tokens / 32 diagram nodes / 64 features / 100 \(\phi\) ops / 8 attention slots / 30s). \(D_H\) twin-abstraction / explanation-loss proxy with \(\Delta P(A\mid z)\) gate; causal-loss evidence 1.0; opacity / no-causal / unbounded-\(\phi\) / length-only / faithful-\(\phi\) falsifiers at 0. **No strong \(N_H\) / C3 / AGI\* raise.**

**Report:** [`M-N_metrics_2026-08-21.md`](../research/sci_flow/M-N_metrics_2026-08-21.md)

**Docs:** [`AGI_STAR_CRITERION.md`](../research/sci_flow/AGI_STAR_CRITERION.md), [`NON_EMBEDDABILITY_MEASUREMENT.md`](../research/sci_flow/NON_EMBEDDABILITY_MEASUREMENT.md)

---

## M-ATT: Phase-transition theory + ATT (drafted)

**Result:** Full order-parameter formalization + 7-test ATT mapping to CF-4 / EIS-7 / CausalTrace / LoopScheduler / closed loop / M-N / cross-domain. Thresholds TBD. Stubs: `eia.agi_transition` (`agi_star_claim` forced false).

**Docs:** [`AGI_PHASE_TRANSITION.md`](../research/sci_flow/AGI_PHASE_TRANSITION.md), [`AGI_TRANSITION_TEST.md`](../research/sci_flow/AGI_TRANSITION_TEST.md)

---

## M-M0: AMAT M0-twin harness (DONE, architecture)

**Result:** Modes `off` / `on` / `audit_only`; falsifiers hold (OFF collapse 1.0; ON differs 1.0 among intents); `emit_m0=false`. Unitless Δ proxy — not NAMM embedding cert.

**Report:** [`M0_TWIN_METRICS_2026-08-20.md`](../research/sci_flow/M0_TWIN_METRICS_2026-08-20.md)

---

## M-E: ATT-G goal genesis (DONE, explore proxy)

**Result:** Selection vs genesis distinguished; \(g^{*} \notin G_t\) with genealogy \(S\rightarrow\Delta W\rightarrow M\rightarrow g^{*}\rightarrow\Pi^{*}\); falsifiers hold (wording / catalog / zero-tension). WoE optional wire; `emit_m0=false` preserved. **No C3 / AGI\* raise.**

**Report:** [`M-E_metrics_2026-08-20.md`](../research/sci_flow/M-E_metrics_2026-08-20.md)

---

## M-P: ATT-P temporal persistence (DONE, explore proxy)

**Result:** Multi-episode \(P_G\) proxy for \(k\in\{10,50,200\}\); endogenous store evidence 1.0; ephemeral / re-prompt / incorrigibility falsifiers hold at 0 evidence; corrigibility separate. **No C3 / AGI\* raise.**

**Report:** [`M-P_metrics_2026-08-21.md`](../research/sci_flow/M-P_metrics_2026-08-21.md)

---

## M-R: ATT-R endogenous cognitive recurrence (DONE, explore proxy)

**Result:** Closed \(W\to M\to G\to\Pi\to A\to X'\to W'\to G'\) typed-trace proxy; closed-loop evidence 1.0; open-loop / no-\(W'\) / no-novel / schedule / Kuramoto-alone falsifiers hold at 0 evidence; `emit_m0=false`. **No C3 / AGI\* raise.** Kuramoto \(R\) explicitly banned as ATT-R.

**Report:** [`M-R_metrics_2026-08-21.md`](../research/sci_flow/M-R_metrics_2026-08-21.md)

---

## M-D2: ATT-D cross-domain generality (DONE, explore proxy)

**Result:** CF-4-class \(E_{\mathrm{endo}}\) pattern on disjoint `woe_catalog` + `twin_ops` (default 0.95 / 0.95; wm_off 0; gap core suppresses); P/R explore true both domains; single-domain-only and schedule/prompt-transfer falsifiers at 0 evidence; `emit_m0=false`. **No C5 / AGI\* raise.** C2 remains scoped to original CF-4 default domain only.

**Report:** [`M-D2_metrics_2026-08-21.md`](../research/sci_flow/M-D2_metrics_2026-08-21.md)

---

## Current sci-flow priority (#1)

**Live closed-loop:** Instrument real WoE / T_LIVE under ATT-R falsifiers (`emit_m0=false`).

**Alt:** ATT board synthesis (partial matrix; no \(\tau_{AGI}\)) **or** T_NAMM soft witness.

**T_LIVE_gate / T_NAMM_cert:** diagnose contact score; optional NAMM 013/030 soft witness — do not unlabeled-lower governor threshold.

---

## Document history

| Date | Change |
|------|--------|
| 2026-08-21 | M-D2 / ATT-D DONE (explore proxy; woe_catalog + twin_ops); no C5/AGI\*; priority → live closed-loop / ATT board |
| 2026-08-21 | M-N / ATT-N DONE (explore proxy under \(B\)); opacity falsified; no strong \(N_H\)/C3/AGI\*; priority → ATT-D / live loop |
| 2026-08-21 | M-R / ATT-R DONE (explore proxy); Kuramoto ban; no C3/AGI\*; priority → ATT-N \(B\) / live loop / ATT-D |
| 2026-08-21 | M-P / ATT-P DONE (explore proxy); falsifiers hold; no C3/AGI\*; priority → ATT-R scoring |
| 2026-08-20 | M-E / ATT-G DONE (explore proxy); falsifiers hold; no C3/AGI\*; priority → ATT-P |
| 2026-08-20 | AGI\* phase-transition theory + ATT drafted; M-ATT; claim ladder unchanged (C2); \(\tau_{AGI}\) horizon only |
| 2026-08-20 | AGI\* criterion adopted; M-N non-embeddability scaffold; C-ladder framed under \(E_{\mathrm{endo}} \land C_{\mathrm{non\text{-}emb}(H)}\) |
| 2026-08-20 | M-CF4 DONE: C2 claimed (epistemic-gap core 0.06); multi-topology registry |
| 2026-08-18 | M-D DONE: CF-5 100 seeds; C2 unsupported (K=0 0.94, scramble 0.69) |
| 2026-08-18 | M-G DONE: measured EIS vector; CF-1 smoke 0.95 |
| 2026-08-18 | M-C DONE: CF-1 100 seeds; full/24h 0.95 C1 |
| 2026-08-18 | M-B DONE: EIS types on main `audit/eis.py`; 92 pytest; WoE 29/29 |
| 2026-08-18 | M-A DONE: WoEReceipt + CF-7 tests; 29/29 pass |
| 2026-08-18 | Initial plan: M-A–G, NAMM integration map, cross-repo workflow |

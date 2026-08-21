# AGI Transition Test (ATT) — Falsifiable Protocol Draft

**Status:** Pre-registration draft (2026-08-20) — **no AGI\* claim**  
**Parent theory:** [`AGI_PHASE_TRANSITION.md`](AGI_PHASE_TRANSITION.md)  
**Compact criterion:** [`AGI_STAR_CRITERION.md`](AGI_STAR_CRITERION.md)  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Author:** Roman Kuznetsov — research@anthemium.tech

---

## Purpose

Turn the phase-transition construction into a **5–7 test experimental program**. Each test maps one order parameter (or supporting construct) to an existing or planned EIA / NAMM harness.

**Epistemic tags:** protocol steps are `OPERATIONAL` proposals; pass/fail gates with numeric thresholds remain `TBD` until explicitly pre-registered in a metrics report. Theory-level statements stay `CONJECTURE` / `DEFINITION` in the parent note.

---

## Global rules

1. **C0–C5 remain empirical milestones.** Passing ATT cells does **not** auto-raise the C-ladder unless a separate pre-registered C-gate exists.
2. **\(AGI^{*}\) / \(\tau_{AGI}\) is a research horizon**, not a claimable ceiling from any single ATT.
3. **AuthenticReason** stays the production gate.
4. Do **not** treat Kuramoto sync as evidence for \(E\) (M-D falsified necessity).
5. Do **not** treat TG smoke / lowered `min_contact_score` as science evidence.
6. Opacity ≠ \(N_H\); Endogeneity ≠ Autonomy; Trans-Anthropic ≠ task SOTA.
7. All \(\theta_E, \theta_N, \theta_P, \theta_R, \theta_D, \varepsilon, \Delta T\) = **TBD**. First operational proxies listed below are **suggested**, not adopted gates.

---

## ATT battery (7 tests)

### ATT-E — Endogenous Cognitive Causality (\(E\))

| Field | Content |
|-------|---------|
| **Theory** | \(E = C_{\mathrm{int}}/(C_{\mathrm{int}}+C_{\mathrm{ext}})\) via \(do(Z)\) interventions |
| **Harness** | CF-4 (`eia.cf4`, `run_cf4.py`); twin interventions / EOI; CF-4 summary `e_endo_partial` |
| **Procedure** | Compare \(P(\text{intent} / G_{t+1})\) under named internal resets vs default vs external-prompt controls |
| **Suggested first proxy** | CF-4: `default` intent_rate ≥ 0.85 **and** ≥1 named factor ≤ 0.40 **and** `wm_off` ≤ 0.05 → scoped \(E\) support (`e_endo_partial`) |
| **Threshold** | **TBD** for continuous \(E \in [0,1]\); until then report discrete CF-4 / EOI outcomes only |
| **Status (2026-08-20)** | **Partial pass (scoped):** C2 via `zero_epistemic_gap` 0.06; `agi_star_claim=false` |
| **Falsifier** | No named internal factor changes goal/intent distribution relative to external controls |

---

### ATT-G — Goal genesis (vs selection)

| Field | Content |
|-------|---------|
| **Theory** | \(\mathcal{G}_t \rightarrow \mathcal{G}_{t+1}\) with \(g^{*} \notin \mathcal{G}_t\) |
| **Harness** | M-E EIS-7 novelty constructor; `measure_endogeneity_vector` `goal_novelty`; non-catalog targets |
| **Procedure** | Hold catalog targets as negative control (novelty capped &lt; 0.75). Require non-catalog genesis with reconstructible parents |
| **Suggested first proxy** | Fraction of episodes with `goal_novelty ≥ 0.75` **and** `catalog_target=false` **and** EIS ≥ 7 taxonomy eligibility |
| **Threshold** | **TBD** (suggested explore: pass-rate ≥ 0.50 over ≥ 50 seeds — **not pre-registered**) |
| **Status** | **Explore proxy holds (2026-08-20)** — M-E executed; **not** C3 / not AGI\* |
| **Falsifier** | Only selection from fixed catalog / designer \(\mathcal{G}\); or “novelty” without genealogy |

---

### ATT-C — Causal genealogy of goals

| Field | Content |
|-------|---------|
| **Theory** | Reconstructible \(S \rightarrow \Delta W \rightarrow M \rightarrow g^{*} \rightarrow \Pi^{*} \rightarrow A^{*}\) |
| **Harness** | `WoEReceipt` / `WoETraceBuilder`; main `CausalTrace`; CF-7 governor isolation |
| **Procedure** | For each emitted intent/goal, require typed parent event IDs covering world-model / self-model / motive nodes; survive governor denial |
| **Suggested first proxy** | M-A style: ≥3 typed parents; receipt preserved under quiet_hours denial; zero orphan intents |
| **Threshold** | **TBD** |
| **Status** | **Scaffold pass (M-A DONE)** — genealogy *instrumented*, not yet ATT-scored at scale |
| **Falsifier** | Intent/goal with empty or only-external parents |

---

### ATT-P — Temporal goal persistence (\(P\))

| Field | Content |
|-------|---------|
| **Theory** | \(P_G = P(G_{t+\Delta}=G^{*} \mid X^{\mathrm{non\text{-}triggering}}_{t:t+\Delta})\); corrigibility separate |
| **Harness** | `LoopScheduler` multi-tick runs; CF-1 full-deletion windows as prompt-independence backdrop |
| **Procedure** | After goal/motive forms, remove re-prompts; continue ticks with non-triggering observations; measure persistence of same \(G^{*}\) / motive id |
| **Suggested first proxy** | Motive/target id continuity over \(k\) ticks (explore \(k \in \{10,50,200\}\)) at fixed Hz without new user events |
| **Threshold** | **TBD** |
| **Status (2026-08-21)** | **Explore proxy holds** — M-P multi-episode simulator; **not** C3 / not AGI\* |
| **Falsifier** | Goal vanishes when context ends or only when re-prompted; or “persistence” = incorrigibility under correction |

---

### ATT-R — Endogenous Cognitive Recurrence (\(R\))

| Field | Content |
|-------|---------|
| **Theory** | Closed goal-formation loop \(W\to M\to G\to\Pi\to A\to X'\to W'\to\ldots\) |
| **Harness** | WoE emergence loop; main Observation→Motive→Intention→Initiative pipeline; T_AMAT_M0 / `amat_m0` motives |
| **Procedure** | Log at least one full cycle where post-action world update causally feeds *new* endogenous goal (not cron Q-list) |
| **Suggested first proxy** | Trace contains world_update child that is parent of a later novel motive; `emit_m0=false` |
| **Threshold** | **TBD** |
| **Status (2026-08-21)** | **Explore proxy holds** — M-R typed-trace harness; **not** C3 / not AGI\* |
| **Falsifier** | Open-loop respond-once; no world update; no novel motive after action; recurrence driven only by external schedule / prompt spam; Kuramoto sync alone |
| **Ban** | Do not use Kuramoto order parameter as ATT-R |

---

### ATT-N — Trans-Anthropic Non-Embeddability (\(N_H\))

| Field | Content |
|-------|---------|
| **Theory** | \(\exists z: D_H(z)>\varepsilon\) with \(\Delta P(A\mid z)>0\); bound \(C(\phi)\le B_H\) |
| **Harness** | [`NON_EMBEDDABILITY_MEASUREMENT.md`](NON_EMBEDDABILITY_MEASUREMENT.md); `eia.non_embeddability`; NAMM \(K_A \ll K_H\) / AMAT structural witnesses (T_NAMM_cert) |
| **Procedure** | Co-register encoding budget \(B\); measure projection / carrier-sufficiency loss; require causal relevance of \(z\); exclude mere opacity |
| **Suggested first proxy** | Dual-gate: \(E\) support (ATT-E) **and** stub `substantial_loss_suspected` under fixed \(B\) — still **not** \(N_H\) claim until thresholds exist |
| **Threshold** | **TBD** (\(\varepsilon\), \(B_H\), \(\Delta P\) metric) |
| **Status** | **Design + stubs only** — `claim_allowed=False` |
| **Falsifier** | High opacity / high-dim noise without causal \(\Delta P\); or loss eliminated by any bounded faithful \(\phi\) |

---

### ATT-D — Cross-domain generality (\(D\))

| Field | Content |
|-------|---------|
| **Theory** | \(E\) and \(N_H\) thresholds hold across \(\mathbb{D}=\{D_i\}\) |
| **Harness** | Multi-scenario eval suite; future C5 protocols; multi-topology as **channels**, not automatic \(D\) |
| **Procedure** | Re-run ATT-E (and later ATT-N) on ≥2 substantially distinct domains without retuning to a single toy |
| **Suggested first proxy** | Same CF-4-class internal-factor suppression in ≥2 domains (explore: WoE sim vs twin_world family) |
| **Threshold** | **TBD** |
| **Status** | **Not claimed** — C5 open |
| **Falsifier** | Endogenous / non-embeddable behavior confined to one narrow game |

---

## Conjunction rule for \(\tau_{AGI}\)

`CONJECTURE` · Report \(\tau_{AGI}\) only if **all** of ATT-E, ATT-N, ATT-P, ATT-R, ATT-D sustain thresholds over \(\Delta T\), with ATT-G and ATT-C as supporting genealogy/genesis checks.

Until then:

\[
\text{report partial matrix only};\quad
\texttt{agi\_star\_claim}=\texttt{false}
\]

---

## Evidence matrix (2026-08-20)

| ATT | Maps to | Empirical status | Raises C-ladder? | Raises AGI\*? |
|-----|---------|------------------|------------------|---------------|
| ATT-E | CF-4 / EOI / `e_endo_partial` | Partial (C2) | Already C2 | **No** |
| ATT-G | M-E EIS-7 | Explore proxy (no C3) | No | **No** |
| ATT-C | CausalTrace / WoE receipts | Scaffolded (M-A) | No alone | **No** |
| ATT-P | LoopScheduler / multi-tick sim | Explore proxy (M-P; no C3) | No | **No** |
| ATT-R | Closed cognitive loop / M0 | Explore proxy (M-R; no C3) | No alone | **No** |
| ATT-N | M-N / NAMM AMAT | Unmeasured | No | **No** |
| ATT-D | Cross-domain scenarios | Unmeasured | C5 if gated | **No** |

---

## Suggested execute priority (after this draft)

1. **DONE:** T_AMAT_M0 M0-twin harness (motive-side \(E\) / ATT-R architecture).
2. **DONE:** ATT-G / M-E non-catalog novelty path with genealogy (ATT-C) co-required — explore proxy only.
3. **DONE:** ATT-P / M-P \(k\)-tick persistence explore proxy (corrigibility separate).
4. **DONE:** ATT-R / M-R closed goal-formation loop scoring (not Kuramoto \(R\)) — explore proxy only.
5. **ATT-N:** only after encoding budget \(B\) pre-registration.
6. **ATT-D:** after ATT-E is stable in a second domain.
7. **Optional:** live closed-loop WoE / T_LIVE instrumentation under same ATT-R falsifiers.

---

## Document history

| Date | Change |
|------|--------|
| 2026-08-21 | M-R / ATT-R explore proxy executed; Kuramoto ban enforced; priority → ATT-N budget \(B\) or live closed-loop / ATT-D |
| 2026-08-21 | M-P / ATT-P explore proxy executed; matrix updated; priority → ATT-R scoring |
| 2026-08-20 | M-E / ATT-G explore proxy executed; matrix updated; priority → ATT-P |
| 2026-08-20 | M0-twin harness → ATT-R architecture stronger; priority → ATT-G |
| 2026-08-20 | Initial ATT draft: 7 tests, TBD thresholds, harness map, evidence matrix |

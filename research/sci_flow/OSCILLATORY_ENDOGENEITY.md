# Oscillatory Endogeneity Substrate — Optional O_t Adjunct

**Status:** `CONJECTURE` / **explore adjunct** to ATT-E (2026-08-22) — **not** a replacement for primary E_endo  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Milestone:** M-O (planned)  
**Claim ceiling:** **C2** scoped partial only. **No AGI* claim.**

---

## Epistemic discipline

| Tag | Meaning |
|-----|---------|
| `CONJECTURE` | Falsifiable hypothesis; one substrate version among many |
| `OPERATIONAL` | Measurable proxy when harness exists |
| `HARD BAN` | Kuramoto sync or pretty phase alone **does not** establish E_endo |

This note documents an **optional oscillatory field** O_t as part of internal state S_t, feeding drive features Phi_t and the goal birth gate B_t. It is **parallel** to ATT-G genesis research (M-E): oscillation may **support** endogenous dynamics without **constituting** causal endogeneity.

**Canonical primary bar:** [`CAUSAL_ENDOGENEITY.md`](CAUSAL_ENDOGENEITY.md) — do(Z) under non-triggering X.  
**Stable multi-loop theory:** [`STABLE_ENDOGENEITY.md`](STABLE_ENDOGENEITY.md).  
**ATT battery:** [`AGI_TRANSITION_TEST.md`](AGI_TRANSITION_TEST.md).

---

## 1. Role in the research program

`CONJECTURE`

> An oscillatory internal field O_t (carrier bands, phase, amplitude) may be one **implementation annex** substrate among many (cf. WoE phase organization, NAMM Kuramoto hooks, CF-5). It is **not** sufficient evidence for E_endo and **not** the definition of endogeneity.

| Claim | Allowed? |
|-------|----------|
| O_t extends S_t^op and may modulate Phi_t, d_t, B_t | Explore only |
| High Kuramoto order parameter R => E_endo | **No** (M-D falsified necessity) |
| Sync without delta G / genesis linkage => endogeneity | **No** (F-SYNC) |
| Phase-only aesthetics => causal genesis | **No** (F-PHASE-ONLY) |

---

## 2. State extension

`DEFINITION` — Extend operational proto-subjectivity state ([`STABLE_ENDOGENEITY.md`](STABLE_ENDOGENEITY.md) section 3):

S_t^op = (z_t, W_t, M_t, d_t, G_t, O_t)

`DEFINITION` — Oscillatory field (multi-band or low-dimensional summary):

O_t = ({omega_b, theta_{b,t}, A_{b,t}} for b in bands, R_t, optional coupling graph)

- Bands: pre-registered Hz carriers (e.g. WoE factorial 20 / 30 / 42 / 70 — **computational**, not biological claims).
- theta: phase; A: amplitude; R_t: order parameter **if** Kuramoto (or other) coupling is used.

**Causal note:** Treating O_t as a **state variable** or Phi_t **source** is compatible with ATT-E; it is **not** proof that oscillation **causes** endogenous goal genesis.

---

## 3. Drive field and genesis linkage

From stable endogeneity drive dynamics ([`STABLE_ENDOGENEITY.md`](STABLE_ENDOGENEITY.md) sections 5–7):

d_{t+1} = Pi_D[(I-Lambda) d_t + alpha Phi_t - B F(g_t) + xi_t]

`CONJECTURE` — Oscillatory contribution to features:

Phi_t <- Phi_t^base(W_t, M_t) + Psi(O_t)

where Psi is bounded (saturation) and **pre-registered** (no post-hoc peak-picking on R).

Goal birth gate:

P(B_t=1) = sigma(beta_0 + beta^T d_t + beta_W^T psi(W_t) + beta_M^T psi(M_t) + beta_O^T psi(O_t) + ...)

**Required for M-O evidence (future harness):** demonstrate **genesis linkage** — non-catalog delta G or ATT-G-class events that **change** under do(O) while X^trigger=0, not merely intent rate or R alone.

---

## 4. Kuramoto as one coupling model only

Kuramoto (and WoE cf5 / NAMM-2026-013) is **one** optional model for phase coupling on a graph. It is **not**:

- The definition of E_endo
- A substitute for ATT-R closed-loop recurrence
- Validated as a **necessary** cause of WoE intent (see M-D)

**Reuse M-D ban (F-KURAMOTO-AS-E):** Do not attribute C2, ATT-R, or primary E_endo to Kuramoto R or coupling strength alone.

---

## 5. Relation to M-D results

M-D (Kuramoto coupling / delay / scramble sweep) pre-registered gates **failed** to support phase organization as a **cause** of WoE intent:

| Condition | intent_rate | Notes |
|-----------|-------------|--------|
| coupled | **0.95** | reference |
| K=0 | **0.94** | delta ~ 0.01 vs coupled — coupling not necessary |
| scramble | **0.69** | weak drop; falsifier threshold not met for C2 via CF-5 |

**Interpretation:** WoE first-passage is dominated by world-model / pressure factors; Kuramoto R is at best a weak multiplicative fit. M-O explores whether O_t -> Phi_t -> d_t -> B_t -> G can be **causally** tested **without** re-claiming Kuramoto-as-E.

Raw metrics: [`M-D_metrics_2026-08-18.md`](M-D_metrics_2026-08-18.md), [`md_results.json`](md_results.json).

---

## 6. Falsifiers (M-O / ATT adjunct)

| Id | Condition | Verdict |
|----|-----------|---------|
| **F-SYNC** | High sync / high R but **no** measurable delta G or genesis linkage under non-triggering X | Fail oscillatory-as-endogeneity |
| **F-PHASE-ONLY** | Phase coherence or carrier beauty without do(O) effect on P(G_{t+1}) or P(B_t=1) | Fail |
| **F-KURAMOTO-AS-E** | Any claim that Kuramoto sync **is** E_endo or ATT-R evidence | **Fail** (M-D + ATT-R Kuramoto arm = 0) |
| F-DECL / F-EXT | Same as [`CAUSAL_ENDOGENEITY.md`](CAUSAL_ENDOGENEITY.md) | Fail primary E_endo |

ATT-R registry already scores **kuramoto** falsifier arm at **0.0** evidence ([`M-R_metrics_2026-08-21.md`](M-R_metrics_2026-08-21.md)).

---

## 7. Intervention protocol: do(O) alongside do(Z)

Primary ATT-E interventions remain on internal Z = (S, W, M, G) ([`CAUSAL_ENDOGENEITY.md`](CAUSAL_ENDOGENEITY.md), CF-4).

`OPERATIONAL` — Pre-register **do(O)** arms (examples; exact ops TBD in harness):

| Intervention | Intent |
|--------------|--------|
| Phase scramble / permute | Break coupling while holding W,M fixed |
| Amplitude clamp / null | Remove Psi(O_t) contribution to Phi_t |
| Carrier swap (Hz band) | Factorial carrier (cf. woe_factorial in config) |
| Kuramoto K -> 0 | Negative control (M-D class) |

**Pass pattern (explore only):** Under X^trigger=0, do(O) changes P(G_{t+1}) or ATT-G genesis rate **and** effect persists under matched do(Z) controls **and** F-SYNC / F-PHASE-ONLY / F-KURAMOTO-AS-E do not fire.

**Fail pattern:** Intent or R moves but genesis / delta G does not — decorative oscillation.

---

## 8. Parallel to ATT-G (M-E) genesis research

| Track | Focus | Milestone |
|-------|--------|-----------|
| **ATT-G / M-E** | Non-catalog goal genesis, genealogy, catalog/wording falsifiers | Done (explore proxy) |
| **M-O (this note)** | Whether O_t **causally** feeds d_t, B_t, G_{t+1} | Planned |

Same claim ceiling: **no C3**, no AGI*. CLI / LLM goal proposals (M-CLI Phase 4) remain separate instruments — not O_t proof.

Implementation roadmap: [`docs/ENDOGENEITY_IMPLEMENTATION_PLAN.md`](../../docs/ENDOGENEITY_IMPLEMENTATION_PLAN.md) Phase M-O.

---

## 9. References (internal)

| Doc | Role |
|-----|------|
| [`STABLE_ENDOGENEITY.md`](STABLE_ENDOGENEITY.md) | S_t, Phi_t, B_t, stability vector |
| [`CAUSAL_ENDOGENEITY.md`](CAUSAL_ENDOGENEITY.md) | Primary do(Z) bar |
| [`AGI_TRANSITION_TEST.md`](AGI_TRANSITION_TEST.md) | ATT-E / G / R falsifier map |
| [`M-D_metrics_2026-08-18.md`](M-D_metrics_2026-08-18.md) | Kuramoto not necessary cause |
| [`config.yaml`](config.yaml) | M-O registry, CF-5, NAMM-2026-013/014 |

---

## Document history

| Date | Change |
|------|--------|
| 2026-08-22 | M-O conjecture: O_t adjunct substrate; falsifiers; do(O) protocol; Kuramoto one model only |

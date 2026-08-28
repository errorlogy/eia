# Theory TZ — Stable Endogeneity (Consolidated)

**Status:** `THEORY` / **M-SE** consolidated technical assignment (TZ)  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Claim ceiling:** **C2** scoped partial. **No AGI* claim.**

This note merges the **invariant theory skeleton** from [`STABLE_ENDOGENEITY.md`](STABLE_ENDOGENEITY.md), the **causal bar** from [`CAUSAL_ENDOGENEITY.md`](CAUSAL_ENDOGENEITY.md), and **order-parameter framing** from [`AGI_PHASE_TRANSITION.md`](AGI_PHASE_TRANSITION.md). Implementation-specific choices (WoE v0.2, CLI adapters, daemon ticks) live in the **implementation annex** — see [`docs/ENDOGENEITY_IMPLEMENTATION_PLAN.md`](../../docs/ENDOGENEITY_IMPLEMENTATION_PLAN.md).

---

## Theory vs implementation annex

| **Theory (invariants)** | **Implementation annex (replaceable)** |
|-------------------------|----------------------------------------|
| State \(S_t = (z_t, W_t, M_t, d_t, G_t)\) (+ optional \(O_t\) adjunct) | Concrete world model (sim / symbolic / LLM) |
| Multi-loop topology \(W \to M \to d \to G \to \Pi \to A\) | `CognitiveLoop`, WoE v0.2, daemon tick |
| Primary metric \(E_{\mathrm{endo}}\) via \(do(Z)\), \(X^{\mathrm{trigger}}=0\) | CF-4, ATT runners, shadow multitick |
| Stability vector \(\mathfrak{E}\), metastability band | Drive hyperparameters, governor config |
| ATT pre-registration + falsifier registry | Seed counts, JSON result files |
| Optional oscillatory field \(O_t \to \Psi(O_t) \to \Phi_t\) | `oscillatory_state.py`, CF-5 / Kuramoto hooks |

**Canonical deep dives (not duplicated here):**

- [`STABLE_ENDOGENEITY.md`](STABLE_ENDOGENEITY.md) — multi-loop dynamics, drives, genesis, toy ablation
- [`CAUSAL_ENDOGENEITY.md`](CAUSAL_ENDOGENEITY.md) — \(E_{\mathrm{endo}}\) causal bar and falsifiers
- [`AGI_PHASE_TRANSITION.md`](AGI_PHASE_TRANSITION.md) — order parameters \(E, P, R, N_H, D\), regime table (explore only)
- [`OSCILLATORY_ENDOGENEITY.md`](OSCILLATORY_ENDOGENEITY.md) — M-O adjunct \(O_t\) (conjecture)
- [`ENDOGENEITY_METRICS_POOL.md`](ENDOGENEITY_METRICS_POOL.md) — Tier A–E registry; \(\mathfrak{E}\) → Tier B; ERI composite (conjecture)

---

## 1. Core thesis (stable endogeneity)

`CONJECTURE`

> **Stable endogeneity** is a sustained dynamical regime: internally generated goals and trajectories arise from **coupled multi-loop architecture** while external initiating signals \(X_t^{\mathrm{trigger}}=0\). It is **not** reducible to optimizing one scalar intrinsic reward or to chat self-ascription.

AGI-transition **under this construction** requires stable endogenous causal recurrence **and** ATT-N / \(N_H\) in the full conjunction — not endogeneity alone ([`AGI_STAR_CRITERION.md`](AGI_STAR_CRITERION.md)).

---

## 2. Multi-loop stack (one tick)

\[
W_t \to M_t \to d_t \to G_t \to \Pi_t \to A_t \to \text{Memory/Update} \to W_{t+1}, M_{t+1}, d_{t+1}, G_{t+1}
\]

Causal endogeneity asks whether \(G_{t+1}\) is still generated when \(X_t^{\mathrm{trigger}}=0\).

---

## 3. Operational state

\[
S_t^{\mathrm{op}} = (z_t, W_t, M_t, d_t, G_t)
\]

Optional adjunct (M-O, explore only): \(S_t^{\mathrm{op}} \leftarrow S_t^{\mathrm{op}} \cup \{O_t\}\) with \(\Phi_t \leftarrow \Phi_t^{\mathrm{base}} + \Psi(O_t)\). Kuramoto \(R\) alone does **not** establish \(E_{\mathrm{endo}}\) (M-D, F-KURAMOTO-AS-E).

**Significance test:** interventions on internal components change \(P(G_{t+1}\mid do(\cdot))\) with triggering off ([`CAUSAL_ENDOGENEITY.md`](CAUSAL_ENDOGENEITY.md)).

---

## 4. Stability vector \(\mathfrak{E}\)

| Component | Role | ATT map |
|-----------|------|---------|
| \(E_C\) | Causal endogeneity index | **ATT-E** (primary) |
| \(\lambda_G\) | Goal birth rate | ATT-G |
| \(P_G\) | Persistence under non-triggering \(X\) | ATT-P |
| \(Q_L\) | Learning productivity | M-E / toy sim |
| \(H_G\) | Goal diversity | ATT-G / R support |
| \(B_D\) | Bounded drives | Engineering guard |

Stable recurrence: \(\mathfrak{E}\) in a bounded non-zero band over \(\Delta T\); avoid noisy-TV trap and \(d \to 0\) freeze.

---

## 5. Drive field and genesis (summary)

\[
d_{t+1} = \Pi_D\Big[(I-\Lambda) d_t + \alpha \Phi_t - B F(g_t) + \xi_t\Big], \quad \Phi_t \not\equiv R^{\mathrm{ext}}
\]

Goal genesis (not selection-only): birth gate \(B_t\) and valuation \(V(g)\) — see STABLE_ENDOGENEITY §6–8.

---

## 6. Phase-transition order parameters (explore framing)

From [`AGI_PHASE_TRANSITION.md`](AGI_PHASE_TRANSITION.md) — **thresholds TBD**; do not claim \(\tau_{AGI}\) from theory or toy sim alone.

| Param | Meaning | Evidence hook |
|-------|---------|---------------|
| \(E\) | Endogenous cognitive causality | ATT-E, M-SE toy ablation |
| \(P\) | Temporal goal persistence | ATT-P |
| \(R\) | Endogenous recurrence | ATT-R, M-R-LIVE shadow |
| \(N_H\) | Non-embeddability | ATT-N |
| \(D\) | Cross-domain generality | ATT-D |

---

## 7. Measurement and falsifiers (cross-cut)

- **Primary:** \(do(Z)\) on internal state with \(X^{\mathrm{trigger}}=0\) ([`CAUSAL_ENDOGENEITY.md`](CAUSAL_ENDOGENEITY.md)).
- **ATT battery:** [`AGI_TRANSITION_TEST.md`](AGI_TRANSITION_TEST.md).
- **M-O adjunct falsifiers:** F-SYNC, F-PHASE-ONLY, F-KURAMOTO-AS-E ([`OSCILLATORY_ENDOGENEITY.md`](OSCILLATORY_ENDOGENEITY.md)).

---

## 8. Implementation annex pointers

| Milestone | Artifact |
|-----------|----------|
| M-CLI | `research/cursor-starter-v0.2/src/eia/model_roles.py` |
| M-O stub | `research/cursor-starter-v0.2/src/eia/oscillatory_state.py` |
| M-R-LIVE | `src/eia/runtime/shadow_multitick.py` |
| Tier 0 lock | `scripts/check_sci_tier0.py` |
| Registry | `research/sci_flow/config.yaml` |
| M-EMP pool | `research/sci_flow/endogeneity_metrics.yaml` + `eia.endogeneity_metrics` |

---

## Document history

| Date | Change |
|------|--------|
| 2026-08-25 | Consolidated TZ from STABLE + CAUSAL + AGI_PHASE_TRANSITION sections; theory vs annex split |
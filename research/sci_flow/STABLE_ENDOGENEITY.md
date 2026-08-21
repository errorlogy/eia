# Stable Endogeneity ? Multi-Loop Operational Theory

**Status:** `OPERATIONAL` / `CONJECTURE` (2026-08-21) ? **not** an AGI* claim  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Milestone:** M-SE (Stable Endogeneity theory + toy ablation)  
**Causal bar (primary metric):** [`CAUSAL_ENDOGENEITY.md`](CAUSAL_ENDOGENEITY.md) ? \(E_{\mathrm{endo}}\) / ATT-E  
**Parent construction:** [`AGI_PHASE_TRANSITION.md`](AGI_PHASE_TRANSITION.md)  
**Falsifiable protocol:** [`AGI_TRANSITION_TEST.md`](AGI_TRANSITION_TEST.md)

---

## Epistemic discipline

| Tag | Meaning |
|-----|---------|
| `DEFINITION` | Notation inside this construction |
| `OPERATIONAL` | Measurable proxy or toy instrument |
| `CONJECTURE` | Falsifiable hypothesis |
| `PHILOSOPHICAL_INFERENCE` | Framing only |

**Hard ban:** Do not equate stable endogeneity with AGI*, consciousness, or a single fixed intrinsic reward. Do not claim \(\tau_{AGI}\) from this note or the toy sim alone.

---

## 1. Core thesis

`CONJECTURE`

> **Stable endogeneity** is not reducible to optimizing one scalar intrinsic reward. It is a **sustained dynamical regime** in which internally generated goals and trajectories arise from **coupled multi-loop architecture** (world model, self-model, drive field, goal genesis, action, memory update) while external initiating signals \(X_t^{\mathrm{trigger}}=0\).

`PHILOSOPHICAL_INFERENCE` ? AGI-transition **under this research construction** is approximated by **stable endogenous causal recurrence** (bounded non-zero internal drives, recurrent goal-formation, sustainable goal birth), **not** by endogeneity alone and **not** without \(N_H\) / ATT-N in the full \(AGI^{*}\) conjunction ([`AGI_STAR_CRITERION.md`](AGI_STAR_CRITERION.md)).

---

## 2. Multi-loop cognitive stack

`DEFINITION` ? Directed influence stack (one tick slice):

| Stage | Symbol | Role |
|-------|--------|------|
| World model | \(W_t\) | Predictive / latent dynamics of environment |
| Self-model | \(M_t\) | Competence, uncertainty, knowledge, meta-state |
| Internal drive field | \(d_t\) | Bounded motivational vector (not external reward) |
| Goal genesis | \(G_t \to G_{t+1}\) | Birth and valuation of goals (not selection-only) |
| Action / policy | \(\Pi_t, A_t\) | Execution |
| Memory / model update | ? | Consolidation ? new \(W, M, d\) |

Cycle (closed contour for recurrence):

\[
W_t \to M_t \to d_t \to G_t \to \Pi_t \to A_t \to \text{Memory/Update} \to d_{t+1}, W_{t+1}, M_{t+1}
\]

External environment \(X_t\) remains coupled at observation and action boundaries; **causal endogeneity** concerns whether \(G_{t+1}\) is still generated when \(X_t^{\mathrm{trigger}}=0\).

---

## 3. Operational proto-subjectivity state

`DEFINITION` ? Compact state vector for stability analysis:

\[
S_t^{\mathrm{op}} = (z_t, W_t, M_t, d_t, G_t)
\]

where \(z_t\) aggregates persistent internal state (may align with \(S_t\) in [`AGI_PHASE_TRANSITION.md`](AGI_PHASE_TRANSITION.md)).

**Causal significance test:** \(S_t \to G_{t+1}\) is operationally significant when interventions on internal components change \(P(G_{t+1}\mid do(\cdot))\) while **external triggering** is off:

\[
X_t^{\mathrm{trigger}} = 0 \quad\Rightarrow\quad
\text{still } \Delta P(G_{t+1}\mid do(S_t)) \neq 0
\]

Full \(do(Z)\) bar and falsifiers: [`CAUSAL_ENDOGENEITY.md`](CAUSAL_ENDOGENEITY.md).

---

## 4. Stability vector \(\mathfrak{E}\)

`DEFINITION` ? Vector of **stability** indicators (metastable endogenous regime, not collapse to zero drive):

\[
\mathfrak{E} = (E_C,\, \lambda_G,\, P_G,\, Q_L,\, H_G,\, B_D)
\]

| Component | Meaning | EIA / ATT map |
|-----------|---------|---------------|
| \(E_C\) | Causal endogeneity index \(C_{\mathrm{int}}/(C_{\mathrm{int}}+C_{\mathrm{ext}})\) via \(do()\)-interventions | **ATT-E** (primary); [`CAUSAL_ENDOGENEITY.md`](CAUSAL_ENDOGENEITY.md) |
| \(\lambda_G\) | Goal **birth** rate (genesis events / tick) | **ATT-G** |
| \(P_G\) | Temporal persistence of endogenous goals under non-triggering \(X\) | **ATT-P** |
| \(Q_L\) | Learning productivity (competence / LP gains per internal episode) | M-E / M-P explore; toy sim |
| \(H_G\) | Goal diversity (entropy / effective number of active goals) | ATT-G / ATT-R support |
| \(B_D\) | Bounded drives (norm of \(d_t\) in admissible envelope) | Engineering guard; toy sim |

`CONJECTURE` ? **Stable endogenous causal recurrence** requires \(\mathfrak{E}\) jointly in a bounded non-zero band over \(\Delta T\), with \(E_C\) above a future \(\theta_E\) **and** \(\lambda_G, P_G, Q_L, H_G\) not collapsing (noisy-TV trap, \(d\to 0\) freeze, or prompt-only revival).

---

## 5. Internal drive field

`DEFINITION` ? Five-channel drive vector:

\[
d_t = [d^{\mathrm{epi}}, d^{\mathrm{comp}}, d^{\mathrm{ctrl}}, d^{\mathrm{coh}}, d^{\mathrm{nov}}]^\top
\]

`DEFINITION` ? Drive dynamics with projection \(\Pi_D\) (non-negativity / saturation / box constraints):

\[
d_{t+1} = \Pi_D\Big[(I-\Lambda)\, d_t + \alpha\, \Phi_t - B\cdot F(g_t) + \xi_t\Big]
\]

- \(\Phi_t\): features from **world/self-model** (prediction error, competence gap, imagined futures) ? **not** external reward \(R^{\mathrm{ext}}\).
- \(F(g_t)\): goal-specific fatigue / satiation.
- \(\Lambda\): leak toward baseline; \(\xi_t\): bounded noise.

`CONJECTURE` ? Metastability: admissible regime has \(\|d_t\|\in [d_{\min}, d_{\max}]\) with \(d_{\min}>0\) on long horizons under \(X^{\mathrm{trigger}}=0\), rather than \(d\to 0\) (shutdown) or unbounded runaway.

---

## 6. Counterfactual endogenous generator

`CONJECTURE` ? Endogenous **counterfactuals** are generated from **imagined trajectories** rollouts in \(W_t\) (and \(M_t\)), not from passive observation curiosity alone:

\[
\tilde{\tau} \sim p(\cdot \mid W_t, M_t, do(\Pi)) \quad\Rightarrow\quad \Delta \Phi_t,\, \text{candidate } g^{*}
\]

This is **not** proof of \(E_{\mathrm{endo}}\) without ATT-E interventions.

---

## 7. Goal genesis (not selection-only)

`DEFINITION` ? Goal set update:

\[
G_{t+1} = G_t \cup \{g^{*}\}
\]

Birth indicator \(B_t\in\{0,1\}\):

\[
P(B_t=1) = \sigma\big(\beta_0 + \beta^\top d_t + \beta_W^\top \psi(W_t) + \beta_M^\top \psi(M_t) + \ldots\big)
\]

`OPERATIONAL` ? EIA explore: ATT-G / M-E non-catalog genesis with genealogy (**ATT-C**).

---

## 8. Goal valuation functional

`DEFINITION` ? Internal score for candidate goal \(g\) at time \(t\):

\[
J_t(g) = w_{\mathrm{IG}}\,\mathrm{IG}(g) + w_{\mathrm{LP}}\,\mathrm{LP}(g) + w_{\mathrm{emp}}\,\mathrm{Emp}(g) + w_{\mathrm{coh}}\,\mathrm{Coh}(g) + w_{\mathrm{nov}}\,\mathrm{Nov}(g) + w_P\,P(g)
\]
\[
\quad - w_{\mathrm{stuck}}\,\mathrm{Stuck}_t(g) - w_{\mathrm{risk}}\,\mathrm{Risk}(g) - w_{\mathrm{cost}}\,\mathrm{Cost}(g)
\]

**Stuck\(_t\):** Noisy-TV / irreducible-error suppressor.

`OPERATIONAL` ? Toy ablation implements LP gating + Stuck\(_t\) + hierarchical unlock; see Section 14.

---

## 9. Multi-timescale separation

`DEFINITION`

\[
\tau_{\mathrm{action}} \ll \tau_{\mathrm{goal}} \ll \tau_{\mathrm{meta}}
\]

`CONJECTURE` ? Stability is **metastable**: drives remain bounded and non-zero.

---

## 10. Formal stability criteria (research targets)

`CONJECTURE` ? \(\rho(A_{\mathrm{cl}}) < 1\) for small perturbations while the operating point maintains **bounded non-zero** recurrent activity.

`CONJECTURE` ? Under \(X^{\mathrm{trigger}}=0\), \(\lambda_G \in [\lambda_{\min}, \lambda_{\max}]\). Bounds **TBD**.

---

## 11. Causal Endogeneity Index \(E_C\)

\[
E_C = \frac{C_{\mathrm{int}}}{C_{\mathrm{int}} + C_{\mathrm{ext}}}
\]

**Primary transition metric:** \(E_{\mathrm{endo}}\) / ATT-E remains the **primary** empirical gate; \(\mathfrak{E}\) refines stable vs spurious endogeneity.

---

## 12. Four coupled loops

| Loop | Drive channel emphasis | Typical trigger in \(\Phi_t\) |
|------|------------------------|-------------------------------|
| Epistemic | \(d^{\mathrm{epi}}\) | Prediction error, information gain |
| Autotelic | \(d^{\mathrm{comp}}, d^{\mathrm{nov}}\) | Learning progress, novelty |
| Homeostatic | \(d^{\mathrm{coh}}\) | Model?self coherence, stress / deficit |
| Metacognitive | \(d^{\mathrm{ctrl}}, M_t\) | Competence gap, control / empowerment |

Epistemic ? autotelic ? homeostatic ? metacognitive co-activation.

---

## 13. Relation to ATT-E / G / P / R / N / D

| ATT | Stable endogeneity role |
|-----|-------------------------|
| **ATT-E** | **Primary** ? \(E_C\), causal bar |
| **ATT-G** | \(\lambda_G\) |
| **ATT-P** | \(P_G\) |
| **ATT-R** | Closed loop recurrence |
| **ATT-C** | Genealogy |
| **ATT-N** | \(N_H\) orthogonal conjunct |
| **ATT-D** | Cross-domain \(\mathfrak{E}\) |

---

## 14. Toy ablation (`endogeneity_stack_sim.py`)

Metrics: [`M-SE_metrics_2026-08-21.md`](M-SE_metrics_2026-08-21.md).

| Mode | mastered | unlocked | noisy_trap_fraction | goal_entropy | max_goal_share |
|------|----------|----------|---------------------|--------------|----------------|
| prediction_error | 0.0 | 5.0 | 0.994 | 0.014 | 0.994 |
| learning_progress | 7.5 | 9.4 | 0.017 | 0.621 | 0.176 |
| stable_stack | 7.5 | 9.4 | 0.009 | 0.613 | 0.199 |

`stable_stack` drive norm: min ? 0.583, max ? 1.099.

---

## 15. Falsifiers

| Id | Condition | Verdict |
|----|-----------|---------|
| F-SR | Single scalar intrinsic reward sufficient | Fail architecture claim |
| F-TV | Noisy-TV trap dominates | Fail \(H_G, Q_L\) |
| F-ZERO | \(d\to 0\) sustained | Fail \(B_D, \lambda_G\) |
| F-DECL | Declaration without \(do(Z)\) | Fail \(E_C\) |
| F-EXT | Endogenous metrics vanish without external trigger | Fail stability |
| F-LOOP | No closed recurrence | Fail ATT-R leg |

---

## 16. References (external ? not proofs)

| Topic | Citation |
|-------|----------|
| World models | Richens et al., ICML 2024 ? [PMLR](https://proceedings.mlr.press/v235/richens24a.html) |
| MAGELLAN | [PMLR v267](https://proceedings.mlr.press/v267/gaven25a.html) |
| Active inference | Parr, Pezzulo, Friston *Active Inference* (MIT Press) |
| Curiosity / Noisy-TV | Burda et al., ICML 2019 |
| Empowerment MBRL | Mohamed & Rezende; Gregor et al. |
| 3M-Progress | NeurIPS 2023 intrinsic-motivation milestones literature |
| DreamerV3 | [arXiv:2301.04104](https://arxiv.org/abs/2301.04104) |

---

## Document history

| Date | Change |
|------|--------|
| 2026-08-21 | M-SE: stable endogeneity stack, \(\mathfrak{E}\), toy sim summary |

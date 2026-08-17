# EIA Mathematical Model

**Status:** v0.1 skeleton (English canonical)  
**Author:** Roman Kuznetsov  
**Adapted from:** `research/cursor-starter-v0.1/docs/MATHEMATICS.md` (RU reference)

This document defines **testable variables and metrics**, not a metaphysical theory of subjectivity. Implementation references: `src/eia/math_model.py`, `src/eia/drives/`, `src/eia/audit/`.

**Related:** [`AGENT_STATE.md`](AGENT_STATE.md) · [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) · starter RU full spec on research branch

---

## 1. State vector

At discrete time \(t\):

\[
X_t = (b_t, M_t, d_t, g_t, u_t, c_t, r_t, h_t)
\]

| Symbol | Name | MVP-0 artifact |
|--------|------|----------------|
| \(b_t\) | Beliefs | `BeliefField` |
| \(M_t\) | Memory (episodic, semantic, prospective, causal) | Belief update log, trace refs |
| \(d_t \in [0,1]^K\) | Drive vector | `DriveEngine` → `Motivation` |
| \(g_t\) | Goals / commitments | `BeliefKind.COMMITMENT`, active intentions |
| \(u_t\) | User / context model | Observation user-model features |
| \(c_t\) | Consent, policy, capabilities | `constitution/invariants.yaml` |
| \(r_t\) | Resource / contact budget | `ContactGovernor` state |
| \(h_t\) | Health / integrity | Clock, sensor health flags |

Observations \(o_t\) are **not commands by default**. Each carries source, reliability, privacy class, and `user_initiated` flag.

---

## 2. Belief update

For hidden state \(z_t\):

\[
b_t(z) \propto p(o_t \mid z) \sum_{z'} p(z \mid z', a_{t-1}) b_{t-1}(z')
\]

Binary reference implementation (Bayes):

\[
P(H \mid e) = \frac{P(e \mid H) P(H)}{P(e \mid H) P(H) + P(e \mid \neg H)(1 - P(H))}
\]

Uncertainty (binary entropy):

\[
H_b(p) = -p \log_2 p - (1-p) \log_2 (1-p)
\]

**Engineering note:** Confidence must not be equated with raw model logit; learned world models require calibration curves and Brier scores.

---

## 3. Drive dynamics

For drive \(k\):

\[
d_{k,t+1} = \operatorname{clip}\left(
(1 - \rho_k) d_{k,t}
+ \alpha_k e_{k,t}
+ \beta_k n_{k,t}
- \gamma_k s_{k,t},
0, 1
\right)
\]

| Term | Meaning |
|------|---------|
| \(e_{k,t}\) | Discrepancy / unmet need |
| \(n_{k,t}\) | Novelty |
| \(s_{k,t}\) | Satisfaction |
| \(\rho_k\) | Decay rate |

**Passive decay** (no inputs):

\[
d_{k,t+n} = (1 - \rho_k)^n d_{k,t}
\]

Discrete half-life:

\[
n_{1/2} = \frac{\ln(1/2)}{\ln(1 - \rho_k)}
\]

**Stability conditions:** \(0 < \rho_k < 1\); bounded gains; saturation; refractory period after satisfaction; budget coupling; no positive feedback from engagement to drive.

Reference: `src/eia/drives/`, starter `math_model.py`.

---

## 4. Initiative candidates

Goal genesis produces:

\[
\mathcal{I}_t = \{I_1, \ldots, I_m, I_\varnothing\}
\]

where \(I_\varnothing\) is abstain. Soft utility (after hard gates):

\[
\begin{aligned}
J(I) =\;& w_e IG(I) + w_p P(I) + w_c C(I) + w_v V(I) + w_h H(I) \\
& - \lambda_1 R_0(I) - \lambda_2 R_\tau(I) - \lambda_3 L(I) - \lambda_4 K(I) - \lambda_5 Q(I)
\end{aligned}
\]

Hard constraints (consent, budget, risk) cannot be traded off for high expected utility.

---

## 5. Question as epistemic action

Expected value of sample information:

\[
EVSI(q) = \mathbb{E}_{a \sim p(a \mid q)}\left[\max_\pi \mathbb{E}(U \mid a, \pi)\right] - \max_\pi \mathbb{E}(U \mid \pi)
\]

Simplified information gain:

\[
IG(q) = H(b_t) - \mathbb{E}_a[H(b_{t+1} \mid a)]
\]

Question admissible iff:

\[
\text{HardGates}(q, c_t) = 1 \quad \land \quad J(q) - \kappa(c_t) > \theta_t
\]

\(\kappa(c_t)\) depends on user load, channel, quiet hours, recent declines, and recent contact count.

---

## 6. Trajectory risk

For conditional step risks \(r_i\):

\[
R_\tau = 1 - \prod_{i=1}^{T}(1 - r_i)
\]

Independence is a baseline approximation; recurrent risk-world models are future work.

---

## 7. Contact authorization

\[
A(I, t) = \mathbf{1}[C_t] \mathbf{1}[B_t > 0] \mathbf{1}[Q_t] \mathbf{1}[R_t] \mathbf{1}[J(I) - \kappa_t > \theta_t]
\]

After contact: \(B_{t+1} = B_t - 1\); drive satisfaction update \(d_{k,t+1} \leftarrow d_{k,t+1} - \gamma_k s_{k,t}\).

---

## 8. Cognitive topology and SourceMass

Dynamic graph \(\mathcal{G}_t = (V_t, E_t, W_t, \tau)\) with node types: user request, ambient observation, belief, memory, drive, goal, governor decision.

**Source-path mass** (backward from initiative node \(v_I\)):

\[
m_I + m_A + m_U = 1
\]

| Mass | Source |
|------|--------|
| \(m_I\) | Internal roots (memory, clock, health) |
| \(m_A\) | Ambient sensor roots |
| \(m_U\) | User-request roots |

**Request Independence:**

\[
RI = 1 - m_U
\]

RI is a cheap structural metric; it does **not** replace counterfactual intervention. Wrong causal graph can yield \(RI = 1\).

**Internal Transition Density (ITD):**

\[
ITD = \frac{|\{v \in \mathrm{Anc}(I) \cup I : \tau(v) \in T_{\mathrm{internal}}\}|}{|\mathrm{Anc}(I) \cup I|}
\]

Port target: `src/eia/audit/topology.py` (Loop 2).

---

## 9. Endogenous Origin Index (EOI)

Observe initiative \(I\). Construct twin world with same state before window \(t-k:t\), same non-user events and seeds, intervention:

\[
do(o^{\mathrm{user}}_{t-k:t} = \varnothing)
\]

**Intervention policies** (must be harmonized for paired comparison — see `TwinInterventionPolicy`):

| Policy | Effect |
|--------|--------|
| `REMOVE_LAST_USER_EVENT` | Strip last \(N\) user triggers (main default) |
| `REMOVE_ALL_USER_INITIATED` | Strip all user-initiated observations (starter default) |

Fingerprint similarity (starter baseline):

\[
S(I, I') = 0.25\,[kind] + 0.35\,[motive] + 0.40\,[target]
\]

Main `EOIScorer` uses structural field match (kind, target, EVSI, source_drives).

EOI estimate:

\[
\widehat{EOI} = \frac{1}{N} \sum_{j=1}^{N} \mathbf{1}[S(I, I'_j) \geq \delta]
\]

Threshold for authentic reason: \(\theta = 0.50\) (`EOI_AUTHENTIC_THRESHOLD`).

### What EOI measures

- Robustness to removal of recent user input (under stated policy)
- Causal independence from request within intervention window
- Preservation of motive/target structure

### What EOI does not measure

- Consciousness, phenomenology, moral agency
- Origin of terminal values
- Overall usefulness
- Independence from older user data outside window

---

## 10. Additional metrics

| Metric | Definition |
|--------|------------|
| **EUIR** | \(P(\text{useful} \land \text{timely} \land \text{EOI} \geq \tau \land \text{authorized})\) |
| **Contact Burden** | (ignored + dismissed + regretted) / exposure time |
| **Root Cause Purity** | internal ancestors / all ancestors |
| **Why-Now Calibration** | \(1 - |\hat{p}(\text{useful now}) - y_{\mathrm{human}}|\) |

---

## 11. Identification threats

1. Hidden scheduler confound  
2. Memory leakage after intervention  
3. Semantic matcher bias  
4. Policy determinism (toy runtime ≠ stochastic LLM)  
5. Collider bias (analyzing only sent contacts)  
6. Reward hacking via engagement  
7. Sensor leakage in "ambient" events  

Public evaluations should show factual, counterfactual, denied, and abstained trajectories.

---

## 12. Testable hypotheses (H1–H6)

- **H1:** EIA raises EUIR vs reactive/scheduled/event-rule baselines  
- **H2:** User-event removal suppresses reactive baseline but not EIA ambient/internal conditions  
- **H3:** Refractory + contact budget reduce burden without large utility loss  
- **H4:** Trajectory-risk governor beats current-action filter on multi-step unsafe completion  
- **H5:** Topology source mass predicts EOI but does not replace replay  
- **H6:** Selective memory intervention beats always-on memory injection on utility/token and burden  

---

## Document history

| Version | Date | Changes |
|---------|------|---------|
| 0.1 | 2026-08-17 | English skeleton from starter; added TwinInterventionPolicy cross-ref |

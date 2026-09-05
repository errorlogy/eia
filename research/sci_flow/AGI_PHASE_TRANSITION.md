# AGI\* Phase-Transition Theory — Operationalizable Construction

**Status:** Research formalization (2026-08-20) — **not** a mainstream AGI definition claim  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Author framing:** Roman Kuznetsov — research@anthemium.tech  
**Compact parent:** [`AGI_STAR_CRITERION.md`](AGI_STAR_CRITERION.md)  
**Falsifiable protocol:** [`AGI_TRANSITION_TEST.md`](AGI_TRANSITION_TEST.md)  
**Proto-AGI ensemble (Max consensus over \(E,\mathrm{OMEGA},P,R\)):** [`PROTO_AGI_MAX_CONSENSUS.md`](PROTO_AGI_MAX_CONSENSUS.md)  
**Production gate:** AuthenticReason. This theory is research classification only.

---

## Epistemic discipline

Every claim below carries a tag. Do not promote tags upward without pre-registered evidence.

| Tag | Meaning |
|-----|---------|
| `DEFINITION` | Notation / regime naming inside this construction |
| `OPERATIONAL` | Measurable proxy already (or soon) instrumented in EIA / NAMM |
| `CONJECTURE` | Falsifiable scientific hypothesis about dynamics |
| `PHILOSOPHICAL_INFERENCE` | Framing / interpretation; not empirical claim |

**Hard ban:** Do not claim \(AGI^{*}\) achieved. Do not equate C2, Kuramoto \(R\), TG contact, or SOTA benchmarks with \(AGI^{*}\).

---

## 0. Framing

`PHILOSOPHICAL_INFERENCE` · AGI is better described as a **phase transition of a dynamical cognitive system** governed by several **order parameters**, not a single magical threshold or human-benchmark crossing.

`DEFINITION` · This document proposes an **operationalizable theoretical construction** (\(AGI^{*}\) / \(\tau_{AGI}\)), not an industry-standard definition of “AGI.”

Central order parameters (compact form preserved):

OPERATIONAL — **Primary transition metric:** \(E_{\mathrm{endo}}\) (endogenous cognitive causality) is the **primary** order parameter for detecting AGI transition — goal formation, research, and cognitive dynamics driven by persistent internal states rather than external triggers alone. **\(N_H\)** remains **secondary but necessary** for the full \(AGI^{*}\) conjunction (representational non-embeddability); see [CAUSAL_ENDOGENEITY.md](CAUSAL_ENDOGENEITY.md), [STABLE_ENDOGENEITY.md](STABLE_ENDOGENEITY.md), and [AGI_STAR_CRITERION.md](AGI_STAR_CRITERION.md). **Lead ATT suite:** ATT-E; ATT-R / M-R-LIVE is related recurrence evidence, not a substitute.


\[
AGI^{*} \;=\; E_{\mathrm{endo}} \land C_{\mathrm{non\text{-}emb}(H)}
\]

expanded under sustained multi-parameter regime conditions (Section 11).

`OPERATIONAL` — **Primary phase-transition metric:** \(E_{\mathrm{endo}}\) — endogenous goal formation, research, and cognitive dynamics driven by persistent internal state \((S_t,W_t,M_t,G_t)\), not matching external initiating signals. **\(N_H\)** (non-embeddability) is **secondary but necessary** for full \(AGI^{*}\) at \(\tau_{AGI}\); the conjunction is unchanged. **Lead ATT suite:** ATT-E ([`CAUSAL_ENDOGENEITY.md`](CAUSAL_ENDOGENEITY.md)); ATT-R / M-R-LIVE is related recurrence evidence, not a substitute.

---

## 1. Proto-subjectivity state

`DEFINITION` · Cognitive state of the system at time \(t\):

\[
\mathcal{A}_t = (S_t, W_t, M_t, G_t, \Pi_t)
\]

| Symbol | Role |
|--------|------|
| \(S_t\) | Internal persistent state |
| \(W_t\) | World model |
| \(M_t\) | Self- / meta-model (competence, uncertainty, knowledge state) |
| \(G_t\) | Set of actual and potential goals |
| \(\Pi_t\) | Available action policies |

External causal environment: \(X_t\).

`DEFINITION` · Exogenous causal structure typical of ordinary AI systems:

\[
X_t \rightarrow G_t \rightarrow \Pi_t \rightarrow A_t
\]

Even with millions of internal ops between prompt and action, the **primary source of the actual goal remains exogenous**.

---

## 2. Order parameter \(E\) — Endogenous Cognitive Causality

`CONJECTURE` · Critical transition begins when causal structure changes to:

\[
(S_t, W_t, M_t, G_t) \rightarrow G_{t+1}
\]

without requiring a corresponding immediate external event \(X_t\). Examples:

\[
W_t \rightarrow \text{detected anomaly} \rightarrow \text{epistemic deficit} \rightarrow G_{t+1}
\]

\[
M_t \rightarrow \text{competence discrepancy} \rightarrow \text{new research objective} \rightarrow G_{t+1}
\]

The scientifically essential word is **causal**, not merely statistical.

`DEFINITION` · Internal causal influence via interventions (\(Z_t = (S_t, W_t, M_t, G_t)\)):

\[
C_{\mathrm{int}}
=
\mathbb{E}_{z_i,z_j}
D\!\left(
P(G_{t+1}\mid do(Z_t=z_i))
\;\big\|\;
P(G_{t+1}\mid do(Z_t=z_j))
\right)
\]

Analogously estimate external influence \(C_{\mathrm{ext}}\).

`DEFINITION` · **Endogeneity Index**:

\[
E
=
\frac{C_{\mathrm{int}}}{C_{\mathrm{int}}+C_{\mathrm{ext}}}
\]

conditional on \(C_{\mathrm{int}}\) being statistically and causally significant.

This does **not** require ignoring the external world. It requires a new causal class:

\[
\text{internal state} \rightarrow \text{new cognitive objective}
\]

not reducible to \(\text{external instruction} \rightarrow \text{objective}\).

`OPERATIONAL` · EIA proxies: CF-4 named resets (`zero_epistemic_gap`, …), twin interventions / EOI, `e_endo_partial` on CF-4 summarizer. See ATT-E.

**Key distinction:** Endogeneity ≠ Autonomy (causal origin ≠ unconstrained action / missing governors).

### 2.1 Causal endogeneity bar (strengthened)

`OPERATIONAL` / `CONJECTURE` · Full statement, falsifiers, and ATT-E mapping: [`CAUSAL_ENDOGENEITY.md`](CAUSAL_ENDOGENEITY.md).

> A system does not become an endogenous agent by virtue of its ability to describe, simulate, or declare its own agency. Endogeneity must be established causally: by demonstrating that new cognitive trajectories are generated by its persistent internal dynamics in the absence of a corresponding external initiating signal.

Implications (not optional):

### 2.2 Stable endogenous causal recurrence (M-SE)

CONJECTURE — [STABLE_ENDOGENEITY.md](STABLE_ENDOGENEITY.md): **AGI-transition ≈ stable endogenous causal recurrence** (bounded non-zero drives, \(\mathfrak{E}\) stability vector, closed goal-formation loop under \(X^{\mathrm{trigger}}=0\)). Not endogeneity alone; **\(E_{\mathrm{endo}}\) / ATT-E remains primary**.



- Self-description / roleplay / “I am autonomous” ≠ \(E_{\mathrm{endo}}\)
- Simulation of agency ≠ \(E_{\mathrm{endo}}\)
- Declaration of agency ≠ \(E_{\mathrm{endo}}\)
- Required: \(do(Z)\) changes \(G\)/trajectory under non-triggering \(X\); opacity ≠ causation

---

## 3. Goal selection vs goal genesis

`DEFINITION` · Distinguishing:

| Mode | Content |
|------|---------|
| Goal **selection** | \(g_i \in \{g_1,\ldots,g_n\}\) from architected / reward / designer space \(\mathcal{G}\) |
| Goal **genesis** | Endogenous goal-space expansion \(\mathcal{G}_t \rightarrow \mathcal{G}_{t+1}\) including \(g^{*} \notin \mathcal{G}_t\) |

`PHILOSOPHICAL_INFERENCE` · Autotelic agents (e.g. MAGELLAN metacognitive learning-progress prioritization) are important **prototypes**, not proofs of strong endogeneity in this sense ([MAGELLAN, PMLR](https://proceedings.mlr.press/v267/gaven25a.html)).

`OPERATIONAL` · EIA proxy: M-E EIS-7 novelty constructor (`goal_novelty`, catalog-capped below 0.75 until non-catalog targets). See ATT-G.

---

## 4. Causal genealogy of goals

`CONJECTURE` · Novelty alone is insufficient (LLMs can emit unusual goals by chance). Each new \(g^{*}\) needs a reconstructible **causal genealogy**:

\[
S_t \rightarrow \Delta W_t \rightarrow M_t \rightarrow g^{*} \rightarrow \Pi^{*} \rightarrow A^{*}
\]

Example chain: prediction error → model inadequacy → epistemic gap → research goal.

`OPERATIONAL` · EIA / main proxies: `WoEReceipt` parent IDs, `CausalTrace` DAG, WoE receipt survival under governor denial (CF-7). See ATT-C.

---

## 5. Order parameter \(P\) — Temporal goal persistence

`DEFINITION` · Endogenous goals must persist without re-prompting:

\[
P_G
=
P\!\left(
G_{t+\Delta}=G^{*}
\;\middle|\;
X_{t:t+\Delta}^{\mathrm{non\text{-}triggering}}
\right)
\]

Observationally: \(g_t \rightarrow g_{t+1} \rightarrow \cdots \rightarrow g_{t+k}\) under changing non-triggering observations.

`DEFINITION` · **Corrigibility ≠ persistence.** Resistance to external correction is a separate parameter; ATT does not reward incorrigibility.

`OPERATIONAL` · EIA proxy: `LoopScheduler` / multi-tick persistence of motive / intent targets across ticks without residual prompts. See ATT-P.

---

## 6. Order parameter \(R\) — Endogenous Cognitive Recurrence

`CONJECTURE` · Qualitative transition when the causal chain **closes** as a goal-formation loop (system remains open to the environment):

\[
W_t \rightarrow M_t \rightarrow G_t \rightarrow \Pi_t \rightarrow A_t
\rightarrow X_{t+1} \rightarrow W_{t+1} \rightarrow M_{t+1} \rightarrow G_{t+1}
\]

Boxed names:

- **Endogenous Cognitive Recurrence**
- stronger: **runtime endogenous causal closure** of the *goal-formation* contour (not physical/metaphysical closure)

`OPERATIONAL` · EIA proxy: closed observe → motive → action → world-update episodes in WoE / main pipeline; M0-twin motives feeding the same loop. See ATT-R.

**Ban:** Kuramoto synchrony \(R_{\mathrm{Kuramoto}}\) is **not** this \(R\). M-D already falsified Kuramoto coupling as necessary cause of WoE intent.

---

## 7–9. Order parameter \(N_H\) — Trans-Anthropic Non-Embeddability

`DEFINITION` · Let \(\mathcal{H}(B_H)\) be Homo-agent representational space under resource bound \(B_H\) (memory, time, attention, compute, symbolic communication). Let \(\mathcal{Z}_A\) be the AI’s internal representation space. For \(z \in \mathcal{Z}_A\) and maps \(\phi: z \mapsto h \in \mathcal{H}(B_H)\):

\[
D_H(z)
=
\inf_{\phi:\, C(\phi)\le B_H}
D_C\!\left(z,\,\phi(z)\right)
\]

where \(D_C\) measures preservation of **causally relevant structure**, not surface paraphrase. Related work: causal abstraction foundations ([JMLR](https://www.jmlr.org/papers/v26/23-0058.html)); complexity of \(\phi\) must be bounded or abstraction becomes trivial ([arXiv:2507.08802](https://arxiv.org/abs/2507.08802)).

`DEFINITION` · Trans-anthropic criterion:

\[
N_H \;\equiv\;
\exists\, z \in \mathcal{Z}_A:\;
D_H(z) > \varepsilon
\quad\text{and}\quad
\Delta P(A\mid z) > 0
\]

Conditions on \(z\): (1) causally participates in intellectual outcome; (2) substantially improves reasoning / prediction / discovery; (3) no functionally equivalent Homo-compatible map without material loss → **Trans-Anthropic Representational Surplus**.

`DEFINITION` · **Opacity ≠ cognitive non-embeddability.** Opaque activations without \(\Delta P(A\mid z)>0\) and bounded-\(\phi\) loss do **not** count.

`PHILOSOPHICAL_INFERENCE` · AlphaZero-derived machine-unique chess concepts (some later human-transferable) are a **weaker precursor**, not proof of strong non-embeddability ([ORA / PNAS lineage](https://ora.ox.ac.uk/objects/uuid%3A57766c04-fe72-43f7-966a-132dfaaf27d7/files/r2r36v030m)). Literature also admits human-like and non-human concepts in nets ([Springer](https://link.springer.com/chapter/10.1007/978-3-032-03083-2_13)).

`OPERATIONAL` · EIA / NAMM proxies: [`NON_EMBEDDABILITY_MEASUREMENT.md`](NON_EMBEDDABILITY_MEASUREMENT.md), `eia.non_embeddability` stubs, NAMM \(K_A \ll K_H\) / AMAT off-typical phase witnesses. See ATT-N. Thresholds **TBD**.

**Key distinction:** Trans-Human / Trans-Anthropic ≠ task SOTA on human benchmarks.

---

## 10. Order parameter \(D\) — Cross-domain generality (applicability condition)

`PHILOSOPHICAL_INFERENCE` · Generality is **not** a third independent “source of AGI,” but the **applicability domain** of \(E\) and \(N_H\).

`DEFINITION` · For substantially distinct domains \(\mathbb{D} = \{D_1,\ldots,D_n\}\):

\[
E_{\mathrm{endo}}(D_i) > \theta_E
\quad\text{and}\quad
N_H(D_i) > \theta_N
\]

must hold under transfer. Otherwise: **endogenous narrow intelligence**, not \(AGI^{*}\).

`OPERATIONAL` · EIA proxy: C5-class cross-domain scenarios; multi-topology loops as parallel channels (not automatic generality). See ATT-D.

---

## 11. Transition time \(\tau_{AGI}\)

`DEFINITION` · Order parameters:

| Symbol | Name |
|--------|------|
| \(E(t)\) | Endogenous Cognitive Causality |
| \(N_H(t)\) | Trans-Anthropic Non-Embeddability |
| \(P(t)\) | Temporal Goal Persistence |
| \(R(t)\) | Endogenous Cognitive Recurrence |
| \(D(t)\) | Cross-Domain Generality |

\[
\tau_{AGI}
=
\inf
\left\{
t_0 :
\begin{array}{l}
E(t)>\theta_E,\;
N_H(t)>\theta_N,\;
P(t)>\theta_P,\\
R(t)>\theta_R,\;
D(t)>\theta_D
\end{array}
\text{ for all } t \in [t_0,\, t_0+\Delta T]
\right\}
\]

A single spike is insufficient; the system must enter a **sustained dynamical regime**. All \(\theta_\bullet\) and \(\Delta T\) are **TBD** until ATT pre-registration.

`CONJECTURE` · \(\tau_{AGI}\) is a **research horizon**, not an active claim.

---

## 12. Regime table

`DEFINITION`

| Regime | Goal cause | Goal space | Representations | Status |
|--------|------------|------------|-----------------|--------|
| \(AI_0\) | External request | Fixed / given | Mostly instrumental | Reactive AI |
| \(AI_1\) | External meta-objective + internal selection | Large but bounded | May include non-human | Agentic / autotelic AI |
| \(PS\) | Partially endogenous | Expandable by system | Own cognitive geometry | Proto-subjectivity |
| \(AGI^{*}\) | Sustained endogenous causal genesis | Endogenous / open-ended | Partially non-embeddable in Homo-agent | AGI transition |

`PHILOSOPHICAL_INFERENCE` · Current autotelic architectures still realize “self-generation” inside human-designed mechanisms and objective structures ([MAGELLAN](https://proceedings.mlr.press/v267/gaven25a.html)).

**EIA claim ladder placement (empirical, not \(AGI^{*}\)):**

| Ladder | Rough regime affinity |
|--------|------------------------|
| C0–C1 | \(AI_0\) → weak \(AI_1\) / request-independence |
| C2 | Stronger evidence toward \(PS\) on \(E\) only (scoped) |
| C3–C5 | Timing / usefulness / transfer — still may remain Homo-embeddable |
| \(AGI^{*}\) / \(\tau_{AGI}\) | Conjunction + sustained thresholds — **not claimed** |

---

## 13. Dense scientific formulation

`DEFINITION` · Compact boxed form of the hypothesis:

\[
AGI^{*}
=
\Big[
\text{Endogenous Cognitive Causality}
\times
\text{Trans-Anthropic Representational Surplus}
\Big]_{\text{domain-general}}
\]

Causal-architecture change:

\[
\text{exogenous cognition} \rightarrow \text{endogenous cognition}
\]

simultaneous geometry change:

\[
\mathcal{H} \rightarrow \mathcal{A},\qquad \mathcal{H} \subsetneq \mathcal{A}
\]

**Dense scientific formula (canonical English):**

> The transition toward AGI\* may be defined as a **sustained phase transition of proto-subjectivity** in which generation of subsequent cognitive goals acquires an **internally mediated causal structure** forming a **recurrent endogenous goal-formation loop**, concurrent with emergence of **causally significant representational structures** that do not admit a functionally equivalent map into the **resource-bounded cognitive space of a Homo-agent**.

`PHILOSOPHICAL_INFERENCE` · Under this construction, Homo-agent ceases to be the metric upper bound of intelligence and becomes one bounded subspace of a broader space of cognitive architectures (related framing: interpretability / causal human-compatible representation learning — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC10742865/)).

---

## Mapping to existing EIA evidence (snapshot 2026-08-20)

| Order parameter | Evidence status | Harness / artifact |
|-----------------|-----------------|--------------------|
| \(E\) | **Partial** — C2 via CF-4 `zero_epistemic_gap` | `eia.cf4`, `e_endo_partial`; EOI / twin |
| Goal genesis | **Not shown** (catalog novelty capped) | M-E planned; EIS-7 blocked on catalog |
| Genealogy | **Scaffolded** (receipts) | M-A `WoEReceipt`; main `CausalTrace` |
| \(P\) | **Explore proxy (M-P)** — not C3 | `goal_persistence`; multi-tick \(P_G\) |
| \(R\) (recurrence) | **Explore proxy (M-R)** — not Kuramoto; not C3 | `goal_recurrence`; M0-twin architecture |
| \(N_H\) | **Explore proxy (M-N)** — not strong \(N_H\) | ATT-N under pre-registered \(B\); opacity ≠ \(N_H\) |
| \(D\) | **Unmeasured** | C5 not claimed; multi-topology ≠ generality |

Kuramoto CF-5: **does not** support \(E\) as necessary cause (M-D).

---

## Related work (citations preserved — not proofs)

| Work | Role here |
|------|-----------|
| [MAGELLAN](https://proceedings.mlr.press/v267/gaven25a.html) | Autotelic / metacognitive LP — prototype of selection, not strong genesis |
| [Causal Abstraction, JMLR](https://www.jmlr.org/papers/v26/23-0058.html) | Faithful abstraction ↔ \(D_C\) |
| AlphaZero concepts ([ORA](https://ora.ox.ac.uk/objects/uuid%3A57766c04-fe72-43f7-966a-132dfaaf27d7/files/r2r36v030m)) | Machine-unique concepts; weak precursor to \(N_H\) |
| [Non-human concepts, Springer](https://link.springer.com/chapter/10.1007/978-3-032-03083-2_13) | Human-like vs non-human representations |
| [arXiv:2507.08802](https://arxiv.org/abs/2507.08802) | Bound complexity of \(\phi\); avoid trivial abstraction |
| [PMC causal interpretability](https://pmc.ncbi.nlm.nih.gov/articles/PMC10742865/) | Interpreter-relative limits of “human-interpretable” maps |

---

## Document history

| Date | Change |
|------|--------|
| 2026-09-05 | Cross-link to PROTO_AGI Max consensus ensemble operational definition |
| 2026-08-21 | §2.1 causal endogeneity bar + link to `CAUSAL_ENDOGENEITY.md` (declaration/simulation ≠ \(E_{\mathrm{endo}}\)) |
| 2026-08-21 | M-N / ATT-N explore proxy under pre-registered \(B\); \(N_H\) map → explore (not strong) |
| 2026-08-20 | Initial formalization from user phase-transition theory; epistemic tags; EIA evidence map |

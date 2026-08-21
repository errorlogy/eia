# AGI\* Criterion — Formal Research Note

**Status:** Adopted into EIA sci-flow (2026-08-20); expanded 2026-08-20  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Author framing:** Roman Kuznetsov — research@anthemium.tech  
**Production gate:** AuthenticReason remains the shipping discriminator. EIS / ECS / WoE / AGI\* measurement stay research-only.

**Expanded theory (order parameters, regimes, \(\tau_{AGI}\)):** [`AGI_PHASE_TRANSITION.md`](AGI_PHASE_TRANSITION.md)  
**Falsifiable protocol:** [`AGI_TRANSITION_TEST.md`](AGI_TRANSITION_TEST.md)  
**Primary transition metric:** $E_{\mathrm{endo}}$ (endogenous cognitive causality) — lead order parameter for transition detection; $N_H$ necessary for full $AGI^{*}$ conjunction.  
**Causal endogeneity bar:** [`CAUSAL_ENDOGENEITY.md`](CAUSAL_ENDOGENEITY.md)  
**Non-embeddability scaffold:** [`NON_EMBEDDABILITY_MEASUREMENT.md`](NON_EMBEDDABILITY_MEASUREMENT.md)

---

## Thesis

AGI arises **not** at functional equivalence of proto-subjecthood with Homo-agent, but at the transition to a regime where **both** appear simultaneously:

1. **Endogenous cognitive causality** — ability to initiate and sustain processes of goal-formation, investigation, and action from the dynamics of own internal states, not exclusively from external prompt / event / reward.

2. **Trans-anthropic representational capacity** — part of formed cognitive structures ceases to be embeddable into Homo-agent representational space without substantial loss.

### Compact form

\[
AGI^{*} = E_{\mathrm{endo}} \land C_{\mathrm{non\text{-}emb}(H)}
\]

Where:

- \(E_{\mathrm{endo}}\) = endogenous cognitive causality (order parameter \(E\) in the expanded theory)
- \(C_{\mathrm{non\text{-}emb}(H)}\) = cognitive non-embeddability relative to Homo-agent \(H\) (order parameter \(N_H\))

**Primary metric (phase transition):** \(E_{\mathrm{endo}}\) — internal-state-driven goal formation, investigation, and cognitive dynamics (not external-trigger-only). **\(N_H\)** is secondary but **required** for full \(AGI^{*}\). **Lead ATT suite:** ATT-E — causal bar in [`CAUSAL_ENDOGENEITY.md`](CAUSAL_ENDOGENEITY.md).

Supporting order parameters (not substitutes for the conjunction): \(P\) (persistence), \(R\) (endogenous recurrence / goal-formation closure), \(D\) (cross-domain applicability). Transition time \(\tau_{AGI}\) requires sustained thresholds over \(\Delta T\) — see phase-transition note.

### Dense scientific formula

> AGI is a phase transition of proto-subjecthood from exogenously conditioned functionality to endogenous cognitive causality, accompanied by emergence of a representational space strictly exceeding Homo-agent cognitive capacity.

### Dense thesis (Section 13 English)

> The transition toward AGI\* may be defined as a sustained phase transition of proto-subjectivity in which generation of subsequent cognitive goals acquires an internally mediated causal structure forming a recurrent endogenous goal-formation loop, concurrent with emergence of causally significant representational structures that do not admit a functionally equivalent map into the resource-bounded cognitive space of a Homo-agent.

Full math, epistemic tags (`DEFINITION` / `OPERATIONAL` / `CONJECTURE` / `PHILOSOPHICAL_INFERENCE`), regime table \(AI_0 \rightarrow AI_1 \rightarrow PS \rightarrow AGI^{*}\), and related-work citations: [`AGI_PHASE_TRANSITION.md`](AGI_PHASE_TRANSITION.md).

---

## Key distinctions (preserve)

| Distinction | Meaning |
|-------------|---------|
| **Endogeneity ≠ Autonomy** | \(E_{\mathrm{endo}}\) is about *causal origin* of cognitive processes (internal-state dynamics), not about unconstrained action, tool use, or lack of governors. |
| **Description / simulation / declaration ≠ \(E_{\mathrm{endo}}\)** | Self-ascription, roleplay, or “I am autonomous” text without \(do(Z)\) trajectory change under non-triggering \(X\) does **not** establish endogeneity. See [`CAUSAL_ENDOGENEITY.md`](CAUSAL_ENDOGENEITY.md). |
| **Opacity ≠ non-embeddability** | Unreadable activations without causal \(\Delta P(A\mid z)>0\) and bounded-\(\phi\) loss do **not** establish \(C_{\mathrm{non\text{-}emb}(H)}\). |
| **Opacity ≠ causation** | Opaque internals without measurable \(\Delta P(G\mid do(Z))\) do **not** establish \(E_{\mathrm{endo}}\). |
| **Trans-Human Cognition ≠ superhuman task performance** | \(C_{\mathrm{non\text{-}emb}(H)}\) / \(N_H\) is about *representational non-embeddability*, not higher scores on human benchmarks, latency, or capability ladders that remain fully human-interpretable. |
| **Corrigibility ≠ persistence** | Goal persistence without re-prompting (\(P\)) is separate from resistance to correction. |

Neither conjunct alone is AGI\*. High task performance without endogeneity is not AGI\*. Endogenous causality with fully Homo-embeddable representations is not AGI\*.

---

## Mapping to EIA claim ladder (C0–C5)

The C-ladder remains an **empirical milestone ladder toward AGI\***, not a declaration of AGI\*. \(AGI^{*}\) / \(\tau_{AGI}\) is a **research horizon**.

| Level | Empirical content | Relation to AGI\* |
|-------|-------------------|-------------------|
| **C0** | Code behavior: simulator emits intent | Prerequisite only |
| **C1** | Proximal request independence (CF-1) | Weak / partial evidence for \(E_{\mathrm{endo}}\) (prompt-independence ≠ full endogenous causality) |
| **C2** | Internal-state causation (CF-4 named factors) | Stronger empirical support for \(E_{\mathrm{endo}}\) under intervention; **still not** \(AGI^{*}\) |
| **C3** | Emergent timing vs cron / rule | Timing structure of \(E_{\mathrm{endo}}\) / \(P\); not \(C_{\mathrm{non\text{-}emb}(H)}\) |
| **C4** | Human usefulness (MVP-1 shadow) | Deployment / product evidence; orthogonal to AGI\* conjunction |
| **C5** | Cross-domain generalization | Transfer of \(E_{\mathrm{endo}}\)-like behavior (\(D\) affinity); still may be Homo-embeddable |

**Active ceiling (2026-08-20):** **C2** via CF-4 (`zero_epistemic_gap`). This supports a **partial** claim on \(E_{\mathrm{endo}}\) (named internal-state causation of WoE first-passage). It does **not** establish \(C_{\mathrm{non\text{-}emb}(H)}\) and does **not** authorize claiming \(AGI^{*}\).

\[
\text{C2} \;\Rightarrow\; \text{evidence for } E_{\mathrm{endo}}\text{ (scoped)}
\qquad
AGI^{*} \;\Leftarrow\; E_{\mathrm{endo}} \land C_{\mathrm{non\text{-}emb}(H)}
\quad\text{(sustained; see }\tau_{AGI}\text{)}
\]

ATT map: [`AGI_TRANSITION_TEST.md`](AGI_TRANSITION_TEST.md) (ATT-E ↔ CF-4; ATT-N ↔ M-N; …).

---

## Measurement tracks

| Conjunct / parameter | Current status | Next work |
|----------------------|----------------|-----------|
| \(E_{\mathrm{endo}}\) / \(E\) | CF-4 C2 claimed (epistemic-gap core); AuthenticReason + EOI on main | Strengthen via M0-twin motives, M-E novelty, ATT-E continuous index |
| Goal genesis / genealogy / \(P\) / \(R\) | Partial scaffolds | ATT-G, ATT-C, ATT-P, ATT-R |
| \(C_{\mathrm{non\text{-}emb}(H)}\) / \(N_H\) | Not measured | [`NON_EMBEDDABILITY_MEASUREMENT.md`](NON_EMBEDDABILITY_MEASUREMENT.md); ATT-N |
| \(D\) | Not measured | ATT-D / C5 prep |

---

## Overclaim ban

- Do **not** equate C2, EIS-6/7, WoE intent, Kuramoto \(R\), or Telegram contact with \(AGI^{*}\).
- Do **not** treat autonomy, tool use, or benchmark SOTA as \(C_{\mathrm{non\text{-}emb}(H)}\).
- Do **not** treat opacity as non-embeddability.
- Do **not** treat self-description, simulation, or declaration of agency as \(E_{\mathrm{endo}}\).
- AuthenticReason remains the **production** gate; AGI\* criteria are **research classification** only.

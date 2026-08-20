# AGI\* Criterion — Formal Research Note

**Status:** Adopted into EIA sci-flow (2026-08-20)  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Author framing:** Roman Kuznetsov — research@anthemium.tech  
**Production gate:** AuthenticReason remains the shipping discriminator. EIS / ECS / WoE / AGI\* measurement stay research-only.

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

- \(E_{\mathrm{endo}}\) = endogenous cognitive causality
- \(C_{\mathrm{non\text{-}emb}(H)}\) = cognitive non-embeddability relative to Homo-agent \(H\)

### Dense scientific formula

> AGI is a phase transition of proto-subjecthood from exogenously conditioned functionality to endogenous cognitive causality, accompanied by emergence of a representational space strictly exceeding Homo-agent cognitive capacity.

### Dense thesis

> AGI begins where proto-subjecthood acquires endogenous cognitive causality and forms representational / inference structures for which Homo-agent ceases to be a sufficient cognitive carrier.

---

## Key distinctions (preserve)

| Distinction | Meaning |
|-------------|---------|
| **Endogeneity ≠ Autonomy** | \(E_{\mathrm{endo}}\) is about *causal origin* of cognitive processes (internal-state dynamics), not about unconstrained action, tool use, or lack of governors. |
| **Trans-Human Cognition ≠ superhuman task performance** | \(C_{\mathrm{non\text{-}emb}(H)}\) is about *representational non-embeddability*, not higher scores on human benchmarks, latency, or capability ladders that remain fully human-interpretable. |

Neither conjunct alone is AGI\*. High task performance without endogeneity is not AGI\*. Endogenous causality with fully Homo-embeddable representations is not AGI\*.

---

## Mapping to EIA claim ladder (C0–C5)

The C-ladder remains an **empirical milestone ladder toward AGI\***, not a declaration of AGI\*.

| Level | Empirical content | Relation to AGI\* |
|-------|-------------------|-------------------|
| **C0** | Code behavior: simulator emits intent | Prerequisite only |
| **C1** | Proximal request independence (CF-1) | Weak / partial evidence for \(E_{\mathrm{endo}}\) (prompt-independence ≠ full endogenous causality) |
| **C2** | Internal-state causation (CF-4 named factors) | Stronger empirical support for \(E_{\mathrm{endo}}\) under intervention; **still not** \(AGI^{*}\) |
| **C3** | Emergent timing vs cron / rule | Timing structure of \(E_{\mathrm{endo}}\); not \(C_{\mathrm{non\text{-}emb}(H)}\) |
| **C4** | Human usefulness (MVP-1 shadow) | Deployment / product evidence; orthogonal to AGI\* conjunction |
| **C5** | Cross-domain generalization | Transfer of \(E_{\mathrm{endo}}\)-like behavior; still may be Homo-embeddable |

**Active ceiling (2026-08-20):** **C2** via CF-4 (`zero_epistemic_gap`). This supports a **partial** claim on \(E_{\mathrm{endo}}\) (named internal-state causation of WoE first-passage). It does **not** establish \(C_{\mathrm{non\text{-}emb}(H)}\) and does **not** authorize claiming \(AGI^{*}\).

\[
\text{C2} \;\Rightarrow\; \text{evidence for } E_{\mathrm{endo}}\text{ (scoped)}
\qquad
AGI^{*} \;\Leftarrow\; E_{\mathrm{endo}} \land C_{\mathrm{non\text{-}emb}(H)}
\]

---

## Measurement tracks

| Conjunct | Current status | Next work |
|----------|----------------|-----------|
| \(E_{\mathrm{endo}}\) | CF-4 C2 claimed (epistemic-gap core); AuthenticReason + EOI on main | Strengthen via M0-twin motives, M-E novelty, CF-3/CF-2 as needed |
| \(C_{\mathrm{non\text{-}emb}(H)}\) | Not measured | Research-doc scaffold: [`NON_EMBEDDABILITY_MEASUREMENT.md`](NON_EMBEDDABILITY_MEASUREMENT.md) |

---

## Overclaim ban

- Do **not** equate C2, EIS-6/7, WoE intent, Kuramoto \(R\), or Telegram contact with \(AGI^{*}\).
- Do **not** treat autonomy, tool use, or benchmark SOTA as \(C_{\mathrm{non\text{-}emb}(H)}\).
- AuthenticReason remains the **production** gate; AGI\* criteria are **research classification** only.

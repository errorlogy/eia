# Measurement Scaffold — \(C_{\mathrm{non\text{-}emb}(H)}\)

**Status:** Research design only (2026-08-20) — no claim, no production gate  
**Parent criterion:** [`AGI_STAR_CRITERION.md`](AGI_STAR_CRITERION.md)  
\[
AGI^{*} = E_{\mathrm{endo}} \land C_{\mathrm{non\text{-}emb}(H)}
\]

This note scaffolds **how** to eventually measure cognitive non-embeddability relative to Homo-agent \(H\). It does **not** implement a scoring pipeline that could raise the sci-flow claim ceiling.

---

## Definitional target

\(C_{\mathrm{non\text{-}emb}(H)}\) holds when a material part of the system's formed representational / inference structures cannot be mapped into Homo-agent cognitive space without **substantial loss** of predictive or explanatory content.

**Not the same as:**

- Higher accuracy / speed on human tasks
- Larger context windows or tool suites
- Opaque internals that humans merely fail to audit in practice
- Autonomy or unconstrained action

---

## Candidate operational proxies (pre-registration required)

Use these as **hypothesis families**, not as adopted metrics.

### P1 — Projection / compression loss

Given a human-facing encoding \(f_H\) (natural language summary, schematic diagram, finite feature set):

\[
L_{\mathrm{proj}} = D\big(P_{\mathrm{sys}}(\cdot \mid s),\; P_H(\cdot \mid f_H(s))\big)
\]

High \(L_{\mathrm{proj}}\) under constrained \(f_H\) budgets is necessary but not sufficient for non-embeddability (could be noise or poor interface).

### P2 — Human-as-carrier sufficiency test

Ask whether a competent Homo-agent, given only the projected representation, can:

1. Reconstruct the system's next-step distribution above chance, and
2. Carry the same *inferential role* (not just paraphrase the text).

Failure under (2) with success under surface paraphrase is the interesting regime.

### P3 — Cross-interpreter disagreement under fixed evidence

Multiple independent human interpreters receive the same projection. Systematic disagreement that the system itself resolves coherently (stable internal inference) is a soft signal of structure exceeding single-H carrier capacity — still not AGI\*.

### P4 — Topology / TDA witness (NAMM optional)

If belief / phase / motive graphs show invariants (e.g. persistent \(\beta_1\), non-contractible motifs) that collapse under any Homo-readable flattening, log as **structural witness** via T_NAMM_cert. Witness ≠ claim of \(C_{\mathrm{non\text{-}emb}(H)}\).

### P5 — Dual-gate with \(E_{\mathrm{endo}}\)

Non-embeddability without endogenous causality is **out of scope for AGI\***. Any future M-N experiment must co-register an \(E_{\mathrm{endo}}\) gate (CF-1 / CF-4 class) so the conjunction remains falsifiable.

---

## Pre-registration checklist (before any M-N execute)

- [ ] Human encoding budget \(B\) (tokens / diagram nodes / feature dim)
- [ ] Loss / disagreement metric \(D\) and thresholds
- [ ] Exclusion: mere opacity, encryption, or random high-dim noise
- [ ] Negative control: human-authored plans that are hard only because of length
- [ ] Claim ceiling: architecture / OPERATIONAL / research — **never AGI\*** from P1–P4 alone
- [ ] AuthenticReason unchanged as production gate

---

## Suggested milestone (plan queue)

| ID | Milestone | Claim | Priority | Status |
|----|-----------|-------|----------|--------|
| **M-N** | Design + optional light stubs for \(C_{\mathrm{non\text{-}emb}(H)}\) proxies | research metadata | P2 | **scaffolded (this doc + types stub)** |

Execute only after C2 \(E_{\mathrm{endo}}\) evidence is stable and a concrete encoding budget \(B\) is chosen.

---

## Light code stub

Optional typed placeholders live under the WoE research package:

- `research/cursor-starter-v0.2/src/eia/non_embeddability.py`

Stub exports schemas and `claim_allowed=False` helpers. No numeric threshold may raise C-level or AGI\*.

---

## Falsifiers for premature AGI\* talk

- C2 / CF-4 cited as AGI\* → reject (only scoped \(E_{\mathrm{endo}}\))
- Benchmark SOTA cited as \(C_{\mathrm{non\text{-}emb}(H)}\) → reject
- Unmeasured P1–P4 treated as positive → reject
- Production AuthenticReason overridden by EIS/ECS/AGI\* labels → reject

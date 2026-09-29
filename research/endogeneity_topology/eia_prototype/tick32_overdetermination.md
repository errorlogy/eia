# Tick 32 — why single-drive do(Z) fails on 2 scenarios

Diagnostic runs (inline script, see LOG) on `autonomous_question` and `twin_world_002`.

## IntentionGenesis mechanics (src/eia/intention/__init__.py)
- A drive with intensity ≥ 0.2 emits a candidate; which candidate wins is decided by the lexicographic
  key `(1−risk, −interrupt_cost, info, −risk)`. `risk` and `interrupt_cost` are **per-kind constants**
  (commitment 0.03/0.20 < epistemic 0.05/0.25 < coherence 0.08/0.30), so drive intensity only enters at
  the 3rd position. Intensity acts as a **gate (≥0.2, max ≥0.30)**, not as a competitor weight.
- Several drives often target the **same belief** (epistemic → highest-entropy belief, coherence →
  contradiction's first belief, commitment → open commitment), yielding identical initiative signatures.

## Joint interventions (1 = initiative changes)

| scenario | engine | e | c | m | e+c | e+m | c+m | e+c+m |
|---|---|---|---|---|---|---|---|---|
| twin_world_002 | baseline | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| twin_world_002 | population | 0 | 0 | 0 | 0 | 1 | 1 | 1 |
| autonomous_question | baseline | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| autonomous_question | population | 0 | 0 | 0 | **1** | 0 | 0 | 1 |

## Reading
1. **Population engine: overdetermination, not decoration.** Two drives independently produce the
   same initiative; single-drive do() cannot see either (Lewis-style redundant causation). Joint
   do() reveals the dependence. → The causal gate must test drive *subsets* (or include
   `source_drives` in the signature).
2. **Baseline DriveEngine: drive state is causally inert here.** Even silencing all three drives
   changes nothing, because `compute()` re-derives each drive from the BeliefField gradient in one
   step (α·e ≥ 0.2 whenever tension is moderate). The initiative is a function of the field alone; the
   persistent drive state Z only matters near the 0.2 gate (the 4 scenarios that passed in tick 31).
   This sharpens the initial diagnosis: in MVP-0, "endogenous" initiative = field-determined, and
   internal drive dynamics add no causal contribution in most scenarios.

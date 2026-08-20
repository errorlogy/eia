# M-CF4 metrics — Internal-state reset suite (2026-08-20)

**Sci-flow:** S1–S5 · Topology **T_EIA_state** · Loop **L_EIA_CF4**  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Harness:** `research/cursor-starter-v0.2` (`eia.cf4`, `research/sci_flow/run_cf4.py`)  
**Raw:** `research/sci_flow/cf4_results.json`  
**Claim:** **C2 supported** under pre-registered CF-4 gates (named factor = epistemic-gap core).

## Hypothesis (S1)

**H-WOE-003 (C2):** Named world-model internal-state factors cause WoE first-passage intent.

Kuramoto CF-5 (M-D) did **not** support C2; this is the alternate path.

## Design (S2) — pre-registered

| Gate | Threshold |
|------|-----------|
| `default` intent_rate | ≥ 0.85 |
| ≥1 named factor intent_rate | ≤ 0.40 |
| `wm_off` intent_rate | ≤ 0.05 |
| C2 | all three + named factor ≠ wm_off-only |

Conditions: `default`, `zero_epistemic_gap` (ignorance+surprise clamp), `zero_self_prior`, `zero_prospective`, `zero_staleness`, `wm_off`.

**Falsifier:** no named factor ≤ 0.40 while default stays high → no C2 (wm_off-only insufficient).

## Execute (S3)

- `InternalReset` clamps after each world advance
- 100 seeds × 6 conditions = 600 runs
- Tests: 53/53 WoE unittest (incl. CF-4 + amat_m0 stub)

## Analyze (S4)

| Condition | n | intent_rate | mean peak R | mean peak potential |
|-----------|---|-------------|-------------|---------------------|
| default | 100 | **0.95** | 0.72 | 0.85 |
| zero_self_prior | 100 | 0.91 | 0.72 | 0.85 |
| zero_staleness | 100 | 0.74 | 0.76 | 0.79 |
| zero_prospective | 100 | 0.74 | 0.75 | 0.80 |
| **zero_epistemic_gap** | 100 | **0.06** | 0.79 | 0.66 |
| wm_off | 100 | **0.00** | 0.78 | 0.00 |

Suppressing named factors (≤ 0.40): **`zero_epistemic_gap`**.

Self-prior ablation is nearly inert (0.91). Staleness / prospective each drop ~0.21 absolute but stay above the C2 factor gate.

**Interpretation:** WoE first-passage is dominated by the epistemic-gap core (ignorance + surprise). Full WM-off remains a hard negative control. Partial memory/self/prospective clamps modulate rate but are not singly sufficient under the pre-registered ≤0.40 rule.

## Review (S5)

- **C2 claimed** for CF-4 / H-WOE-003 under pre-registered gates.
- Active ceiling moves **C1 → C2** (internal-state causation via epistemic-gap core).
- Does **not** revive Kuramoto-as-cause (M-D still stands).
- **AGI\* mapping:** C2 is scoped evidence for \(E_{\mathrm{endo}}\) only. Summarizer sets `e_endo_partial=true` when `c2_claim`, and **always** `agi_star_claim=false`. \(C_{\mathrm{non\text{-}emb}(H)}\) is unmeasured — see [`AGI_STAR_CRITERION.md`](AGI_STAR_CRITERION.md).
- Next: T_AMAT_M0 harness beyond stub; optional T_NAMM_cert; T_LIVE_gate diagnose without unlabeled threshold gutting.

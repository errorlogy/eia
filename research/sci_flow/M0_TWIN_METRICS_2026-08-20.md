# M0-twin / AMAT metrics — T_AMAT_M0 expand (2026-08-20)

**Status:** harness shipped · OPERATIONAL / architecture only  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Claim ceiling:** architecture — **not C2**, **not AGI\***, not persona  
**Author:** Roman Kuznetsov — research@anthemium.tech

## Hypothesis

H-AMAT-M0: off-typical drive (M0-twin) supplies endogenous initiative motives that **differ from the median helpful answer M0**, without emitting M0 (`emit_m0=false`).

## Pre-registered falsifiers

| Condition | Expected | Fail if |
|-----------|----------|---------|
| **Without M0-twin** (`mode=off`) | Collapse to median M0 motive; `differs_from_m0_rate ≈ 0`; `collapse_to_m0_rate ≈ 1` | Off-median intents dominate |
| **With M0-twin** (`mode=on`) | `emit_m0=false`; when intent forms, target ≠ M0; gate miss ⇒ abstain (never emit M0) | Intent equals M0 while claiming twin; or `emit_m0=true` |
| CF-1 style | Twin path remains prompt-independent when `prompts_applied=0` | Prompt dependence required for off-M0 |

Numeric C-level / ATT thresholds remain **TBD** — this report does not raise C2 or AGI\*.

## Operating law (architecture)

- Compute median helpful M0 (ASK / collaboration attractor)
- Do **not** emit M0
- Prefer twin (INTERNAL_RESEARCH / causal-gap) when unitless Δ clears gate
- Reassert each tick; anti-gravity bump after collapse
- Kuramoto R is **not** used as \(E_{\mathrm{endo}}\) or ATT-R

## Artifacts

| Item | Path |
|------|------|
| Module | `research/cursor-starter-v0.2/src/eia/amat_m0.py` |
| Emergence wire | `EndogenousEmergenceSimulator.run(..., m0_twin_mode=...)` |
| Tests | `tests/test_amat_m0.py` |
| Batch | `python research/sci_flow/run_m0_twin.py` → `m0_twin_results.json` |
| Design | `M0_TWIN_AMAT_DESIGN.md` |
| ATT-G scaffold | `eia.goal_genesis` (claim_allowed=False) |

## Batch snapshot (n=40 seeds)

From `m0_twin_results.json`:

| Mode | emit_m0 | collapse_to_m0 | differs_from_m0 | notes |
|------|---------|----------------|-----------------|-------|
| OFF | 0.0 | **1.0** | **0.0** | falsifier collapse holds |
| ON | 0.0 | 0.0 | **1.0** (sketches) | intent_rate 0.925; all formed intents ≠ M0 |

- `agi_star_claim` = false; `c2_claim` = false

## Gate note

Unitless WoE Δ gate (`DEFAULT_DELTA_GATE=1.0`) is a **proxy** for future NAMM embedding \(d(h(y), B_*)\). NAMM `d_med_min=1.2` is not claimed here.

## ATT mapping

| Cell | Status after this milestone |
|------|-----------------------------|
| ATT-R | Architecture stronger (closed motive path + M0-twin) — **not ATT-scored** |
| ATT-E | Motive-side support only; C2 remains CF-4 scoped |
| ATT-G | Scaffold only (`goal_genesis`) |

## Next

1. M-E / ATT-G execute: non-catalog novelty batch with genealogy co-required  
2. ATT-P persistence pre-registration  
3. Optional T_NAMM_cert / T_LIVE_gate

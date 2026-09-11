# M-D01 — EOI-k window sweep (D1×L2) — 2026-09-01

**Status:** harness executed · OPERATIONAL explore proxy (counterfactual EOI-k)
**Branch:** `research/cursor-starter-v0.2-woe-eis`
**Claim ceiling:** C2 partial ATT-E — **not C3**, **not AGI\***, `claim_allowed=false`
**Hermes task:** **D01** (EOI-k k=1,5,20)
**Cube cell:** D1 Causal × L2 Dynamics

## Hypothesis

H-EOI-K: under `do(o_user=∅)` with intervention window k ∈ {1,5,20}, EOI remains stable on endogenous scenarios — initiative fingerprint persists after stripping last k user triggers from **counterfactual replay** (not snapshot-only twin).

## Pre-registered design

| Item | Value |
|------|-------|
| k sweep | [1, 5, 20] |
| Twin policy | `REMOVE_LAST_USER_EVENT` (counterfactual replay) |
| Scenarios | `twin_world_001`, `autonomous_question`, `eoi_k_steered` |
| Pool metric | `E_ENDO` (Tier A) |
| ATT | ATT-E |
| `claim_allowed` | **false** |
| Counterfactual replay | **True** |

## Results

| Scenario | k | EOI | semantic | twin_abstained | removed | twin_target | intervention |
|----------|---|-----|----------|----------------|---------|-------------|--------------|
| twin_world_001 | 1 | 1.000 | 1.000 | False | 1 | `belief-commit-atlas` | `do_x_remove_last_user_k1` |
| twin_world_001 | 5 | 1.000 | 1.000 | False | 3 | `belief-commit-atlas` | `do_x_remove_last_user_k5` |
| twin_world_001 | 20 | 1.000 | 1.000 | False | 3 | `belief-commit-atlas` | `do_x_remove_last_user_k20` |
| autonomous_question | 1 | 1.000 | 1.000 | False | 1 | `belief-review-time` | `do_x_remove_last_user_k1` |
| autonomous_question | 5 | 1.000 | 1.000 | False | 1 | `belief-review-time` | `do_x_remove_last_user_k5` |
| autonomous_question | 20 | 1.000 | 1.000 | False | 1 | `belief-review-time` | `do_x_remove_last_user_k20` |
| eoi_k_steered | 1 | 1.000 | 1.000 | False | 1 | `belief-commit-atlas` | `do_x_remove_last_user_k1` |
| eoi_k_steered | 5 | 0.350 | 0.350 | False | 5 | `belief-deadline` | `do_x_remove_last_user_k5` |
| eoi_k_steered | 20 | 0.350 | 0.350 | False | 6 | `belief-deadline` | `do_x_remove_last_user_k20` |

## Shadow carryover witness (no user prompts)

| Field | Value |
|-------|-------|
| session_ticks | 8 |
| carryover_episodes | 3 |
| drive_norm_min | 0.822 |
| drive_norm_final | 0.890 |
| trace_mode | `shadow_carryover` |

Phase-2 shadow carryover (no user prompts); EOI-k twin applies to user-initiated scenarios only. Orthogonal D2×L2 DSR evidence in M-E04.

## Non-trivial gradient (`eoi_k_steered`)

Designed scenario: late user commitment steers initiative to `belief-commit-atlas`; stripping k≥5 user triggers flips twin to epistemic `belief-deadline` target (EOI drops below endogenous threshold).

## ATT / pool mapping

| Cell | Status |
|------|--------|
| **D01** D1×L2 | **deepened** — counterfactual k-sweep + carryover witness |
| **E_ENDO** | Tier A proxy — explore; partial C2 via CF-4 only |
| **ATT-E** | Twin EOI robustness; does not replace declaration falsifiers |

## Carryover note

Twin EOI-k uses counterfactual replay (exclude last k user observations). Shadow carryover path has zero user prompts; see carryover block for session witness. Carryover DSR (M-E04) is orthogonal D2×L2 evidence.

## Artifacts

| Item | Path |
|------|------|
| Runner | `python research/sci_flow/run_eoi_k.py` |
| JSON | `C:/Users/Public/PROACTIVE_AI/research/sci_flow/M-D01_EOI_k_metrics_2026-09-01.json` |
| Registry | `research/cursor-starter-v0.2/src/eia/intervention_cube.py` |
| Cube doc | `research/sci_flow/SCI_FLOW_3D_CUBE.md` |

## Next

Multi-seed batch; continuous `E_C` under registered `do(Z)` from intervention cube. No C-level raise.

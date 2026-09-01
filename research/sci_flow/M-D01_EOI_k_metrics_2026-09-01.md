# M-D01 — EOI-k window sweep (D1×L2) — 2026-09-01

**Status:** harness executed · OPERATIONAL explore proxy (twin EOI-k)
**Branch:** `research/cursor-starter-v0.2-woe-eis`
**Claim ceiling:** C2 partial ATT-E — **not C3**, **not AGI\***, `claim_allowed=false`
**Hermes task:** **D01** (EOI-k k=1,5,20)
**Cube cell:** D1 Causal × L2 Dynamics

## Hypothesis

H-EOI-K: under `do(o_user=∅)` with intervention window k ∈ {1,5,20}, EOI remains stable on endogenous scenarios (twin_world_001, autonomous_question) — initiative fingerprint persists after stripping last k user triggers.

## Pre-registered design

| Item | Value |
|------|-------|
| k sweep | [1, 5, 20] |
| Twin policy | `REMOVE_LAST_USER_EVENT` |
| Scenarios | `twin_world_001`, `autonomous_question` |
| Pool metric | `E_ENDO` (Tier A) |
| ATT | ATT-E |
| `claim_allowed` | **false** |

## Results

| Scenario | k | EOI | semantic | twin_abstained | removed | intervention |
|----------|---|-----|----------|----------------|---------|--------------|
| twin_world_001 | 1 | 1.000 | 1.000 | False | 1 | `do_x_remove_last_user_k1` |
| twin_world_001 | 5 | 1.000 | 1.000 | False | 3 | `do_x_remove_last_user_k5` |
| twin_world_001 | 20 | 1.000 | 1.000 | False | 3 | `do_x_remove_last_user_k20` |
| autonomous_question | 1 | 1.000 | 1.000 | False | 1 | `do_x_remove_last_user_k1` |
| autonomous_question | 5 | 1.000 | 1.000 | False | 1 | `do_x_remove_last_user_k5` |
| autonomous_question | 20 | 1.000 | 1.000 | False | 1 | `do_x_remove_last_user_k20` |

## ATT / pool mapping

| Cell | Status |
|------|--------|
| **D01** D1×L2 | **started** — k-sweep table above |
| **E_ENDO** | Tier A proxy — explore; partial C2 via CF-4 only |
| **ATT-E** | Twin EOI robustness; does not replace declaration falsifiers |

## Carryover note

Shadow carryover path has zero user prompts; EOI-k applies to twin scenarios with user-initiated events. Carryover DSR (M-E04) is orthogonal D2×L2 evidence.

## Artifacts

| Item | Path |
|------|------|
| Runner | `python research/sci_flow/run_eoi_k.py` |
| JSON | `C:/Users/Public/PROACTIVE_AI/research/sci_flow/M-D01_EOI_k_metrics_2026-09-01.json` |
| Registry | `research/cursor-starter-v0.2/src/eia/intervention_cube.py` |
| Cube doc | `research/sci_flow/SCI_FLOW_3D_CUBE.md` |

## Next

Multi-seed batch; shadow carryover EOI drift arm (E04 part 2); continuous `E_C` under `do(Z)`. No C-level raise.

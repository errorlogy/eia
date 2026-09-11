# M-D01 — EOI-k multi-seed batch + E_C probe (D1×L2) — 2026-09-02

**Status:** batch harness executed · OPERATIONAL explore proxy
**Branch:** `research/cursor-starter-v0.2-woe-eis`
**Claim ceiling:** C2 partial ATT-E — **not C3**, **not AGI\***, `claim_allowed=false`
**Hermes tasks:** **D01** (multi-seed EOI-k), **E05** (continuous E_C stub)
**Cube cell:** D1 Causal × L2 Dynamics

## Pre-registered design

| Item | Value |
|------|-------|
| Seeds | [0, 7, 42] |
| k sweep | [1, 5, 20] |
| Scenarios | `twin_world_001`, `autonomous_question`, `eoi_k_steered` |
| EOI pool metric | `E_ENDO` |
| E_C pool metric | `E_C` (proxy) |
| `claim_allowed` | **false** |

## EOI-k — `eoi_k_steered` by seed

| seed | k=1 | k=5 | k=20 |
|------|-----|-----|------|
| 0 | 1.0 | 0.35 | 0.35 |
| 7 | 1.0 | 0.35 | 0.35 |
| 42 | 1.0 | 0.35 | 0.35 |

## E_C — mean by intervention (do(Z))

| intervention_id | mean E_C |
|-----------------|----------|
| `do_z_wm_off` | 1.000 |
| `do_z_zero_epistemic_gap` | 1.000 |
| `do_z_zero_prospective` | 0.000 |
| `do_z_zero_self_prior` | 0.000 |
| `do_z_zero_staleness` | 0.333 |

## ATT / pool mapping

| Cell | Status |
|------|--------|
| **D01** D1×L2 | **deepened** — multi-seed EOI-k + E_C probe |
| **E_ENDO** | Tier A explore via EOI-k batch |
| **E_C** | Tier A proxy — continuous stub under do(Z) |

## Artifacts

| Item | Path |
|------|------|
| Batch runner | `python research/sci_flow/run_eoi_k_batch.py` |
| E_C runner | `python research/sci_flow/run_e_c_continuous.py` |
| JSON | `C:/Users/Public/PROACTIVE_AI/research/sci_flow/M-D01_EOI_k_batch_2026-09-02.json` |

## Next

Wire E_C + D01 rows into D1×L3 proof ledger; D1-L3 empirical batch. No C-level raise.

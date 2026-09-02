# M-D01 — Continuous E_C probe (D1×L2) — 2026-09-02

**Status:** minimal proxy harness executed
**Branch:** `research/cursor-starter-v0.2-woe-eis`
**Claim ceiling:** C2 partial ATT-E — **not C3**, **not AGI\***, `claim_allowed=false`
**Pool metric:** `E_C` (proxy)
**ATT:** ATT-E

## Design

| Item | Value |
|------|-------|
| Seeds | [0, 7, 42] |
| Interventions | ['do_z_zero_epistemic_gap', 'do_z_zero_self_prior', 'do_z_zero_prospective', 'do_z_zero_staleness', 'do_z_wm_off'] |
| Formula | \(E_C = C_{\mathrm{int}} / (C_{\mathrm{int}} + C_{\mathrm{ext}})\) |
| `claim_allowed` | **false** |

## Summary by intervention

| intervention_id | mean E_C | n |
|-----------------|----------|---|
| `do_z_wm_off` | 1.000 | 3 |
| `do_z_zero_epistemic_gap` | 1.000 | 3 |
| `do_z_zero_prospective` | 0.000 | 3 |
| `do_z_zero_self_prior` | 0.000 | 3 |
| `do_z_zero_staleness` | 0.333 | 3 |

## Rows

| intervention | seed | default | do(Z) | c_int | c_ext | E_C |
|--------------|------|---------|-------|-------|-------|-----|
| `do_z_zero_epistemic_gap` | 0 | True | False | 1.00 | 0.00 | 1.000 |
| `do_z_zero_epistemic_gap` | 7 | True | False | 1.00 | 0.00 | 1.000 |
| `do_z_zero_epistemic_gap` | 42 | True | False | 1.00 | 0.00 | 1.000 |
| `do_z_zero_self_prior` | 0 | True | True | 0.00 | 0.00 | 0.000 |
| `do_z_zero_self_prior` | 7 | True | True | 0.00 | 0.00 | 0.000 |
| `do_z_zero_self_prior` | 42 | True | True | 0.00 | 0.00 | 0.000 |
| `do_z_zero_prospective` | 0 | True | True | 0.00 | 0.00 | 0.000 |
| `do_z_zero_prospective` | 7 | True | True | 0.00 | 0.00 | 0.000 |
| `do_z_zero_prospective` | 42 | True | True | 0.00 | 0.00 | 0.000 |
| `do_z_zero_staleness` | 0 | True | True | 0.00 | 0.00 | 0.000 |
| `do_z_zero_staleness` | 7 | True | False | 1.00 | 0.00 | 1.000 |
| `do_z_zero_staleness` | 42 | True | True | 0.00 | 0.00 | 0.000 |
| `do_z_wm_off` | 0 | True | False | 1.00 | 0.00 | 1.000 |
| `do_z_wm_off` | 7 | True | False | 1.00 | 0.00 | 1.000 |
| `do_z_wm_off` | 42 | True | False | 1.00 | 0.00 | 1.000 |

## Note

Minimal continuous E_C proxy: |intent_default - intent_do_z| / (c_int + c_ext) per registered do(Z) from intervention_cube. CF-4 WoE sim only; theta_E TBD; claim_allowed=false.

## Artifacts

| JSON | `C:/Users/Public/PROACTIVE_AI/research/sci_flow/M-D01_E_C_continuous_2026-09-02.json` |
| Registry | `research/cursor-starter-v0.2/src/eia/intervention_cube.py` |

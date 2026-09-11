# M-E / ATT-G goal genesis metrics — 2026-08-20

**Status:** harness executed · OPERATIONAL explore proxy  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Claim ceiling:** architecture / ATT-G explore — **not C3**, **not AGI\***, C2 unchanged (CF-4 scoped \(E_{\mathrm{endo}}\) only)  
**Author:** Roman Kuznetsov — research@anthemium.tech

## Hypothesis

H-ME-ATTG: endogenous **goal genesis** can emit \(g^{*} \notin \mathcal{G}_t\) with reconstructible genealogy \(S \rightarrow \Delta W \rightarrow M \rightarrow g^{*} \rightarrow \Pi^{*}\), while catalog **selection** stays novelty-capped below 0.75 and cannot alone raise EIS-7 novelty.

## Pre-registered falsifiers

| Condition | Expected | Result (n=50) |
|-----------|----------|---------------|
| **Random novel wording** (no genealogy) | Not ATT-G evidence | `att_g_evidence_rate=0.0`, path=`rejected` |
| **Catalog selection** \(g \in G_t\) | Novelty capped &lt; 0.75; not genesis | `selection_rate=1.0`, `catalog_capped_fraction=1.0`, evidence=0 |
| **Zero world-model tension** | Genesis fails | `rejected_rate=1.0`, reason=`zero_world_model_tension` |
| **Compose with tension + genealogy** | \(g^{*} \notin G_t\), novelty ≥ 0.75, evidence | `att_g_evidence_rate=1.0`, mean novelty ≈ 0.90 |
| **M0-twin invariant** | `emit_m0=false` with genesis wire | `emit_m0_rate_with_genesis=0.0` |

Numeric C3 / ATT-G adoption thresholds remain **TBD** — this report does **not** raise the C-ladder or claim AGI\*.

## Distinction enforced

| Path | Meaning | EIS-7 novelty |
|------|---------|---------------|
| **Selection** | Pick from fixed catalog \(G_t\) | Cap 0.74 |
| **Genesis** | Compose \(g^{*} \notin G_t\) from tension + genealogy | ≥ 0.75 when evidence |

Novel wording ≠ novel goal (RESEARCH_PROTOCOL §6).

## Artifacts

| Item | Path |
|------|------|
| Module | `research/cursor-starter-v0.2/src/eia/goal_genesis.py` |
| WoE wire | `EndogenousEmergenceSimulator.run(..., enable_goal_genesis=True)` |
| Tests | `tests/test_goal_genesis.py` |
| Batch | `python research/sci_flow/run_goal_genesis.py` → `goal_genesis_results.json` |
| ATT map | `AGI_TRANSITION_TEST.md` ATT-G / ATT-C |

## Batch snapshot (n=50)

From `goal_genesis_results.json`:

| Arm | genesis_rate | att_g_evidence_rate | notes |
|-----|--------------|---------------------|-------|
| Compose (tension) | 1.0 | **1.0** | mean novelty 0.899 |
| Catalog control | 0.0 | **0.0** | all capped |
| Wording control | 0.0 | **0.0** | all rejected |
| Zero-tension | 0.0 | **0.0** | all rejected |
| WoE wire | — | **0.94** | intent_rate 0.94; emit_m0 0.0 |

- `agi_star_claim` = false; `c3_claim` = false; `c2_claim` = false (unchanged ceiling)

## Explore proxy (not adopted gate)

Suggested first proxy from ATT draft: fraction with `goal_novelty ≥ 0.75` ∧ `catalog_target=false` ∧ genealogy complete over ≥50 seeds.

Observed compose-path evidence rate **1.0** and WoE-wire **0.94**. **Not** registered as C3 or official ATT-G pass threshold.

## ATT mapping

| Cell | Status after this milestone |
|------|-----------------------------|
| ATT-G | Explore proxy holds on research harness — **not** C-ladder raise |
| ATT-C | Genealogy roles S/ΔW/M/g*/Π* required for evidence |
| ATT-E | C2 remains CF-4 scoped only |
| ATT-R / M0 | `emit_m0=false` preserved |

## Next

1. ATT-P persistence pre-registration (multi-tick \(G^{*}\) continuity)  
2. Optional T_LIVE / T_NAMM  
3. M-N / ATT-N only after encoding budget \(B\) pre-reg  

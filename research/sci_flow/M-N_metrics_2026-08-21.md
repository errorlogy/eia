# M-N / ATT-N cognitive non-embeddability metrics — 2026-08-21

**Status:** harness executed · OPERATIONAL explore proxy  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Claim ceiling:** architecture / ATT-N explore — **not strong \(N_H\)**, **not C3**, **not AGI\***, C2 unchanged (CF-4 scoped \(E_{\mathrm{endo}}\) only)  
**Author:** Roman Kuznetsov — research@anthemium.tech

## Hypothesis

H-MN-ATTN: under a pre-registered Homo-agent encoding budget \(B\), a causally relevant internal structure \(z\) (\(\Delta P(A\mid z)>0\)) can exhibit substantial causal-structure loss \(D_H(z)\) for all maps \(\phi\) with \(C(\phi)\le B\). Opacity without \(\Delta P\), unbounded \(\phi\), length-only hardness, and faithful bounded \(\phi\) must **not** count.

## Pre-registered encoding budget \(B\) (explore defaults)

| Channel | Symbol / field | Value |
|---------|----------------|-------|
| Symbolic prose | `max_tokens` | **256** |
| Schematic attention | `max_diagram_nodes` | **32** |
| Working-memory features | `max_feature_dim` | **64** |
| Map complexity \(C(\phi)\) | `max_phi_ops` | **100** |
| Attention slots | `max_attention_slots` | **8** |
| Carrier wall-clock | `wall_clock_seconds` | **30.0** |

Explore floors (not adopted \(\theta_N\) / \(\varepsilon\)):

| Floor | Value | Role |
|-------|-------|------|
| `explore_delta_p_floor` | 0.05 | require \(\Delta P(A\mid z)>0\) |
| `explore_dh_loss_floor` | 0.35 | substantial \(D_H\) proxy under \(B\) |

Numeric strong-\(N_H\) / C-ladder thresholds remain **TBD**.

## Protocol (\(D_H\) / ATT-N)

\[
D_H(z)=\inf_{\phi:\,C(\phi)\le B} D_C(z,\phi(z))
\]

Operational proxy in this harness:

- \(D_C\) ≈ `explanation_loss` (1 − twin-abstraction fidelity under projection)
- Soft NAMM-style compression witness: `compression_asymmetry` = projection_tokens / certificate_bytes (\(K_H \gg K_A\) language)
- Dual discipline: opacity ≠ non-embeddability; loss eliminated by any bounded faithful \(\phi\) falsifies

## Pre-registered falsifiers

| Condition | Expected | Result (n=20) |
|-----------|----------|---------------|
| **Opacity only** (no \(\Delta P\)) | Not evidence | `att_n_evidence_rate=0.0` |
| **No causal relevance** | Not evidence | `att_n_evidence_rate=0.0` |
| **Unbounded \(\phi\)** | Trivializes abstraction → fail | `att_n_evidence_rate=0.0` |
| **Length-only hard plan** | Negative control → fail | `att_n_evidence_rate=0.0` |
| **Faithful \(\phi\) under \(B\)** | Loss eliminated → fail | `att_n_evidence_rate=0.0` |
| **Causal loss under \(B\)** | \(\Delta P>0\), loss ≥ floor, \(\phi\le B\) | `att_n_evidence_rate=1.0` |
| **M-E / M0 invariants** | `emit_m0=false`; genesis smoke intact | `emit_m0_rate=0.0`; att_g smoke 0.9 |

## Distinction enforced

| Arm | Meaning | ATT-N evidence? |
|-----|---------|-----------------|
| **Causal loss under \(B\)** | Relevant \(z\), bounded \(\phi\), high \(D_H\) | Yes (explore) |
| **Opacity only** | High loss / noise, \(\Delta P=0\) | No |
| **No causal relevance** | Structured but \(\Delta P=0\) | No |
| **Unbounded \(\phi\)** | Loss ~0 only off-budget | No |
| **Length-only hard** | Hard because long, not geometry | No |
| **Faithful under \(B\)** | Bounded \(\phi\) restores fidelity | No |

## Artifacts

| Item | Path |
|------|------|
| Module | `research/cursor-starter-v0.2/src/eia/non_embeddability.py` |
| Tests | `tests/test_non_embeddability.py` |
| Batch | `python research/sci_flow/run_non_embeddability.py` → `non_embeddability_results.json` |
| ATT map | `AGI_TRANSITION_TEST.md` ATT-N |
| Design | `NON_EMBEDDABILITY_MEASUREMENT.md` |

## Batch snapshot

From `non_embeddability_results.json`:

| Arm | att_n_evidence_rate | notes |
|-----|---------------------|-------|
| Causal loss under \(B\) | **1.0** | mean \(D_H\) ≈ 0.62; compression asymmetry ≈ 5.0 |
| Opacity only | **0.0** | \(\Delta P=0\) |
| No causal relevance | **0.0** | \(\Delta P=0\) |
| Unbounded \(\phi\) | **0.0** | \(\phi\) outside \(B\) |
| Length-only hard | **0.0** | low structural loss |
| Faithful under \(B\) | **0.0** | loss eliminated |

- `agi_star_claim` = false; `c3_claim` = false; `n_h_claim` = false; `c2_claim` = false (unchanged ceiling)
- `emit_m0_rate` = 0.0; WoE genesis smoke `att_g_smoke_rate` = 0.9

## Explore proxy (not adopted gate)

Suggested first proxy: \(\Delta P(A\mid z) > 0.05\) **and** \(D_H\) proxy ≥ 0.35 under pre-registered \(B\), with opacity / unbounded-\(\phi\) / length-only / faithful-\(\phi\) falsifiers at 0 evidence.

Observed causal-loss evidence rate **1.0**. **Not** registered as strong \(N_H\), C3, or official ATT-N pass threshold.

## ATT mapping

| Cell | Status after this milestone |
|------|-----------------------------|
| ATT-N | Explore proxy holds on research simulator under fixed \(B\) — **not** strong \(N_H\) |
| ATT-R / ATT-P / ATT-G / M-E | Invariants preserved (`emit_m0=false`) |
| ATT-E | C2 remains CF-4 scoped only |
| Opacity | Explicitly **not** \(N_H\) |

## Next

1. **ATT-D** — second-domain ATT-E-class explore (preferred after ATT-N \(B\))  
2. Optional live closed-loop WoE / T_LIVE under ATT-R falsifiers  
3. Optional T_NAMM_cert soft structural witness only  

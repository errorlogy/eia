# M-D metrics — Kuramoto coupling / delay / scramble (2026-08-18)

**Sci-flow:** S1–S5 · Milestone **M-D**  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Harness:** `research/cursor-starter-v0.2` (`eia.cf5`, `research/sci_flow/run_md.py`)  
**Raw:** `research/sci_flow/md_results.json`  
**Claim:** **C2 not claimed.** Ceiling stays **C1**.

## Hypothesis (S1)

**H-WOE-002 (C2):** Phase organization (Kuramoto coupling) is a cause of WoE intent.

## Design (S2) — pre-registered

| Gate | Threshold |
|------|-----------|
| coupled intent_rate | ≥ 0.85 |
| scramble intent_rate | ≤ 0.20 |
| K=0 intent_rate | ≤ 0.40 |
| coupled − scramble | ≥ 0.50 |

Negative controls: `scramble_phases`, `base_coupling=0` + `pressure_coupling_gain=0`.  
Secondary: sparse typed graph; delay_steps 32 and 128 (dt=0.001).  
42 Hz remains a computational carrier, not a biological claim.

**Falsifier:** scramble and/or K=0 fail to drop intent vs coupled → do **not** claim C2 (coherence may be decorative).

## Execute (S3)

- `CoherenceConfig.delay_steps`, `coupling_graph`
- `sparse_typed_graph`, `all_to_all_graph`, `permute_graph`, `k_zero_config`
- 100 seeds × 6 conditions = 600 runs
- Tests: 46/46 WoE unittest

## Analyze (S4)

| Condition | n | intent_rate | mean peak R |
|-----------|---|-------------|-------------|
| coupled | 100 | **0.95** | 0.72 |
| k0 | 100 | **0.94** | 0.68 |
| delay_32 | 100 | 0.96 | 0.67 |
| delay_128 | 100 | 0.97 | 0.69 |
| sparse | 100 | 0.98 | 0.78 |
| scramble | 100 | **0.69** | 0.88 |

Scramble delta vs coupled = **0.26** (below 0.50). K=0 delta = **0.01**.

Seed 7 scramble still blocks (unit test), but that does **not** generalize (P5 confirmed).

Scramble mean *peak* R is high because peak is a max-over-time of random phases, not a stationary order parameter.

**Interpretation:** WoE first-passage is dominated by world-model factors (pressure, goal_separation, semantic/temporal/causal terms). Kuramoto R is a weak multiplicative fit, not a necessary cause of intent. Sparse graph does not break the demo.

## Review (S5)

- **M-D executed.** C2 via CF-5 **unsupported**.
- Active ceiling remains **C1**.
- Next C2 path: **CF-4 internal reset** (zero world-model tension already blocks intent in unit tests). M-E (EIS-7) stays P2.

# Sci-Flow 3D Evidence Cube — D1 × D2 × D3

**Status:** `OPERATIONAL` scaffold (2026-09-01) — **not** an AGI\* claim  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Milestone:** M-3D-01 + M-3D-EXPRESS + M-3D-EXPRESS + M-3D-EXPRESS + M-3D-EXPRESS + M-3D-EXPRESS + M-3D-EXPRESS + M-3D-EXPRESS + M-3D-EXPRESS + M-3D-EXPRESS + M-3D-EXPRESS + M-3D-EXPRESS + M-3D-EXPRESS + M-3D-EXPRESS + M-3D-EXPRESS + M-3D-EXPRESS + M-3D-EXPRESS + M-3D-EXPRESS + M-3D-EXPRESS + M-3D-EXPRESS + M-3D-EXPRESS + M-3D-EXPRESS + M-3D-EXPRESS + M-3D-EXPRESS + M-3D-EXPRESS + M-3D-EXPRESS + M-3D-EXPRESS + M-3D-EXPRESS + M-3D-EXPRESS + M-3D-EXPRESS  
**Methodology:** [`SCI_FLOW_V3_CELL_FILLING.md`](SCI_FLOW_V3_CELL_FILLING.md) — sci-flow v3 = incremental cube cell-filling with harnesses  
**Registry:** `research/cursor-starter-v0.2/src/eia/intervention_cube.py` · [`cell_registry.yaml`](cell_registry.yaml)  
**Claim ceiling:** **C2** — scoped \(E_{\mathrm{endo}}\) / ATT-E partial only

---

## Резюме (RU)

**3D-куб эвиденции sci-flow v3** — матрица 3×3 для отслеживания прогресса по трём осям: **D1** каузальная эндогенность (\(E_{\mathrm{endo}}\)), **D2** динамика (\(\mathfrak{E}\), OMEGA, рекуррентность), **D3** граница (\(N_H\), governor, фальсификаторы). На каждой оси три слоя: **L1** инварианты, **L2** динамика, **L3** witness. Ячейки помечены filled / partial / empty. Существующая работа (Phase 2 carryover, DSR, M-EMP, OMEGA, ATT) отображена на ячейки. **D01** (EOI-k) стартует в **D1×L2**. Горизонт AGI\* = конъюнкция параметров при **C2 ceiling**; без overclaim.

---

## Axes and layers

| Axis | Symbol | Scope |
|------|--------|-------|
| **D1** Causal | \(E_{\mathrm{endo}}\), \(do(Z)\), twin \(do(X)\) | ATT-E lead suite |
| **D2** Dynamic | \(\mathfrak{E}\), OMEGA, recurrence | ATT-G/P/R, M-SE |
| **D3** Boundary | \(N_H\), governor, falsifiers | ATT-N, CF-7 |

| Layer | Role |
|-------|------|
| **L1** Invariants | Definitions, falsifier taxonomy, hard bans |
| **L2** Dynamics | Harnesses, interventions, longitudinal metrics |
| **L3** Witness | Trace receipts, JSON metrics, external certs |

---

## 9-cell matrix (status)

| | **L1 Invariants** | **L2 Dynamics** | **L3 Witness** |
|---|-------------------|-----------------|----------------|
| **D1 Causal** | **filled** — [`CAUSAL_ENDOGENEITY.md`](CAUSAL_ENDOGENEITY.md) bar, F-DECL/F-EXT | **filled** — CF-4, EOI, **D01 deepened** (counterfactual + carryover) | **filled** — [`EIA_PROOF_PROTOCOL.md`](EIA_PROOF_PROTOCOL.md), ATT-E witness stub |
| **D2 Dynamic** | **filled** — [`STABLE_ENDOGENEITY.md`](STABLE_ENDOGENEITY.md), \(\mathfrak{E}\) vector | **filled** — ATT-R/M-R-LIVE, DSR smoke, OMEGA | **filled** — M-R-LIVE JSON, ATT-R shadow witness |
| **D3 Boundary** | **filled** — [`AGI_STAR_CRITERION.md`](AGI_STAR_CRITERION.md) conjunction | **filled** — ATT-N explore + **CF-7** governor isolation | **filled** — [`D3_BOUNDARY_WITNESS.md`](D3_BOUNDARY_WITNESS.md) Tier B soft \(N_H\); no strong \(N_H\) |

Legend: **filled** = theory + falsifiers documented; **partial** = harness exists, thresholds TBD or explore-only; **empty** = not instrumented.

---

## Existing work → cells

| Work / milestone | Cube cell(s) | Notes |
|------------------|--------------|-------|
| [`CAUSAL_ENDOGENEITY.md`](CAUSAL_ENDOGENEITY.md) | D1×L1 | Primary causal bar |
| M-CF4 / `run_cf4.py` | D1×L2, D1×L3 | C2 partial via `zero_epistemic_gap` |
| **D01** EOI-k (`run_eoi_k.py`) | **D1×L2** | k=1,5,20 counterfactual + `eoi_k_steered` gradient + carryover witness |
| [`ENDOGENEITY_METRICS_POOL.md`](ENDOGENEITY_METRICS_POOL.md) | D1×L1, all tiers | `E_ENDO` Tier A |
| M-CLI-P2 carryover | D2×L2 | Shadow + StateStore hydration |
| M-E04 / D05 DSR | D2×L2 | 50-tick shadow carryover |
| M-R / M-R-LIVE | D2×L2, D2×L3 | ATT-R recurrence |
| M-O / [`OMEGA_WAVE_METRIC.md`](OMEGA_WAVE_METRIC.md) | D2×L2 | Tier C explore |
| M-N / ATT-N | D3×L2 | Explore under budget \(B\) |
| **M-D3-L2-CF7** | **D3×L2** | Paired governor-off vs governor-on under \(X^{\mathrm{trigger}}=0\) |
| D3 boundary witness (`boundary_witness_harness.py`) | **D3×L3** | Tier B soft \(N_H\); falsifier + governor + NAMM corpus |
| M-EMP pool | cross-axis | Registry YAML |

---

## Intervention registry

Typed interventions in `intervention_cube.py`:

| Kind | Examples | Axis |
|------|----------|------|
| `do(Z)` | CF-4 named resets (`zero_epistemic_gap`, …) | D1 |
| `do(O)` | CF-5 scramble, OMEGA decor | D2 |
| `do(X)` | Twin `remove_last_n` (EOI-k), ATT-N budget | D1 / D3 |

API: `get_intervention(id)`, `list_by_axis("D1"|"D2"|"D3")`, `eoi_k_interventions()`.

---

## Cross-links

| Doc | Role |
|-----|------|
| [`arxiv/sci_flow_3d_cube/main.tex`](../../arxiv/sci_flow_3d_cube/main.tex) | **I03** standalone arXiv paper (theory + empirical) |
| [`CAUSAL_ENDOGENEITY.md`](CAUSAL_ENDOGENEITY.md) | D1 causal bar |
| [`STABLE_ENDOGENEITY.md`](STABLE_ENDOGENEITY.md) | D2 stability vector |
| [`OMEGA_WAVE_METRIC.md`](OMEGA_WAVE_METRIC.md) | D2 OMEGA adjunct |
| [`ENDOGENEITY_METRICS_POOL.md`](ENDOGENEITY_METRICS_POOL.md) | Tier A–E registry |
| [`NEUROPLASTICITY_OSS_SURVEY.md`](NEUROPLASTICITY_OSS_SURVEY.md) | M-O explore: 27 OSS repos (Tier A → Neuraxon/Graphitti doc) |
| [`NEUROPLASTICITY_EIA_APPLICATION.md`](NEUROPLASTICITY_EIA_APPLICATION.md) | Tier A vendors: Neuraxon + Graphitti install/EIA map |
| [`M-O_NEURAXON_GRAPHITTI_ENDOGENEITY.md`](M-O_NEURAXON_GRAPHITTI_ENDOGENEITY.md) | M-O endogeneity factor analysis + probe (D2×L2) |
| [`PROTO_AGI_MAX_CONSENSUS.md`](PROTO_AGI_MAX_CONSENSUS.md) | 12-member proto-AGI ensemble; \(\Phi_{\max}\) + \((E,\mathrm{OMEGA},P,R)\) consensus over \(\Delta T\) |
| [`docs/CURSOR_TASKS.md`](../../docs/CURSOR_TASKS.md) | Hermes **D01** |
| [`config.yaml`](config.yaml) | Milestone M-3D-01 |
| [`SCI_FLOW_V3_CELL_FILLING.md`](SCI_FLOW_V3_CELL_FILLING.md) | v3 cell-filling methodology + rubric |
| [`cell_registry.yaml`](cell_registry.yaml) | Machine-readable cell → harness map |

---

## AGI\* horizon (no overclaim)

\(AGI^{*} = E_{\mathrm{endo}} \land C_{\mathrm{non\text{-}emb}(H)} \land \cdots\) per [`AGI_STAR_CRITERION.md`](AGI_STAR_CRITERION.md).

- Active empirical ceiling: **C2** (`config.yaml` `claim_ladder.active_ceiling`).
- Partial cube cells do **not** raise C-level.
- OMEGA / Kuramoto / DSR / EOI-k alone **never** imply \(AGI^{*}\) or \(\tau_{AGI}\).

---

## Next (M-3D-01+)

Multi-seed batch; E04 EOI drift on carryover. D3×L3 filled via boundary witness harness (Tier B soft \(N_H\); not strong \(N_H\)).
3. Continuous `E_C` under registered `do(Z)` from intervention cube.
4. **M-3D-EXPRESS** — `python research/sci_flow/run_3d_express.py` (<60s 9-cell smoke).

## Express pass (M-3D-EXPRESS)

Last run: 2026-09-01 — `1451.8` ms — `python research/sci_flow/run_3d_express.py`

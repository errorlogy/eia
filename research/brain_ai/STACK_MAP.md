# Stack Map (brief)

```
connectome adjacency (source: bundled | google_male_cns | flywire_female | synthetic)
    → brian2 LIF subgraph (optional) | synthetic spike trains (fallback)
    → per-neuron / per-band phase extraction
    → OmegaWaveState.from_carrier_phases
    → omega_metric() → OMEGA_t
    → T-BRAIN-03 shadow bridge → T-BRAIN-04 carryover
```

| Layer | Module | Tier | Source keys |
|-------|--------|------|-------------|
| Connectome | `adapters/connectome_export.py` | C | `bundled_tiny`, `google_male_cns`, `flywire_female`, `synthetic` |
| Dynamics | `adapters/brian2_lif_subgraph.py` | C | — |
| Crosswalk | `adapters/ot_injection.py` | C | — |
| Metric | `research/cursor-starter-v0.2/src/eia/oscillatory_state.py` | C | — |
| Harness T-BRAIN-01 | `harnesses/t_brain_01_connectome_ot.py` | C | default `bundled_tiny` |
| Behavior metrics | `adapters/behavior_metrics.py` | C | — |
| Harness T-BRAIN-02 | `harnesses/t_brain_02_omega_behavior.py` | C | — |
| Shadow bridge | `adapters/shadow_bridge.py` | C | T-BRAIN-03/04 |
| Harness T-BRAIN-05 | `harnesses/t_brain_05_connectome_parity.py` | C | **planned** — multi-source parity |

## Connectome source tiers

| Tier | Source | CI | Offline export |
|------|--------|----|----------------|
| 0 | `bundled_tiny` | yes | committed stub |
| 0 | `synthetic` | yes | generated in-process |
| 1 | `google_male_cns` | fallback stub | `data/google_male_subgraph.json` (gitignored) |
| 1 | `flywire_female` | fallback stub | `data/flywire_female_subgraph.json` (gitignored) |
| 2 | Full MaleCNS / FlyWire | **never in CI** | GCS / neuPrint bulk only |

No shadow multitick or ATT-R closure in T-BRAIN-01/02 MVP — observational O_t crosswalk and behavior diagnostic only. T-BRAIN-03/04 add omega-bridged shadow at X_trigger=0 (still tier C, `claim_allowed=false`).

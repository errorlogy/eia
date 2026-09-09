# Stack Map (brief)

```
connectome adjacency
    → brian2 LIF subgraph (optional) | synthetic spike trains (fallback)
    → per-neuron / per-band phase extraction
    → OmegaWaveState.from_carrier_phases
    → omega_metric() → OMEGA_t
```

| Layer | Module | Tier |
|-------|--------|------|
| Connectome | `adapters/connectome_export.py` | C |
| Dynamics | `adapters/brian2_lif_subgraph.py` | C |
| Crosswalk | `adapters/ot_injection.py` | C |
| Metric | `research/cursor-starter-v0.2/src/eia/oscillatory_state.py` | C |
| Harness | `harnesses/t_brain_01_connectome_ot.py` | C |

No shadow multitick or ATT-R closure in T-BRAIN-01 MVP — observational O_t crosswalk only.

# Connectome-Grounded EIA Brain Modeling (C2 Scoped)

**Milestone:** M-BRAIN-AI · **Harness:** T-BRAIN-06 · **Tier:** C · `claim_allowed=false`

## Honest biological scope

This strand models **Drosophila CNS connectome** substrates — not mammalian neocortex.

| Source | Dataset | Notes |
|--------|---------|-------|
| `google_male_cns` | MaleCNS v1.0 (Cell 2026, neuPrint `male-cns:v1.0`) | Google/HHMI Janelia milestone — 166k neurons, 125M synapses |
| `flywire_female` | FlyWire v783 female brain | Janelia female connectome reference |
| `bundled_tiny` / `synthetic` | CI/offline fallbacks | Deterministic subgraphs for regression |

The **neocortex-as-substrate thesis** is applied analogically: connectome structure grounds spike dynamics → OMEGA_t → EIA shadow multitick. Empirical anchor is fly CNS until zebrafish/mouse connectomics mature (Google blog roadmap).

## Pipeline mapping

```
connectome subgraph
  → spike dynamics (coupled_active | passive_quiescent)
  → OmegaWaveState / OMEGA_t + behavior metrics
  → shadow bridge at X_trigger=0 (Ψ injection tick 0 only)
  → 2-tick ShadowSessionCarryover
  → EIA proxies: genesis_Δ, EOI, ATT-R, drive_norm
```

## Endogenous vs passive comparison

| Arm | EIA baseline | Ψ(O_t) | Role |
|-----|--------------|--------|------|
| `coupled_active` | full_eia | tick 0 | Endogenous embodied proxy |
| `passive_quiescent` | reactive_only | none | Passive control |

Genesis is **behavior-gated** (activity rate proxy), not omega_t alone (F-OMEGA-DECOR).

## Claim ceiling

- **C2** — scoped observational crosswalk only
- `e_endo_support=none` — no D1 bleed
- `claim_allowed=false` — does not establish \(E_{\mathrm{endo}}\)
- Kuramoto R ≠ ATT-R endogeneity (F-KURAMOTO-AS-E)

## Limitations

1. Offline stubs when `data/` exports absent (google_male_cns, flywire_female)
2. 8-node subgraphs — not full connectome scale
3. Brian2 LIF optional; default numpy fallback
4. Genesis uniform across sources at fixed n_nodes (behavior-gated, not structure-gated yet)

## Next steps

- Real neuPrint MaleCNS / FlyWire ego-network fetch (≤500 nodes)
- Brian2 multi-source spike parity
- Structure-sensitive genesis coupling (beyond activity proxy)
- Zebrafish/mouse horizon when Google releases next connectomics tier

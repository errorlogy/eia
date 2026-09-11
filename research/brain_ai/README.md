# Brain-AI Connectome Research (M-BRAIN-AI)

Tier **C** adjunct strand: connectome subgraph → spike dynamics → `OmegaWaveState` / OMEGA_t crosswalk → EIA shadow multitick bridge.

**Claim ceiling:** C2 · `claim_allowed=false` · `agi_star_claim=false` · no D1 `e_endo_support` bleed.

## Quick start

```bash
python research/brain_ai/run_t_brain_01.py
python research/brain_ai/run_t_brain_02.py
python research/brain_ai/run_t_brain_03.py
pytest tests/test_t_brain_01_connectome_ot.py tests/test_t_brain_02_omega_behavior.py tests/test_t_brain_03_shadow_bridge.py -q
```

## Layout

| Path | Role |
|------|------|
| `harnesses/t_brain_01_connectome_ot.py` | T-BRAIN-01 payload builder |
| `harnesses/t_brain_02_omega_behavior.py` | T-BRAIN-02 OMEGA vs behavior diagnostic |
| `harnesses/t_brain_03_shadow_bridge.py` | T-BRAIN-03 OMEGA → shadow multitick bridge |
| `adapters/connectome_export.py` | Synthetic / offline connectome subgraph |
| `adapters/brian2_lif_subgraph.py` | Optional Brian2 LIF (graceful skip) |
| `adapters/behavior_metrics.py` | Activity / burstiness / sync proxies |
| `adapters/spike_arms.py` | Multi-arm spike falsifier suite |
| `adapters/ot_injection.py` | Spike phases → `OmegaWaveState` |
| `adapters/shadow_bridge.py` | Brain-AI OMEGA → shadow multitick adapter |
| `config.yaml` | Harness defaults |
| `CONNECTOME_SOURCES.md` | MaleCNS / FlyWire / offline source notes |
| `STACK_MAP.md` | Stack crosswalk (brief) |
| `data/README.md` | Offline subgraph fetch instructions |
| `harnesses/t_brain_05_connectome_parity.py` | T-BRAIN-05 multi-source parity (spec stub) |

## T-BRAIN-03 (shadow bridge)

Closes the causal gap between Brain-AI OMEGA_t and EIA shadow multitick at **X_trigger=0**:

| Arm | Role |
|-----|------|
| `coupled_active` | High activity → bridged novel G' (genesis_Δ=1) |
| `passive_quiescent` | Low activity → bridged G repeat (genesis_Δ=0) |
| `phase_scramble_control` | Matched spikes, scrambled OMEGA (F-OMEGA-DECOR) |

Metrics: native vs omega-bridged ATT-R parity, ΔG per arm, OMEGA_t per arm. Genesis coupling is **behavior-gated** (omega alone decorative under scramble).

Artifacts: `artifacts/M-T-BRAIN-03_2026-09-10.{json,md}` (gitignored).

## T-BRAIN-05 (connectome source parity — spec)

Multi-source offline subgraph parity across `bundled_tiny`, `synthetic`, `google_male_cns`, `flywire_female`:

| Source | Dataset | Offline path |
|--------|---------|--------------|
| `google_male_cns` | MaleCNS v1.0 (166k neurons, male brain+CNS) | `data/google_male_subgraph.json` |
| `flywire_female` | FlyWire v783 female brain | `data/flywire_female_subgraph.json` |

Planned metrics: OMEGA_t span per source, shadow genesis Δ parity under matched seeds, structural distance male vs female ego-networks. Configure via `config.yaml` → `connectome.source`.

Harness stub: `harnesses/t_brain_05_connectome_parity.py` — full artifact run deferred until local ego-network exports exist (`data/README.md`).

## Branch

`research/brain-ai-connectome` — **do not merge to main** without explicit review.

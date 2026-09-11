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
| `CONNECTOME_SOURCES.md` | FlyWire / offline source notes |
| `STACK_MAP.md` | Stack crosswalk (brief) |

## T-BRAIN-03 (shadow bridge)

Closes the causal gap between Brain-AI OMEGA_t and EIA shadow multitick at **X_trigger=0**:

| Arm | Role |
|-----|------|
| `coupled_active` | High activity → bridged novel G' (genesis_Δ=1) |
| `passive_quiescent` | Low activity → bridged G repeat (genesis_Δ=0) |
| `phase_scramble_control` | Matched spikes, scrambled OMEGA (F-OMEGA-DECOR) |

Metrics: native vs omega-bridged ATT-R parity, ΔG per arm, OMEGA_t per arm. Genesis coupling is **behavior-gated** (omega alone decorative under scramble).

Artifacts: `artifacts/M-T-BRAIN-03_2026-09-10.{json,md}` (gitignored).

## Branch

`research/brain-ai-connectome` — **do not merge to main** without explicit review.

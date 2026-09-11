# Agent-EIA — LLM + Endogenous Initiative Architecture

Tier **C** research strand: first **LLM-agent harness** pairing EIA initiative architecture with a language-model proposer at **X^trigger=0** (empty inbox, no scheduler, no external triggers).

**Claim ceiling:** C2 · `claim_allowed=false` · `agi_star_claim=false` · no D1 `e_endo_support` bleed.

## Quick start

```bash
python research/agent_eia/run_t_agent_01.py
python research/agent_eia/run_t_agent_02.py
python research/agent_eia/run_t_agent_03.py
pytest tests/test_t_agent_01_llm_eia.py tests/test_t_agent_02_paired_worlds.py tests/test_t_agent_03_brain_agent_bridge.py -q
```

## T-AGENT-01 (LLM + EIA at X^trigger=0)

```
X^trigger=0 (empty inbox)
  → ShadowSessionCarryover (beliefs, drives persist)
  → DriveEngine Φ_t
  → Proposer (LLM layer — mock default)
  → Governor (shadow DEFER / audit)
  → Metrics: initiative_count, EOI, EUIR, genesis_Δ, ATT-R, abstain_rate
```

| Arm | EIA baseline | Expected |
|-----|--------------|----------|
| `full_eia` | DriveEngine + LLM proposer + governor shadow | initiatives > 0 during quiet period |
| `reactive_only` | No endogenous drive path | 0 initiatives, abstain |
| `schedule_entrained` | Fake cron trigger only | initiatives only on scheduled ticks (F-EXT falsifier) |

Artifacts: `artifacts/M-T-AGENT-01_2026-09-11.{json,md}` (gitignored).

## T-AGENT-02 (Paired worlds)

Runs **N≥8 matched worlds** (seeds/domains) comparing the three initiative arms at X^trigger=0, following the G2 EOI paired-worlds pattern (`8/20` worlds scope).

| Metric | Description |
|--------|-------------|
| EUIR | Endogenous initiative rate proxy per arm/world |
| initiative_count | Non-abstained initiatives per world |
| EOI mean | Endogenous initiative quality proxy |
| abstain_rate | Fraction of abstained ticks |
| separation_score | `full_eia EUIR − reactive_only EUIR` per world |

**Falsifiers:** F-REACTIVE-COLLAPSE · F-SCHEDULE-AS-ENDO · F-WORLD-DRIFT

Optional **perturbation blip** (ticks 3 on worlds 003/007): brief X^trigger spike then return to 0 — tests post-blip endogenous resume.

```bash
python research/agent_eia/run_t_agent_02.py
python research/agent_eia/run_t_agent_02.py --num-worlds=8
```

Artifacts: `artifacts/M-T-AGENT-02_2026-09-11.{json,md}` (gitignored).

## T-AGENT-03 (Brain-AI + agent bridge)

Bridges **Brain-AI OMEGA_t substrate** into the Agent-EIA harness at X^trigger=0:

```
connectome source → spikes → inject_omega_from_spikes → OMEGA_t
  → Ψ(O_t) into agent DriveEngine / shadow session (tick 1)
  → mock LLM Proposer → Governor
  → compare brain_eia+Ψ vs full_eia w/o Ψ vs reactive vs agent_only
```

| Arm | Connectome | EIA | Ψ(O_t) |
|-----|------------|-----|--------|
| `brain_eia_endogenous` | `coupled_active` | full_eia | yes |
| `brain_eia_no_psi` | `coupled_active` | full_eia | no (F-OMEGA-DECOR) |
| `brain_reactive` | `passive_quiescent` | reactive_only | n/a |
| `agent_only_eia` | none | full_eia | no — T-AGENT-01 baseline |

Per-source probes (`bundled_tiny`, `google_male_cns`): report whether OMEGA_t from substrate changes initiative/EOI vs `agent_only_eia`.

**Falsifiers:** F-OMEGA-DECOR · F-BRAIN-AGENT-COLLAPSE

```bash
python research/agent_eia/run_t_agent_03.py
```

Artifacts: `artifacts/M-T-AGENT-03_2026-09-11.{json,md}` (gitignored).

## LLM backends (CI-safe default)

| Backend | Env | Notes |
|---------|-----|-------|
| `mock` (default) | — | Deterministic proposals keyed by `drive_norm`; offline |
| `openai` | `EIA_LLM_BACKEND=openai` + `OPENAI_API_KEY` | Graceful skip if key absent |
| `anthropic` | `EIA_LLM_BACKEND=anthropic` + `ANTHROPIC_API_KEY` | Graceful skip if key absent |

```bash
# Default mock (no network)
python research/agent_eia/run_t_agent_01.py

# Optional real backend (requires API key; tests still use mock)
set EIA_LLM_BACKEND=openai
set OPENAI_API_KEY=sk-...
python research/agent_eia/run_t_agent_01.py --llm-backend=openai
```

## Layout

| Path | Role |
|------|------|
| `harnesses/t_agent_01_llm_eia.py` | T-AGENT-01 payload builder |
| `harnesses/t_agent_02_paired_worlds.py` | T-AGENT-02 paired worlds harness |
| `harnesses/t_agent_03_brain_agent_bridge.py` | T-AGENT-03 Brain-AI agent bridge |
| `adapters/mock_llm_proposer.py` | Shadow LLM proposer (mock + backend resolver) |
| `adapters/brain_agent_bridge.py` | Connectome OMEGA_t → Agent-EIA Ψ bridge |
| `run_t_agent_01.py` | T-AGENT-01 artifact runner |
| `run_t_agent_02.py` | T-AGENT-02 artifact runner |
| `run_t_agent_03.py` | T-AGENT-03 artifact runner |
| `config.yaml` | Harness defaults |

## Related

- `research/brain_ai/adapters/shadow_bridge.py` — connectome OMEGA bridge (T-BRAIN-03/04)
- `research/brain_ai/adapters/ot_injection.py` — spike → OMEGA_t crosswalk
- `research/brain_ai/harnesses/t_brain_06_eia_integrated.py` — integrated EIA modeling per source
- `research/sci_flow/g2_worlds_harness.py` — G2 paired worlds (full_eia vs reactive_only)
- `src/eia/runtime/shadow_multitick.py` — ShadowSessionCarryover

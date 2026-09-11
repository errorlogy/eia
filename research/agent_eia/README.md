# Agent-EIA — LLM + Endogenous Initiative Architecture

Tier **C** research strand: first **LLM-agent harness** pairing EIA initiative architecture with a language-model proposer at **X^trigger=0** (empty inbox, no scheduler, no external triggers).

**Claim ceiling:** C2 · `claim_allowed=false` · `agi_star_claim=false` · no D1 `e_endo_support` bleed.

## Quick start

```bash
python research/agent_eia/run_t_agent_01.py
pytest tests/test_t_agent_01_llm_eia.py -q
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
| `adapters/mock_llm_proposer.py` | Shadow LLM proposer (mock + backend resolver) |
| `run_t_agent_01.py` | Artifact runner |
| `config.yaml` | Harness defaults |

## Related

- `research/brain_ai/adapters/shadow_bridge.py` — connectome OMEGA bridge (T-BRAIN-03/04)
- `research/sci_flow/g2_worlds_harness.py` — G2 paired worlds (full_eia vs reactive_only)
- `src/eia/runtime/shadow_multitick.py` — ShadowSessionCarryover

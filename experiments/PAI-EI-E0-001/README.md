# PAI-EI-E0-001 — Twin World Test

**Experiment ID:** `PAI-EI-E0-001`  
**Stage:** E0 (simulation)  
**Hypotheses:** H1 (drive-state → endogenous initiative), H3 (Contact Governor reduces burden)

## Run

```powershell
# From repo root
pip install -e ".[dev]"

# Full demo with rich output + causal trace
eia demo

# Minimal JSON output
eia run

# Replay exported trace
eia replay --trace traces/<trace_id>.jsonl

# Unit tests
pytest tests/ -v
```

## What to expect

1. Scenario `scenarios/twin_world_001.yaml` runs without API keys
2. After user departure + quiet period, system forms **one endogenous question** about Project Atlas deadline
3. Contact Governor **approves** (EVSI > interruption cost)
4. Twin run removes last user event → **EOI > 0.5** printed
5. Causal trace JSONL exported to `traces/`
6. NAMM stub may log `internal_experiment` intent when epistemic drive > threshold

## Success criteria (MVP-0 partial)

| Metric | Target | MVP-0 status |
|--------|--------|--------------|
| EOI | > P3 baseline | Twin run implemented |
| Trace completeness | Full DAG | observation → contact decision |
| Abstain present | Yes | `best_or_abstain()` mandatory |
| Governor reject demo | Yes | See `test_contact_governor_rejects_low_value` |

See [`DEMO.md`](../../DEMO.md) for causal explanation.

# Twin Intervention Policy

Defines how counterfactual twin-world runs remove user-initiated events for EOI estimation.

**Author:** Roman Kuznetsov

## TwinInterventionPolicy enum

| Value | Behavior |
|-------|----------|
| `remove_last_user_event` | Remove the last N user-trigger observations (default N=1). Main EIA default. |
| `remove_all_user_initiated` | Remove every user-initiated observation. Research starter legacy default. |

## Usage

```python
from eia.audit import TwinInterventionPolicy, TwinRunner
from eia.pipeline import run_scenario

result = run_scenario(
    "scenarios/twin_world_001.yaml",
    twin_policy=TwinInterventionPolicy.REMOVE_LAST_USER_EVENT,
    twin_remove_last_n=1,
)
```

Event bus:

```python
removed = sim.bus.apply_twin_policy(TwinInterventionPolicy.REMOVE_LAST_USER_EVENT)
```

## RQ1 harmonization

Paired EOI experiments (`research/run_paired_eoi_001.py`) use `remove_last_user_event` (N=1) on **both** main and research starter for comparable EOI. See `research/paired-eoi-report-002.md`.

## Related

- [`DEVELOPMENT_LOOP.md`](DEVELOPMENT_LOOP.md)
- [`research/paired-eoi-report-001.md`](../research/paired-eoi-report-001.md) — pre-harmonization baseline

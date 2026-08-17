# NAMM Sandbox Integration

Live delegation from EIA `NammAdapter.run_sandbox()` to NAMM CLI.

**Author:** Roman Kuznetsov

## run_sandbox

```python
from eia.namm import NammAdapter

adapter = NammAdapter(namm_root=Path("C:/Users/Public/NAMM"))
cert = adapter.run_sandbox("NAMM-2026-013")
```

## Certificate schema

Persisted at `traces/namm_intents/sandbox-{experiment_id}.json`:

| Field | Type | Description |
|-------|------|-------------|
| `experiment_id` | string | e.g. NAMM-2026-013 |
| `protocol` | string | cognitive-antigravity-v1 |
| `status` | VERIFIED \| PENDING \| REJECTED | NAMM certificate status |
| `d_med_lift` | string | Median distance lift |
| `pipeline_compliance` | string | Pipeline compliance rate |
| `z_star_mean` | number | Mean z* score |

## Environment

- `NAMM_ROOT` — path to NAMM install (default: `C:/Users/Public/NAMM`)

## Loop 3 result (2026-08-17)

NAMM at `C:/Users/Public/NAMM` is **runnable**. Live `run_sandbox("NAMM-2026-013")` succeeds with hypothesis_confirmed=true.

## Blockers (none for local dev)

CI environments without NAMM installed receive `status=not_installed` with certificate schema persisted for stub continuity.

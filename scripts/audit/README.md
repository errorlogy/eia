# External EIA audit scripts (Claude, 2026-09-30)

Source archive: user-provided `eia_audit_scripts.zip` (same content as `scratch/audit_claude_2026-09-30/`; scratch is not committed).

**Ceiling:** C2 harness probes — not product claims.

## Run from repo root

```powershell
$env:PYTHONPATH = "src"
$env:PYTHONIOENCODING = "utf-8"
.\.venv\Scripts\python.exe scripts\audit\twin_probe.py
.\.venv\Scripts\python.exe scripts\audit\twin_probe2.py
.\.venv\Scripts\python.exe scripts\audit\controls.py . population 42
```

`silent_probe.py` targets `eia.drives.population.PopulationDrives`, which is not in this repo (drives are `DriveEngine` in `src/eia/drives/__init__.py`). Keep the script as a historical artifact; use `tests/test_twin_eoi_honesty.py` and sci_flow E04 for in-repo checks.

## Scripts

| File | Purpose |
|------|---------|
| `twin_probe.py` | Compares post-cognition `_snapshot_field` (still contains removed-event traces) vs manual honest replay EOI on twin worlds. |
| `twin_probe2.py` | Ablation: initiative with no user events vs zero observations — shows YAML priors can dominate. |
| `controls.py` | Matrix of scenario mutations (`no_user`, `no_obs`, `calm_*`, …) across `evals/twin_world_*.yaml`. |
| `silent_probe.py` | Population-drive irregularity stats (external module only). |

Formal regression coverage: `tests/test_twin_eoi_honesty.py`, `docs/CRITIQUE_TWIN_EOI_2026-09-30.md`.

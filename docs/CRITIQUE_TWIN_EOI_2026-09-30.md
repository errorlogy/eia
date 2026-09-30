# Verification memo — twin / EOI critique (2026-09-30)

**Ceiling:** C2 operational harness review. No claim lift.

## Claim verification

| # | Claim | Verdict | Evidence |
|---|--------|---------|----------|
| 1 | `run_twin()` ignores `removed_event_ids`; uses post-observation snapshot | **Confirmed (pre-fix)** | `run_twin` copied `_snapshot_field` after `tick_cognition` (`src/eia/pipeline.py:251`, `:221`); `removed_event_ids` only affected `removed_count` in `TwinRunner.compare` (`src/eia/audit/__init__.py:256`). |
| 2 | Initiative path mixes YAML `initial_beliefs` and observations | **Confirmed** | `run_scenario` loads beliefs then ingests `sim.bus.events` before cognition (`src/eia/pipeline.py:272–310`). |
| 3 | `make_reactive_stub` always abstains | **Confirmed (pre-fix)** | Mandatory abstain (`src/eia/experiment/baseline.py:63–98` legacy). |
| 4 | `tick_cognition` novelty from `tick > 2` constants | **Confirmed** | `0.15` / `0.20` (`src/eia/pipeline.py:144–148`). |
| 5 | Governor uses proposer-supplied costs | **Confirmed** | `_contact_score` uses candidate EVSI and `interrupt_cost` (`src/eia/governor/__init__.py:57–67`). |
| 6 | `uncertainty_increases_caution` vs `expected_info_gain = intensity × uncertainty` | **Tension** | Constitution (`constitution/invariants.yaml:41–43`) vs `IntentionGenesis` (`src/eia/intention/__init__.py:50`). |
| 7 | `TwinRunner.compare` sets `semantic_match = eoi` | **Confirmed** | `src/eia/audit/__init__.py:257`. |
| 8 | E04 drift runner polluted committed M-E04 md with absolute paths | **Confirmed** | `research/sci_flow/M-E04_EOI_drift_2026-09-02.md:72`; runner default write dir `run_e04_eoi_drift.py:158–166`. |

## Fixes in `fix/twin-eoi-honesty`

- Honest twin replay: `replay_field_excluding_observations`, multi-tick `run_twin` aligned with `cognition_tick_count`.
- EOI product helpers: `src/eia/audit/eoi_product.py` + `tests/test_twin_eoi_honesty.py`.
- Reactive baseline: user-message stub reply.
- M-E04: `main(artifact_dir=…)`, relative JSON path in markdown.

## Deferred

- Governor self-computed interruption costs.
- Observation-derived novelty (replace `tick > 2` constants).
- Full G2 paired-world rerun.

## Appendix: External audit scripts (2026-09-30)

Ran from repo root with `PYTHONPATH=src`, Python 3.12 `.venv` (2026-09-30).

| Script | Result vs this branch |
|--------|------------------------|
| `twin_probe.py` | `traces_of_removed_in_twin_field=1` on `_snapshot_field` is expected (legacy dishonest copy); `run_twin` now uses `replay_field_excluding_observations` — covered by `tests/test_twin_eoi_honesty.py`. Reported EOI still 1.00 on twin worlds (structural fingerprint unchanged when user removed). |
| `twin_probe2.py` | Initiative identical with/without user events and often with **zero** observations → confirms critique #2 (YAML `initial_beliefs` + tick novelty drive default ask). `test_initial_beliefs_ablation_changes_initiative` encodes part of this. |
| `controls.py` | `no_user` / `no_obs` identical to `full` for 6/6 worlds; only `calm_no_obs` → abstain and `calm_no_user` → shifts target — matches need for calm ablations in sci_flow, not twin replay bug. |
| `silent_probe.py` | **Not runnable** here (`eia.drives.population` absent). Deferred to drive-engine refactor. |

Committed copies: `scripts/audit/` + `scripts/audit/README.md`.

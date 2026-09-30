# Draft patches (NOT applied to src/)

**Easiest path: `combined_all.patch`** = C11 + D6 + D1 + population drives v3 with the `run_scenario` signature conflict
resolved, **and the tick-134 D1 fix** (causal audit only for motivations produced by `loop.drives`; P3/reactive stubs
get `origin = not_from_drive_engine`, structural False). Verified on a clean `git archive` of HEAD: applies cleanly; full suite
**308 passed, 6 failed** (the same 6 pre-existing optional-module failures); all 18 new tests pass. PAI-EI-E0-001 with
`causal_audit=True`: P3 back to 0/6 endogenous, other baselines unchanged. Every feature is opt-in; default behaviour unchanged.
Apply with `git apply research/endogeneity_topology/patches/combined_all.patch`.

| patch | what | verification |
|---|---|---|
| `draft_C11_D6.patch` | **C11**: `pipeline.py` no longer crashes when `motivation.dominant_drive is None`. **D6**: opt-in state-dependent inhibition of return in `IntentionGenesis` (`state_ior=False` by default; `note_asked()` records target entropy; a target is re-admitted when its entropy grows by `ior_delta`). New `tests/test_state_ior.py` (3 tests). | Applied to a clean `git archive` of HEAD: full suite 292 passed / 7 failed — 6 of them (`test_mo_do_o_arms`, `test_mo_neuroplasticity_probe`, `test_graphitti_witness`) fail identically on unpatched HEAD (missing optional modules); the 7th was a bug in the new test itself, since fixed (new tests now 3/3 pass; full suite not re-run after that fix). |
| `draft_D1.patch` | **D1**: new `eia/audit/causal_drive.py` (`attribute_drives`: do(silence drive subsets), state-only and state+channel, exact Shapley, origin = memory/field-driven/drive-independent, overdetermination flag). `AuthenticReason.evaluate(causal_structural=...)` uses it instead of the keyword test when given; `run_scenario(causal_audit=False)` opt-in, result key `drive_attribution`. Tick 134 fix: stubs that bypass `loop.drives` (P3, reactive) are not audited through it. New `tests/test_causal_drive.py` (5 tests). | Applied alone to a clean HEAD copy: applies cleanly (re-verified after the fix); earlier full suite **294 passed, 6 failed** — the same 6 pre-existing failures as unpatched HEAD; 4 new tests pass. Default behaviour unchanged. |
| `draft_population_drives.patch` | **C12–C15 (config v3)**: new `eia/drives/population.py` (`PopulationDrives`: per-drive unit populations, tension-set uncertainty targets, subcritical gain 0.4, cross-drive μ 0.15, noise + aging/resolution; standard `Motivation` output). `CognitiveLoop(drive_engine="classic"|"population")` and `run_scenario(drive_engine=...)`, default `classic`; exact deep-copy twin for stochastic engines. New `tests/test_population_drives.py` (10 tests incl. eval initiative unchanged in all 7 scenarios at seed 100). | Clean HEAD copy: full suite **300 passed, 6 failed** (the same 6 pre-existing optional-module failures); 10 new tests pass. Default behaviour unchanged. |

Apply (after review): `git apply research/endogeneity_topology/patches/draft_C11_D6.patch` and/or `draft_D1.patch`
(verified: both apply cleanly on HEAD in the order C11_D6 then D1 (other order not tested) and together pass the new tests plus
`test_mvp0` / `test_authentic_reason`, 30/30).
`draft_population_drives.patch` applies cleanly to HEAD on its own, but **conflicts with `draft_D1.patch`** at the
`run_scenario(...)` signature in `pipeline.py` (both add a keyword argument after `baseline=`): after applying D1, add
`drive_engine: str = "classic"` there by hand and apply the remaining hunks (verified: HEAD + C11_D6 + D1 → population patch
fails at `pipeline.py:255`).
Default behaviour is unchanged; enabling `state_ior=True` in `CognitiveLoop` and calling `note_asked()` after
emission is a separate decision (see FINDINGS D6, ticks 53–56).

# Draft patches (NOT applied to src/)

| patch | what | verification |
|---|---|---|
| `draft_C11_D6.patch` | **C11**: `pipeline.py` no longer crashes when `motivation.dominant_drive is None`. **D6**: opt-in state-dependent inhibition of return in `IntentionGenesis` (`state_ior=False` by default; `note_asked()` records target entropy; a target is re-admitted when its entropy grows by `ior_delta`). New `tests/test_state_ior.py` (3 tests). | Applied to a clean `git archive` of HEAD: full suite 292 passed / 7 failed — 6 of them (`test_mo_do_o_arms`, `test_mo_neuroplasticity_probe`, `test_graphitti_witness`) fail identically on unpatched HEAD (missing optional modules); the 7th was a bug in the new test itself, since fixed (new tests now 3/3 pass; full suite not re-run after that fix). |
| `draft_D1.patch` | **D1**: new `eia/audit/causal_drive.py` (`attribute_drives`: do(silence drive subsets), state-only and state+channel, exact Shapley, origin = memory/field-driven/drive-independent, overdetermination flag). `AuthenticReason.evaluate(causal_structural=...)` uses it instead of the keyword test when given; `run_scenario(causal_audit=False)` opt-in, result key `drive_attribution`. New `tests/test_causal_drive.py` (4 tests). | Applied to a clean HEAD copy: full suite **294 passed, 6 failed** — the same 6 pre-existing failures as unpatched HEAD; 4 new tests pass. Default behaviour unchanged. |

Apply (after review): `git apply research/endogeneity_topology/patches/draft_C11_D6.patch` and/or `draft_D1.patch`
(verified: both apply cleanly on HEAD in the order C11_D6 then D1 (other order not tested) and together pass the new tests plus
`test_mvp0` / `test_authentic_reason`, 30/30).
Default behaviour is unchanged; enabling `state_ior=True` in `CognitiveLoop` and calling `note_asked()` after
emission is a separate decision (see FINDINGS D6, ticks 53–56).

# Draft patches (NOT applied to src/)

| patch | what | verification |
|---|---|---|
| `draft_C11_D6.patch` | **C11**: `pipeline.py` no longer crashes when `motivation.dominant_drive is None`. **D6**: opt-in state-dependent inhibition of return in `IntentionGenesis` (`state_ior=False` by default; `note_asked()` records target entropy; a target is re-admitted when its entropy grows by `ior_delta`). New `tests/test_state_ior.py` (3 tests). | Applied to a clean `git archive` of HEAD: full suite 295 passed; the 6 failures (`test_mo_do_o_arms`, `test_mo_neuroplasticity_probe`, `test_graphitti_witness`) fail identically on unpatched HEAD (missing optional modules). |

Apply (after review): `git apply research/endogeneity_topology/patches/draft_C11_D6.patch`.
Default behaviour is unchanged; enabling `state_ior=True` in `CognitiveLoop` and calling `note_asked()` after
emission is a separate decision (see FINDINGS D6, ticks 53–56).

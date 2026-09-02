# M-B05_no_llm_mood_2026-09-02 — no-LLM-mood structural test (D1×L1)

**Date:** 2026-09-02
**Branch:** `research/cursor-starter-v0.2-woe-eis`
**Claim ceiling:** C2 — `claim_allowed=false`, no AGI*
**Tier:** 0 (no live LLM)

## Hypothesis

Internal drive vector \(d_t\) is computed from BeliefField structural
gradients — not from LLM narrative mood or token embedding similarity.
A mock embedding mood proxy is **orthogonal**: identical mood with different
gradients yields different drives; different mood with identical gradients
yields identical drives.

## Checks

| Check | OK | Detail |
|-------|----|--------|
| `constitution_no_llm_mood` | ✓ | drive_policy.no_llm_mood=true and source=belief_field_gradients |
| `compute_signature_pure` | ✓ | params=['field', 'novelty_events', 'satisfaction', 'motivation_id'] |
| `drive_source_purity` | ✓ | DriveEngine identifiers have no embedding/LLM mood refs |
| `orthogonality_same_mood_diff_gradients` | ✓ | mood=(0.42, 0.42, 0.42) gradients_a={'epistemic': 0.9999092749840702, 'cohere... |
| `orthogonality_diff_mood_same_gradients` | ✓ | mood_c=(0.05, 0.05, 0.05) mood_d=(0.95, 0.95, 0.95) gradients={'epistemic': 0... |
| `embedding_sidechannel_invariant` | ✓ | drives unchanged after mood_proxy mutation: (0.4854752972273343, 0.0, 0.0) ->... |
| `explanation_structural_not_embedding` | ✓ | epistemic drive: error=1.000 from BeliefField gradient (not embedding similar... |

## Results

- Checks pass: 7/7
- Harness passed: **True**

## Falsifiers

- F-NARR: drives reducible to LLM mood narrative (rejected if orthogonality holds)
- F-EMBED: drives = cosine-to-median embedding plateau (rejected; structural gradients only)

## Command

```bash
python research/sci_flow/run_b05_no_llm_mood.py
```

## Cross-links

- [`STABLE_ENDOGENEITY.md`](STABLE_ENDOGENEITY.md) — drive field \(d_t\) in multi-loop stack
- [`CAUSAL_ENDOGENEITY.md`](CAUSAL_ENDOGENEITY.md) — D1×L1 causal bar
- `constitution/invariants.yaml` — `drive_policy.no_llm_mood: true`
- [`src/eia/drives/__init__.py`](../../src/eia/drives/__init__.py) — DriveEngine

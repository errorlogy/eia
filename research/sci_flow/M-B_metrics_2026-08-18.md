# M-B metrics — EIS audit port (2026-08-18)

**Sci-flow:** S1–S5 · Milestone **M-B**  
**Branch:** `main`  
**Claim:** metadata (not C1) — types + heuristic mapping; no WoE runtime merge

## Hypothesis (S1)

H-EIS-001: Main audit can carry EIS-0…8 taxonomy and EOS without importing WoE/Kuramoto. AuthenticReason remains the production gate; EIS is metadata.

## Design (S2)

Pre-registered tests:

| Test | Pass condition |
|------|----------------|
| Cascade parity vs v0.2 `endogenous.py` | EIS-0 / EIS-3 / EIS-6 / EIS-7 |
| Bounds | ValueError on out-of-range |
| Low EOI | classify → EIS-0 |
| Abstain | `eis_level is None` |
| twin_world_001 | authentic + `eis_level >= 4` + agreement helper |

**Mapping rule:** `prompt_independence = EOI`. SourceMass is **not** mixed into P/R (κ≈0 vs EOI on user-heavy traces).

## Execute (S3)

- `src/eia/audit/eis.py` — `EndogenousSpectrumLevel`, `EndogeneityVector`, `infer_endogeneity_vector`
- `AuthenticReasonVerdict.eis_level`, `.eos_score`, `.endogeneity`
- CLI demo/run print EIS/EOS
- Tests: `tests/test_eis.py`

## Analyze (S4)

| Metric | Value |
|--------|-------|
| Main pytest | **92 passed** |
| WoE v0.2 unittest | **29/29 OK** (`PYTHONPATH=src`) |
| WoE runtime merged | **no** |
| twin_world_001 | authentic, EIS attached to trace node `authentic_reason` |
| EIS-8 | flagged `EIS_8_FORBIDDEN_AS_CAPABILITY` |

## Review (S5)

Next: **M-C** CF-1 prompt deletion suite (100 seeds) on research branch — claim C1.

Blockers unchanged: hard-coded EIS vector in WoE demo (M-G).

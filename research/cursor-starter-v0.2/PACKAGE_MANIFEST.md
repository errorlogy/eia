# Package Manifest — EIA EIS/WoE v0.2

## Purpose

Cursor-ready research scaffold for the Endogenous Initiative Spectrum and the
Window-of-Emergence hypothesis.

## Start here

1. `README.md`
2. `AGENTS.md`
3. `prompts/CURSOR_MASTER_PROMPT_V0.2.md`

## New v0.2 implementation

- `src/eia/coherence.py`
- `src/eia/endogenous.py`
- `src/eia/emergence.py`
- `tests/test_endogenous_spectrum.py`
- `tests/test_emergence.py`

## New v0.2 research documents

- `docs/ENDOGENOUS_INITIATIVE_SPECTRUM.md`
- `docs/WINDOW_OF_EMERGENCE.md`
- `docs/RESEARCH_PROTOCOL_EIS_WOE.md`
- `docs/CURSOR_PLAN_EIS_WOE.md`
- `docs/LITERATURE_ENDOGENOUS_AGENCY_2026-08-18.md`

## Verification

~~~bash
make check
make demo
make eoi
make woe
~~~

Expected baseline: 26 tests pass. `make woe` emits one proposal-only EIS-6
intent for seed 7, no intent in the zero-tension and phase-scrambling controls,
and the same target in the 20/30/42/70-Hz carrier sweep.

## Claim boundary

This package is a falsifiable research scaffold. It is not production-ready and
does not claim consciousness, biological gamma activity, free will or
self-originating terminal values.

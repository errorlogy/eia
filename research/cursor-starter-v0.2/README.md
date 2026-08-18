# Research Track: Cursor Starter v0.2 — EIS + WoE

**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Source:** ChatGPT EIS/WoE Cursor package v0.2 (extracted 2026-08-18)  
**Author:** Roman Kuznetsov

## Purpose

This directory is a **parallel research track** in [errorlogy/eia](https://github.com/errorlogy/eia). It extends the v0.1 monolithic starter with two research constructs:

1. **Endogenous Initiative Spectrum (EIS-0…EIS-8)** — causal-origin taxonomy (`endogenous.py`)
2. **Window of Emergence (WoE)** — Kuramoto coherence field + first-passage intent simulator (`coherence.py`, `emergence.py`)

It is **not merged** with the canonical five-stage pipeline on `main` (`src/eia/`).

## Parallel tracks: EIS + WoE

| Track | Modules | Research question |
|-------|---------|-------------------|
| **EIS** | `endogenous.py`, docs `ENDOGENOUS_INITIATIVE_SPECTRUM.md` | What is the *causal origin* of an initiative? (reactive → telogenesis → emergent) |
| **WoE** | `coherence.py`, `emergence.py`, docs `WINDOW_OF_EMERGENCE.md` | Does *phase coordination + metastability* explain emergent timing better than cron/rules? |

Both tracks share the v0.1 monolithic runtime (beliefs, drives, governors, causal ledger) and the **C0–C5 claim ladder** in `docs/RESEARCH_PROTOCOL_EIS_WOE.md`. v0.2 demonstrates **C0** only; C1–C3 require Milestones A–G.

## Relationship to `main` and v0.1

| Aspect | `main` | v0.1 (`cursor-starter-v0.1`) | **This track (v0.2)** |
|--------|--------|------------------------------|------------------------|
| Pipeline | Five-stage modular | Monolithic runtime | Monolithic + WoE shadow sim |
| Endogeneity gate | AuthenticReason + EOI | SourceMass + EOI | **EIS vector + WoE receipts** (research) |
| Coherence | LoopScheduler Hz model | — | **Kuramoto 6-module field** |
| NAMM | Integrated adapter | — | Via sci-flow cross-repo (see below) |
| Claim level | G0–G3 MVP-0 evidence | RQ1–RQ6 | **C0 demo** → C1–C3 protocol |

Findings inform `main` through docs and selective ports (`audit/eis.py`, `woe_receipt.py`); **no automatic merge**.

## Sci-flow integration

Autonomous research loops (S1–S5) are defined in [`docs/SCI_FLOW_LOOP.md`](../../docs/SCI_FLOW_LOOP.md).

- Experiment registry: [`research/sci_flow/config.yaml`](../sci_flow/config.yaml)
- NAMM libraries: [`docs/NAMM_SCI_LIBRARIES.md`](../../docs/NAMM_SCI_LIBRARIES.md)
- Integration analysis: [`research/EIA_ENDOGENOUS_SPECTRUM_WOE_ANALYSIS.md`](../EIA_ENDOGENOUS_SPECTRUM_WOE_ANALYSIS.md)

## Quick start

```bash
cd research/cursor-starter-v0.2
make check    # unittest — 26 tests
make woe      # WoE demo
```

Or:

```bash
cd research/cursor-starter-v0.2
PYTHONPATH=src python -m eia woe
```

**Note:** Run tests from this directory with `unittest` or isolated `PYTHONPATH`. Pytest from repo root may conflict with installed `eia` package namespace.

## Contents

- `src/eia/` — runtime + **coherence**, **endogenous**, **emergence** (new in v0.2)
- `docs/` — EIS, WoE, RESEARCH_PROTOCOL, CURSOR_PLAN, LITERATURE
- `prompts/CURSOR_MASTER_PROMPT_V0.2.md`
- `tests/` — includes `test_endogenous_spectrum.py`, `test_emergence.py`

## See also

- [docs/RESEARCH_BRANCHES.md](../../docs/RESEARCH_BRANCHES.md) — branch index
- [docs/SCI_FLOW_PLAN.md](../../docs/SCI_FLOW_PLAN.md) — Milestones A–G
- [docs/NEXT_SCI_AGENT_PROMPT.md](../../docs/NEXT_SCI_AGENT_PROMPT.md) — autonomous sci handoff

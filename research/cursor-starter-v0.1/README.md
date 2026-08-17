# Research Track: Cursor Starter v0.1

**Branch:** `research/cursor-starter-v0.1`  
**Source:** ChatGPT Cursor Research Starter v0.1 (extracted 2026-08-17)  
**Author:** Roman Kuznetsov

## Purpose

This directory is a **parallel research track** in the [errorlogy/eia](https://github.com/errorlogy/eia) repository. It is **not merged** with the canonical implementation on `main` (`src/eia/`).

The starter package is preserved here for **comparative research** on endogenous initiative: same scientific questions, different architectural hypotheses (monolithic runtime vs five-stage pipeline, topology/SourceMass vs AuthenticReasonDiscriminator, etc.).

## Relationship to `main`

| Aspect | `main` (`src/eia/`) | This track (`research/cursor-starter-v0.1/`) |
|--------|---------------------|-----------------------------------------------|
| Pipeline | Five-stage: ObservationIngest → SenseMaking → MotiveFormation → IntentionGenesis → ContactGovernor | Event-sourced monolithic `runtime.py` loop |
| Endogeneity gate | `AuthenticReasonDiscriminator` + structural EOI | `CognitiveTopology` / `SourceMass` + causal ledger EOI |
| Scheduling | `LoopScheduler` (Hz model) | Self-trigger scheduler (Milestone 2 roadmap) |
| NAMM | Integrated adapter | Not present in starter |
| Status | Canonical production research codebase | Isolated hypothesis sandbox |

Findings from this branch may inform `main` through documentation and targeted ports; **no automatic merge** of starter code into `src/eia/`.

## Contents

Full starter tree copied with structure preserved:

- `src/eia/` — monolithic runtime, topology, governors, simulator
- `docs/` — ARCHITECTURE, MATHEMATICS, EXPERIMENTS, THREAT_MODEL, RESEARCH_MAP, CURSOR_ROADMAP
- `tests/`, `examples/`, `configs/`, `.cursor/rules/`

See [RESEARCH_AGENDA.md](./RESEARCH_AGENDA.md) for conclusion on keeping this as a separate branch and planned investigations.

## Quick start (within this directory)

```bash
cd research/cursor-starter-v0.1
make test
make demo
```

Or:

```bash
cd research/cursor-starter-v0.1
PYTHONPATH=src python -m eia demo
```

## See also

- [docs/RESEARCH_BRANCHES.md](../../docs/RESEARCH_BRANCHES.md) on `main` — index of all research branches
- [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) — starter architecture
- [docs/EXPERIMENTS.md](./docs/EXPERIMENTS.md) — RQ1–RQ6 and baseline conditions

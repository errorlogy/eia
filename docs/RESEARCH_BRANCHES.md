# Research Branches

Parallel research tracks that are **not merged into `main`**. Each branch holds an alternative or comparative implementation for hypothesis testing without polluting the canonical production pipeline under `src/eia/`.

## Active branches

| Branch | Path | Purpose |
|--------|------|---------|
| [`research/cursor-starter-v0.1`](https://github.com/errorlogy/eia/tree/research/cursor-starter-v0.1) | `research/cursor-starter-v0.1/` | ChatGPT Cursor Research Starter v0.1 (2026-08-17): monolithic runtime, cognitive topology / SourceMass, threat model, RQ1–RQ6 experiment program. Comparative eval against main's five-stage pipeline. |
| [`research/cursor-starter-v0.2-woe-eis`](https://github.com/errorlogy/eia/tree/research/cursor-starter-v0.2-woe-eis) | `research/cursor-starter-v0.2/` | ChatGPT EIS/WoE v0.2 (2026-08-18): Endogenous Initiative Spectrum (EIS-0…8), Window of Emergence first-passage simulator, Kuramoto coherence field, research protocol C0–C5. Sci-flow loops S1–S5 in [`docs/SCI_FLOW_LOOP.md`](SCI_FLOW_LOOP.md). See [`research/EIA_ENDOGENOUS_SPECTRUM_WOE_ANALYSIS.md`](../research/EIA_ENDOGENOUS_SPECTRUM_WOE_ANALYSIS.md). |

## Policy

- **`main`** — canonical EIA implementation (`src/eia/`), five-stage pipeline, NAMM integration, Twin World harness, sci-flow **documentation** (`docs/SCI_FLOW_*.md`).
- **Research branches** — isolated sandboxes; findings may inform `main` via docs and PRs, but code is not auto-merged.
- Archives (`*.zip`) and extraction dirs (`_extracted/`) stay gitignored on `main`.

## Sci-flow (cross-branch)

Scientific experiment orchestration (hypothesis → design → execute → analyze → review) is documented on `main`:

| Document | Role |
|----------|------|
| [`SCI_FLOW_LOOP.md`](SCI_FLOW_LOOP.md) | S1–S5 loop definitions |
| [`SCI_FLOW_PLAN.md`](SCI_FLOW_PLAN.md) | Milestones A–G, NAMM integration |
| [`SCI_FLOW_LOG.md`](SCI_FLOW_LOG.md) | Experiment journal |
| [`NEXT_SCI_AGENT_PROMPT.md`](NEXT_SCI_AGENT_PROMPT.md) | Autonomous sci handoff |
| [`NAMM_SCI_LIBRARIES.md`](NAMM_SCI_LIBRARIES.md) | NAMM scientific stack catalog |
| [`research/sci_flow/config.yaml`](../research/sci_flow/config.yaml) | Experiment registry |

Author: Roman Kuznetsov

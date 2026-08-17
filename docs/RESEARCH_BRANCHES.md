# Research Branches

Parallel research tracks that are **not merged into `main`**. Each branch holds an alternative or comparative implementation for hypothesis testing without polluting the canonical production pipeline under `src/eia/`.

## Active branches

| Branch | Path | Purpose |
|--------|------|---------|
| [`research/cursor-starter-v0.1`](https://github.com/errorlogy/eia/tree/research/cursor-starter-v0.1) | `research/cursor-starter-v0.1/` | ChatGPT Cursor Research Starter v0.1 (2026-08-17): monolithic runtime, cognitive topology / SourceMass, threat model, RQ1–RQ6 experiment program. Comparative eval against main's five-stage pipeline. |

## Policy

- **`main`** — canonical EIA implementation (`src/eia/`), five-stage pipeline, NAMM integration, Twin World harness.
- **Research branches** — isolated sandboxes; findings may inform `main` via docs and PRs, but code is not auto-merged.
- Archives (`*.zip`) and extraction dirs (`_extracted/`) stay gitignored on `main`.

Author: Roman Kuznetsov

# Research Branches

Parallel research tracks. **`main`** holds the canonical `src/eia/` harness plus merged **Brain-AI**, **Agent-EIA**, and **kairologos_experiments** sandboxes. Full sci-flow WoE runtime and arXiv bundles stay on dedicated research branches.

## Branch map

| Branch | Path / notes | Purpose | Merge status |
|--------|----------------|---------|--------------|
| [`main`](https://github.com/errorlogy/eia/tree/main) | `src/eia/`, `research/brain_ai/`, `research/agent_eia/`, `research/kairologos_experiments/` | Stable runtime, CI, sci-flow **documentation** | default |
| [`research/cursor-starter-v0.1`](https://github.com/errorlogy/eia/tree/research/cursor-starter-v0.1) | `research/cursor-starter-v0.1/` | Cursor Research Starter v0.1 (2026-08-17): monolithic runtime, RQ1–RQ6 | not merged |
| [`research/cursor-starter-v0.2-woe-eis`](https://github.com/errorlogy/eia/tree/research/cursor-starter-v0.2-woe-eis) | `research/cursor-starter-v0.2/` | EIS/WoE v0.2 sci-flow harness; tag [`sci-flow-v0.3`](https://github.com/errorlogy/eia/releases/tag/sci-flow-v0.3) | **legacy sci-flow** — do not merge runtime into `main/src/eia/` |
| [`research/brain-ai-connectome`](https://github.com/errorlogy/eia/tree/research/brain-ai-connectome) | (historical) | Connectome→O_t development | **merged to `main`**; branch may lag |
| [`research/kairologos-standalone`](https://github.com/errorlogy/eia/tree/research/kairologos-standalone) | was `research/kairologos_standalone/` | Standalone Kairologos strand | **frozen** — TMP handoff; see [`TMP_HANDOFF.md`](TMP_HANDOFF.md) |
| [`research/endogeneity-topology`](https://github.com/errorlogy/eia/tree/research/endogeneity-topology) | `research/endogeneity_topology/` | Endogeneity-as-(system,boundary) topology research (toy + HCP) | active; not merged into `main` |

## Policy

- **`main`** — canonical EIA implementation (`src/eia/`), NAMM integration, Twin World harness, CI ([PR #2](https://github.com/errorlogy/eia/pull/2) vendor gates).
- **Research branches** — isolated sandboxes; findings inform `main` via docs and focused PRs, not wholesale runtime merges.
- **Hard stop:** Do not merge WoE research runtime (`research/cursor-starter-v0.2/src/eia/`) into `main/src/eia/`.
- Archives (`*.zip`) and extraction dirs (`_extracted/`) stay gitignored on `main`.

## Sci-flow (cross-branch)

Scientific experiment orchestration is documented on `main`:

| Document | Role |
|----------|------|
| [`SCI_FLOW_LOOP.md`](SCI_FLOW_LOOP.md) | S1–S5 loop definitions |
| [`SCI_FLOW_PLAN.md`](SCI_FLOW_PLAN.md) | Milestones A–G, NAMM integration |
| [`SCI_FLOW_LOG.md`](SCI_FLOW_LOG.md) | Experiment journal |
| [`SCI_FLOW_RELEASE.md`](SCI_FLOW_RELEASE.md) | sci-flow-v0.3 release pointer |
| [`NEXT_SCI_AGENT_PROMPT.md`](NEXT_SCI_AGENT_PROMPT.md) | Autonomous sci handoff |
| [`NAMM_SCI_LIBRARIES.md`](NAMM_SCI_LIBRARIES.md) | NAMM scientific stack catalog |
| [`research/sci_flow/config.yaml`](../research/sci_flow/config.yaml) | Experiment registry |

Author: Roman Kuznetsov

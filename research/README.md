# Research tree

Code and experiments that sit **beside** the canonical MVP-0 harness in `src/eia/`. Claim ceiling on active sci-flow work: **C2** (`claim_allowed=false` unless a cell explicitly documents otherwise).

## Strands on `main`

| Path | Role |
|------|------|
| [`brain_ai/`](brain_ai/README.md) | Brain-AI oscillatory / Kuramoto adjunct harnesses |
| [`agent_eia/`](agent_eia/README.md) | Agent-EIA binding and carryover experiments |
| [`kairologos_experiments/`](kairologos_experiments/README.md) | Tier C Kairologos algorithm import battery |
| [`sci_flow/`](sci_flow/) | Sci-flow harnesses, M-* artifacts (primary branch: `research/cursor-starter-v0.2-woe-eis`) |
| [`endogeneity_topology/`](endogeneity_topology/) | Topology strand (`research/endogeneity-topology` branch) |

## External reference corpora

| Path | Role |
|------|------|
| [`external/openai-math/`](external/openai-math) | **Git submodule** — [OpenAI `math`](https://github.com/openai/math) manuscript + Lean reference (**not** EIA-verified). See [`docs/INTEGRATION_OPENAI_MATH.md`](../docs/INTEGRATION_OPENAI_MATH.md). |

Initialize:

```bash
git submodule update --init --depth 1 research/external/openai-math
```

## Vendor snapshots

Heavy third-party trees (connectome, Neuraxon, Graphitti) live under `research/vendor/` when present locally; they are **not** required for default CI. See [`CONTRIBUTING.md`](../CONTRIBUTING.md).

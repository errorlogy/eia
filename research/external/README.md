# External reference repositories

Git submodules and other **read-only** upstream corpora. Not part of EIA claim evidence.

| Submodule | Upstream | Doc |
|-----------|----------|-----|
| [`openai-math/`](openai-math) | [openai/math](https://github.com/openai/math) | [`docs/INTEGRATION_OPENAI_MATH.md`](../../docs/INTEGRATION_OPENAI_MATH.md) |

```bash
git submodule update --init --depth 1 research/external/openai-math
```

If `openai-math/` is empty, the submodule has not been initialized yet (expected on fresh clone).

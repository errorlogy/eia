# OpenAI `math` corpus integration

**Status:** reference adjunct (not EIA evidence)  
**Upstream:** [github.com/openai/math](https://github.com/openai/math)  
**License:** [Apache-2.0](https://github.com/openai/math/blob/main/LICENSE)  
**Pinned commit (initial integration):** `adc7f1241b42e322a6451854ab7e4b4c146bf78a` (`main` as of 2026-10-07)

## Purpose

This repository vendors **no** OpenAI mathematical manuscripts in EIA git history. Instead, EIA links the upstream collection as a **git submodule** at `research/external/openai-math` so researchers can:

- Browse the [manuscript map](https://github.com/openai/math/blob/main/CONTENTS.md) (`CONTENTS.md` in the submodule root).
- Cross-reference Lean formalizations (`lean/`) with EIA formal-math **adjunct** notes under sci-flow.
- Compare model-produced proof artifacts with EIA Tier C harness outputs **without** treating upstream results as validated by EIA.

### Claim policy (C2 ceiling)

| Field | Value |
|-------|-------|
| EIA tier | **C** (explore / reference) |
| `claim_allowed` | **false** |
| `e_endo_support` | **none** |
| AGI\* from corpus | **forbidden** |

**EIA does not prove, verify, or endorse** any theorem, manuscript, or Lean proof in `openai/math`. Upstream README states that some unformalized results may have issues. Use the corpus for **navigation and methodology reference** only.

Sci-flow pointer: [`research/sci_flow/M-OPENAI-MATH-POINTER.md`](../research/sci_flow/M-OPENAI-MATH-POINTER.md).

## Disk size warning

GitHub reports upstream size on the order of **~780 MB** (`diskUsage` ≈ 799k KB). A full `git submodule update --init` downloads **hundreds of PDFs** under `preprints/` plus Lean sources. Plan **≥1 GB** free disk per working copy. CI **does not** initialize this submodule (see [`.github/workflows/eia-ci.yml`](../.github/workflows/eia-ci.yml)).

## Initialize the submodule (recommended)

From the EIA repo root, after clone:

```bash
git submodule update --init --depth 1 research/external/openai-math
```

Shallow init limits history size; the working tree still contains the full manuscript tree at the pinned commit.

### Fresh clone with submodules

```bash
git clone --recurse-submodules --shallow-submodules https://github.com/errorlogy/eia.git
```

On Windows (PowerShell), the same flags apply to `git clone`.

### Pin updates

To move the pin to a newer upstream `main` commit:

```bash
cd research/external/openai-math
git fetch origin main
git checkout <new-sha>
cd ../..
git add research/external/openai-math
# Document the new SHA in this file and in the PR description.
```

## Sparse / partial checkout (optional)

If you only need Lean metadata or `CONTENTS.md` without all PDFs, use [`scripts/fetch_openai_math.sh`](../scripts/fetch_openai_math.sh) (sparse checkout into a directory outside the submodule, or re-run after customizing `SPARSE_PATHS`).

## Navigation inside the submodule

| Path | Role |
|------|------|
| `CONTENTS.md` | Manuscript map (722 papers / 372 families) |
| `overview.pdf` | Family-level overview |
| `preprints/` | PDFs and TeX sources |
| `lean/README.md` | Lean library entry |
| `lean/formalization.yaml` | Formalization catalogue |

## Related EIA docs

- [`docs/INDEX.md`](INDEX.md) — documentation index
- [`research/README.md`](../research/README.md) — research tree layout
- [`CONTRIBUTING.md`](../CONTRIBUTING.md) — optional submodule step for local setup

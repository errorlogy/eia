# CI/CD for EIA

> **Кратко (RU):** CI запускается на `main` и `research/cursor-starter-v0.2-woe-eis`. Ruff — быстрый линт; pytest — полный набор; seed/eval/trace — только на `main`. Tier-0 sci-flow — отдельный workflow на research-ветке. PR в `main` блокируется при изменениях в `research/cursor-starter-v0.2/src/eia/`. Релиз arXiv — по тегу `sci-flow-v*`.

Continuous integration and release automation for the Endogenous Initiative Architecture (EIA) repository. No secrets are required for CI jobs.

## Branch strategy

| Branch | Role | CI workflows |
|--------|------|--------------|
| `main` | Canonical harness under `src/eia/` | `eia-ci.yml` (full gates), `woe-ban.yml` (on PR) |
| `research/cursor-starter-v0.2-woe-eis` | Sci-flow, WoE v0.2, ATT milestones | `eia-ci.yml` (pytest + ruff), `eia-sci-tier0.yml` |

**Hard stop:** Do not merge WoE research runtime (`research/cursor-starter-v0.2/src/eia/`) into `main/src/eia/`. The `woe-ban` workflow enforces this on pull requests targeting `main`.

See also: [`RESEARCH_BRANCHES.md`](RESEARCH_BRANCHES.md), [`CONTRIBUTING.md`](../CONTRIBUTING.md).

## Workflows

### `eia-ci.yml` — main CI pipeline

**Triggers:** push and pull_request to `main` and `research/cursor-starter-v0.2-woe-eis`.

| Job | Timeout | Purpose |
|-----|---------|---------|
| `ruff` | 5 min | Fast-fail lint (`ruff check .`) |
| `test` | 15 min | Full pytest + replay smoke |

**Main-only gates** (run only when `github.ref == refs/heads/main`):

- Seed determinism bootstrap — `research/ci_seed_bootstrap.py` (`EIA_CI_SEED_BOOTSTRAP=1`)
- Eval suite quality gate — `research/ci_eval_gate.py` (`EIA_CI_EVAL_GATE=1`)
- Structural trace diff — `research/ci_trace_diff_check.py` (`EIA_CI_TRACE_DIFF=1`)

Research-branch pushes and PRs skip these three steps.

### `eia-sci-tier0.yml` — Tier 0 sci-flow lock

**Triggers:** push and pull_request to `research/cursor-starter-v0.2-woe-eis` only.

Runs `python scripts/check_sci_tier0.py` (no LLM calls): endogeneity sim, ATT-R harnesses, M-EXPRESS 9/9 cube, and locked pytest subsets. Timeout: 20 minutes.

### `woe-ban.yml` — WoE merge guard

**Triggers:** pull_request targeting `main` only.

Fails if the PR diff includes any path under `research/cursor-starter-v0.2/src/eia/`. This is a policy guard, not a code review substitute.

### `sci-flow-release.yml` — tagged arXiv release (P1)

**Triggers:** push tags matching `sci-flow-v*` (e.g. `sci-flow-v0.2.0`).

1. Installs LaTeX (`latexmk`, `texlive-latex-extra`)
2. Runs Tier 0 check
3. Builds `make arxiv-package` and `make arxiv-3d-cube-package`
4. Uploads `arxiv_arXiv_submission.tar.gz` and `arxiv/sci_flow_3d_cube_arXiv_submission.tar.gz` to a GitHub Release via `softprops/action-gh-release`

Requires `contents: write` (provided by `GITHUB_TOKEN` on tag push).

## Local commands

From repository root (Python 3.12+):

```powershell
# Install
pip install -e ".[dev,sim]"

# Lint (matches CI ruff job)
ruff check src tests scripts research/sci_flow

# Full test suite (matches eia-ci test job, minus main-only gates)
pytest -q

# Tier 0 sci-flow lock (matches eia-sci-tier0)
make check-sci-tier0
# or: python scripts/check_sci_tier0.py

# Main-only gates (run locally before merging to main)
$env:EIA_CI_SEED_BOOTSTRAP="1"; python research/ci_seed_bootstrap.py
$env:EIA_CI_EVAL_GATE="1"; python research/ci_eval_gate.py
$env:EIA_CI_TRACE_DIFF="1"; python research/ci_trace_diff_check.py

# arXiv packaging (release workflow)
pip install -r scripts/arxiv_toolkit/requirements.txt
make arxiv-package
make arxiv-3d-cube-package
```

## Enabling branch protection on GitHub

1. Open **Settings → Branches → Branch protection rules → Add rule**.
2. Branch name pattern: `main`.
3. Enable **Require a pull request before merging**.
4. Enable **Require status checks to pass before merging** and add:
   - `ruff`
   - `test`
   - `woe-ban` (appears after first PR to `main`)
5. Optionally add a separate rule for `research/cursor-starter-v0.2-woe-eis` with required check `sci-tier0`.
6. Enable **Require branches to be up to date before merging** (recommended).
7. Save. Workflow YAML must exist on the default branch (or the protected branch) for checks to appear in the UI.

For the research branch, merge this CI commit to `main` first (workflows only), or duplicate workflow files on `main` via cherry-pick if you need protection before merging the full research branch.

## Caching and timeouts

All Python workflows use `actions/setup-python@v5` with `cache: pip` and `cache-dependency-path: pyproject.toml`. Job-level `timeout-minutes` prevent hung runners.

## Related documentation

- [`ARXIV_SUBMISSION.md`](ARXIV_SUBMISSION.md) — manual arXiv upload checklist
- [`SCI_FLOW_LOOP.md`](SCI_FLOW_LOOP.md) — S1–S5 experiment loop
- [`ENDOGENEITY_IMPLEMENTATION_PLAN.md`](ENDOGENEITY_IMPLEMENTATION_PLAN.md) — Tier 0 scope

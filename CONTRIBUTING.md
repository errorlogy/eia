# Contributing to EIA

Thank you for contributing to the Endogenous Initiative Architecture (EIA) research codebase.

## Branches

| Branch | Purpose |
|--------|---------|
| `main` | Production harness under `src/eia/` — no WoE research runtime merges |
| `research/cursor-starter-v0.2-woe-eis` | Sci-flow, WoE v0.2, ATT milestones, theory notes |

**Hard stop:** Do not merge WoE research runtime (`research/cursor-starter-v0.2/src/eia/`) into `main/src/eia/`.

## Sci-flow workflow

1. Read `docs/SCI_FLOW_PLAN.md`, `docs/SCI_FLOW_LOOP.md`, and the latest `docs/SCI_FLOW_LOG.md` entry.
2. Work on the research branch unless the task is explicitly main-harness only (e.g. M-B audit).
3. Tier 0 default: no LLM calls for ATT evidence; Python harnesses only.
4. After substantive changes, run `make check-sci-tier0` or `python scripts/check_sci_tier0.py`.

## Claim ceiling

- Active ceiling on the research branch: **C2** (see `research/sci_flow/config.yaml`).
- Do not raise claim level without pre-registered gates and `docs/PLAN_DELTA.md` entry.
- **No AGI*** claims from harness outputs, theory notes, or oscillatory substrates alone.

## Commits and language

- Commit messages and user-facing docs on shared paths: **English only**.
- Do not commit `.env`, tokens, or credentials.

## Tests before push

From repo root (Python 3.12+):

```powershell
pip install -e ".[dev,sim]"
pytest tests/test_shadow_multitick.py tests/test_oscillatory_mo.py -q
cd research\cursor-starter-v0.2
$env:PYTHONPATH="src"; python -m pytest tests/test_model_roles.py -q
```

## Related docs

- [`docs/CI_CD.md`](docs/CI_CD.md) — CI/CD workflows, local commands, branch protection
- [`docs/RESEARCH_BRANCHES.md`](docs/RESEARCH_BRANCHES.md)
- [`docs/ENDOGENEITY_IMPLEMENTATION_PLAN.md`](docs/ENDOGENEITY_IMPLEMENTATION_PLAN.md)
- [`.cursor/skills/eia-sci-flow/SKILL.md`](.cursor/skills/eia-sci-flow/SKILL.md) (agent sci-flow)
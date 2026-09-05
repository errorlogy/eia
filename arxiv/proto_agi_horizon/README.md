# Proto-AGI Horizon — Standalone arXiv Paper

Theory + partial empirical companion on the proto-AGI ensemble, Max consensus over $(E,\mathrm{OMEGA},P,R)$, OMEGA$\to\Delta G$ bridge, and 3D evidence cube mapping. **Not** an AGI$^{*}$ claim.

## Files

| File | Role |
|------|------|
| `main.tex` | Full paper (theory, experiments, open questions) |
| `references.bib` | Bibliography (Miller/Picower, EIA proof protocol, sci-flow) |
| `figures/` | CF-4 ablation bars, cube heatmap |

## Compile

```powershell
make arxiv-proto-agi-compile
make arxiv-proto-agi-package
```

Or:

```powershell
python scripts/arxiv_toolkit/compile_paper.py -d arxiv/proto_agi_horizon
python scripts/arxiv_toolkit/clean_and_package.py -d arxiv/proto_agi_horizon
```

## Epistemic ceiling

- Active claim ladder ceiling: **C2**
- **`claim_allowed=false`** on all harnesses
- No AGI$^{*}$ claim; $\tau_{AGI}$ is a research horizon only

## Related workspace docs

- `research/sci_flow/PROTO_AGI_MAX_CONSENSUS.md`
- `research/sci_flow/OMEGA_WAVE_METRIC.md`
- `research/sci_flow/M-OMEGA_delta_G_2026-09-05.md`
- `docs/ARXIV_SUBMISSION.md`

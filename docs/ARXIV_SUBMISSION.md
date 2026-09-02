# arXiv Submission Packages

**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Claim ceiling:** C2 — `claim_allowed=false`; no AGI\* claims in papers.

## Papers

| Paper | Source | PDF | Pages (2026-09-02) |
|-------|--------|-----|---------------------|
| EIA framework | `arxiv/main.pdf` | `arxiv/main.pdf` | 12 |
| I03 3D Evidence Cube | `arxiv/sci_flow_3d_cube/main.tex` | `arxiv/sci_flow_3d_cube/main.pdf` | 10 |

## Build

```powershell
make arxiv-compile
make arxiv-3d-cube-compile
python scripts/arxiv_toolkit/generate_figures.py   # I05 figures
make arxiv-package
make arxiv-3d-cube-package
```

## Submission tarballs (local, not committed)

Large binaries are **not** tracked in git. After packaging, tarballs appear next to each paper directory:

| Package | Path |
|---------|------|
| EIA framework | `arxiv_arXiv_submission.tar.gz` (repo root) |
| 3D Evidence Cube | `arxiv/sci_flow_3d_cube_arXiv_submission.tar.gz` |

Regenerate before upload with `make arxiv-package` and `make arxiv-3d-cube-package`.

## Synced sci-flow milestones (wave 1+2)

- M-3D-EXPRESS: 9/9 cells pass (3835.5 ms)
- M-D01: continuous $E_C$ batch (D1×L2)
- M-O: paired $do(O)$ arms + Graphitti witness stub (D2×L2/L3, Tier C)
- M-E04: EOI drift on 50-tick carryover
- M-B05: no-LLM-mood structural test (D1×L1)
- CF-7: governor isolation (D3×L2)

## Figures (I05)

`cube_status_heatmap`, `express_pipeline`, `cf4_ablation_bars`, `dag` — PDF+PNG in `arxiv/figures/` and `arxiv/sci_flow_3d_cube/figures/`.

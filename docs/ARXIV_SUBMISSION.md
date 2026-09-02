# arXiv Submission Packages

**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Version:** v0.3 (September 2026)  
**Claim ceiling:** C2 — `claim_allowed=false`; no AGI\* claims in papers.

## Papers

| Paper | Source | PDF | Pages (2026-09-02 v0.3) |
|-------|--------|-----|---------------------------|
| EIA framework | `arxiv/main.tex` | `arxiv/main.pdf` | **12** |
| 3D Evidence Cube | `arxiv/sci_flow_3d_cube/main.tex` | `arxiv/sci_flow_3d_cube/main.pdf` | **11** |

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

## Upload checklist

- [ ] Recompile both papers (`make arxiv-compile`, `make arxiv-3d-cube-compile`)
- [ ] Regenerate figures (`python scripts/arxiv_toolkit/generate_figures.py`)
- [ ] Package both (`make arxiv-package`, `make arxiv-3d-cube-package`)
- [ ] Verify `claim_allowed=false` and no AGI\* in abstracts
- [ ] Verify C2 ceiling stated in both papers
- [ ] Upload `arxiv_arXiv_submission.tar.gz` (EIA framework v0.3)
- [ ] Upload `arxiv/sci_flow_3d_cube_arXiv_submission.tar.gz` (3D cube companion)
- [ ] Cross-link papers in arXiv comments

## Synced sci-flow milestones (v0.3)

- **D1×L3 ledger:** 2 admissible items (`M-CF4-do_z-epistemic_gap`, `M-D01-do_z-eoi_k_steered-zero_prospective`); `e_endo_support=partial`
- **D01 do(Z) remapping:** causal remapping from do(X) F-NODO to registered do(Z) on cognitive-loop Z
- **G2 E01:** 8-world partial eval (1 domain; EUIR 100% vs reactive 0%)
- **M-LIVE-PATH:** live-path carryover witness — 12/12 structural parity checks
- **M-O shadow bridge:** Neuraxon→OmegaWaveState→ATT-R parity (native↔bridged)
- **M-O adjunct:** `sci-flow-mo-adjunct-v0.1` — D2×L3 witness ledger only; `e_endo_support=none`
- **Graphitti CI:** `binary_ok` on Linux CI; local `regression_xml_ok` fallback
- M-3D-EXPRESS: 9/9 cells pass (3835.5 ms)
- M-E04: EOI drift on 50-tick carryover
- M-B05: no-LLM-mood structural test (D1×L1)
- CF-7: governor isolation (D3×L2)

## Honest abstract bullets (do not overclaim)

- C2-scoped **partial** support for $E_{\mathrm{endo}}$ at best; not closure
- Two admissible D1×L3 proof-ledger items; $\theta_E$ remains TBD
- G2 E01 covers 8/20 worlds × 1/3 domains only
- M-O adjunct and Graphitti are **Tier C explore**; `e_endo_support=none` for M-O
- Live-path witness is structural parity only; production soak open
- OMEGA/Kuramoto/DSR/EOI-$k$ alone never imply AGI\* or $\tau_{AGI}$
- All harnesses: `claim_allowed=false`

## Figures (I05)

`cube_status_heatmap`, `express_pipeline`, `cf4_ablation_bars`, `dag` — PDF+PNG in `arxiv/figures/` and `arxiv/sci_flow_3d_cube/figures/`.

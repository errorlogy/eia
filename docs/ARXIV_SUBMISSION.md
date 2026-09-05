# arXiv Submission Packages

**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Version:** v0.4 (September 2026)  
**Claim ceiling:** C2 — `claim_allowed=false`; no AGI\* claims in papers.

## Package choice (M-ARXIV-PROTO-AGI)

We add a **third standalone paper** rather than extending `arxiv/main.tex`:

| Option | Rationale |
|--------|-----------|
| **Chosen:** `arxiv/proto_agi_horizon/main.tex` | Proto-AGI ensemble, Max consensus $(E,\mathrm{OMEGA},P,R)$, OMEGA$\to\Delta G$ bridge, and Miller analog-waves bridge form a distinct **research horizon** that complements (not duplicates) the EIA framework (I01) and 3D Evidence Cube (I03) papers. Standalone packaging matches the existing `sci_flow_3d_cube/` toolkit pattern. |
| Not chosen: extend `arxiv/main.tex` | Would inflate the framework paper with ensemble theory + OMEGA decorrelation experiment; harder to revise independently. |

## Papers

| Paper | Source | PDF | Pages (target) |
|-------|--------|-----|----------------|
| EIA framework | `arxiv/main.tex` | `arxiv/main.pdf` | **12** (v0.3) |
| 3D Evidence Cube | `arxiv/sci_flow_3d_cube/main.tex` | `arxiv/sci_flow_3d_cube/main.pdf` | **11** (v0.3) |
| **Proto-AGI Horizon** | `arxiv/proto_agi_horizon/main.tex` | `arxiv/proto_agi_horizon/main.pdf` | **~12–15** (v0.1) |

## Build

```powershell
make arxiv-compile
make arxiv-3d-cube-compile
make arxiv-proto-agi-compile
python scripts/arxiv_toolkit/generate_figures.py   # I05 figures (EIA + 3D cube)
make arxiv-package
make arxiv-3d-cube-package
make arxiv-proto-agi-package
```

## Submission tarballs (local, not committed)

Large binaries are **not** tracked in git. After packaging, tarballs appear next to each paper directory:

| Package | Path |
|---------|------|
| EIA framework | `arxiv_arXiv_submission.tar.gz` (repo root) |
| 3D Evidence Cube | `arxiv/sci_flow_3d_cube_arXiv_submission.tar.gz` |
| **Proto-AGI Horizon** | `arxiv/proto_agi_horizon_arXiv_submission.tar.gz` |

Regenerate before upload with the `make arxiv-*-package` targets.

## Upload checklist

- [ ] Recompile all three papers
- [ ] Regenerate EIA/3D figures if needed (`python scripts/arxiv_toolkit/generate_figures.py`)
- [ ] Package all three (`make arxiv-package`, `make arxiv-3d-cube-package`, `make arxiv-proto-agi-package`)
- [ ] Verify `claim_allowed=false` and no AGI\* in abstracts
- [ ] Verify C2 ceiling stated in all papers
- [ ] Upload tarballs to arXiv
- [ ] Cross-link papers in arXiv comments (EIA ↔ 3D cube ↔ Proto-AGI horizon)

## Synced sci-flow milestones (v0.4)

- **M-PROTO-AGI:** 12-member ensemble; $\Phi_{\max}$; consensus over $(E,\mathrm{OMEGA},P,R)$
- **M-OMEGA-DELTA-G:** F-OMEGA-DECOR confirmed aggregate (OMEGA span 0.604, genesis span 0.0)
- **D1×L3 ledger:** 2 admissible items; `e_endo_support=partial`
- **G2 E01:** 8-world partial eval (1 domain; EUIR 100% vs reactive 0%)
- **M-3D-EXPRESS:** 9/9 cells pass (3783.4 ms, 2026-09-05)
- **M-O adjunct/shadow bridge:** Tier C; `e_endo_support=none`
- M-LIVE-PATH, Graphitti CI, CF-7, CF-4 do(Z) — see v0.3 entries

## Honest abstract bullets (do not overclaim)

- C2-scoped **partial** support for $E_{\mathrm{endo}}$ at best; not closure
- Proto-AGI ensemble is **operational**, not biological; no AGI\* certificate
- F-OMEGA-DECOR **confirmed aggregate** — OMEGA is decorative w.r.t. $\Delta G$ on matched shadow bridge
- G2 E01 covers 8/20 worlds × 1/3 domains only
- $\theta_E,\theta_\Omega,\theta_P,\theta_R,\Delta T$ remain **TBD**
- T-PROTO-01 ensemble batch **proposed**, not executed in this paper
- OMEGA/Kuramoto/DSR/EOI-$k$ alone never imply AGI\* or $\tau_{AGI}$
- All harnesses: `claim_allowed=false`

## Figures (Proto-AGI paper)

`cf4_ablation_bars`, `cube_status_heatmap` — PDF in `arxiv/proto_agi_horizon/figures/` (copied from `arxiv/figures/`).

## Figures (I05 — EIA + 3D cube)

`cube_status_heatmap`, `express_pipeline`, `cf4_ablation_bars`, `dag` — PDF+PNG in `arxiv/figures/` and `arxiv/sci_flow_3d_cube/figures/`.

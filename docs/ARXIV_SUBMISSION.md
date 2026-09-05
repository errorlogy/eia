# arXiv Submission Packages

**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Version:** v0.4 (September 2026)  
**Claim ceiling:** C2 — `claim_allowed=false`; no AGI\* claims in papers.

## Upload strategy (M-ARXIV-PROTO-AGI)

**Primary (sole) arXiv upload:** `arxiv/proto_agi_horizon/main.tex` — the most comprehensive horizon paper (proto-AGI ensemble, Max consensus, OMEGA→ΔG bridge, Miller analog-waves bridge, metrics catalog, manifesto/NAMM lineage).

| Package | arXiv upload | Role |
|---------|--------------|------|
| **`arxiv/proto_agi_horizon/`** | **Yes — upload this** | Standalone horizon monograph; §Code and Data Availability; repo tag `sci-flow-v0.3` |
| `arxiv/main.tex` | **No — deferred** | Repo companion (EIA framework v0.3); cited from proto paper only |
| `arxiv/sci_flow_3d_cube/` | **No — deferred** | Repo companion (3D Evidence Cube theory); cited from proto paper only |

Companion LaTeX for EIA framework and 3D cube remains in-repo under tag `sci-flow-v0.3`; proto paper states they are **not** separate arXiv submissions.

## Build (proto only)

```powershell
make arxiv-proto-agi-compile
make arxiv-proto-agi-package
make check-sci-tier0
```

Optional (companions, not packaged for upload):

```powershell
make arxiv-compile
make arxiv-3d-cube-compile
python scripts/arxiv_toolkit/generate_figures.py   # I05 figures (EIA + 3D cube)
```

## Submission tarball (local, not committed)

Large binaries are **not** tracked in git. Regenerate before upload:

| Package | Path |
|---------|------|
| **Proto-AGI Horizon (upload)** | `arxiv/proto_agi_horizon_arXiv_submission.tar.gz` |

Deferred companions (regenerate only if editing those sources):

| Package | Path |
|---------|------|
| EIA framework | `arxiv_arXiv_submission.tar.gz` (repo root) |
| 3D Evidence Cube | `arxiv/sci_flow_3d_cube_arXiv_submission.tar.gz` |

## Upload checklist (single tarball)

- [ ] Recompile proto paper (`make arxiv-proto-agi-compile`)
- [ ] Regenerate proto tarball (`make arxiv-proto-agi-package`)
- [ ] Verify `claim_allowed=false` and no AGI\* in abstract
- [ ] Verify C2 ceiling stated; §Code and Data Availability before References
- [ ] Verify bib: `kuznetsov2026eia` + `sci-flow-v0.3`; artifact URLs under `research/sci_flow/...`
- [ ] Run tier-0 smoke (`make check-sci-tier0`)
- [ ] Upload `arxiv/proto_agi_horizon_arXiv_submission.tar.gz` to arXiv
- [ ] arXiv comment: cite repo companions (`arxiv/main.tex`, `arxiv/sci_flow_3d_cube/main.tex`) at tag `sci-flow-v0.3`, not as co-submissions

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

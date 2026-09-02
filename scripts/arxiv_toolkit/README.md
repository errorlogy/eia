# arXiv Toolkit (I01 / I03)

Ported from [AI_NATIVE_GOV](https://github.com/errorlogy) generic arXiv workflow for EIA papers.

**Task crosswalk:** [docs/CURSOR_TASKS.md](../../docs/CURSOR_TASKS.md) — **I01** arXiv v0.1 problematization; **I03** sci-flow 3D Evidence Cube standalone (C2 ceiling; no AGI\* claims in edits).

## Layout

```text
PROACTIVE_AI/
├── arxiv/
│   ├── main.tex                    # I01 v0.2 framework paper
│   ├── references.bib
│   ├── main.pdf
│   ├── figures/                    # I05 figures (dag.pdf, drive_decay.pdf, …)
│   └── sci_flow_3d_cube/           # I03 3D Evidence Cube standalone
│       ├── main.tex
│       ├── sections_empirical.tex
│       ├── references.bib          # merged (base + references_empirical.bib)
│       ├── references_empirical.bib
│       └── figures/
└── scripts/arxiv_toolkit/
    ├── compile_paper.py
    ├── clean_and_package.py
    ├── fetch_literature.py
    ├── generate_figures.py
    └── requirements.txt
```

## Prerequisites

- **LaTeX:** `latexmk` (MiKTeX / TeX Live) for compile; `pdflatex` fallback if `latexmk` missing.
- **Python (optional):** install toolkit deps only when using fetch/clean/figures scripts:

```powershell
pip install -r scripts/arxiv_toolkit/requirements.txt
```

## I01 workflow

From repo root (`PROACTIVE_AI/`):

### 1. Compile and verify PDF

```powershell
python scripts/arxiv_toolkit/compile_paper.py
# or explicitly:
python scripts/arxiv_toolkit/compile_paper.py -d arxiv
```

## I03 workflow (3D Evidence Cube standalone)

```powershell
python scripts/arxiv_toolkit/compile_paper.py -d arxiv/sci_flow_3d_cube
# or:
make arxiv-3d-cube-compile
make arxiv-3d-cube-package
```

Produces `sci_flow_3d_cube_arXiv_submission.tar.gz` next to `arxiv/sci_flow_3d_cube/`.

### 2. Fetch literature (verified BibTeX via arXiv API)

```powershell
python scripts/arxiv_toolkit/fetch_literature.py -q "proactive LLM agents endogenous" -n 5 -o arxiv/references.bib
```

### 3. Generate figures (placeholder until I05)

```powershell
python scripts/arxiv_toolkit/generate_figures.py
```

### 4. Clean and package for arXiv upload

```powershell
python scripts/arxiv_toolkit/clean_and_package.py
```

Produces `arxiv_arXiv_submission.tar.gz` next to `arxiv/`.

## Makefile shortcuts

```powershell
make arxiv-compile
make arxiv-package
make arxiv-3d-cube-compile
make arxiv-3d-cube-package
```

## Notes

- Do **not** copy AI_NATIVE_GOV `.venv`; use `requirements.txt` above.
- `make check-sci-tier0` is independent of this toolkit.
- Paper edits stay within C2 ceiling; see `research/sci_flow/config.yaml` claim ladder.

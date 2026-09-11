# Sci-Flow 3D Evidence Cube — Standalone arXiv Paper

Theory-focused standalone article on the EIA 3D Evidence Cube methodology. Empirical results are assembled separately via `sections_empirical.tex`.

## Files

| File | Role |
|------|------|
| `main.tex` | Theory sections (axes, layers, matrix, EIA bridge) |
| `sections_empirical.tex` | Placeholder for empirical agent |
| `references.bib` | Bibliography (theory + sci-flow internal refs) |

## Compile

From this directory:

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Or with `latexmk`:

```bash
latexmk -pdf main.tex
```

## Epistemic ceiling

- Active claim ladder ceiling: **C2**
- No AGI$^{*}$ claim
- Partial cube cells do not raise C-level

## Related workspace docs

- `research/sci_flow/SCI_FLOW_3D_CUBE.md`
- `research/sci_flow/CAUSAL_ENDOGENEITY.md`
- `research/sci_flow/STABLE_ENDOGENEITY.md`
- `research/sci_flow/EIA_PROOF_PROTOCOL.md`

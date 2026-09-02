.PHONY: check-sci-tier0 arxiv-compile arxiv-package arxiv-3d-cube-compile arxiv-3d-cube-package

# M-CLI Phase 0 — Tier 0 ATT baseline + M-EXPRESS-CI 3D cube smoke (no LLM). See docs/ENDOGENEITY_IMPLEMENTATION_PLAN.md
check-sci-tier0:
	python scripts/check_sci_tier0.py

# I01 arXiv problematization — see scripts/arxiv_toolkit/README.md
arxiv-compile:
	python scripts/arxiv_toolkit/compile_paper.py -d arxiv

arxiv-package:
	python scripts/arxiv_toolkit/clean_and_package.py -d arxiv

# I03 arXiv 3D Evidence Cube standalone — see scripts/arxiv_toolkit/README.md
arxiv-3d-cube-compile:
	python scripts/arxiv_toolkit/compile_paper.py -d arxiv/sci_flow_3d_cube

arxiv-3d-cube-package:
	python scripts/arxiv_toolkit/clean_and_package.py -d arxiv/sci_flow_3d_cube

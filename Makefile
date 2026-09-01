.PHONY: check-sci-tier0 arxiv-compile arxiv-package

# M-CLI Phase 0 — Tier 0 ATT baseline (no LLM). See docs/ENDOGENEITY_IMPLEMENTATION_PLAN.md
check-sci-tier0:
	python scripts/check_sci_tier0.py

# I01 arXiv problematization — see scripts/arxiv_toolkit/README.md
arxiv-compile:
	python scripts/arxiv_toolkit/compile_paper.py -d arxiv

arxiv-package:
	python scripts/arxiv_toolkit/clean_and_package.py -d arxiv

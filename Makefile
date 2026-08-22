.PHONY: check-sci-tier0

# M-CLI Phase 0 — Tier 0 ATT baseline (no LLM). See docs/ENDOGENEITY_IMPLEMENTATION_PLAN.md
check-sci-tier0:
	python scripts/check_sci_tier0.py

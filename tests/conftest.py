"""Shared pytest fixtures and optional vendor gates for CI."""

from __future__ import annotations

from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
_NEURAXON2 = _REPO_ROOT / "research" / "vendor" / "neuraxon" / "neuraxon2.py"
_GRAPHITTI_REGRESSION_XML = (
    _REPO_ROOT
    / "research"
    / "vendor"
    / "graphitti"
    / "Testing"
    / "RegressionTesting"
    / "GoodOutput"
    / "Cpu"
    / "test-tiny-out.xml"
)

has_neuraxon_vendor = _NEURAXON2.is_file()
has_graphitti_regression_fixture = _GRAPHITTI_REGRESSION_XML.is_file()

requires_neuraxon_vendor = pytest.mark.skipif(
    not has_neuraxon_vendor,
    reason=(
        "research/vendor/neuraxon not in tree (main excludes vendor snapshot; "
        "see .github/workflows/graphitti-witness.yml)"
    ),
)
requires_graphitti_regression_fixture = pytest.mark.skipif(
    not has_graphitti_regression_fixture,
    reason="research/vendor/graphitti regression GoodOutput not in tree",
)

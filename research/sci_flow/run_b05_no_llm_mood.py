#!/usr/bin/env python3
"""M-B05: no-LLM-mood structural harness (D1×L1 invariant).

Proves internal drives are not reducible to LLM mood/embedding proxy.
Output: M-B05_no_llm_mood_2026-09-02.json + markdown witness.

claim_allowed=false · Tier 0 · C2 ceiling · no AGI* · no WoE→main merge.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCI_FLOW = Path(__file__).resolve().parent
MAIN_SRC = REPO / "src"

if str(MAIN_SRC) not in sys.path:
    sys.path.insert(0, str(MAIN_SRC))
if str(SCI_FLOW) not in sys.path:
    sys.path.insert(0, str(SCI_FLOW))

from b05_no_llm_mood_harness import run_b05_batch  # noqa: E402

ARTIFACT_STEM = "M-B05_no_llm_mood_2026-09-02"


def _markdown_summary(payload: dict[str, object]) -> str:
    checks = payload.get("checks", [])
    lines = [
        f"# {ARTIFACT_STEM} — no-LLM-mood structural test (D1×L1)",
        "",
        f"**Date:** {payload.get('date', '')}",
        "**Branch:** `research/cursor-starter-v0.2-woe-eis`",
        "**Claim ceiling:** C2 — `claim_allowed=false`, no AGI*",
        "**Tier:** 0 (no live LLM)",
        "",
        "## Hypothesis",
        "",
        "Internal drive vector \\(d_t\\) is computed from BeliefField structural",
        "gradients — not from LLM narrative mood or token embedding similarity.",
        "A mock embedding mood proxy is **orthogonal**: identical mood with different",
        "gradients yields different drives; different mood with identical gradients",
        "yields identical drives.",
        "",
        "## Checks",
        "",
        "| Check | OK | Detail |",
        "|-------|----|--------|",
    ]
    for row in checks:
        ok = "✓" if row.get("ok") else "✗"
        detail = str(row.get("detail", "")).replace("|", "\\|")
        if len(detail) > 80:
            detail = detail[:77] + "..."
        lines.append(f"| `{row.get('name', '')}` | {ok} | {detail} |")
    lines.extend(
        [
            "",
            "## Results",
            "",
            f"- Checks pass: {payload.get('n_pass', 0)}/{payload.get('n_checks', 0)}",
            f"- Harness passed: **{payload.get('passed', False)}**",
            "",
            "## Falsifiers",
            "",
            "- F-NARR: drives reducible to LLM mood narrative (rejected if orthogonality holds)",
            "- F-EMBED: drives = cosine-to-median embedding plateau (rejected; structural gradients only)",
            "",
            "## Command",
            "",
            "```bash",
            "python research/sci_flow/run_b05_no_llm_mood.py",
            "```",
            "",
            "## Cross-links",
            "",
            "- [`STABLE_ENDOGENEITY.md`](STABLE_ENDOGENEITY.md) — drive field \\(d_t\\) in multi-loop stack",
            "- [`CAUSAL_ENDOGENEITY.md`](CAUSAL_ENDOGENEITY.md) — D1×L1 causal bar",
            "- `constitution/invariants.yaml` — `drive_policy.no_llm_mood: true`",
            "- [`src/eia/drives/__init__.py`](../../src/eia/drives/__init__.py) — DriveEngine",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    result = run_b05_batch(REPO)
    today = date.today().isoformat()
    payload: dict[str, object] = {
        "artifact_id": ARTIFACT_STEM,
        "date": today,
        "branch": "research/cursor-starter-v0.2-woe-eis",
        **result.to_dict(),
    }

    json_path = SCI_FLOW / f"{ARTIFACT_STEM}.json"
    md_path = SCI_FLOW / f"{ARTIFACT_STEM}.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_path.write_text(_markdown_summary(payload), encoding="utf-8")

    summary = {k: v for k, v in payload.items() if k != "checks"}
    print(json.dumps(summary, indent=2))
    print(f"wrote {json_path}")
    print(f"wrote {md_path}")
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

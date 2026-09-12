"""T-KAI-11 — Interactive 3D TopoLang visualization export + schema validation."""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
VIZ_DIR = ROOT / "viz"
if str(VIZ_DIR) not in sys.path:
    sys.path.insert(0, str(VIZ_DIR))

from export_topo_json import (  # noqa: E402
    export_all_examples,
    program_to_viz_json,
    validate_viz_json,
)

HARNESS_ID = "T-KAI-11"
DATE = date.today().isoformat()
ARTIFACT_ID = f"{HARNESS_ID}_{DATE}"
EXAMPLE_TOPO = ROOT / "topo_lang" / "examples" / "if_then_else.topo"
HTML_PATH = VIZ_DIR / "topo_program_3d.html"


def run_experiment() -> dict[str, Any]:
    payload_if = program_to_viz_json(EXAMPLE_TOPO)
    schema_errors = validate_viz_json(payload_if)
    export_paths = export_all_examples()

    slugs = [k for k in export_paths if k not in ("manifest", "bundle_js")]
    programs_ok = len(slugs) >= 3
    schema_ok = len(schema_errors) == 0
    html_ok = HTML_PATH.is_file()
    bundle_ok = (VIZ_DIR / "programs_bundle.js").is_file()

    return {
        "harness_id": HARNESS_ID,
        "artifact_id": ARTIFACT_ID,
        "date": DATE,
        "strand": "kairologos_standalone",
        "theory_section": "§1 TopoLang 3D syntax visualization",
        "schema_version": payload_if.get("schema_version"),
        "example_program": "if_then_else.topo",
        "exported_programs": slugs,
        "export_count": len(slugs),
        "html_path": str(HTML_PATH),
        "bundle_js": str(VIZ_DIR / "programs_bundle.js"),
        "schema_validation": {
            "errors": schema_errors,
            "pass": schema_ok,
        },
        "smoke_checks": {
            "schema_valid": schema_ok,
            "min_three_programs": programs_ok,
            "html_exists": html_ok,
            "bundle_js_exists": bundle_ok,
        },
        "lemma_results": {
            "L-TOPO-VIZ-1": {
                "pass": schema_ok and programs_ok,
                "description": "Export if_then_else.topo to valid viz JSON schema",
            },
            "L-TOPO-VIZ-2": {
                "pass": html_ok and bundle_ok,
                "description": "HTML viz + programs_bundle.js present for file:// loading",
            },
        },
        "sample_node_count": len(payload_if["nodes"]),
        "sample_edge_count": len(payload_if["edges"]),
        "execution_path": payload_if["execution"]["path"],
        "open_questions": {
            "interactive_3d_topo_syntax": schema_ok and html_ok,
        },
        "interpretation_notes": [
            "Visualization is illustrative — geodesic animation mirrors TopoInterpreter path.",
            "Not evidence for external ND attractor; standalone Kairologos research artifact.",
        ],
    }


def write_artifacts(payload: dict[str, Any]) -> tuple[Path, Path]:
    artifacts = ROOT / "artifacts"
    artifacts.mkdir(parents=True, exist_ok=True)
    json_path = artifacts / f"{ARTIFACT_ID}.json"
    md_path = artifacts / f"{ARTIFACT_ID}.md"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    checks = payload["smoke_checks"]
    md = "\n".join(
        [
            f"# {ARTIFACT_ID}",
            "",
            "**Strand:** Kairologos standalone (not EIA)",
            "",
            "## Question",
            "Can TopoLang `.topo` programs export to a valid JSON schema and load in an interactive 3D viewer?",
            "",
            "## Summary",
            f"- Exported programs: **{payload['export_count']}** ({', '.join(payload['exported_programs'])})",
            f"- Schema validation (if_then_else): **{'PASS' if checks['schema_valid'] else 'FAIL'}**",
            f"- HTML viz: `{payload['html_path']}`",
            f"- Execution path: `{' → '.join(payload['execution_path'])}`",
            "",
            "## Open viz",
            f"```",
            f"python research/kairologos_standalone/run_t_kai_11_viz.py",
            f"```",
            "",
        ]
    )
    md_path.write_text(md + "\n", encoding="utf-8")
    return json_path, md_path


def main() -> dict[str, Any]:
    payload = run_experiment()
    json_path, md_path = write_artifacts(payload)
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    return payload


if __name__ == "__main__":
    main()

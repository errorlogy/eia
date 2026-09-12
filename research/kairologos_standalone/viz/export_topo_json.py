"""Export .topo programs to JSON for the interactive 3D visualizer."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TOPO_ROOT = ROOT / "topo_lang"
VIZ_DIR = Path(__file__).resolve().parent
PROGRAMS_DIR = VIZ_DIR / "programs"
EXAMPLES_DIR = TOPO_ROOT / "examples"

if str(TOPO_ROOT) not in sys.path:
    sys.path.insert(0, str(TOPO_ROOT))

from interpreter import TopoInterpreter  # noqa: E402
from parser import load_topo  # noqa: E402

VIZ_SCHEMA_VERSION = "1.0"

NODE_KINDS = {"concept", "operator", "braid-crossing"}
EDGE_RELATIONS = {"geodesic", "braid-over", "braid-under", "lift", "loop"}


def program_to_viz_json(path: str | Path) -> dict[str, Any]:
    """Parse a .topo file and build the visualization JSON schema."""
    topo_path = Path(path)
    program = load_topo(topo_path)

    trace = TopoInterpreter(program).execute()

    return {
        "schema_version": VIZ_SCHEMA_VERSION,
        "source_file": topo_path.name,
        "name": program.name,
        "layer": program.layer,
        "curvature": program.curvature,
        "entry": program.entry,
        "exit": program.exit,
        "nodes": [n.to_dict() for n in program.nodes.values()],
        "edges": [e.to_dict() for e in program.edges],
        "execution": {
            "path": trace.path,
            "phases": trace.phases,
            "order_parameter": trace.order_parameter,
            "final_vector": trace.final_vector.tolist(),
        },
        "representation_dimension": program.representation_dimension(),
    }


def validate_viz_json(payload: dict[str, Any]) -> list[str]:
    """Return a list of schema validation errors (empty if valid)."""
    errors: list[str] = []
    required_top = {
        "schema_version",
        "name",
        "layer",
        "curvature",
        "entry",
        "exit",
        "nodes",
        "edges",
        "execution",
    }
    for key in required_top:
        if key not in payload:
            errors.append(f"missing top-level key: {key}")

    if not isinstance(payload.get("nodes"), list) or not payload["nodes"]:
        errors.append("nodes must be a non-empty list")
    else:
        for i, node in enumerate(payload["nodes"]):
            for key in ("name", "kind", "position", "phase", "param", "glyph"):
                if key not in node:
                    errors.append(f"nodes[{i}] missing key: {key}")
            if node.get("kind") not in NODE_KINDS:
                errors.append(f"nodes[{i}] invalid kind: {node.get('kind')}")
            pos = node.get("position")
            if not isinstance(pos, list) or len(pos) != 3:
                errors.append(f"nodes[{i}] position must be [x,y,z]")

    if not isinstance(payload.get("edges"), list):
        errors.append("edges must be a list")
    else:
        for i, edge in enumerate(payload["edges"]):
            for key in ("source", "target", "relation", "weight"):
                if key not in edge:
                    errors.append(f"edges[{i}] missing key: {key}")
            if edge.get("relation") not in EDGE_RELATIONS:
                errors.append(f"edges[{i}] invalid relation: {edge.get('relation')}")

    execution = payload.get("execution", {})
    if not isinstance(execution.get("path"), list) or not execution["path"]:
        errors.append("execution.path must be a non-empty list")
    if not isinstance(execution.get("phases"), dict):
        errors.append("execution.phases must be a dict")

    return errors


def _slug_from_path(path: Path) -> str:
    return path.stem


def export_program(path: str | Path, *, out_dir: Path | None = None) -> Path:
    """Export one .topo file to viz/programs/<slug>.json."""
    topo_path = Path(path)
    payload = program_to_viz_json(topo_path)
    errors = validate_viz_json(payload)
    if errors:
        raise ValueError(f"Schema validation failed for {topo_path.name}: {errors}")

    dest_dir = out_dir or PROGRAMS_DIR
    dest_dir.mkdir(parents=True, exist_ok=True)
    out_path = dest_dir / f"{_slug_from_path(topo_path)}.json"
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return out_path


def export_all_examples(*, out_dir: Path | None = None) -> dict[str, Path]:
    """Export every .topo example to JSON; also write manifest + bundle JS."""
    dest_dir = out_dir or PROGRAMS_DIR
    dest_dir.mkdir(parents=True, exist_ok=True)

    paths: dict[str, Path] = {}
    bundle: dict[str, Any] = {}

    for topo_path in sorted(EXAMPLES_DIR.glob("*.topo")):
        slug = _slug_from_path(topo_path)
        out_path = export_program(topo_path, out_dir=dest_dir)
        paths[slug] = out_path
        bundle[slug] = json.loads(out_path.read_text(encoding="utf-8"))

    manifest = {
        "schema_version": VIZ_SCHEMA_VERSION,
        "programs": [
            {
                "slug": slug,
                "name": bundle[slug]["name"],
                "layer": bundle[slug]["layer"],
                "source_file": bundle[slug]["source_file"],
                "node_count": len(bundle[slug]["nodes"]),
                "edge_count": len(bundle[slug]["edges"]),
            }
            for slug in sorted(bundle)
        ],
    }
    manifest_path = dest_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    paths["manifest"] = manifest_path

    bundle_js = (
        "// Auto-generated by export_topo_json.py — do not edit\n"
        f"window.TOPO_PROGRAMS = {json.dumps(bundle, ensure_ascii=False)};\n"
        f"window.TOPO_MANIFEST = {json.dumps(manifest, ensure_ascii=False)};\n"
    )
    bundle_path = VIZ_DIR / "programs_bundle.js"
    bundle_path.write_text(bundle_js, encoding="utf-8")
    paths["bundle_js"] = bundle_path

    return paths


def main() -> dict[str, Path]:
    paths = export_all_examples()
    for slug, path in paths.items():
        print(f"Wrote {path}")
    return paths


if __name__ == "__main__":
    main()

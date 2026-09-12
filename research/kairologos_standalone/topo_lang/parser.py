"""Human-readable .topo / .t3d parser — spatial declarations, not C-like blocks."""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np

from program import NodeKind, TopoEdge, TopoNode, TopoProgram

_COORD_RE = re.compile(
    r"@\s*\(\s*([+-]?\d*\.?\d+)\s*,\s*([+-]?\d*\.?\d+)\s*,\s*([+-]?\d*\.?\d+)\s*\)"
)
_KV_RE = re.compile(r"(\w+)\s*=\s*([+-]?\d*\.?\d+)")


def _parse_coord(text: str) -> np.ndarray:
    match = _COORD_RE.search(text)
    if not match:
        raise ValueError(f"Missing @ (x,y,z) coordinate in: {text}")
    return np.array([float(match.group(i)) for i in range(1, 4)], dtype=float)


def _parse_kv(text: str) -> dict[str, float]:
    return {m.group(1): float(m.group(2)) for m in _KV_RE.finditer(text)}


def parse_topo(text: str) -> TopoProgram:
    program = TopoProgram()
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue

        if line.startswith("@program"):
            program.name = line.split(maxsplit=1)[1].strip()
        elif line.startswith("@layer"):
            program.layer = line.split(maxsplit=1)[1].strip()
        elif line.startswith("@curvature"):
            program.curvature = float(line.split(maxsplit=1)[1].strip())
        elif line.startswith("@entry"):
            program.entry = line.split(maxsplit=1)[1].strip()
        elif line.startswith("@exit"):
            program.exit = line.split(maxsplit=1)[1].strip()
        elif line.startswith("node "):
            body = line[len("node ") :]
            name, rest = body.split(":", 1)
            name = name.strip()
            kind_str, coord_part = rest.split("@", 1)
            kind = NodeKind(kind_str.strip())
            pos = _parse_coord("@" + coord_part)
            kv = _parse_kv(coord_part)
            glyph = ""
            if " :" in coord_part or coord_part.rstrip().endswith(":"):
                glyph_part = coord_part.split(":", 1)[-1].strip()
                if glyph_part:
                    glyph = glyph_part.split()[0]
            program.add_node(
                TopoNode(
                    name=name,
                    kind=kind,
                    position=pos,
                    phase=kv.get("phase", 0.0),
                    param=kv.get("param", 0.0),
                    glyph=glyph,
                )
            )
        elif line.startswith("edge "):
            body = line[len("edge ") :]
            src_tgt, _, attrs = body.partition(":")
            src, tgt = [p.strip() for p in src_tgt.split("->", 1)]
            kv = _parse_kv(attrs)
            relation = "geodesic"
            for token in attrs.split():
                if token in ("geodesic", "braid-over", "braid-under", "lift", "loop"):
                    relation = token
                    break
            program.add_edge(
                TopoEdge(
                    source=src,
                    target=tgt,
                    relation=relation,
                    weight=kv.get("weight", 1.0),
                )
            )
    return program


def load_topo(path: str | Path) -> TopoProgram:
    return parse_topo(Path(path).read_text(encoding="utf-8"))

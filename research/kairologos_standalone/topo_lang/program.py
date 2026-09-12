"""3D topological program representation — not a linear token stream."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import numpy as np


class NodeKind(str, Enum):
    CONCEPT = "concept"
    OPERATOR = "operator"
    BRAID_CROSSING = "braid-crossing"


@dataclass
class TopoNode:
    name: str
    kind: NodeKind
    position: np.ndarray
    phase: float = 0.0
    glyph: str = ""
    param: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "kind": self.kind.value,
            "position": self.position.tolist(),
            "phase": self.phase,
            "glyph": self.glyph,
            "param": self.param,
        }


@dataclass
class TopoEdge:
    source: str
    target: str
    relation: str = "geodesic"
    weight: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "relation": self.relation,
            "weight": self.weight,
        }


@dataclass
class TopoProgram:
    name: str = "untitled"
    curvature: float = 0.0
    layer: str = "D11"
    nodes: dict[str, TopoNode] = field(default_factory=dict)
    edges: list[TopoEdge] = field(default_factory=list)
    entry: str | None = None
    exit: str | None = None

    def add_node(self, node: TopoNode) -> None:
        self.nodes[node.name] = node

    def add_edge(self, edge: TopoEdge) -> None:
        self.edges.append(edge)

    def neighbors(self, name: str) -> list[TopoEdge]:
        return [e for e in self.edges if e.source == name]

    def geodesic_length(self, a: str, b: str) -> float:
        pa = self.nodes[a].position
        pb = self.nodes[b].position
        euclid = float(np.linalg.norm(pb - pa))
        r2 = float(np.sum(((pa + pb) / 2.0) ** 2))
        factor = 1.0 / max(0.01, (1.0 + (self.curvature / 4.0) * r2) ** 2)
        return euclid * factor

    def representation_dimension(self) -> int:
        """Effective encoding dimension: 3 coords + phase + param per node, 2 per edge."""
        n = len(self.nodes)
        m = len(self.edges)
        return 3 * n + 2 * m + n

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "curvature": self.curvature,
            "layer": self.layer,
            "entry": self.entry,
            "exit": self.exit,
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "edges": [e.to_dict() for e in self.edges],
            "representation_dimension": self.representation_dimension(),
        }

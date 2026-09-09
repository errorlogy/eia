"""Connectome subgraph export — offline synthetic MVP + bundled tiny adjacency."""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

BRAIN_AI = Path(__file__).resolve().parents[1]
DATA = BRAIN_AI / "data"
BUNDLED_SUBGRAPH = DATA / "tiny_subgraph.json"


@dataclass(frozen=True, slots=True)
class ConnectomeSubgraph:
    """Small directed weighted subgraph for T-BRAIN-01 MVP."""

    source: str
    node_ids: tuple[str, ...]
    adjacency: tuple[tuple[int, ...], ...]
    weights: tuple[tuple[float, ...], ...]

    @property
    def n_nodes(self) -> int:
        return len(self.node_ids)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "n_nodes": self.n_nodes,
            "node_ids": list(self.node_ids),
            "adjacency": [list(row) for row in self.adjacency],
            "weights": [list(row) for row in self.weights],
        }


def _validate_square(matrix: list[list[Any]], n: int, name: str) -> None:
    if len(matrix) != n:
        raise ValueError(f"{name}: expected {n} rows, got {len(matrix)}")
    for i, row in enumerate(matrix):
        if len(row) != n:
            raise ValueError(f"{name}: row {i} length {len(row)} != {n}")


def load_bundled_subgraph(path: Path = BUNDLED_SUBGRAPH) -> ConnectomeSubgraph:
    """Load bundled tiny adjacency from ``data/tiny_subgraph.json``."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    node_ids = tuple(str(n) for n in payload["node_ids"])
    n = len(node_ids)
    adj = payload["adjacency"]
    wts = payload.get("weights") or adj
    _validate_square(adj, n, "adjacency")
    _validate_square(wts, n, "weights")
    return ConnectomeSubgraph(
        source=str(payload.get("source", "bundled_tiny")),
        node_ids=node_ids,
        adjacency=tuple(tuple(int(x) for x in row) for row in adj),
        weights=tuple(tuple(float(x) for x in row) for row in wts),
    )


def generate_synthetic_subgraph(
    *,
    n_nodes: int = 8,
    seed: int = 42,
    p_edge: float = 0.35,
) -> ConnectomeSubgraph:
    """Deterministic Erdős–Rényi-style subgraph for offline MVP."""
    rng = random.Random(seed)
    node_ids = tuple(f"n{i}" for i in range(n_nodes))
    adj: list[list[int]] = [[0] * n_nodes for _ in range(n_nodes)]
    wts: list[list[float]] = [[0.0] * n_nodes for _ in range(n_nodes)]
    for i in range(n_nodes):
        for j in range(n_nodes):
            if i == j:
                continue
            if rng.random() < p_edge:
                adj[i][j] = 1
                wts[i][j] = round(rng.uniform(0.3, 1.0), 3)
    return ConnectomeSubgraph(
        source=f"synthetic_er_{n_nodes}_seed{seed}",
        node_ids=node_ids,
        adjacency=tuple(tuple(row) for row in adj),
        weights=tuple(tuple(row) for row in wts),
    )


def load_subgraph(
    *,
    path: Path | None = None,
    n_nodes: int = 8,
    seed: int = 42,
    prefer_bundled: bool = True,
) -> ConnectomeSubgraph:
    """Load connectome subgraph: bundled file → synthetic fallback."""
    if path is not None and path.is_file():
        return load_bundled_subgraph(path)
    if prefer_bundled and BUNDLED_SUBGRAPH.is_file():
        return load_bundled_subgraph(BUNDLED_SUBGRAPH)
    return generate_synthetic_subgraph(n_nodes=n_nodes, seed=seed)


def export_connectome_stub(out_path: Path, *, seed: int = 42, n_nodes: int = 8) -> dict[str, Any]:
    """Write synthetic subgraph JSON (stub for future FlyWire export pipeline)."""
    subgraph = generate_synthetic_subgraph(n_nodes=n_nodes, seed=seed)
    payload = subgraph.to_dict()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload

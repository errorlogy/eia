"""Connectome subgraph export — offline synthetic MVP + bundled tiny adjacency."""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

BRAIN_AI = Path(__file__).resolve().parents[1]
DATA = BRAIN_AI / "data"
BUNDLED_SUBGRAPH = DATA / "tiny_subgraph.json"
GOOGLE_MALE_SUBGRAPH = DATA / "google_male_subgraph.json"
FLYWIRE_FEMALE_SUBGRAPH = DATA / "flywire_female_subgraph.json"

ConnectomeSourceName = Literal[
    "bundled_tiny",
    "synthetic",
    "google_male_cns",
    "flywire_female",
]

SOURCE_PATHS: dict[str, Path] = {
    "bundled_tiny": BUNDLED_SUBGRAPH,
    "google_male_cns": GOOGLE_MALE_SUBGRAPH,
    "flywire_female": FLYWIRE_FEMALE_SUBGRAPH,
}


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
    source_tag: str | None = None,
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
    tag = source_tag or f"synthetic_er_{n_nodes}_seed{seed}"
    return ConnectomeSubgraph(
        source=tag,
        node_ids=node_ids,
        adjacency=tuple(tuple(row) for row in adj),
        weights=tuple(tuple(row) for row in wts),
    )


def _load_source_path(path: Path, *, fallback_source: str, seed: int, n_nodes: int) -> ConnectomeSubgraph:
    """Load offline export or fall back to deterministic synthetic."""
    if path.is_file():
        return load_bundled_subgraph(path)
    return generate_synthetic_subgraph(
        n_nodes=n_nodes,
        seed=seed,
        source_tag=f"{fallback_source}_fallback_seed{seed}",
    )


def load_subgraph(
    *,
    path: Path | None = None,
    connectome_source: ConnectomeSourceName | str = "bundled_tiny",
    n_nodes: int = 8,
    seed: int = 42,
    prefer_bundled: bool = True,
) -> ConnectomeSubgraph:
    """Load connectome subgraph with offline-first source selection.

    ``connectome_source`` values:
    - ``bundled_tiny`` — ``data/tiny_subgraph.json`` (default CI path)
    - ``synthetic`` — deterministic Erdős–Rényi stub
    - ``google_male_cns`` — ``data/google_male_subgraph.json`` or synthetic fallback
    - ``flywire_female`` — ``data/flywire_female_subgraph.json`` or synthetic fallback
    """
    if path is not None and path.is_file():
        return load_bundled_subgraph(path)

    source = str(connectome_source)
    if source == "synthetic":
        return generate_synthetic_subgraph(n_nodes=n_nodes, seed=seed)
    if source == "google_male_cns":
        return _load_source_path(
            GOOGLE_MALE_SUBGRAPH,
            fallback_source="google_male_cns",
            seed=seed,
            n_nodes=n_nodes,
        )
    if source == "flywire_female":
        return _load_source_path(
            FLYWIRE_FEMALE_SUBGRAPH,
            fallback_source="flywire_female",
            seed=seed,
            n_nodes=n_nodes,
        )
    if prefer_bundled and BUNDLED_SUBGRAPH.is_file():
        return load_bundled_subgraph(BUNDLED_SUBGRAPH)
    return generate_synthetic_subgraph(n_nodes=n_nodes, seed=seed)


def export_google_male_subgraph(
    out_path: Path = GOOGLE_MALE_SUBGRAPH,
    *,
    seed: int = 42,
    n_nodes: int = 64,
) -> dict[str, Any]:
    """Write MaleCNS ego-network JSON or offline stub when data absent.

    Real exports: query ``male-cns:v1.0`` via neuprint-python (see ``data/README.md``).
    CI/tier-0 never require the 166k-neuron full connectome on disk.
    """
    if out_path.is_file():
        return load_bundled_subgraph(out_path).to_dict()

    subgraph = generate_synthetic_subgraph(
        n_nodes=n_nodes,
        seed=seed,
        source_tag="google_male_cns_stub",
    )
    payload = subgraph.to_dict()
    payload["export_note"] = (
        "Stub only — fetch MaleCNS ego-network offline per research/brain_ai/data/README.md"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def export_flywire_female_subgraph(
    out_path: Path = FLYWIRE_FEMALE_SUBGRAPH,
    *,
    seed: int = 42,
    n_nodes: int = 64,
) -> dict[str, Any]:
    """Write FlyWire v783 ego-network JSON or offline stub when data absent."""
    if out_path.is_file():
        return load_bundled_subgraph(out_path).to_dict()

    subgraph = generate_synthetic_subgraph(
        n_nodes=n_nodes,
        seed=seed,
        source_tag="flywire_female_stub",
    )
    payload = subgraph.to_dict()
    payload["export_note"] = (
        "Stub only — fetch FlyWire v783 ego-network offline per research/brain_ai/data/README.md"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def export_connectome_stub(out_path: Path, *, seed: int = 42, n_nodes: int = 8) -> dict[str, Any]:
    """Write synthetic subgraph JSON (legacy stub for bundled/synthetic export)."""
    subgraph = generate_synthetic_subgraph(n_nodes=n_nodes, seed=seed)
    payload = subgraph.to_dict()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload

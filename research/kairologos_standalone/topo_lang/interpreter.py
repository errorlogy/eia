"""TopoInterpreter — execution as geodesic flow + Kuramoto phase evolution."""

from __future__ import annotations

import heapq
import math
from dataclasses import dataclass
from typing import Any

import numpy as np

from program import NodeKind, TopoProgram


@dataclass
class ExecutionTrace:
    path: list[str]
    activations: list[np.ndarray]
    phases: dict[str, float]
    final_vector: np.ndarray
    order_parameter: float

    def signature(self) -> str:
        return "->".join(self.path)


class TopoInterpreter:
    """Execute a TopoProgram by propagating activation along geodesics."""

    def __init__(self, program: TopoProgram, *, coupling_k: float = 2.5, dim: int = 3):
        self.program = program
        self.coupling_k = coupling_k
        self.dim = dim

    def _metric(self, point: np.ndarray) -> np.ndarray:
        r2 = float(np.sum(point**2))
        denom = max(0.01, (1.0 + (self.program.curvature / 4.0) * r2) ** 2)
        return np.eye(self.dim) * (1.0 / denom)

    def _transform(self, node_name: str, packet: np.ndarray) -> np.ndarray:
        node = self.program.nodes[node_name]
        g = self._metric(node.position)
        out = g @ packet

        if node.kind == NodeKind.CONCEPT:
            out[0] += node.param
        elif node.kind == NodeKind.OPERATOR:
            angle = node.phase
            rot = np.array(
                [
                    [math.cos(angle), -math.sin(angle), 0.0],
                    [math.sin(angle), math.cos(angle), 0.0],
                    [0.0, 0.0, 1.0],
                ]
            )
            out = rot @ out
            out *= 1.0 + node.param * 0.1
        elif node.kind == NodeKind.BRAID_CROSSING:
            out = np.roll(out, 1) * math.cos(node.phase)
            if node.param:
                out += node.param * 0.05
        return out

    def _geodesic_path(self, start: str, goal: str) -> list[str]:
        """Dijkstra on geodesic edge costs."""
        dist: dict[str, float] = {start: 0.0}
        prev: dict[str, str | None] = {start: None}
        heap: list[tuple[float, str]] = [(0.0, start)]

        while heap:
            cost, u = heapq.heappop(heap)
            if u == goal:
                break
            if cost > dist.get(u, float("inf")):
                continue
            for edge in self.program.neighbors(u):
                v = edge.target
                step = self.program.geodesic_length(u, v) / max(edge.weight, 1e-6)
                alt = cost + step
                if alt < dist.get(v, float("inf")):
                    dist[v] = alt
                    prev[v] = u
                    heapq.heappush(heap, (alt, v))

        if goal not in prev:
            return [start]

        path: list[str] = []
        cur: str | None = goal
        while cur is not None:
            path.append(cur)
            cur = prev[cur]
        path.reverse()
        return path

    def _kuramoto_phases(self, path: list[str], *, steps: int = 40) -> dict[str, float]:
        names = list(self.program.nodes.keys())
        idx = {n: i for i, n in enumerate(names)}
        phases = np.array([self.program.nodes[n].phase for n in names], dtype=float)
        n = len(names)
        path_set = set(path)

        for _ in range(steps):
            diffs = phases[None, :] - phases[:, None]
            coupling = (self.coupling_k / n) * np.sum(np.sin(diffs), axis=1)
            for name in path_set:
                i = idx[name]
                coupling[i] *= 1.5
            phases = (phases + 0.05 * coupling) % (2.0 * math.pi)

        return {names[i]: float(phases[i]) for i in range(n)}

    def execute(
        self,
        initial_vector: list[float] | np.ndarray | None = None,
        *,
        entry: str | None = None,
        exit: str | None = None,
    ) -> ExecutionTrace:
        start = entry or self.program.entry
        goal = exit or self.program.exit
        if not start or not goal:
            raise ValueError("TopoProgram requires @entry and @exit (or explicit args)")

        path = self._geodesic_path(start, goal)
        packet = np.array(initial_vector if initial_vector is not None else [1.0, 0.0, 0.0], dtype=float)
        if packet.size < self.dim:
            packet = np.pad(packet, (0, self.dim - packet.size))
        packet = packet[: self.dim]

        activations: list[np.ndarray] = []
        for name in path:
            packet = self._transform(name, packet)
            activations.append(packet.copy())

        phases = self._kuramoto_phases(path)
        order_r = float(np.abs(np.mean(np.exp(1j * np.array(list(phases.values()))))))

        return ExecutionTrace(
            path=path,
            activations=activations,
            phases=phases,
            final_vector=packet,
            order_parameter=order_r,
        )


def compare_curvature_runs(
    program: TopoProgram,
    initial_vector: list[float],
    curvatures: list[float],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for k in curvatures:
        prog = TopoProgram(
            name=program.name,
            curvature=k,
            layer=program.layer,
            nodes=program.nodes,
            edges=program.edges,
            entry=program.entry,
            exit=program.exit,
        )
        trace = TopoInterpreter(prog).execute(initial_vector)
        rows.append(
            {
                "curvature": k,
                "final_norm": float(np.linalg.norm(trace.final_vector)),
                "path": trace.path,
                "order_parameter": trace.order_parameter,
            }
        )
    return rows

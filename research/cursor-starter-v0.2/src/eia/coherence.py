"""Oscillatory coordination primitives for the EIA Window of Emergence.

The implementation is a computational analogue, not a claim that an AI has
biological brain waves.  ``nominal_frequency_hz`` is deliberately sweepable;
the research signal is relative phase organization and metastability.
"""

from __future__ import annotations

import cmath
import math
import random
from collections import deque
from dataclasses import dataclass
from statistics import pstdev

from .math_model import clamp01


@dataclass(frozen=True, slots=True)
class CoherenceConfig:
    nominal_frequency_hz: float = 42.0
    frequency_offsets_hz: tuple[float, ...] = (-1.4, -0.8, -0.2, 0.3, 0.9, 1.5)
    base_coupling: float = 3.2
    pressure_coupling_gain: float = 7.0
    noise_radians_per_sqrt_second: float = 0.025
    metastability_window: int = 160
    delay_steps: int = 0
    coupling_graph: tuple[tuple[float, ...], ...] | None = None

    def __post_init__(self) -> None:
        if self.nominal_frequency_hz <= 0.0:
            raise ValueError("nominal_frequency_hz must be positive")
        if len(self.frequency_offsets_hz) < 3:
            raise ValueError("at least three modules are required")
        if self.base_coupling < 0.0 or self.pressure_coupling_gain < 0.0:
            raise ValueError("coupling values must be non-negative")
        if self.noise_radians_per_sqrt_second < 0.0:
            raise ValueError("noise must be non-negative")
        if self.metastability_window < 2:
            raise ValueError("metastability_window must be at least two")
        if self.delay_steps < 0:
            raise ValueError("delay_steps must be non-negative")
        count = len(self.frequency_offsets_hz)
        if self.coupling_graph is not None:
            if len(self.coupling_graph) != count:
                raise ValueError("coupling_graph must be square with module count")
            for row in self.coupling_graph:
                if len(row) != count:
                    raise ValueError("coupling_graph rows must match module count")
                if any(weight < 0.0 for weight in row):
                    raise ValueError("coupling weights must be non-negative")


def all_to_all_graph(n: int) -> tuple[tuple[float, ...], ...]:
    return tuple(tuple(0.0 if i == j else 1.0 for j in range(n)) for i in range(n))


def sparse_typed_graph(n: int = 6) -> tuple[tuple[float, ...], ...]:
    """Designed 6-module graph: pressure hub + memory/self/prospective + semantic/causal."""
    weights = [[0.0] * n for _ in range(n)]

    def undirected(i: int, j: int, weight: float = 1.0) -> None:
        if i == j or i >= n or j >= n:
            return
        weights[i][j] = weights[j][i] = weight

    for other in range(1, n):
        undirected(0, other, 1.0)
    if n >= 3:
        undirected(1, 2, 1.0)
    if n >= 4:
        undirected(2, 3, 1.0)
    if n >= 6:
        undirected(4, 5, 1.2)
        undirected(3, 4, 0.6)
    return tuple(tuple(row) for row in weights)


def permute_graph(
    graph: tuple[tuple[float, ...], ...],
    *,
    seed: int,
) -> tuple[tuple[float, ...], ...]:
    n = len(graph)
    order = list(range(n))
    random.Random(seed).shuffle(order)
    return tuple(tuple(graph[order[i]][order[j]] for j in range(n)) for i in range(n))


def k_zero_config(*, nominal_frequency_hz: float = 42.0) -> CoherenceConfig:
    return CoherenceConfig(
        nominal_frequency_hz=nominal_frequency_hz,
        base_coupling=0.0,
        pressure_coupling_gain=0.0,
    )


@dataclass(frozen=True, slots=True)
class CoherenceSample:
    elapsed_seconds: float
    order_parameter: float
    metastability: float
    collective_phase: float
    effective_coupling: float


class OscillatoryCoherenceField:
    """Small Kuramoto-style field coupling specialized cognitive modules.

    A common carrier frequency cancels from the Kuramoto order parameter.  This
    is useful experimentally: 42 Hz can be tested without making it a privileged
    causal constant. The relative offsets, coupling and delays organize the
    coordination regime.
    """

    def __init__(self, config: CoherenceConfig = CoherenceConfig(), *, seed: int = 0) -> None:
        self.config = config
        self._rng = random.Random(seed)
        self._phases = [
            self._rng.uniform(-math.pi, math.pi) for _ in config.frequency_offsets_hz
        ]
        self._history: deque[float] = deque(maxlen=config.metastability_window)
        self.elapsed_seconds = 0.0
        graph = config.coupling_graph or all_to_all_graph(len(self._phases))
        self._graph = graph
        delay = max(0, config.delay_steps)
        initial = tuple(self._phases)
        self._phase_log: deque[tuple[float, ...]] = deque(
            [initial] * (delay + 1),
            maxlen=delay + 1,
        )

    @property
    def module_count(self) -> int:
        return len(self._phases)

    @staticmethod
    def _order(phases: tuple[float, ...]) -> tuple[float, float]:
        field = sum((cmath.exp(1j * phase) for phase in phases), start=0j) / len(phases)
        return (clamp01(abs(field)), cmath.phase(field))

    def _interaction(self, index: int, phase: float, other_phases: tuple[float, ...], activations: tuple[float, ...]) -> float:
        weights = self._graph[index]
        weighted = 0.0
        total = 0.0
        for other, weight in enumerate(weights):
            if other == index or weight <= 0.0:
                continue
            weighted += weight * activations[other] * math.sin(other_phases[other] - phase)
            total += weight
        if total <= 0.0:
            return 0.0
        return weighted / total

    def neighborhood_orders(self, phases: tuple[float, ...]) -> tuple[float, ...]:
        locals_: list[float] = []
        for index, _phase in enumerate(phases):
            members = [index]
            for other, weight in enumerate(self._graph[index]):
                if other != index and weight > 0.0:
                    members.append(other)
            cluster = tuple(phases[item] for item in members)
            order, _ = self._order(cluster)
            locals_.append(order)
        return tuple(locals_)

    def step(
        self,
        dt_seconds: float,
        *,
        integration_pressure: float,
        module_activations: tuple[float, ...],
        scramble_phases: bool = False,
    ) -> CoherenceSample:
        if dt_seconds <= 0.0:
            raise ValueError("dt_seconds must be positive")
        if len(module_activations) != self.module_count:
            raise ValueError("module_activations must match module count")
        activations = tuple(clamp01(value) for value in module_activations)
        pressure = clamp01(integration_pressure)
        coupling = self.config.base_coupling + self.config.pressure_coupling_gain * pressure
        phases_before = tuple(self._phases)
        if self.config.delay_steps <= 0:
            other_phases = phases_before
        else:
            other_phases = self._phase_log[0]
        next_phases: list[float] = []
        for index, phase in enumerate(phases_before):
            if scramble_phases:
                next_phases.append(self._rng.uniform(-math.pi, math.pi))
                continue
            interaction = self._interaction(index, phase, other_phases, activations)
            frequency = self.config.nominal_frequency_hz + self.config.frequency_offsets_hz[index]
            noise = self._rng.gauss(0.0, 1.0)
            phase_velocity = 2.0 * math.pi * frequency + coupling * interaction
            updated = (
                phase
                + phase_velocity * dt_seconds
                + self.config.noise_radians_per_sqrt_second
                * math.sqrt(dt_seconds)
                * noise
            )
            next_phases.append(math.remainder(updated, 2.0 * math.pi))
        self._phases = next_phases
        self._phase_log.append(tuple(next_phases))
        self.elapsed_seconds += dt_seconds
        order, collective_phase = self._order(tuple(self._phases))
        self._history.append(order)
        metastability = pstdev(self._history) if len(self._history) > 1 else 0.0
        return CoherenceSample(
            elapsed_seconds=self.elapsed_seconds,
            order_parameter=order,
            metastability=clamp01(metastability),
            collective_phase=collective_phase,
            effective_coupling=coupling,
        )


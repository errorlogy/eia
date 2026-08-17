"""Metrics for the causal cognitive topology of initiative formation."""

from __future__ import annotations

from dataclasses import dataclass

from .causal import CausalLedger


@dataclass(frozen=True, slots=True)
class SourceMass:
    internal: float
    ambient: float
    user_request: float

    @property
    def request_independence(self) -> float:
        return max(0.0, min(1.0, 1.0 - self.user_request))


@dataclass(frozen=True, slots=True)
class TopologyMetrics:
    source_mass: SourceMass
    internal_transition_density: float
    depth: int
    branching_factor: float


class CognitiveTopology:
    """Analyze paths into a selected initiative without anthropomorphic claims.

    Edge mass is divided uniformly among parents in this reference version.
    Learned or calibrated causal weights can replace that choice later.
    """

    INTERNAL_ROOTS = {"memory", "clock", "health"}
    AMBIENT_ROOTS = {"observation", "sensor_event"}
    USER_ROOTS = {"user_event", "user_request"}
    INTERNAL_TRANSITIONS = {"belief", "drive", "goal", "memory", "clock", "health"}

    def __init__(self, ledger: CausalLedger) -> None:
        self.ledger = ledger

    def _source_mass(self, node_id: str, memo: dict[str, SourceMass]) -> SourceMass:
        if node_id in memo:
            return memo[node_id]
        node = self.ledger.get(node_id)
        if not node.parents:
            if node.node_type in self.USER_ROOTS:
                result = SourceMass(0.0, 0.0, 1.0)
            elif node.node_type in self.AMBIENT_ROOTS:
                result = SourceMass(0.0, 1.0, 0.0)
            else:
                result = SourceMass(1.0, 0.0, 0.0)
            memo[node_id] = result
            return result
        weight = 1.0 / len(node.parents)
        parent_mass = [self._source_mass(parent, memo) for parent in node.parents]
        result = SourceMass(
            internal=sum(item.internal for item in parent_mass) * weight,
            ambient=sum(item.ambient for item in parent_mass) * weight,
            user_request=sum(item.user_request for item in parent_mass) * weight,
        )
        memo[node_id] = result
        return result

    def _depth(self, node_id: str, memo: dict[str, int]) -> int:
        if node_id in memo:
            return memo[node_id]
        node = self.ledger.get(node_id)
        value = 0 if not node.parents else 1 + max(self._depth(parent, memo) for parent in node.parents)
        memo[node_id] = value
        return value

    def measure(self, target_node_id: str) -> TopologyMetrics:
        ancestors = self.ledger.ancestors(target_node_id)
        source_mass = self._source_mass(target_node_id, {})
        transitions = (self.ledger.get(target_node_id), *ancestors)
        density = sum(
            node.node_type in self.INTERNAL_TRANSITIONS for node in transitions
        ) / len(transitions)
        non_leaf = tuple(node for node in transitions if node.parents)
        branching = (
            sum(len(node.parents) for node in non_leaf) / len(non_leaf) if non_leaf else 0.0
        )
        return TopologyMetrics(
            source_mass=source_mass,
            internal_transition_density=density,
            depth=self._depth(target_node_id, {}),
            branching_factor=branching,
        )


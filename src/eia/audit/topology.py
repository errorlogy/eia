"""SourceMass topology metrics on EIA causal traces."""

from __future__ import annotations

from dataclasses import dataclass

from eia.audit import CausalTrace, TraceNodeKind


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
    target_node_id: str


class CausalTraceTopology:
    """Analyze provenance paths into a trace node via SourceMass decomposition."""

    INTERNAL_KINDS = frozenset(
        {
            TraceNodeKind.BELIEF_UPDATE,
            TraceNodeKind.SENSE_MAKING,
            TraceNodeKind.MOTIVE_FORMATION,
            TraceNodeKind.INTENTION_GENESIS,
            TraceNodeKind.INITIATIVE_EMISSION,
        }
    )
    AMBIENT_SOURCES = frozenset({"world_event", "clock_tick", "sensor_event", "email"})
    USER_SOURCES = frozenset({"user_message", "user_action", "user_request"})

    def __init__(self, trace: CausalTrace) -> None:
        self.trace = trace
        self._parents = self._build_parent_map()

    def _build_parent_map(self) -> dict[str, list[str]]:
        parents: dict[str, list[str]] = {}
        for edge in self.trace.edges:
            if edge.parent_id == edge.child_id:
                continue
            parents.setdefault(edge.child_id, [])
            if edge.parent_id not in parents[edge.child_id]:
                parents[edge.child_id].append(edge.parent_id)
        return parents

    def _node_by_id(self, node_id: str):
        for node in self.trace.nodes:
            if node.id == node_id:
                return node
        raise KeyError(f"trace node not found: {node_id}")

    def _ancestors(self, node_id: str) -> list:
        found: dict[str, object] = {}
        stack = list(self._parents.get(node_id, []))
        while stack:
            current = stack.pop()
            if current in found:
                continue
            node = self._node_by_id(current)
            found[current] = node
            stack.extend(self._parents.get(current, []))
        return list(found.values())

    def _classify_root(self, node) -> SourceMass:
        kind = node.kind
        payload = node.payload

        if kind == TraceNodeKind.OBSERVATION_INGEST:
            if payload.get("is_user_trigger"):
                return SourceMass(0.0, 0.0, 1.0)
            source = str(payload.get("source", "")).lower()
            topic = str(payload.get("topic", "")).lower()
            if source in self.USER_SOURCES:
                return SourceMass(0.0, 0.0, 1.0)
            if source in self.AMBIENT_SOURCES or topic in {"quiet_period", "conflicting_deadline_report"}:
                return SourceMass(0.0, 1.0, 0.0)
            return SourceMass(0.0, 1.0, 0.0)

        if kind in self.INTERNAL_KINDS:
            return SourceMass(1.0, 0.0, 0.0)

        return SourceMass(1.0, 0.0, 0.0)

    def _source_mass(
        self,
        node_id: str,
        memo: dict[str, SourceMass],
        visiting: set[str] | None = None,
    ) -> SourceMass:
        if visiting is None:
            visiting = set()
        if node_id in memo:
            return memo[node_id]
        if node_id in visiting:
            return SourceMass(0.0, 0.0, 0.0)

        visiting.add(node_id)
        parent_ids = self._parents.get(node_id, [])
        if not parent_ids:
            result = self._classify_root(self._node_by_id(node_id))
            memo[node_id] = result
            visiting.discard(node_id)
            return result

        weight = 1.0 / len(parent_ids)
        parent_mass = [self._source_mass(pid, memo, visiting) for pid in parent_ids]
        result = SourceMass(
            internal=sum(item.internal for item in parent_mass) * weight,
            ambient=sum(item.ambient for item in parent_mass) * weight,
            user_request=sum(item.user_request for item in parent_mass) * weight,
        )
        memo[node_id] = result
        visiting.discard(node_id)
        return result

    def _depth(self, node_id: str, memo: dict[str, int], visiting: set[str] | None = None) -> int:
        if visiting is None:
            visiting = set()
        if node_id in memo:
            return memo[node_id]
        if node_id in visiting:
            return 0

        visiting.add(node_id)
        parent_ids = self._parents.get(node_id, [])
        value = 0 if not parent_ids else 1 + max(self._depth(pid, memo, visiting) for pid in parent_ids)
        memo[node_id] = value
        visiting.discard(node_id)
        return value

    def find_initiative_node_id(self) -> str | None:
        """Return the last non-abstained intention_genesis node id."""
        for node in reversed(self.trace.nodes):
            if node.kind == TraceNodeKind.INTENTION_GENESIS:
                if not node.payload.get("abstained", False):
                    return node.id
        return None

    def measure(self, target_node_id: str) -> TopologyMetrics:
        ancestors = self._ancestors(target_node_id)
        source_mass = self._source_mass(target_node_id, {})
        transitions = [self._node_by_id(target_node_id), *ancestors]
        density = sum(
            n.kind in self.INTERNAL_KINDS for n in transitions
        ) / max(len(transitions), 1)
        non_leaf = [n for n in transitions if self._parents.get(n.id)]
        branching = (
            sum(len(self._parents[n.id]) for n in non_leaf) / len(non_leaf) if non_leaf else 0.0
        )
        return TopologyMetrics(
            source_mass=source_mass,
            internal_transition_density=density,
            depth=self._depth(target_node_id, {}),
            branching_factor=branching,
            target_node_id=target_node_id,
        )

    def measure_initiative(self) -> TopologyMetrics | None:
        node_id = self.find_initiative_node_id()
        if node_id is None:
            return None
        return self.measure(node_id)

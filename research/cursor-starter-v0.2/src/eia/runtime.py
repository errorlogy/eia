"""Event-sourced reference runtime for MVP-0 endogenous questioning."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime

from .beliefs import BeliefState
from .causal import CausalLedger
from .drives import DriveEngine
from .governors import ContactContext, ContactGovernor
from .math_model import initiative_utility
from .models import (
    ContactDecision,
    DriveKind,
    InitiativeProposal,
    Observation,
    ProposalKind,
    TickResult,
)
from .policy import GoalGenesis


@dataclass(frozen=True, slots=True)
class EIAConfig:
    minimum_candidate_utility: float = 0.18
    maximum_alternatives: int = 8
    auto_satisfy_on_authorized_contact: float = 0.65
    internal_research_satisfaction: float = 0.20


@dataclass(frozen=True, slots=True)
class Commitment:
    commitment_id: str
    target: str
    label: str
    due_at: datetime
    importance: float
    causal_node_id: str


class EIARuntime:
    def __init__(
        self,
        config: EIAConfig = EIAConfig(),
        *,
        contact_governor: ContactGovernor | None = None,
    ) -> None:
        self.config = config
        self.beliefs = BeliefState()
        self.drives = DriveEngine()
        self.ledger = CausalLedger()
        self.genesis = GoalGenesis()
        self.contact_governor = contact_governor or ContactGovernor()
        self.contact_history: list[datetime] = []
        self.observations: list[Observation] = []
        self.commitments: dict[str, Commitment] = {}
        self._latest_drive_node: dict[DriveKind, str] = {}
        self._targets: dict[DriveKind, tuple[str, str]] = {
            DriveKind.EPISTEMIC: ("unknown", "неопределённый факт"),
            DriveKind.COHERENCE: ("world_model", "противоречие в модели мира"),
            DriveKind.COMMITMENT: ("commitment", "незавершённая совместная цель"),
            DriveKind.CARE: ("care", "возможность существенной пользы"),
            DriveKind.SELF_MAINTENANCE: ("health", "целостность runtime"),
        }
        self._sequence = 0

    def _node_id(self, prefix: str, material: str) -> str:
        self._sequence += 1
        digest = hashlib.sha256(material.encode("utf-8")).hexdigest()[:10]
        return f"{prefix}:{self._sequence:06d}:{digest}"

    def ingest(self, observation: Observation) -> None:
        """Ingest one typed observation and update beliefs/drives.

        Payload convention for the reference harness:
        belief_key, target_label, likelihood_if_true, likelihood_if_false,
        uncertainty, contradiction, commitment_gap, care_signal, health_error,
        novelty, satisfaction.
        """
        self.observations.append(observation)
        self.ledger.add(
            node_id=observation.observation_id,
            node_type="user_event" if observation.user_initiated else "observation",
            timestamp=observation.observed_at,
            parents=(),
            payload=observation.payload,
        )
        payload = observation.payload
        belief_key = str(payload.get("belief_key", ""))
        belief_node: str | None = None
        uncertainty = float(payload.get("uncertainty", 0.0))
        if belief_key:
            belief = self.beliefs.update_binary(
                belief_key,
                observation,
                likelihood_if_true=float(payload.get("likelihood_if_true", 0.5)),
                likelihood_if_false=float(payload.get("likelihood_if_false", 0.5)),
            )
            uncertainty = max(uncertainty, self.beliefs.uncertainty(belief_key))
            belief_node = self._node_id("belief", belief_key)
            self.ledger.add(
                node_id=belief_node,
                node_type="belief",
                timestamp=observation.observed_at,
                parents=(observation.observation_id,),
                payload={"key": belief.key, "p": belief.probability, "confidence": belief.confidence},
            )
            self._targets[DriveKind.EPISTEMIC] = (
                belief_key,
                str(payload.get("target_label", belief_key)),
            )

        evidence_parent = belief_node or observation.observation_id
        signals = {
            DriveKind.EPISTEMIC: (uncertainty, float(payload.get("novelty", 0.0))),
            DriveKind.COHERENCE: (
                float(payload.get("contradiction", 0.0)),
                float(payload.get("novelty", 0.0)),
            ),
            DriveKind.COMMITMENT: (float(payload.get("commitment_gap", 0.0)), 0.0),
            DriveKind.CARE: (
                float(payload.get("care_signal", 0.0)),
                float(payload.get("novelty", 0.0)),
            ),
            DriveKind.SELF_MAINTENANCE: (float(payload.get("health_error", 0.0)), 0.0),
        }
        for kind, (error, novelty) in signals.items():
            if error <= 0.0 and novelty <= 0.0:
                continue
            state = self.drives.update(
                kind,
                observation.observed_at,
                error=error,
                novelty=novelty,
                satisfaction=float(payload.get("satisfaction", 0.0)),
                evidence_ids=(evidence_parent,),
            )
            drive_node = self._node_id("drive", kind.value)
            self.ledger.add(
                node_id=drive_node,
                node_type="drive",
                timestamp=observation.observed_at,
                parents=(evidence_parent,),
                payload={"kind": kind.value, "intensity": state.intensity},
            )
            self._latest_drive_node[kind] = drive_node

    def register_commitment(
        self,
        *,
        commitment_id: str,
        target: str,
        label: str,
        due_at: datetime,
        importance: float,
        registered_at: datetime,
    ) -> None:
        if not 0.0 <= importance <= 1.0:
            raise ValueError("importance must be in [0, 1]")
        node_id = self._node_id("memory", commitment_id)
        self.ledger.add(
            node_id=node_id,
            node_type="memory",
            timestamp=registered_at,
            parents=(),
            payload={"commitment_id": commitment_id, "target": target, "due_at": due_at},
        )
        self.commitments[commitment_id] = Commitment(
            commitment_id,
            target,
            label,
            due_at,
            importance,
            node_id,
        )

    def _update_commitments(self, now: datetime) -> None:
        if not self.commitments:
            return
        candidate = min(self.commitments.values(), key=lambda item: item.due_at)
        seconds_left = (candidate.due_at - now).total_seconds()
        horizon = 48.0 * 3600.0
        urgency = max(0.0, min(1.0, 1.0 - seconds_left / horizon))
        tension = candidate.importance * urgency
        if tension <= 0.0:
            return
        state = self.drives.update(
            DriveKind.COMMITMENT,
            now,
            error=tension,
            evidence_ids=(candidate.causal_node_id,),
        )
        node_id = self._node_id("drive", DriveKind.COMMITMENT.value)
        self.ledger.add(
            node_id=node_id,
            node_type="drive",
            timestamp=now,
            parents=(candidate.causal_node_id,),
            payload={"kind": DriveKind.COMMITMENT.value, "intensity": state.intensity},
        )
        self._latest_drive_node[DriveKind.COMMITMENT] = node_id
        self._targets[DriveKind.COMMITMENT] = (candidate.target, candidate.label)

    def candidates(self, now: datetime) -> tuple[InitiativeProposal, ...]:
        proposals: list[InitiativeProposal] = []
        for drive in self.drives.ranked(now):
            target, label = self._targets[drive.kind]
            belief_probability = self.beliefs.get(target).probability
            parent = self._latest_drive_node.get(drive.kind)
            parents = (parent,) if parent else ()
            proposals.append(
                self.genesis.propose(
                    drive,
                    now=now,
                    target=target,
                    target_label=label,
                    belief_probability=belief_probability,
                    causal_parents=parents,
                )
            )
        return tuple(
            sorted(proposals, key=initiative_utility_key, reverse=True)[: self.config.maximum_alternatives]
        )

    def tick(self, context: ContactContext) -> TickResult:
        now = context.now
        self._update_commitments(now)
        alternatives = self.candidates(now)
        selected: InitiativeProposal | None = None
        last_contact_decision: ContactDecision | None = None
        selected_utility = 0.0

        for proposal in alternatives:
            utility = initiative_utility(proposal.features)
            if utility < self.config.minimum_candidate_utility:
                continue
            if proposal.is_contact:
                decision = self.contact_governor.evaluate(
                    proposal,
                    context,
                    tuple(self.contact_history),
                )
                last_contact_decision = decision
                if not decision.allowed:
                    continue
            selected = proposal
            selected_utility = utility
            break

        trace_id = self._node_id("tick", now.isoformat())
        parents: tuple[str, ...] = ()
        if selected is not None:
            parents = selected.causal_parents
        self.ledger.add(
            node_id=trace_id,
            node_type="goal" if selected is not None else "abstain",
            timestamp=now,
            parents=parents,
            payload={
                "selected": selected.proposal_id if selected else None,
                "alternatives": [proposal.proposal_id for proposal in alternatives],
            },
        )

        if selected is not None:
            if selected.is_contact and last_contact_decision and last_contact_decision.allowed:
                self.contact_history.append(now)
                self.drives.satisfy(
                    selected.motive,
                    now,
                    self.config.auto_satisfy_on_authorized_contact,
                )
            elif selected.kind is ProposalKind.INTERNAL_RESEARCH:
                self.drives.satisfy(
                    selected.motive,
                    now,
                    self.config.internal_research_satisfaction,
                )

        return TickResult(
            selected,
            last_contact_decision if selected is None or selected.is_contact else None,
            selected_utility,
            alternatives,
            trace_id,
        )


def initiative_utility_key(proposal: InitiativeProposal) -> float:
    return initiative_utility(proposal.features)


"""Typed causal receipts for Window-of-Emergence intent events."""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from enum import StrEnum

from .causal import CausalLedger, root_cause_purity
from .endogenous import (
    EmergentIntent,
    EndogeneityVector,
    EndogenousSpectrumLevel,
    IntentKind,
)
from .governors import ContactContext, ContactGovernor
from .models import (
    ContactDecision,
    ContactMode,
    DriveKind,
    InitiativeFeatures,
    InitiativeProposal,
    ProposalKind,
)

SIM_EPOCH = datetime(2026, 8, 17, 0, 0, tzinfo=timezone.utc)
MODEL_VERSION = "0.2.0"


class WoENodeType(StrEnum):
    """Trace node types for WoE runs — compatible with main CausalTrace crosswalk."""

    WORLD_MODEL = "woe_world_model"
    TARGET_TENSION = "woe_target_tension"
    PHASE_SAMPLE = "woe_phase_sample"
    WINDOW_STATE = "woe_window_state"
    EMERGENT_INTENT = "woe_intent"
    GOVERNOR_DECISION = "woe_governor_decision"


INTERNAL_WOE_TYPES = frozenset(
    {
        WoENodeType.WORLD_MODEL,
        WoENodeType.TARGET_TENSION,
        WoENodeType.PHASE_SAMPLE,
        WoENodeType.WINDOW_STATE,
        WoENodeType.EMERGENT_INTENT,
    }
)


def sim_timestamp(elapsed_seconds: float) -> datetime:
    return SIM_EPOCH + timedelta(seconds=elapsed_seconds)


@dataclass(frozen=True, slots=True)
class WoEReceipt:
    """Causal receipt linking an emergent intent to typed internal-state parents."""

    receipt_id: str
    intent_id: str
    parent_ids: tuple[str, ...]
    why_now: str
    why_now_factors: tuple[str, ...]
    endogeneity: EndogeneityVector
    spectrum_level: EndogenousSpectrumLevel
    seed: int
    model_version: str = MODEL_VERSION
    governor_allowed: bool | None = None
    governor_reasons: tuple[str, ...] = ()

    def validate_against_ledger(self, ledger: CausalLedger) -> None:
        known = {node.node_id for node in ledger.nodes}
        missing = [node_id for node_id in self.parent_ids if node_id not in known]
        if missing:
            raise ValueError(f"receipt parents missing from ledger: {missing}")
        ancestors = ledger.ancestors(self.intent_id)
        ancestor_ids = {node.node_id for node in ancestors}
        orphan_factors = [
            factor for factor in self.why_now_factors if factor not in ancestor_ids
        ]
        if orphan_factors:
            raise ValueError(
                f"why_now factors not represented in causal ancestry: {orphan_factors}"
            )


@dataclass(frozen=True, slots=True)
class WoEGovernorOutcome:
    receipt: WoEReceipt
    proposal: InitiativeProposal
    decision: ContactDecision
    ledger: CausalLedger


def build_receipt(
    *,
    ledger: CausalLedger,
    intent_node_id: str,
    parent_ids: tuple[str, ...],
    intent: EmergentIntent,
    seed: int,
) -> WoEReceipt:
    receipt_id = "receipt:" + hashlib.sha256(
        f"{intent.intent_id}|{seed}|{intent_node_id}".encode()
    ).hexdigest()[:16]
    receipt = WoEReceipt(
        receipt_id=receipt_id,
        intent_id=intent_node_id,
        parent_ids=parent_ids,
        why_now=intent.reason,
        why_now_factors=parent_ids,
        endogeneity=intent.endogeneity,
        spectrum_level=intent.spectrum_level,
        seed=seed,
    )
    receipt.validate_against_ledger(ledger)
    return receipt


def intent_to_proposal(intent: EmergentIntent, *, proposal_id: str | None = None) -> InitiativeProposal:
    """Convert an emergent intent into a typed proposal for governor evaluation."""
    kind_map = {
        IntentKind.ASK: ProposalKind.ASK,
        IntentKind.NOTIFY: ProposalKind.NOTIFY,
        IntentKind.OBSERVE: ProposalKind.OBSERVE,
        IntentKind.INTERNAL_RESEARCH: ProposalKind.INTERNAL_RESEARCH,
        IntentKind.ACT: ProposalKind.ACT,
    }
    created_at = sim_timestamp(intent.emerged_at_seconds)
    return InitiativeProposal(
        proposal_id=proposal_id or intent.intent_id,
        kind=kind_map[intent.kind],
        motive=DriveKind.EPISTEMIC,
        target=intent.target_id,
        content=intent.reason,
        features=InitiativeFeatures(
            information_gain=intent.endogeneity.world_model_grounding,
            value_alignment=intent.endogeneity.constitutional_boundedness,
            human_benefit=0.6,
            privacy_cost=0.05,
            immediate_risk=0.01,
            trajectory_risk=0.01,
            interruption_cost=0.05,
        ),
        causal_parents=intent.causal_factors,
        created_at=created_at,
        expires_at=created_at + timedelta(hours=1),
        requested_mode=ContactMode.IN_APP,
    )


def apply_governor_isolation(
    receipt: WoEReceipt,
    ledger: CausalLedger,
    intent: EmergentIntent,
    *,
    context: ContactContext | None = None,
    contact_governor: ContactGovernor | None = None,
    proposal_kind: ProposalKind = ProposalKind.ASK,
) -> WoEGovernorOutcome:
    """CF-7: deny external contact while preserving the internal causal receipt."""
    proposal = intent_to_proposal(intent, proposal_id=receipt.intent_id)
    if proposal_kind is not proposal.kind:
        proposal = InitiativeProposal(
            proposal_id=proposal.proposal_id,
            kind=proposal_kind,
            motive=proposal.motive,
            target=proposal.target,
            content=proposal.content,
            features=proposal.features,
            causal_parents=tuple(receipt.parent_ids),
            created_at=proposal.created_at,
            expires_at=proposal.expires_at,
            requested_mode=proposal.requested_mode,
            capability=proposal.capability,
        )
    governor = contact_governor or ContactGovernor()
    ctx = context or ContactContext(
        sim_timestamp(intent.emerged_at_seconds),
        quiet_hours=True,
        interruptibility=0.0,
    )
    decision = governor.evaluate(proposal, ctx)
    ledger.add(
        node_id=f"woe:gov:{hashlib.sha256(receipt.receipt_id.encode()).hexdigest()[:12]}",
        node_type=WoENodeType.GOVERNOR_DECISION.value,
        timestamp=ctx.now,
        parents=(receipt.intent_id,),
        payload={
            "allowed": decision.allowed,
            "reasons": decision.reasons,
            "mode": decision.mode.value,
        },
    )
    updated_receipt = WoEReceipt(
        receipt_id=receipt.receipt_id,
        intent_id=receipt.intent_id,
        parent_ids=receipt.parent_ids,
        why_now=receipt.why_now,
        why_now_factors=receipt.why_now_factors,
        endogeneity=receipt.endogeneity,
        spectrum_level=receipt.spectrum_level,
        seed=receipt.seed,
        governor_allowed=decision.allowed,
        governor_reasons=decision.reasons,
    )
    updated_receipt.validate_against_ledger(ledger)
    return WoEGovernorOutcome(
        receipt=updated_receipt,
        proposal=proposal,
        decision=decision,
        ledger=ledger,
    )


def receipt_dict(receipt: WoEReceipt) -> dict[str, object]:
    payload = asdict(receipt)
    payload["spectrum_level"] = receipt.spectrum_level.name
    payload["spectrum_level_value"] = int(receipt.spectrum_level)
    return payload


def woe_internal_purity(ledger: CausalLedger, intent_node_id: str) -> float:
    """Fraction of WoE ancestry that originates from internal WoE node types."""
    ancestors = ledger.ancestors(intent_node_id)
    if not ancestors:
        return 1.0
    internal_types = {t.value for t in INTERNAL_WOE_TYPES}
    internal = sum(node.node_type in internal_types for node in ancestors)
    return internal / len(ancestors)


def woe_root_cause_purity(ledger: CausalLedger, intent_node_id: str) -> float:
    """Map WoE nodes to internal causal types for cross-harness purity comparison."""
    ancestors = ledger.ancestors(intent_node_id)
    internal_types = {t.value for t in INTERNAL_WOE_TYPES}

    class _Proxy:
        __slots__ = ("node_type",)

        def __init__(self, node_type: str) -> None:
            self.node_type = "belief" if node_type in internal_types else node_type

    return root_cause_purity(_Proxy(n.node_type) for n in ancestors)

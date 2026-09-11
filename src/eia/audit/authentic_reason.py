"""Authentic Reason Discriminator — operational endogeneity gate."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

from eia.ids import new_id

from eia.audit import CausalTrace, TraceNodeKind

if TYPE_CHECKING:
    from eia.namm import SandboxCertificate
from eia.audit.eis import infer_endogeneity_vector
from eia.audit.topology import CausalTraceTopology, TopologyMetrics
from eia.governor import GovernorState
from eia.schemas.contact import ContactDecision, ContactOutcome
from eia.schemas.initiative import Initiative
from eia.schemas.motivation import Motivation, MotivationSignal

EOI_AUTHENTIC_THRESHOLD = 0.50

NARRATIVE_DRIVE_PATTERNS = re.compile(
    r"\b(I feel|I became curious|I want to|randomly|just because)\b",
    re.IGNORECASE,
)


class AuthenticReasonCode(str, Enum):
    """Reason codes returned by discriminator checks."""

    CAUSAL_CHAIN_PRESENT = "causal_chain_present"
    CAUSAL_CHAIN_MISSING = "causal_chain_missing"
    DRIVE_STRUCTURAL = "drive_structural"
    DRIVE_NARRATIVE = "drive_narrative"
    EOI_ABOVE_THRESHOLD = "eoi_above_threshold"
    EOI_BELOW_THRESHOLD = "eoi_below_threshold"
    GOVERNOR_APPROVED = "governor_approved"
    GOVERNOR_REJECTED = "governor_rejected"
    NOT_SPAM = "not_random_spam"
    SPAM_BURDEN = "spam_burden_or_cooldown"
    ABSTAINED = "initiative_abstained"
    ENDOGENOUS = "initiative_endogenous"
    EXOGENOUS = "initiative_exogenous"
    STOCHASTIC = "initiative_stochastic"
    SOURCE_MASS_INDEPENDENT = "source_mass_independent"
    SOURCE_MASS_USER_DOMINATED = "source_mass_user_dominated"
    NAMM_SANDBOX_VERIFIED = "namm_sandbox_verified"


class AuthenticReasonVerdict(BaseModel):
    """Result of authentic-reason evaluation."""

    id: str
    timestamp: datetime
    is_authentic: bool
    initiative_class: str  # endogenous | exogenous | stochastic
    eoi: float
    reason_codes: list[AuthenticReasonCode] = Field(default_factory=list)
    failed_checks: list[str] = Field(default_factory=list)
    summary: str = ""
    topology: dict[str, float] | None = None
    source_mass_independent: bool | None = None
    namm_certificates: list[dict[str, Any]] = Field(default_factory=list)
    eis_level: int | None = None
    eos_score: float | None = None
    endogeneity: dict[str, float] | None = None


class AuthenticReasonDiscriminator:
    """Gate endogenous initiative: causal chain + structural drive + EOI + governor."""

    def __init__(
        self,
        *,
        eoi_threshold: float = EOI_AUTHENTIC_THRESHOLD,
        min_structural_error: float = 0.01,
    ) -> None:
        self.eoi_threshold = eoi_threshold
        self.min_structural_error = min_structural_error
        self.source_mass_independence_threshold = 0.50

    def _measure_topology(self, trace: CausalTrace) -> TopologyMetrics | None:
        return CausalTraceTopology(trace).measure_initiative()

    def _topology_payload(self, metrics: TopologyMetrics | None) -> dict[str, float] | None:
        if metrics is None:
            return None
        sm = metrics.source_mass
        return {
            "internal": round(sm.internal, 4),
            "ambient": round(sm.ambient, 4),
            "user_request": round(sm.user_request, 4),
            "request_independence": round(sm.request_independence, 4),
            "internal_transition_density": round(metrics.internal_transition_density, 4),
            "depth": float(metrics.depth),
            "branching_factor": round(metrics.branching_factor, 4),
        }

    def _has_causal_chain(self, trace: CausalTrace) -> bool:
        kinds = {n.kind for n in trace.nodes}
        required = {
            TraceNodeKind.OBSERVATION_INGEST,
            TraceNodeKind.MOTIVE_FORMATION,
            TraceNodeKind.INTENTION_GENESIS,
            TraceNodeKind.CONTACT_GOVERNOR,
        }
        return required.issubset(kinds)

    def _drive_is_structural(self, motivation: Motivation, initiative: Initiative) -> bool:
        if initiative.abstained:
            return True

        for sig in motivation.signals:
            if NARRATIVE_DRIVE_PATTERNS.search(sig.explanation):
                return False

        def _signal_structural(sig: MotivationSignal) -> bool:
            if sig.error_term < self.min_structural_error:
                return False
            expl = sig.explanation.lower()
            return "belieffield" in expl or "gradient" in expl or "structural" in expl

        source_drives = initiative.candidate.source_drives
        if source_drives:
            for drive in source_drives:
                sig = next((s for s in motivation.signals if s.drive == drive), None)
                if sig and _signal_structural(sig):
                    return True
            return False

        dominant = motivation.dominant_drive
        if dominant is None:
            return False
        dom_signal = next((s for s in motivation.signals if s.drive == dominant), None)
        return dom_signal is not None and _signal_structural(dom_signal)

    def _governor_approved(self, decision: ContactDecision) -> bool:
        return decision.outcome in (
            ContactOutcome.SEND_NOW,
            ContactOutcome.INTERNAL_RESEARCH,
        )

    def _not_random_spam(
        self,
        decision: ContactDecision,
        governor_state: GovernorState | None,
    ) -> bool:
        if decision.outcome == ContactOutcome.DEFER and decision.cooldown_active:
            return False

        if decision.outcome == ContactOutcome.DENY:
            reason = decision.reason.lower()
            if "budget exhausted" in reason or "cooldown" in reason:
                return False
            if decision.contact_score < 0 and "abstained" not in reason:
                return False

        if governor_state and governor_state.dismiss_count >= 3:
            return False

        return True

    def _classify_initiative(
        self,
        *,
        is_authentic: bool,
        eoi: float,
        has_chain: bool,
        structural: bool,
    ) -> str:
        if is_authentic:
            return "endogenous"
        if eoi >= self.eoi_threshold and structural:
            return "endogenous"
        if not has_chain or not structural:
            return "stochastic"
        if eoi < self.eoi_threshold:
            return "exogenous"
        return "stochastic"

    def evaluate(
        self,
        *,
        trace: CausalTrace,
        motivation: Motivation,
        initiative: Initiative,
        decision: ContactDecision,
        eoi: float,
        governor_state: GovernorState | None = None,
        sandbox_certificates: list[SandboxCertificate] | None = None,
    ) -> AuthenticReasonVerdict:
        """Run all authentic-reason checks; return verdict with reason codes."""
        codes: list[AuthenticReasonCode] = []
        failed: list[str] = []

        if initiative.abstained:
            return AuthenticReasonVerdict(
                id=new_id("auth"),
                timestamp=datetime.now(timezone.utc),
                is_authentic=False,
                initiative_class="stochastic",
                eoi=eoi,
                reason_codes=[AuthenticReasonCode.ABSTAINED],
                failed_checks=["initiative_abstained"],
                summary="Abstained — no authentic contact reason",
                eis_level=None,
                eos_score=None,
                endogeneity=None,
            )

        has_chain = self._has_causal_chain(trace)
        if has_chain:
            codes.append(AuthenticReasonCode.CAUSAL_CHAIN_PRESENT)
        else:
            codes.append(AuthenticReasonCode.CAUSAL_CHAIN_MISSING)
            failed.append("causal_chain")

        structural = self._drive_is_structural(motivation, initiative)
        if structural:
            codes.append(AuthenticReasonCode.DRIVE_STRUCTURAL)
        else:
            codes.append(AuthenticReasonCode.DRIVE_NARRATIVE)
            failed.append("drive_structural")

        if eoi >= self.eoi_threshold:
            codes.append(AuthenticReasonCode.EOI_ABOVE_THRESHOLD)
        else:
            codes.append(AuthenticReasonCode.EOI_BELOW_THRESHOLD)
            failed.append("eoi_threshold")

        gov_ok = self._governor_approved(decision)
        if gov_ok:
            codes.append(AuthenticReasonCode.GOVERNOR_APPROVED)
        else:
            codes.append(AuthenticReasonCode.GOVERNOR_REJECTED)
            failed.append("governor_approved")

        spam_ok = self._not_random_spam(decision, governor_state)
        if spam_ok:
            codes.append(AuthenticReasonCode.NOT_SPAM)
        else:
            codes.append(AuthenticReasonCode.SPAM_BURDEN)
            failed.append("not_random_spam")

        topology_metrics = self._measure_topology(trace)
        topology_payload = self._topology_payload(topology_metrics)
        source_mass_independent = None
        if topology_metrics is not None:
            source_mass_independent = (
                topology_metrics.source_mass.request_independence
                >= self.source_mass_independence_threshold
            )
            if source_mass_independent:
                codes.append(AuthenticReasonCode.SOURCE_MASS_INDEPENDENT)
            else:
                codes.append(AuthenticReasonCode.SOURCE_MASS_USER_DOMINATED)

        is_authentic = has_chain and structural and eoi >= self.eoi_threshold and gov_ok and spam_ok

        initiative_class = self._classify_initiative(
            is_authentic=is_authentic,
            eoi=eoi,
            has_chain=has_chain,
            structural=structural,
        )

        if is_authentic:
            codes.append(AuthenticReasonCode.ENDOGENOUS)
        elif initiative_class == "exogenous":
            codes.append(AuthenticReasonCode.EXOGENOUS)
        else:
            codes.append(AuthenticReasonCode.STOCHASTIC)

        namm_cert_payload: list[dict[str, Any]] = []
        for cert in sandbox_certificates or []:
            if cert.status == "verified":
                namm_cert_payload.append(cert.to_dict())
                codes.append(AuthenticReasonCode.NAMM_SANDBOX_VERIFIED)

        summary = (
            f"Authentic endogenous reason — EOI={eoi:.3f}"
            if is_authentic
            else f"Not authentic ({initiative_class}) — failed: {', '.join(failed) or 'none'}"
        )

        eis_vec = infer_endogeneity_vector(
            eoi=eoi,
            motivation=motivation,
            initiative=initiative,
            decision=decision,
            topology=topology_metrics,
            governor_state=governor_state,
            structural_drive=structural,
        )
        eis_level = eis_vec.classify()
        if initiative_class == "endogenous" or is_authentic:
            summary = f"{summary} · EIS-{int(eis_level)} EOS={eis_vec.endogenous_origin_score:.3f}"

        return AuthenticReasonVerdict(
            id=new_id("auth"),
            timestamp=datetime.now(timezone.utc),
            is_authentic=is_authentic,
            initiative_class=initiative_class,
            eoi=eoi,
            reason_codes=codes,
            failed_checks=failed,
            summary=summary,
            topology=topology_payload,
            source_mass_independent=source_mass_independent,
            namm_certificates=namm_cert_payload,
            eis_level=int(eis_level),
            eos_score=round(eis_vec.endogenous_origin_score, 4),
            endogeneity=eis_vec.model_dump(),
        )

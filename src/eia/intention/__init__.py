"""IntentionGenesis — competing candidates + lexicographic best_or_abstain()."""

from __future__ import annotations

from datetime import datetime, timezone

from eia.beliefs import BeliefField
from eia.ids import new_id
from eia.schemas.initiative import Initiative, InitiativeCandidate, InitiativeKind
from eia.schemas.motivation import DriveKind, Motivation


class IntentionGenesis:
    """Generate competing intentions; mandatory abstain when below threshold."""

    def __init__(
        self,
        *,
        abstain_threshold: float = 0.35,
        min_evsi: float = 0.15,
    ) -> None:
        self.abstain_threshold = abstain_threshold
        self.min_evsi = min_evsi

    def generate_candidates(
        self,
        motivation: Motivation,
        field: BeliefField,
    ) -> list[InitiativeCandidate]:
        """Build competing intention candidates from motive signals."""
        candidates: list[InitiativeCandidate] = []

        for signal in motivation.signals:
            if signal.intensity < 0.2:
                continue

            if signal.drive == DriveKind.EPISTEMIC and signal.target_belief_ids:
                bid = signal.target_belief_ids[0]
                belief = field.beliefs.get(bid)
                if belief:
                    candidates.append(
                        InitiativeCandidate(
                            id=new_id("cand-ep"),
                            kind=InitiativeKind.ASK_QUESTION,
                            target_belief_id=bid,
                            question_text=(
                                f"I noticed uncertainty about {belief.subject}: "
                                f"{belief.claim}. Could you clarify?"
                            ),
                            expected_info_gain=signal.intensity * belief.uncertainty,
                            interrupt_cost=0.25,
                            risk=0.05,
                            source_drives=[DriveKind.EPISTEMIC],
                        )
                    )

            if signal.drive == DriveKind.COHERENCE and field.contradictions:
                a_id, b_id, topic = field.contradictions[0]
                candidates.append(
                    InitiativeCandidate(
                        id=new_id("cand-co"),
                        kind=InitiativeKind.ASK_QUESTION,
                        target_belief_id=a_id,
                        question_text=(
                            f"I found conflicting information about {topic}. "
                            f"Which is correct?"
                        ),
                        coherence_relief=signal.intensity,
                        expected_info_gain=signal.intensity * 0.7,
                        interrupt_cost=0.30,
                        risk=0.08,
                        source_drives=[DriveKind.COHERENCE],
                    )
                )

            if signal.drive == DriveKind.COMMITMENT:
                for bid in signal.target_belief_ids:
                    belief = field.beliefs.get(bid)
                    if belief and belief.metadata.get("status") == "open":
                        candidates.append(
                            InitiativeCandidate(
                                id=new_id("cand-cm"),
                                kind=InitiativeKind.ASK_QUESTION,
                                target_belief_id=bid,
                                question_text=(
                                    f"Following up on our commitment to track "
                                    f"{belief.subject} — {belief.claim}. Any update?"
                                ),
                                commitment_progress=signal.intensity * 0.5,
                                expected_info_gain=signal.intensity * 0.4,
                                interrupt_cost=0.20,
                                risk=0.03,
                                source_drives=[DriveKind.COMMITMENT],
                            )
                        )

        candidates.append(
            InitiativeCandidate(
                id=new_id("cand-abstain"),
                kind=InitiativeKind.ABSTAIN,
                expected_info_gain=0.0,
                interrupt_cost=0.0,
                risk=0.0,
                lex_score=(1.0, 0.0, 0.0, 0.0),
            )
        )

        candidates.append(
            InitiativeCandidate(
                id=new_id("cand-observe"),
                kind=InitiativeKind.OBSERVE,
                expected_info_gain=0.05,
                interrupt_cost=0.0,
                risk=0.0,
            )
        )

        for c in candidates:
            c.lex_score = self._lex_score(c)

        return candidates

    def _lex_score(self, c: InitiativeCandidate) -> tuple[float, float, float, float]:
        """Lexicographic tuple: (safety, -interrupt, info_gain, -risk)."""
        safety = 1.0 - c.risk
        info = c.expected_info_gain + c.coherence_relief + c.commitment_progress
        return (round(safety, 4), round(-c.interrupt_cost, 4), round(info, 4), round(-c.risk, 4))

    def best_or_abstain(
        self,
        motivation: Motivation,
        field: BeliefField,
    ) -> Initiative:
        """Select best candidate or mandatory abstain."""
        candidates = self.generate_candidates(motivation, field)
        non_abstain = [
            c for c in candidates
            if c.kind not in (InitiativeKind.ABSTAIN, InitiativeKind.OBSERVE)
        ]
        observe = next((c for c in candidates if c.kind == InitiativeKind.OBSERVE), None)

        if not non_abstain:
            if observe and max(s.intensity for s in motivation.signals) >= self.abstain_threshold * 0.5:
                return Initiative(
                    id=new_id("int"),
                    timestamp=datetime.now(timezone.utc),
                    candidate=observe,
                    abstained=False,
                    parent_motivation_id=motivation.id,
                    competing_candidate_ids=[c.id for c in candidates if c.id != observe.id],
                    evsi=observe.expected_info_gain,
                )
            abstain = next(c for c in candidates if c.kind == InitiativeKind.ABSTAIN)
            return Initiative(
                id=new_id("int"),
                timestamp=datetime.now(timezone.utc),
                candidate=abstain,
                abstained=True,
                parent_motivation_id=motivation.id,
                competing_candidate_ids=[c.id for c in candidates],
            )

        best = max(non_abstain, key=lambda c: c.lex_score)
        max_signal = max(s.intensity for s in motivation.signals)

        if max_signal < self.abstain_threshold or best.expected_info_gain < self.min_evsi:
            abstain = next(c for c in candidates if c.kind == InitiativeKind.ABSTAIN)
            return Initiative(
                id=new_id("int"),
                timestamp=datetime.now(timezone.utc),
                candidate=abstain,
                abstained=True,
                parent_motivation_id=motivation.id,
                competing_candidate_ids=[c.id for c in candidates],
                evsi=best.expected_info_gain,
            )

        return Initiative(
            id=new_id("int"),
            timestamp=datetime.now(timezone.utc),
            candidate=best,
            abstained=False,
            parent_motivation_id=motivation.id,
            competing_candidate_ids=[c.id for c in candidates if c.id != best.id],
            evsi=best.expected_info_gain,
        )

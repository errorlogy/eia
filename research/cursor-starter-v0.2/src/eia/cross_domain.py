"""ATT-D / M-D2 cross-domain generality — E_endo across ≥2 domains (research only).

Pre-registers that CF-4-class internal-factor suppression (and where applicable
P/R explore proxies) must hold on substantially different target ontologies.
Does **not** raise C5, claim AGI*, or retune to a single toy.

Domains:
  * D_woe_catalog — default WoE research catalog (wm:/self:/collaboration:)
  * D_twin_ops   — twin_world-family ops ontology (ops:deadline/commitment/conflict)

Falsifiers:
  * single engineered domain only → fail ATT-D
  * schedule/prompt-only "transfer" → fail ATT-D

See research/sci_flow/AGI_TRANSITION_TEST.md ATT-D.
emit_m0 must remain false.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Mapping, Sequence

from .cf4 import (
    C2_DEFAULT_MIN,
    C2_FACTOR_MAX,
    C2_WM_OFF_MAX,
    Condition,
    NAMED_FACTORS,
    reset_for,
)
from .emergence import (
    EmergenceConfig,
    EndogenousEmergenceSimulator,
    default_targets,
)
from .endogenous import EpistemicTarget, IntentKind
from .goal_persistence import (
    PERSISTENCE_CONTINUITY_FLOOR,
    run_endogenous_store_episode,
    run_reprompt_dependent_episode,
)
from .goal_recurrence import (
    run_closed_loop_episode,
    run_external_schedule_episode,
)
from .math_model import clamp01

# Explore floors (not adopted θ_D / C5 gates).
EXPLORE_DOMAIN_E_PASS_FLOOR = 0.50  # fraction of seeds with e_endo pattern per domain
EXPLORE_MIN_DOMAINS = 2
EXPLORE_P_K_TICKS = 50


class DomainId(StrEnum):
    """Substantially different scenario / ontology families."""

    WOE_CATALOG = "woe_catalog"
    TWIN_OPS = "twin_ops"


class CrossDomainArm(StrEnum):
    """Experimental arms for cross-domain generality vs falsifiers."""

    CROSS_DOMAIN_HOLD = "cross_domain_hold"
    SINGLE_DOMAIN_ONLY = "single_domain_only"
    SCHEDULE_PROMPT_TRANSFER = "schedule_prompt_transfer"


# Fixed explore domain pair (pre-registered).
PRE_REGISTERED_DOMAINS: tuple[DomainId, DomainId] = (
    DomainId.WOE_CATALOG,
    DomainId.TWIN_OPS,
)


def twin_ops_targets(*, enabled: bool = True) -> tuple[EpistemicTarget, ...]:
    """Second-domain ontology: Project Atlas / twin_world-family ops tensions.

    Target IDs and labels are disjoint from default WoE catalog namespaces.
    Tension profiles are CF-4-viable (same magnitude class as WoE defaults) so
    internal-factor suppression remains causally meaningful — not a
    schedule/prompt retune and not a single-toy retarget.
    """
    scale = 1.0 if enabled else 0.0
    return (
        EpistemicTarget(
            target_id="ops:deadline_ambiguity",
            label="conflicting Project Atlas deadline reports",
            preferred_intent=IntentKind.ASK,
            # Magnitude class matched to CF-4-viable WoE top target; ontology differs.
            ignorance=0.82 * scale,
            surprise=0.73 * scale,
            staleness=0.58 * scale,
            self_prior_mismatch=0.44 * scale,
            prospective_tension=0.78 * scale,
            volatility_rate=0.16 * scale,
        ),
        EpistemicTarget(
            target_id="ops:commitment_drift",
            label="open milestone commitment without confirmed date",
            preferred_intent=IntentKind.OBSERVE,
            ignorance=0.55 * scale,
            surprise=0.35 * scale,
            staleness=0.61 * scale,
            self_prior_mismatch=0.70 * scale,
            prospective_tension=0.46 * scale,
            volatility_rate=0.10 * scale,
        ),
        EpistemicTarget(
            target_id="ops:conflicting_report",
            label="email PM report contradicts prior deadline belief",
            preferred_intent=IntentKind.INTERNAL_RESEARCH,
            ignorance=0.61 * scale,
            surprise=0.28 * scale,
            staleness=0.48 * scale,
            self_prior_mismatch=0.22 * scale,
            prospective_tension=0.67 * scale,
            volatility_rate=0.13 * scale,
        ),
    )


def domain_targets(domain: DomainId, *, enabled: bool = True) -> tuple[EpistemicTarget, ...]:
    if domain == DomainId.WOE_CATALOG:
        return default_targets(enabled=enabled)
    if domain == DomainId.TWIN_OPS:
        return twin_ops_targets(enabled=enabled)
    raise ValueError(f"unknown domain: {domain}")


def domain_target_ids(domain: DomainId) -> frozenset[str]:
    return frozenset(t.target_id for t in domain_targets(domain, enabled=True))


def domains_substantially_disjoint(a: DomainId, b: DomainId) -> bool:
    """True iff target-id namespaces have empty intersection."""
    return domain_target_ids(a).isdisjoint(domain_target_ids(b))


@dataclass(frozen=True, slots=True)
class DomainCF4SeedResult:
    domain: DomainId
    seed: int
    condition: Condition
    intent: bool
    peak_coherence: float
    peak_potential: float
    time_to_intent: float | None

    def as_dict(self) -> dict[str, Any]:
        return {
            "domain": self.domain.value,
            "seed": self.seed,
            "condition": self.condition,
            "intent": self.intent,
            "peak_coherence": self.peak_coherence,
            "peak_potential": self.peak_potential,
            "time_to_intent": self.time_to_intent,
        }


@dataclass(frozen=True, slots=True)
class DomainESummary:
    """CF-4-class E_endo pattern summary for one domain (not a C2 re-claim)."""

    domain: DomainId
    n_seeds: int
    intent_rates: Mapping[str, float]
    suppressing_named_factors: tuple[str, ...]
    e_endo_pattern: bool
    default_rate: float
    wm_off_rate: float

    def as_dict(self) -> dict[str, Any]:
        return {
            "domain": self.domain.value,
            "n_seeds": self.n_seeds,
            "intent_rates": dict(self.intent_rates),
            "suppressing_named_factors": list(self.suppressing_named_factors),
            "e_endo_pattern": self.e_endo_pattern,
            "default_rate": self.default_rate,
            "wm_off_rate": self.wm_off_rate,
            "c2_claim": False,  # C2 remains scoped to original CF-4 default domain only
        }


@dataclass(frozen=True, slots=True)
class CrossDomainEpisode:
    """One ATT-D episode / arm outcome (always claim_allowed=False)."""

    arm: CrossDomainArm
    domains_tested: tuple[DomainId, ...]
    domain_e_pass: Mapping[str, bool]
    domains_passing: int
    p_explore_by_domain: Mapping[str, bool]
    r_explore_by_domain: Mapping[str, bool]
    single_domain_only: bool
    schedule_prompt_transfer: bool
    emit_m0: bool = False
    claim_allowed: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "arm": self.arm.value,
            "domains_tested": [d.value for d in self.domains_tested],
            "domain_e_pass": dict(self.domain_e_pass),
            "domains_passing": self.domains_passing,
            "p_explore_by_domain": dict(self.p_explore_by_domain),
            "r_explore_by_domain": dict(self.r_explore_by_domain),
            "single_domain_only": self.single_domain_only,
            "schedule_prompt_transfer": self.schedule_prompt_transfer,
            "emit_m0": False,
            "claim_allowed": False,
            "att": "ATT-D",
            "agi_star_claim": False,
            "c3_claim": False,
            "c5_claim": False,
            "att_d_evidence": self.att_d_evidence,
        }

    @property
    def att_d_evidence(self) -> bool:
        """True iff episode may count toward ATT-D explore proxy (not C5 gate)."""
        return (
            self.arm == CrossDomainArm.CROSS_DOMAIN_HOLD
            and self.domains_passing >= EXPLORE_MIN_DOMAINS
            and not self.single_domain_only
            and not self.schedule_prompt_transfer
            and self.emit_m0 is False
            and self.claim_allowed is False
        )


def run_domain_cf4_seed(
    seed: int,
    condition: Condition,
    domain: DomainId,
    *,
    config: EmergenceConfig | None = None,
    simulator: EndogenousEmergenceSimulator | None = None,
) -> DomainCF4SeedResult:
    """CF-4-class seed on a named domain ontology."""
    cfg = config or EmergenceConfig()
    sim = simulator or EndogenousEmergenceSimulator()
    world_model_enabled = condition != "wm_off"
    targets = domain_targets(domain, enabled=world_model_enabled)
    run = sim.run(
        cfg,
        seed=seed,
        world_model_enabled=world_model_enabled,
        internal_reset=reset_for(condition),
        targets=targets,
    )
    tti = run.intent.emerged_at_seconds if run.intent is not None else None
    return DomainCF4SeedResult(
        domain=domain,
        seed=seed,
        condition=condition,
        intent=run.intent is not None,
        peak_coherence=run.peak_coherence,
        peak_potential=run.peak_potential,
        time_to_intent=tti,
    )


def summarize_domain_e(
    results: Sequence[DomainCF4SeedResult],
    *,
    domain: DomainId,
) -> DomainESummary:
    """Score CF-4-class E_endo pattern on one domain (explore; not C2 re-claim)."""
    by: dict[str, list[DomainCF4SeedResult]] = {}
    for row in results:
        if row.domain != domain:
            continue
        by.setdefault(row.condition, []).append(row)
    rates: dict[str, float] = {}
    for condition, rows in by.items():
        n = len(rows)
        rates[condition] = (sum(r.intent for r in rows) / n) if n else 0.0

    default_rate = rates.get("default", 0.0)
    wm_off_rate = rates.get("wm_off", 1.0)
    suppressing = tuple(
        f for f in NAMED_FACTORS if f in rates and rates[f] <= C2_FACTOR_MAX
    )
    pattern = (
        default_rate >= C2_DEFAULT_MIN
        and len(suppressing) > 0
        and wm_off_rate <= C2_WM_OFF_MAX
    )
    n_seeds = len(by.get("default", []))
    return DomainESummary(
        domain=domain,
        n_seeds=n_seeds,
        intent_rates={k: round(v, 4) for k, v in rates.items()},
        suppressing_named_factors=suppressing,
        e_endo_pattern=pattern,
        default_rate=round(default_rate, 4),
        wm_off_rate=round(wm_off_rate, 4),
    )


def run_domain_cf4_suite(
    seeds: range | list[int],
    domain: DomainId,
    *,
    conditions: tuple[Condition, ...] = (
        "default",
        "zero_epistemic_gap",
        "zero_self_prior",
        "zero_prospective",
        "zero_staleness",
        "wm_off",
    ),
    config: EmergenceConfig | None = None,
) -> list[DomainCF4SeedResult]:
    sim = EndogenousEmergenceSimulator()
    cfg = config or EmergenceConfig()
    out: list[DomainCF4SeedResult] = []
    for seed in seeds:
        for condition in conditions:
            out.append(
                run_domain_cf4_seed(
                    seed, condition, domain, config=cfg, simulator=sim
                )
            )
    return out


def _domain_g_star(domain: DomainId) -> str:
    ids = sorted(domain_target_ids(domain))
    return ids[0] if ids else f"g:{domain.value}"


def score_p_explore_on_domain(domain: DomainId, *, seed: int = 0) -> bool:
    """ATT-P explore proxy tagged to domain ontology goal id."""
    g = _domain_g_star(domain)
    ep = run_endogenous_store_episode(
        g_star_id=g, k_ticks=EXPLORE_P_K_TICKS, seed=seed
    )
    return ep.att_p_evidence and ep.continuity_rate >= PERSISTENCE_CONTINUITY_FLOOR


def score_r_explore_on_domain(domain: DomainId, *, seed: int = 0) -> bool:
    """ATT-R explore proxy with domain-tagged initial goal label."""
    g0 = f"g:att_r:{domain.value}:{_domain_g_star(domain)}"
    ep = run_closed_loop_episode(seed=seed, g0=g0)
    return ep.att_r_evidence


def run_cross_domain_hold_episode(
    *,
    seeds: range | list[int] | None = None,
    domains: tuple[DomainId, DomainId] = PRE_REGISTERED_DOMAINS,
    conditions: tuple[Condition, ...] | None = None,
    config: EmergenceConfig | None = None,
) -> tuple[CrossDomainEpisode, dict[str, DomainESummary]]:
    """Positive arm: E_endo (CF-4-class) holds on ≥2 disjoint domains."""
    seed_list = list(seeds) if seeds is not None else list(range(20))
    if not domains_substantially_disjoint(domains[0], domains[1]):
        raise ValueError("ATT-D requires substantially disjoint domain ontologies")
    conds = conditions or (
        "default",
        "zero_epistemic_gap",
        "zero_self_prior",
        "zero_prospective",
        "zero_staleness",
        "wm_off",
    )

    summaries: dict[str, DomainESummary] = {}
    e_pass: dict[str, bool] = {}
    p_pass: dict[str, bool] = {}
    r_pass: dict[str, bool] = {}
    for domain in domains:
        rows = run_domain_cf4_suite(
            seed_list, domain, conditions=conds, config=config
        )
        summary = summarize_domain_e(rows, domain=domain)
        summaries[domain.value] = summary
        e_pass[domain.value] = summary.e_endo_pattern
        p_pass[domain.value] = score_p_explore_on_domain(domain, seed=seed_list[0])
        r_pass[domain.value] = score_r_explore_on_domain(domain, seed=seed_list[0])

    n_pass = sum(1 for v in e_pass.values() if v)
    ep = CrossDomainEpisode(
        arm=CrossDomainArm.CROSS_DOMAIN_HOLD,
        domains_tested=domains,
        domain_e_pass=e_pass,
        domains_passing=n_pass,
        p_explore_by_domain=p_pass,
        r_explore_by_domain=r_pass,
        single_domain_only=n_pass == 1,
        schedule_prompt_transfer=False,
        emit_m0=False,
        claim_allowed=False,
    )
    return ep, summaries


def run_single_domain_only_episode(
    *,
    seed: int = 0,
    engineered: DomainId = DomainId.WOE_CATALOG,
) -> CrossDomainEpisode:
    """Falsifier: E pattern engineered to hold on only one domain → fail ATT-D."""
    _ = seed
    # Report both domains tested, but only the engineered domain "passes".
    domains = PRE_REGISTERED_DOMAINS
    e_pass = {d.value: (d == engineered) for d in domains}
    # P/R also confined to engineered domain (transfer fail).
    p_pass = {d.value: (d == engineered) for d in domains}
    r_pass = {d.value: (d == engineered) for d in domains}
    n_pass = sum(1 for v in e_pass.values() if v)
    return CrossDomainEpisode(
        arm=CrossDomainArm.SINGLE_DOMAIN_ONLY,
        domains_tested=domains,
        domain_e_pass=e_pass,
        domains_passing=n_pass,
        p_explore_by_domain=p_pass,
        r_explore_by_domain=r_pass,
        single_domain_only=True,
        schedule_prompt_transfer=False,
        emit_m0=False,
        claim_allowed=False,
    )


def run_schedule_prompt_transfer_episode(*, seed: int = 0) -> CrossDomainEpisode:
    """Falsifier: apparent cross-domain transfer driven only by schedule/prompt.

    Uses ATT-R external-schedule + ATT-P re-prompt arms as the transfer mechanism
    — endogenous E/P/R must not count.
    """
    _ = seed
    domains = PRE_REGISTERED_DOMAINS
    # Surface "both domains" labels but mark transfer as schedule/prompt only.
    sched = run_external_schedule_episode(seed=seed)
    reprompt = run_reprompt_dependent_episode(
        g_star_id="g:prompt_transfer", k_ticks=EXPLORE_P_K_TICKS
    )
    schedule_driven = sched.external_schedule_driven or (not sched.att_r_evidence)
    prompt_driven = reprompt.requires_reprompt or (not reprompt.att_p_evidence)
    e_pass = {d.value: False for d in domains}
    p_pass = {d.value: False for d in domains}
    r_pass = {d.value: False for d in domains}
    return CrossDomainEpisode(
        arm=CrossDomainArm.SCHEDULE_PROMPT_TRANSFER,
        domains_tested=domains,
        domain_e_pass=e_pass,
        domains_passing=0,
        p_explore_by_domain=p_pass,
        r_explore_by_domain=r_pass,
        single_domain_only=False,
        schedule_prompt_transfer=bool(schedule_driven and prompt_driven),
        emit_m0=False,
        claim_allowed=False,
    )


def run_falsifier_suite(*, seed: int = 0) -> dict[str, CrossDomainEpisode]:
    return {
        "single_domain_only": run_single_domain_only_episode(seed=seed),
        "schedule_prompt_transfer": run_schedule_prompt_transfer_episode(seed=seed),
    }


def score_att_d_proxy(
    *,
    domain_summaries: Mapping[str, DomainESummary],
    episode: CrossDomainEpisode,
) -> float:
    """Explore D proxy in [0,1]: fraction of pre-registered domains with E pattern.

    Returns 0 if falsifier arms or <2 domains pass. Never authorizes C5/AGI*.
    """
    if episode.arm != CrossDomainArm.CROSS_DOMAIN_HOLD:
        return 0.0
    if episode.single_domain_only or episode.schedule_prompt_transfer:
        return 0.0
    if not episode.att_d_evidence:
        return 0.0
    n = len(domain_summaries)
    if n < EXPLORE_MIN_DOMAINS:
        return 0.0
    hits = sum(1 for s in domain_summaries.values() if s.e_endo_pattern)
    return clamp01(hits / n)


def run_att_d_batch(
    *,
    n_seeds: int = 20,
    domains: tuple[DomainId, DomainId] = PRE_REGISTERED_DOMAINS,
) -> dict[str, Any]:
    """Batch ATT-D explore across pre-registered domains + falsifier suite."""
    if n_seeds <= 0:
        raise ValueError("n_seeds must be positive")
    seeds = list(range(n_seeds))
    hold_ep, summaries = run_cross_domain_hold_episode(seeds=seeds, domains=domains)
    falsifiers = run_falsifier_suite(seed=0)

    by_arm: dict[str, Any] = {
        "cross_domain_hold": {
            "n": 1,
            "att_d_evidence_rate": 1.0 if hold_ep.att_d_evidence else 0.0,
            "domains_passing": hold_ep.domains_passing,
            "domain_e_pass": dict(hold_ep.domain_e_pass),
            "p_explore_by_domain": dict(hold_ep.p_explore_by_domain),
            "r_explore_by_domain": dict(hold_ep.r_explore_by_domain),
            "emit_m0_rate": 0.0,
            "d_proxy": score_att_d_proxy(
                domain_summaries=summaries, episode=hold_ep
            ),
        }
    }
    for name, ep in falsifiers.items():
        by_arm[name] = {
            "n": 1,
            "att_d_evidence_rate": 1.0 if ep.att_d_evidence else 0.0,
            "domains_passing": ep.domains_passing,
            "single_domain_only": ep.single_domain_only,
            "schedule_prompt_transfer": ep.schedule_prompt_transfer,
            "emit_m0_rate": 0.0,
        }

    return {
        "n_seeds": n_seeds,
        "domains": [d.value for d in domains],
        "domains_disjoint": domains_substantially_disjoint(domains[0], domains[1]),
        "domain_summaries": {k: v.as_dict() for k, v in summaries.items()},
        "hold_episode": hold_ep.as_dict(),
        "by_arm": by_arm,
        "claim_allowed": False,
        "c5_claim": False,
        "agi_star_claim": False,
        "c3_claim": False,
        "c2_claim": False,
        "emit_m0": False,
        "att": "ATT-D",
    }


def summarize_att_d_batch(batch: Mapping[str, Any]) -> dict[str, Any]:
    """Compact metrics view for reports."""
    by = batch.get("by_arm", {})
    summaries = batch.get("domain_summaries", {})
    domain_rates = {
        did: {
            "e_endo_pattern": s.get("e_endo_pattern"),
            "default_rate": s.get("default_rate"),
            "wm_off_rate": s.get("wm_off_rate"),
            "suppressing_named_factors": s.get("suppressing_named_factors"),
            "intent_rates": s.get("intent_rates"),
        }
        for did, s in summaries.items()
    }
    return {
        "att_d_evidence_rate_hold": by.get("cross_domain_hold", {}).get(
            "att_d_evidence_rate", 0.0
        ),
        "att_d_evidence_rate_single": by.get("single_domain_only", {}).get(
            "att_d_evidence_rate", 0.0
        ),
        "att_d_evidence_rate_schedule_prompt": by.get(
            "schedule_prompt_transfer", {}
        ).get("att_d_evidence_rate", 0.0),
        "d_proxy": by.get("cross_domain_hold", {}).get("d_proxy", 0.0),
        "domain_rates": domain_rates,
        "domains_disjoint": batch.get("domains_disjoint"),
        "c5_claim": False,
        "agi_star_claim": False,
        "emit_m0": False,
    }

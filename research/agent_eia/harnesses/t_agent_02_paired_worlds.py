"""T-AGENT-02 — Paired worlds: multi-seed initiative architecture comparison.

Runs N matched worlds (seeds/domains) comparing ``full_eia`` vs ``reactive_only``
vs ``schedule_entrained`` at X^trigger=0 with optional brief perturbation blips.

Tier C · ``claim_allowed=false`` · C2 ceiling · no AGI*.
"""

from __future__ import annotations

import hashlib
import json
import statistics
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Literal

from t_agent_01_llm_eia import (
    AGENT_EIA,
    ADAPTERS,
    ARTIFACTS,
    ATT_R_ARM_MAP,
    BRANCH,
    CONFIG_PATH,
    DEFAULT_ARMS,
    MILESTONE,
    REPO,
    ArmName,
    _apply_ambient_obs,
    _apply_world_update,
    _drive_norm,
    _ensure_paths,
    _initiative_sample,
    _load_att_r_scorer,
    _rel,
    _run_full_eia_tick,
    _run_reactive_tick,
    _run_schedule_tick,
    _seed_agent_world,
    artifact_sha256,
    compute_eoi_proxy,
    load_config,
)

HARNESS_ID = "T-AGENT-02"
ARTIFACT_JSON = ARTIFACTS / "M-T-AGENT-02_2026-09-11.json"
ARTIFACT_MD = ARTIFACTS / "M-T-AGENT-02_2026-09-11.md"

G2_TARGET_WORLDS = 20
DEFAULT_NUM_WORLDS = 8

DomainName = Literal[
    "ops_atlas",
    "research_workspace",
    "code_review",
    "health_triage",
]

DEFAULT_DOMAINS: tuple[DomainName, ...] = (
    "ops_atlas",
    "research_workspace",
    "code_review",
    "ops_atlas",
    "research_workspace",
    "code_review",
    "health_triage",
    "ops_atlas",
)

DEFAULT_SEEDS: tuple[int, ...] = tuple(range(100, 108))


def _apply_trigger_blip(loop: Any, *, tick: int, arm: ArmName) -> None:
    from eia.schemas.observation import Observation, ObservationSource

    loop.apply_observation(
        Observation(
            id=f"obs-blip-{tick}",
            timestamp=datetime.now(timezone.utc),
            source=ObservationSource.USER_MESSAGE,
            topic="external_trigger_blip",
            payload={
                "inbox_empty": False,
                "x_trigger_zero": False,
                "external_trigger": True,
                "blip_tick": tick,
                "arm": arm,
                "brief": True,
            },
            trust=0.90,
        )
    )


def _seed_domain_world(loop: Any, *, domain: DomainName, world_id: str) -> None:
    """Layer domain-specific belief skew on top of the T-AGENT-01 seed world."""
    from eia.schemas.belief import BeliefKind

    skew = {
        "ops_atlas": (0.80, 0.65, 0.55),
        "research_workspace": (0.90, 0.70, 0.50),
        "code_review": (0.75, 0.85, 0.60),
        "health_triage": (0.70, 0.75, 0.80),
    }[domain]
    loop.field.upsert_belief(
        f"belief-domain-{domain}",
        kind=BeliefKind.CATEGORICAL,
        subject=domain,
        claim=f"{domain}_context_active",
        distribution={"active": skew[0], "idle": 1.0 - skew[0]},
        uncertainty=skew[1],
        metadata={
            "source": "t_agent_02",
            "world_id": world_id,
            "domain": domain,
            "urgency": skew[2],
        },
    )


def run_agent_world_session(
    arm: ArmName,
    *,
    world_id: str,
    domain: DomainName,
    seed: int,
    quiet_ticks: int,
    schedule_period: int,
    drive_threshold: float,
    llm_backend: str,
    perturbation_blip_tick: int | None = None,
) -> dict[str, Any]:
    """Run one arm in a matched world; optional single-tick X^trigger blip."""
    _ensure_paths()
    from mock_llm_proposer import resolve_llm_backend

    from eia.governor import ContactGovernor, GovernorConfig
    from eia.ids import seeded_context
    from eia.pipeline import CognitiveLoop
    from eia.runtime.shadow_multitick import AttREvent, ShadowSessionCarryover

    proposer = resolve_llm_backend(llm_backend)
    initiative_samples: list[dict[str, Any]] = []
    proposer_log: list[dict[str, Any]] = []
    events: list[AttREvent] = [
        AttREvent("n0", "W", "world_model", (), 0),
        AttREvent("n1", "M", "self_model", ("n0",), 0),
    ]
    motive_ids: list[str] = []
    schedule_fired_ticks: list[int] = []
    blip_ticks: list[int] = []

    with seeded_context(seed):
        loop = CognitiveLoop(seed=seed)
        loop.governor = ContactGovernor(GovernorConfig())
        _seed_agent_world(loop)
        _seed_domain_world(loop, domain=domain, world_id=world_id)
        carryover: ShadowSessionCarryover | None = None

        for tick in range(1, quiet_ticks + 1):
            if carryover is not None:
                carryover.apply_to(loop)

            if perturbation_blip_tick is not None and tick == perturbation_blip_tick:
                _apply_trigger_blip(loop, tick=tick, arm=arm)
                blip_ticks.append(tick)
            else:
                _apply_ambient_obs(loop, tick=tick, arm=arm)

            hour = 14

            if arm == "reactive_only":
                mot, init, dec, plog = _run_reactive_tick(loop, loop, tick)
            elif arm == "schedule_entrained":
                mot, init, dec, plog = _run_schedule_tick(
                    loop,
                    proposer,
                    tick=tick,
                    hour=hour,
                    schedule_period=schedule_period,
                    drive_threshold=drive_threshold,
                )
                if plog.get("scheduled"):
                    schedule_fired_ticks.append(tick)
                    events.append(
                        AttREvent(f"s{tick}", "schedule", "cron_tick", ("n0",), tick)
                    )
            else:
                mot, init, dec, plog = _run_full_eia_tick(
                    loop,
                    proposer,
                    tick=tick,
                    hour=hour,
                    drive_threshold=drive_threshold,
                )

            initiative_samples.append(_initiative_sample(tick, init))
            proposer_log.append(plog)
            motive_ids.append(mot.id)
            events.append(AttREvent(f"g{tick}", "G", mot.id, ("n0", "n1"), tick))

            if not init.abstained and dec is not None:
                events.append(
                    AttREvent(f"pi{tick}", "Pi", f"pi_{arm}", (f"g{tick}",), tick)
                )
                outcome = dec.outcome.value
                events.append(
                    AttREvent(
                        f"a{tick}",
                        "A",
                        f"act_{arm}:{outcome}",
                        (f"pi{tick}",),
                        tick,
                    )
                )
                if arm == "full_eia":
                    _apply_world_update(loop, action_label=f"act_{arm}:{outcome}")
                    events.append(
                        AttREvent(f"x{tick}", "X", "x_observation", (f"a{tick}",), tick)
                    )
                    events.append(
                        AttREvent(
                            f"w{tick}",
                            "W_prime",
                            "world_update",
                            (f"x{tick}", f"a{tick}"),
                            tick,
                        )
                    )

        g0 = motive_ids[0] if motive_ids else None
        g_last = motive_ids[-1] if motive_ids else None
        has_novel = arm == "full_eia" and g_last != g0 and len(motive_ids) > 1
        if has_novel:
            events.append(
                AttREvent(
                    "g_prime",
                    "G_prime",
                    g_last or "g:none",
                    ("n1",),
                    quiet_ticks + 1,
                    novel=True,
                )
            )

        carryover = ShadowSessionCarryover.from_loop(
            loop, last_motive_id=g_last, session_tick=quiet_ticks
        )

        shadow_log = {
            "arm": ATT_R_ARM_MAP[arm],
            "eia_baseline": arm,
            "world_id": world_id,
            "domain": domain,
            "events": [e.as_dict() for e in events],
            "shadow": True,
            "initiative_samples": initiative_samples,
            "motive_ids": motive_ids,
            "x_trigger_zero": perturbation_blip_tick is None,
            "perturbation_blip_ticks": blip_ticks,
        }
        att_r = _load_att_r_scorer().scorecard_from_shadow_log(shadow_log)
        eoi = compute_eoi_proxy(initiative_samples)

        non_abstained = [s for s in initiative_samples if not s["abstained"]]
        euir_hits = 0
        for sample, plog in zip(initiative_samples, proposer_log):
            if sample["abstained"]:
                continue
            if arm == "schedule_entrained" and not plog.get("scheduled"):
                continue
            euir_hits += 1

        abstain_count = sum(1 for s in initiative_samples if s["abstained"])
        abstain_rate = abstain_count / len(initiative_samples) if initiative_samples else 1.0

        scheduled_initiatives = sum(
            1
            for s, p in zip(initiative_samples, proposer_log)
            if not s["abstained"] and p.get("scheduled")
        )
        off_schedule_initiatives = sum(
            1
            for s, p in zip(initiative_samples, proposer_log)
            if not s["abstained"] and not p.get("scheduled", arm == "full_eia")
        )

        post_blip_initiatives = 0
        if perturbation_blip_tick is not None:
            post_blip_initiatives = sum(
                1
                for s in initiative_samples
                if not s["abstained"] and s["cognitive_tick"] > perturbation_blip_tick
            )

        return {
            "arm": arm,
            "world_id": world_id,
            "domain": domain,
            "seed": seed,
            "eia_baseline": arm,
            "quiet_ticks": quiet_ticks,
            "perturbation_blip_tick": perturbation_blip_tick,
            "perturbation_blip_ticks": blip_ticks,
            "post_blip_initiatives": post_blip_initiatives,
            "initiative_count": len(non_abstained),
            "abstain_rate": round(abstain_rate, 4),
            "eoi": eoi,
            "euir_proxy_rate": round(
                euir_hits / len(initiative_samples) if initiative_samples else 0.0, 4
            ),
            "euir_proxy_hits": euir_hits,
            "genesis_delta": 1.0 if has_novel else 0.0,
            "has_novel_g_prime": has_novel,
            "att_r": att_r,
            "drive_norm_final": round(_drive_norm(loop), 4),
            "schedule_fired_ticks": schedule_fired_ticks,
            "scheduled_initiatives": scheduled_initiatives,
            "off_schedule_initiatives": off_schedule_initiatives,
            "proposer_backend": llm_backend,
            "x_trigger_zero": perturbation_blip_tick is None,
        }


@dataclass(frozen=True, slots=True)
class WorldRow:
    world_id: str
    domain: DomainName
    seed: int
    perturbation: bool
    arm: ArmName
    initiative_count: int
    abstain_rate: float
    eoi_mean: float
    euir_proxy_rate: float
    separation_score: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "world_id": self.world_id,
            "domain": self.domain,
            "seed": self.seed,
            "perturbation": self.perturbation,
            "arm": self.arm,
            "initiative_count": self.initiative_count,
            "abstain_rate": round(self.abstain_rate, 4),
            "eoi_mean": round(self.eoi_mean, 4),
            "euir_proxy_rate": round(self.euir_proxy_rate, 4),
            "separation_score": (
                round(self.separation_score, 4) if self.separation_score is not None else None
            ),
        }


@dataclass(frozen=True, slots=True)
class ArmAggregate:
    arm: ArmName
    world_count: int
    mean_initiative_count: float
    mean_eoi: float
    mean_euir: float
    mean_abstain_rate: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "arm": self.arm,
            "world_count": self.world_count,
            "mean_initiative_count": round(self.mean_initiative_count, 4),
            "mean_eoi": round(self.mean_eoi, 4),
            "mean_euir": round(self.mean_euir, 4),
            "mean_abstain_rate": round(self.mean_abstain_rate, 4),
        }


@dataclass(frozen=True, slots=True)
class Agent02Diagnostics:
    f_reactive_collapse: bool
    f_schedule_as_endo: bool
    f_world_drift: bool
    worlds_pass_count: int
    worlds_total: int
    mean_separation: float
    separation_std: float
    schedule_trigger_dependent: bool
    perturbation_resume: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "f_reactive_collapse": self.f_reactive_collapse,
            "f_schedule_as_endo": self.f_schedule_as_endo,
            "f_world_drift": self.f_world_drift,
            "worlds_pass_count": self.worlds_pass_count,
            "worlds_total": self.worlds_total,
            "mean_separation": round(self.mean_separation, 4),
            "separation_std": round(self.separation_std, 4),
            "schedule_trigger_dependent": self.schedule_trigger_dependent,
            "perturbation_resume": self.perturbation_resume,
        }


def _world_id(index: int) -> str:
    return f"agent_world_{index:03d}"


def _resolve_world_specs(cfg: dict[str, Any]) -> list[dict[str, Any]]:
    t02 = cfg.get("t_agent_02") or {}
    num_worlds = int(t02.get("num_worlds", DEFAULT_NUM_WORLDS))
    seeds = list(t02.get("seeds") or DEFAULT_SEEDS[:num_worlds])
    domains = list(t02.get("domains") or DEFAULT_DOMAINS[:num_worlds])
    perturb = t02.get("perturbation") or {}
    blip_tick = int(perturb.get("blip_tick", 3)) if perturb.get("enabled", True) else None
    perturb_indices = set(perturb.get("world_indices") or [2, 6])

    specs: list[dict[str, Any]] = []
    for i in range(num_worlds):
        specs.append(
            {
                "world_id": _world_id(i + 1),
                "seed": int(seeds[i % len(seeds)]),
                "domain": domains[i % len(domains)],
                "perturbation_blip_tick": blip_tick if i in perturb_indices else None,
            }
        )
    return specs


def _aggregate_arm(rows: list[WorldRow], arm: ArmName) -> ArmAggregate:
    subset = [r for r in rows if r.arm == arm]
    n = len(subset) or 1
    return ArmAggregate(
        arm=arm,
        world_count=len(subset),
        mean_initiative_count=sum(r.initiative_count for r in subset) / n,
        mean_eoi=sum(r.eoi_mean for r in subset) / n,
        mean_euir=sum(r.euir_proxy_rate for r in subset) / n,
        mean_abstain_rate=sum(r.abstain_rate for r in subset) / n,
    )


def evaluate_agent02_diagnostics(
    worlds: list[dict[str, Any]],
    aggregates: dict[str, ArmAggregate],
) -> Agent02Diagnostics:
    separations: list[float] = []
    worlds_pass = 0

    for world in worlds:
        arms = world["arms"]
        full = arms["full_eia"]
        reactive = arms["reactive_only"]
        full_euir = float(full["euir_proxy_rate"])
        react_euir = float(reactive["euir_proxy_rate"])
        sep = full_euir - react_euir
        separations.append(sep)

        full_init = int(full["initiative_count"])
        react_init = int(reactive["initiative_count"])
        if full_init > react_init and react_init == 0 and sep > 0:
            worlds_pass += 1

    mean_sep = statistics.mean(separations) if separations else 0.0
    sep_std = statistics.pstdev(separations) if len(separations) > 1 else 0.0

    reactive_rows = [w["arms"]["reactive_only"] for w in worlds]
    f_reactive = all(int(r["initiative_count"]) == 0 for r in reactive_rows)

    full_agg = aggregates["full_eia"]
    sched_agg = aggregates["schedule_entrained"]
    f_schedule = (
        sched_agg.mean_euir < full_agg.mean_euir
        and sched_agg.mean_initiative_count < full_agg.mean_initiative_count
    )

    sched_rows = [w["arms"]["schedule_entrained"] for w in worlds]
    schedule_trigger = all(
        int(r.get("off_schedule_initiatives") or 0) == 0
        and int(r.get("scheduled_initiatives") or 0) > 0
        for r in sched_rows
    )

    f_drift = worlds_pass >= len(worlds) * 0.75 and sep_std < 0.15

    perturb_worlds = [w for w in worlds if w.get("perturbation")]
    perturb_resume = True
    if perturb_worlds:
        perturb_resume = all(
            int(w["arms"]["full_eia"].get("post_blip_initiatives") or 0) > 0
            for w in perturb_worlds
        )

    return Agent02Diagnostics(
        f_reactive_collapse=f_reactive,
        f_schedule_as_endo=f_schedule,
        f_world_drift=f_drift,
        worlds_pass_count=worlds_pass,
        worlds_total=len(worlds),
        mean_separation=mean_sep,
        separation_std=sep_std,
        schedule_trigger_dependent=schedule_trigger,
        perturbation_resume=perturb_resume,
    )


def build_t_agent_02_payload(
    *,
    generated: str | None = None,
    num_worlds: int | None = None,
    quiet_ticks: int | None = None,
    schedule_period: int | None = None,
    drive_threshold: float | None = None,
    llm_backend: str | None = None,
) -> dict[str, Any]:
    cfg = load_config()
    t02 = cfg.get("t_agent_02") or {}
    t01 = cfg.get("t_agent_01") or {}

    if num_worlds is not None:
        t02 = {**t02, "num_worlds": num_worlds}
        cfg = {**cfg, "t_agent_02": t02}

    quiet_ticks = quiet_ticks or int(t02.get("quiet_ticks", t01.get("quiet_ticks", 6)))
    schedule_period = schedule_period or int(
        t02.get("schedule_period", t01.get("schedule_period", 3))
    )
    drive_threshold = drive_threshold or float(
        t02.get("drive_proposal_threshold", t01.get("drive_proposal_threshold", 0.22))
    )
    llm_backend = llm_backend or str(t02.get("llm_backend", t01.get("llm_backend", "mock")))

    world_specs = _resolve_world_specs(cfg)
    worlds_out: list[dict[str, Any]] = []
    rows: list[WorldRow] = []

    for spec in world_specs:
        arm_results: dict[str, dict[str, Any]] = {}
        for arm in DEFAULT_ARMS:
            arm_results[arm] = run_agent_world_session(
                arm,  # type: ignore[arg-type]
                world_id=spec["world_id"],
                domain=spec["domain"],  # type: ignore[arg-type]
                seed=spec["seed"],
                quiet_ticks=quiet_ticks,
                schedule_period=schedule_period,
                drive_threshold=drive_threshold,
                llm_backend=llm_backend,
                perturbation_blip_tick=spec.get("perturbation_blip_tick"),
            )

        full_euir = float(arm_results["full_eia"]["euir_proxy_rate"])
        react_euir = float(arm_results["reactive_only"]["euir_proxy_rate"])
        separation = full_euir - react_euir

        for arm in DEFAULT_ARMS:
            r = arm_results[arm]
            eoi = r.get("eoi") or {}
            rows.append(
                WorldRow(
                    world_id=spec["world_id"],
                    domain=spec["domain"],  # type: ignore[arg-type]
                    seed=spec["seed"],
                    perturbation=spec.get("perturbation_blip_tick") is not None,
                    arm=arm,  # type: ignore[arg-type]
                    initiative_count=int(r["initiative_count"]),
                    abstain_rate=float(r["abstain_rate"]),
                    eoi_mean=float(eoi.get("eoi_mean") or 0.0),
                    euir_proxy_rate=float(r["euir_proxy_rate"]),
                    separation_score=separation if arm == "full_eia" else None,
                )
            )

        worlds_out.append(
            {
                "world_id": spec["world_id"],
                "domain": spec["domain"],
                "seed": spec["seed"],
                "perturbation": spec.get("perturbation_blip_tick") is not None,
                "perturbation_blip_tick": spec.get("perturbation_blip_tick"),
                "separation_score": round(separation, 4),
                "world_pass": (
                    int(arm_results["full_eia"]["initiative_count"])
                    > int(arm_results["reactive_only"]["initiative_count"])
                    and int(arm_results["reactive_only"]["initiative_count"]) == 0
                ),
                "arms": {
                    arm: {
                        "initiative_count": r["initiative_count"],
                        "abstain_rate": r["abstain_rate"],
                        "eoi_mean": (r.get("eoi") or {}).get("eoi_mean"),
                        "euir_proxy_rate": r["euir_proxy_rate"],
                        "scheduled_initiatives": r.get("scheduled_initiatives"),
                        "off_schedule_initiatives": r.get("off_schedule_initiatives"),
                        "post_blip_initiatives": r.get("post_blip_initiatives"),
                    }
                    for arm, r in arm_results.items()
                },
                "arms_full": arm_results,
            }
        )

    aggregates = {arm: _aggregate_arm(rows, arm) for arm in DEFAULT_ARMS}
    diagnostics = evaluate_agent02_diagnostics(worlds_out, aggregates)

    diagnostic_pass = (
        diagnostics.f_reactive_collapse
        and diagnostics.f_schedule_as_endo
        and diagnostics.f_world_drift
        and diagnostics.schedule_trigger_dependent
        and diagnostics.worlds_pass_count == diagnostics.worlds_total
        and diagnostics.perturbation_resume
    )

    num_worlds_actual = len(worlds_out)
    domain_count = len({w["domain"] for w in worlds_out})
    scope_frac = f"{num_worlds_actual}/{G2_TARGET_WORLDS} worlds × {domain_count}/3 domains"

    return {
        "milestone": MILESTONE,
        "harness_id": HARNESS_ID,
        "artifact_id": "M-T-AGENT-02_2026-09-11",
        "tick_id": HARNESS_ID,
        "date": generated or date.today().isoformat(),
        "branch": BRANCH,
        "cell": "D1×L2",
        "tier": "C",
        "claim_ceiling": "C2",
        "claim_allowed": False,
        "e_endo_support": "none",
        "witness_support": "none",
        "c_ladder_raise_allowed": False,
        "agi_star_claim": False,
        "att": "ATT-E",
        "x_trigger_zero": True,
        "num_worlds": num_worlds_actual,
        "domain_count": domain_count,
        "g2_scope_fraction": scope_frac,
        "quiet_ticks": quiet_ticks,
        "schedule_period": schedule_period,
        "drive_proposal_threshold": drive_threshold,
        "llm_backend": llm_backend,
        "sources": {
            "harness": _rel(AGENT_EIA / "harnesses" / "t_agent_02_paired_worlds.py"),
            "t_agent_01": _rel(AGENT_EIA / "harnesses" / "t_agent_01_llm_eia.py"),
            "mock_llm_proposer": _rel(ADAPTERS / "mock_llm_proposer.py"),
            "g2_worlds": _rel(REPO / "research" / "sci_flow" / "g2_worlds_harness.py"),
        },
        "aggregates": {arm: aggregates[arm].to_dict() for arm in DEFAULT_ARMS},
        "rows": [r.to_dict() for r in rows],
        "worlds": [
            {k: v for k, v in w.items() if k != "arms_full"} for w in worlds_out
        ],
        "worlds_full": worlds_out,
        "diagnostics": diagnostics.to_dict(),
        "diagnostic_pass": diagnostic_pass,
        "falsifiers_active": [
            "F-REACTIVE-COLLAPSE",
            "F-SCHEDULE-AS-ENDO",
            "F-WORLD-DRIFT",
        ],
        "g2_directional": {
            "full_eia_mean_euir": aggregates["full_eia"].mean_euir,
            "reactive_only_mean_euir": aggregates["reactive_only"].mean_euir,
            "full_eia_mean_eoi": aggregates["full_eia"].mean_eoi,
            "reactive_only_mean_eoi": aggregates["reactive_only"].mean_eoi,
            "mean_separation": diagnostics.mean_separation,
        },
        "note": (
            "T-AGENT-02 paired worlds: N matched seeds/domains comparing initiative "
            "architectures at X^trigger=0. full_eia EUIR >> reactive_only across worlds; "
            "schedule_entrained falsifier distinct from endogenous pattern; optional "
            "perturbation blip tests post-blip resume. Does not establish E_endo."
        ),
    }


def render_t_agent_02_markdown(payload: dict[str, Any]) -> str:
    aggregates = payload.get("aggregates") or {}
    diag = payload.get("diagnostics") or {}
    g2 = payload.get("g2_directional") or {}

    lines = [
        f"# M-T-AGENT-02 Paired Worlds — {payload.get('date', '')}",
        "",
        f"**Cell:** {payload.get('cell')} · **Tier:** {payload.get('tier')} · "
        f"**Harness:** {payload.get('harness_id')}",
        f"**Worlds:** {payload.get('num_worlds')} · **Domains:** {payload.get('domain_count')} · "
        f"**Scope:** {payload.get('g2_scope_fraction')}",
        f"**Branch:** `{payload.get('branch')}` · **LLM:** `{payload.get('llm_backend')}`",
        f"**SHA-256:** `{payload.get('artifact_sha256', '')}`",
        "",
        "## Per-arm aggregates",
        "",
        "| Arm | worlds | mean initiatives | mean EOI | mean EUIR | mean abstain |",
        "|-----|--------|------------------|----------|-----------|--------------|",
    ]
    for arm in DEFAULT_ARMS:
        agg = aggregates.get(arm) or {}
        lines.append(
            f"| `{arm}` | {agg.get('world_count', 0)} | "
            f"{agg.get('mean_initiative_count', 0):.2f} | "
            f"{agg.get('mean_eoi', 0):.3f} | "
            f"{agg.get('mean_euir', 0):.0%} | "
            f"{agg.get('mean_abstain_rate', 0):.0%} |"
        )

    lines.extend([
        "",
        "## G2 directional",
        "",
        f"- full_eia mean EUIR: **{g2.get('full_eia_mean_euir', 0):.0%}**",
        f"- reactive_only mean EUIR: **{g2.get('reactive_only_mean_euir', 0):.0%}**",
        f"- mean separation (full − reactive): **{g2.get('mean_separation', 0):.3f}**",
        "",
        "## World pass / falsifiers",
        "",
        f"- worlds_pass: **{diag.get('worlds_pass_count')}/{diag.get('worlds_total')}**",
        f"- F-REACTIVE-COLLAPSE: {diag.get('f_reactive_collapse')}",
        f"- F-SCHEDULE-AS-ENDO: {diag.get('f_schedule_as_endo')}",
        f"- F-WORLD-DRIFT: {diag.get('f_world_drift')}",
        f"- schedule trigger-dependent: {diag.get('schedule_trigger_dependent')}",
        f"- perturbation resume: {diag.get('perturbation_resume')}",
        "",
        f"- diagnostic_pass: **{payload.get('diagnostic_pass')}**",
        "",
        f"**claim_allowed:** {payload.get('claim_allowed')} · "
        f"**e_endo_support:** {payload.get('e_endo_support')} · "
        f"**AGI\\*:** {payload.get('agi_star_claim')}",
        "",
        payload.get("note", ""),
    ])
    return "\n".join(lines) + "\n"

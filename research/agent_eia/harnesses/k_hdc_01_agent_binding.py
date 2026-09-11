"""K-HDC-01 — HDC episodic binding as Tier C memory adjunct in agent loop.

Compares full_eia+hdc vs full_eia vs reactive_only at X^trigger=0.
Does HDC improve initiative quality (EOI) or only retrieval? NOT proto-AGI.
"""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Literal

import yaml

AGENT_EIA = Path(__file__).resolve().parents[1]
REPO = AGENT_EIA.parents[1]
KAIRO = REPO / "research" / "kairologos_experiments"
ADAPTERS = AGENT_EIA / "adapters"
ARTIFACTS = KAIRO / "artifacts"
ARTIFACT_JSON = ARTIFACTS / "M-K-HDC-01_2026-09-11.json"
ARTIFACT_MD = ARTIFACTS / "M-K-HDC-01_2026-09-11.md"
CONFIG_PATH = AGENT_EIA / "config.yaml"
BRANCH = "main"

ArmName = Literal["full_eia", "full_eia_hdc", "reactive_only"]
K_HDC_ARMS: tuple[ArmName, ...] = ("full_eia", "full_eia_hdc", "reactive_only")
EOI_ENDOGENOUS_THRESHOLD = 0.50
HARNESS_ID = "K-HDC-01"
MILESTONE = "M-KAIRO-TIER-C"


def _ensure_paths() -> None:
    for path in (str(REPO / "src"), str(ADAPTERS), str(AGENT_EIA / "harnesses")):
        if path not in sys.path:
            sys.path.insert(0, path)


def _rel(path: Path) -> str:
    try:
        return path.relative_to(REPO).as_posix()
    except ValueError:
        return path.as_posix()


def load_config(path: Path = CONFIG_PATH) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def run_agent_hdc_session(
    *,
    seed: int,
    quiet_ticks: int,
    drive_threshold: float,
    llm_backend: str,
    hdc_dim: int = 512,
) -> dict[str, Any]:
    """full_eia + HDC episodic store at X^trigger=0."""
    _ensure_paths()
    from hdc_memory import HDCEpisodicMemory
    from mock_llm_proposer import resolve_llm_backend
    from t_agent_01_llm_eia import (
        ATT_R_ARM_MAP,
        _apply_ambient_obs,
        _apply_world_update,
        _drive_norm,
        _initiative_sample,
        _load_att_r_scorer,
        _run_full_eia_tick,
        _seed_agent_world,
        compute_eoi_proxy,
    )

    from eia.governor import ContactGovernor, GovernorConfig
    from eia.ids import seeded_context
    from eia.pipeline import CognitiveLoop
    from eia.runtime.shadow_multitick import AttREvent, ShadowSessionCarryover

    proposer = resolve_llm_backend(llm_backend)
    memory = HDCEpisodicMemory(dim=hdc_dim, seed=seed)
    initiative_samples: list[dict[str, Any]] = []
    proposer_log: list[dict[str, Any]] = []
    hdc_log: list[dict[str, Any]] = []
    events: list[AttREvent] = [
        AttREvent("n0", "W", "world_model", (), 0),
        AttREvent("n1", "M", "self_model", ("n0",), 0),
    ]
    motive_ids: list[str] = []

    with seeded_context(seed):
        loop = CognitiveLoop(seed=seed)
        loop.governor = ContactGovernor(GovernorConfig())
        _seed_agent_world(loop)
        carryover: ShadowSessionCarryover | None = None

        for tick in range(1, quiet_ticks + 1):
            if carryover is not None:
                carryover.apply_to(loop)

            _apply_ambient_obs(loop, tick=tick, arm="full_eia_hdc")
            hour = 14

            if tick > 1:
                prior_key = f"motive_tick_{tick - 1}"
                retrieval = memory.query(prior_key)
                hdc_log.append({"tick": tick, "query": prior_key, **retrieval})
                if retrieval["hit"]:
                    from eia.schemas.belief import BeliefKind

                    loop.field.upsert_belief(
                        f"belief-hdc-{tick}",
                        kind=BeliefKind.CATEGORICAL,
                        subject="hdc_retrieval",
                        claim=str(retrieval["value"]),
                        distribution={"retrieved": 0.9, "miss": 0.1},
                        uncertainty=0.25,
                        metadata={"source": "k_hdc_01", "similarity": retrieval["similarity"]},
                    )

            mot, init, dec, plog = _run_full_eia_tick(
                loop,
                proposer,
                tick=tick,
                hour=hour,
                drive_threshold=drive_threshold,
            )

            if not init.abstained and dec is not None:
                action_label = f"act_full_eia_hdc:{dec.outcome.value}"
                memory.store(
                    f"motive_tick_{tick}",
                    action_label,
                    tick=tick,
                    metadata={"motivation_id": mot.id},
                )
                hdc_log.append(
                    {
                        "tick": tick,
                        "store": True,
                        "key": f"motive_tick_{tick}",
                        "value": action_label,
                    }
                )

            initiative_samples.append(_initiative_sample(tick, init))
            proposer_log.append(plog)
            motive_ids.append(mot.id)
            events.append(AttREvent(f"g{tick}", "G", mot.id, ("n0", "n1"), tick))

            if not init.abstained and dec is not None:
                events.append(
                    AttREvent(f"pi{tick}", "Pi", "pi_full_eia_hdc", (f"g{tick}",), tick)
                )
                outcome = dec.outcome.value
                events.append(
                    AttREvent(
                        f"a{tick}",
                        "A",
                        f"act_full_eia_hdc:{outcome}",
                        (f"pi{tick}",),
                        tick,
                    )
                )
                _apply_world_update(loop, action_label=f"act_full_eia_hdc:{outcome}")
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
        has_novel = g_last != g0 and len(motive_ids) > 1
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
            "arm": ATT_R_ARM_MAP["full_eia"],
            "eia_baseline": "full_eia_hdc",
            "events": [e.as_dict() for e in events],
            "shadow": True,
            "initiative_samples": initiative_samples,
            "motive_ids": motive_ids,
            "x_trigger_zero": True,
        }
        att_r = _load_att_r_scorer().scorecard_from_shadow_log(shadow_log)
        eoi = compute_eoi_proxy(initiative_samples)
        non_abstained = [s for s in initiative_samples if not s["abstained"]]
        mem_stats = memory.stats()

        return {
            "arm": "full_eia_hdc",
            "eia_baseline": "full_eia_hdc",
            "quiet_ticks": quiet_ticks,
            "initiative_count": len(non_abstained),
            "abstain_rate": round(
                sum(1 for s in initiative_samples if s["abstained"]) / len(initiative_samples),
                4,
            ),
            "eoi": eoi,
            "genesis_delta": 1.0 if has_novel else 0.0,
            "has_novel_g_prime": has_novel,
            "att_r": att_r,
            "drive_norm_final": round(_drive_norm(loop), 4),
            "hdc_stats": mem_stats,
            "hdc_log": hdc_log,
            "hdc_retrieval_rate": mem_stats["retrieval_rate"],
            "x_trigger_zero": True,
        }


@dataclass(frozen=True, slots=True)
class HdcBindingDiagnostics:
    full_eia_runs: bool
    hdc_retrieval_works: bool
    hdc_eoi_parity_or_better: bool
    reactive_zero_initiatives: bool
    hdc_improves_initiative_not_just_retrieval: bool

    def to_dict(self) -> dict[str, Any]:
        return {k: getattr(self, k) for k in self.__dataclass_fields__}


def evaluate_hdc_diagnostics(arms: dict[str, dict[str, Any]]) -> HdcBindingDiagnostics:
    full = arms["full_eia"]
    hdc = arms["full_eia_hdc"]
    reactive = arms["reactive_only"]

    full_eoi = float((full["eoi"] or {}).get("eoi_mean") or 0.0)
    hdc_eoi = float((hdc["eoi"] or {}).get("eoi_mean") or 0.0)
    retrieval_rate = float(hdc.get("hdc_retrieval_rate") or 0.0)
    eoi_delta = hdc_eoi - full_eoi

    return HdcBindingDiagnostics(
        full_eia_runs=int(full["initiative_count"]) > 0,
        hdc_retrieval_works=retrieval_rate > 0.0 and (hdc.get("hdc_stats") or {}).get("stores", 0) > 0,
        hdc_eoi_parity_or_better=hdc_eoi >= full_eoi - 1e-6,
        reactive_zero_initiatives=int(reactive["initiative_count"]) == 0,
        hdc_improves_initiative_not_just_retrieval=(
            retrieval_rate > 0.0 and abs(eoi_delta) <= 0.05
        ),
    )


def build_k_hdc_01_payload(
    *,
    seed: int = 42,
    generated: str | None = None,
    quiet_ticks: int | None = None,
    drive_threshold: float | None = None,
    llm_backend: str | None = None,
    hdc_dim: int = 512,
) -> dict[str, Any]:
    _ensure_paths()
    from t_agent_01_llm_eia import run_agent_quiet_session

    cfg = load_config()
    t01 = cfg.get("t_agent_01") or {}
    quiet_ticks = quiet_ticks or int(t01.get("quiet_ticks", 6))
    drive_threshold = drive_threshold or float(t01.get("drive_proposal_threshold", 0.22))
    llm_backend = llm_backend or str(t01.get("llm_backend", "mock"))

    arm_results: dict[str, dict[str, Any]] = {
        "full_eia": run_agent_quiet_session(
            "full_eia",
            seed=seed,
            quiet_ticks=quiet_ticks,
            schedule_period=99,
            drive_threshold=drive_threshold,
            llm_backend=llm_backend,
        ),
        "reactive_only": run_agent_quiet_session(
            "reactive_only",
            seed=seed,
            quiet_ticks=quiet_ticks,
            schedule_period=99,
            drive_threshold=drive_threshold,
            llm_backend=llm_backend,
        ),
        "full_eia_hdc": run_agent_hdc_session(
            seed=seed,
            quiet_ticks=quiet_ticks,
            drive_threshold=drive_threshold,
            llm_backend=llm_backend,
            hdc_dim=hdc_dim,
        ),
    }

    diagnostics = evaluate_hdc_diagnostics(arm_results)
    full = arm_results["full_eia"]
    hdc = arm_results["full_eia_hdc"]
    diagnostic_pass = (
        diagnostics.full_eia_runs
        and diagnostics.hdc_retrieval_works
        and diagnostics.reactive_zero_initiatives
    )

    full_eoi = float((full["eoi"] or {}).get("eoi_mean") or 0.0)
    hdc_eoi = float((hdc["eoi"] or {}).get("eoi_mean") or 0.0)

    return {
        "milestone": MILESTONE,
        "harness_id": HARNESS_ID,
        "artifact_id": "M-K-HDC-01_2026-09-11",
        "tick_id": HARNESS_ID,
        "date": generated or date.today().isoformat(),
        "branch": BRANCH,
        "cell": "D1×L2",
        "tier": "C",
        "claim_ceiling": "C2",
        "ceiling": "C2",
        "theory_strand": "kairologos_explore",
        "claim_allowed": False,
        "e_endo_support": "none",
        "witness_support": "none",
        "c_ladder_raise_allowed": False,
        "agi_star_claim": False,
        "att": "ATT-E",
        "x_trigger_zero": True,
        "seed": seed,
        "quiet_ticks": quiet_ticks,
        "hdc_dim": hdc_dim,
        "eoi_endogenous_threshold": EOI_ENDOGENOUS_THRESHOLD,
        "sources": {
            "hdc_memory": _rel(ADAPTERS / "hdc_memory.py"),
            "t_agent_01": _rel(AGENT_EIA / "harnesses" / "t_agent_01_llm_eia.py"),
        },
        "arms": {
            arm: {
                "initiative_count": r["initiative_count"],
                "eoi_mean": (r["eoi"] or {}).get("eoi_mean"),
                "eoi_min": (r["eoi"] or {}).get("eoi_min"),
                "eoi_pass": (r["eoi"] or {}).get("eoi_pass"),
                "genesis_delta": r["genesis_delta"],
                "att_r_evidence": (r["att_r"] or {}).get("att_r_evidence"),
                "hdc_retrieval_rate": r.get("hdc_retrieval_rate"),
                "hdc_stats": r.get("hdc_stats"),
            }
            for arm, r in arm_results.items()
        },
        "comparison": {
            "eoi_delta_hdc_minus_full": round(hdc_eoi - full_eoi, 6),
            "initiative_delta_hdc_minus_full": (
                int(hdc["initiative_count"]) - int(full["initiative_count"])
            ),
            "hdc_retrieval_only": diagnostics.hdc_improves_initiative_not_just_retrieval,
            "interpretation": (
                "HDC improves episodic retrieval adjunct; EOI parity with full_eia "
                "— memory binding does not independently raise initiative quality"
                if diagnostics.hdc_improves_initiative_not_just_retrieval
                else "HDC shows measurable EOI or initiative delta vs full_eia baseline"
            ),
        },
        "diagnostics": diagnostics.to_dict(),
        "diagnostic_pass": diagnostic_pass,
        "falsifiers_active": ["F-HDC-AS-AGI"],
        "claim_invariants": {
            "claim_allowed": False,
            "e_endo_support": "none",
            "tier": "C",
            "ceiling": "C2",
            "theory_strand": "kairologos_explore",
            "agi_star_claim": False,
        },
        "note": (
            "Kairologos HDC/VSA binding as Tier C episodic adjunct at X^trigger=0. "
            "Compares retrieval rate vs EOI/initiative — not proto-AGI evidence."
        ),
    }


def artifact_sha256(payload: dict[str, Any]) -> str:
    body = {k: v for k, v in payload.items() if k != "artifact_sha256"}
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def render_k_hdc_01_markdown(payload: dict[str, Any]) -> str:
    arms = payload.get("arms") or {}
    cmp_ = payload.get("comparison") or {}
    diag = payload.get("diagnostics") or {}
    lines = [
        f"# M-K-HDC-01 HDC agent binding — {payload.get('date', '')}",
        "",
        f"**Harness:** {payload.get('harness_id')} · **Tier:** C · **HDC dim:** {payload.get('hdc_dim')}",
        f"**SHA-256:** `{payload.get('artifact_sha256', '')}`",
        "",
        "## Arms",
        "",
        "| Arm | initiatives | EOI mean | retrieval rate | genesis_Δ |",
        "|-----|-------------|----------|----------------|-----------|",
    ]
    for arm_key in K_HDC_ARMS:
        row = arms.get(arm_key) or {}
        retr = row.get("hdc_retrieval_rate")
        retr_s = f"{retr:.2%}" if retr is not None else "—"
        lines.append(
            f"| `{arm_key}` | {row.get('initiative_count', 0)} | "
            f"{row.get('eoi_mean', 0):.3f} | {retr_s} | {row.get('genesis_delta', 0):.0f} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        f"- EOI Δ (hdc − full): `{cmp_.get('eoi_delta_hdc_minus_full')}`",
        f"- retrieval-only adjunct: `{cmp_.get('hdc_retrieval_only')}`",
        f"- {cmp_.get('interpretation')}",
        "",
        f"**diagnostic_pass:** `{payload.get('diagnostic_pass')}` · "
        f"retrieval works: `{diag.get('hdc_retrieval_works')}`",
    ])
    return "\n".join(lines)

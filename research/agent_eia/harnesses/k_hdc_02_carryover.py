"""K-HDC-02 — HDC episodic carryover across 2+ session ticks.

Extends hdc_memory + ShadowSessionCarryover bridge (T-AGENT-04 pattern).
Compares full_eia+hdc vs full_eia at X^trigger=0 over multiple ticks.
Metrics: retrieval accuracy tick-to-tick, EOI persistence, cumulative initiatives.
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
ARTIFACT_JSON = ARTIFACTS / "M-K-HDC-02_2026-09-11.json"
ARTIFACT_MD = ARTIFACTS / "M-K-HDC-02_2026-09-11.md"
CONFIG_PATH = AGENT_EIA / "config.yaml"
BRANCH = "main"

ArmName = Literal["full_eia", "full_eia_hdc"]
K_HDC_02_ARMS: tuple[ArmName, ...] = ("full_eia", "full_eia_hdc")
MIN_SESSION_TICKS = 2
HARNESS_ID = "K-HDC-02"
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


def run_agent_carryover_session(
    arm: ArmName,
    *,
    seed: int,
    session_ticks: int,
    drive_threshold: float,
    llm_backend: str,
    hdc_dim: int = 512,
) -> dict[str, Any]:
    """Run one arm with per-tick carryover metrics at X^trigger=0."""
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

    use_hdc = arm == "full_eia_hdc"
    proposer = resolve_llm_backend(llm_backend)
    memory = HDCEpisodicMemory(dim=hdc_dim, seed=seed) if use_hdc else None
    initiative_samples: list[dict[str, Any]] = []
    per_tick: list[dict[str, Any]] = []
    hdc_log: list[dict[str, Any]] = []
    retrieval_expectations: list[dict[str, Any]] = []
    stored_values: dict[str, str] = {}
    events: list[AttREvent] = [
        AttREvent("n0", "W", "world_model", (), 0),
        AttREvent("n1", "M", "self_model", ("n0",), 0),
    ]
    motive_ids: list[str] = []
    cumulative_initiatives = 0

    with seeded_context(seed):
        loop = CognitiveLoop(seed=seed)
        loop.governor = ContactGovernor(GovernorConfig())
        _seed_agent_world(loop)
        carryover: ShadowSessionCarryover | None = None

        for tick in range(1, session_ticks + 1):
            if carryover is not None:
                carryover.apply_to(loop)

            _apply_ambient_obs(loop, tick=tick, arm=arm)
            hour = 14

            if use_hdc and memory is not None and tick > 1:
                prior_key = f"motive_tick_{tick - 1}"
                retrieval = memory.query(prior_key)
                hdc_log.append({"tick": tick, "query": prior_key, **retrieval})
                retrieval_expectations.append(
                    {
                        "tick": tick,
                        "key": prior_key,
                        "expected_value": stored_values.get(prior_key),
                    }
                )
                if retrieval["hit"]:
                    from eia.schemas.belief import BeliefKind

                    loop.field.upsert_belief(
                        f"belief-hdc-{tick}",
                        kind=BeliefKind.CATEGORICAL,
                        subject="hdc_retrieval",
                        claim=str(retrieval["value"]),
                        distribution={"retrieved": 0.9, "miss": 0.1},
                        uncertainty=0.25,
                        metadata={"source": "k_hdc_02", "similarity": retrieval["similarity"]},
                    )

            mot, init, dec, plog = _run_full_eia_tick(
                loop,
                proposer,
                tick=tick,
                hour=hour,
                drive_threshold=drive_threshold,
            )

            if use_hdc and memory is not None and not init.abstained and dec is not None:
                action_label = f"act_full_eia_hdc:{dec.outcome.value}"
                memory.store(
                    f"motive_tick_{tick}",
                    action_label,
                    tick=tick,
                    metadata={"motivation_id": mot.id},
                )
                stored_values[f"motive_tick_{tick}"] = action_label
                hdc_log.append(
                    {"tick": tick, "store": True, "key": f"motive_tick_{tick}", "value": action_label}
                )

            sample = _initiative_sample(tick, init)
            initiative_samples.append(sample)
            if not init.abstained:
                cumulative_initiatives += 1

            motive_ids.append(mot.id)
            events.append(AttREvent(f"g{tick}", "G", mot.id, ("n0", "n1"), tick))

            if not init.abstained and dec is not None:
                events.append(AttREvent(f"pi{tick}", "Pi", f"pi_{arm}", (f"g{tick}",), tick))
                outcome = dec.outcome.value
                events.append(
                    AttREvent(f"a{tick}", "A", f"act_{arm}:{outcome}", (f"pi{tick}",), tick)
                )
                if arm == "full_eia":
                    _apply_world_update(loop, action_label=f"act_{arm}:{outcome}")
                elif use_hdc:
                    _apply_world_update(loop, action_label=f"act_full_eia_hdc:{outcome}")
                events.append(AttREvent(f"x{tick}", "X", "x_observation", (f"a{tick}",), tick))
                events.append(
                    AttREvent(
                        f"w{tick}",
                        "W_prime",
                        "world_update",
                        (f"x{tick}", f"a{tick}"),
                        tick,
                    )
                )

            tick_eoi = compute_eoi_proxy([sample])
            per_tick.append(
                {
                    "session_tick": tick,
                    "initiative_count": 1 if not init.abstained else 0,
                    "cumulative_initiatives": cumulative_initiatives,
                    "eoi_mean": (tick_eoi or {}).get("eoi_mean"),
                    "drive_norm": round(_drive_norm(loop), 4),
                    "used_carryover": carryover is not None,
                }
            )

            carryover = ShadowSessionCarryover.from_loop(
                loop, last_motive_id=mot.id, session_tick=tick
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
                    session_ticks + 1,
                    novel=True,
                )
            )

        shadow_log = {
            "arm": ATT_R_ARM_MAP.get("full_eia" if arm == "full_eia_hdc" else arm, arm),
            "eia_baseline": arm,
            "events": [e.as_dict() for e in events],
            "shadow": True,
            "initiative_samples": initiative_samples,
            "motive_ids": motive_ids,
            "x_trigger_zero": True,
        }
        att_r = _load_att_r_scorer().scorecard_from_shadow_log(shadow_log)
        eoi = compute_eoi_proxy(initiative_samples)
        non_abstained = [s for s in initiative_samples if not s["abstained"]]

        tick_retrieval = (
            memory.evaluate_tick_retrieval(retrieval_expectations)
            if memory is not None and retrieval_expectations
            else {"accuracy": 0.0, "per_tick": [], "hits": 0, "total": 0}
        )
        eoi_values = [float(t["eoi_mean"] or 0.0) for t in per_tick if t["eoi_mean"] is not None]
        eoi_persistence = (
            min(eoi_values) / max(eoi_values) if eoi_values and max(eoi_values) > 0 else 1.0
        )

        return {
            "arm": arm,
            "session_ticks": session_ticks,
            "initiative_count": len(non_abstained),
            "cumulative_initiatives": cumulative_initiatives,
            "abstain_rate": round(
                sum(1 for s in initiative_samples if s["abstained"]) / len(initiative_samples),
                4,
            ),
            "eoi": eoi,
            "eoi_persistence": round(eoi_persistence, 4),
            "per_tick": per_tick,
            "tick_retrieval": tick_retrieval,
            "genesis_delta": 1.0 if has_novel else 0.0,
            "has_novel_g_prime": has_novel,
            "att_r": att_r,
            "drive_norm_final": round(_drive_norm(loop), 4),
            "hdc_stats": memory.stats() if memory is not None else None,
            "hdc_log": hdc_log if use_hdc else None,
            "x_trigger_zero": True,
        }


@dataclass(frozen=True, slots=True)
class HdcCarryoverDiagnostics:
    both_arms_run: bool
    hdc_retrieval_across_ticks: bool
    eoi_persistence_hdc: bool
    initiative_parity_or_hdc_ge: bool

    def to_dict(self) -> dict[str, Any]:
        return {k: getattr(self, k) for k in self.__dataclass_fields__}


def evaluate_carryover_diagnostics(arms: dict[str, dict[str, Any]]) -> HdcCarryoverDiagnostics:
    full = arms["full_eia"]
    hdc = arms["full_eia_hdc"]
    retrieval_acc = float((hdc.get("tick_retrieval") or {}).get("accuracy") or 0.0)
    return HdcCarryoverDiagnostics(
        both_arms_run=int(full["initiative_count"]) > 0 and int(hdc["initiative_count"]) > 0,
        hdc_retrieval_across_ticks=retrieval_acc > 0.0,
        eoi_persistence_hdc=float(hdc.get("eoi_persistence") or 0.0) >= 0.5,
        initiative_parity_or_hdc_ge=int(hdc["cumulative_initiatives"]) >= int(
            full["cumulative_initiatives"]
        ),
    )


def build_k_hdc_02_payload(
    *,
    seed: int = 42,
    generated: str | None = None,
    session_ticks: int | None = None,
    drive_threshold: float | None = None,
    llm_backend: str | None = None,
    hdc_dim: int = 512,
) -> dict[str, Any]:
    _ensure_paths()
    cfg = load_config()
    t01 = cfg.get("t_agent_01") or {}
    session_ticks = session_ticks or max(MIN_SESSION_TICKS, int(t01.get("quiet_ticks", 4)))
    drive_threshold = drive_threshold or float(t01.get("drive_proposal_threshold", 0.22))
    llm_backend = llm_backend or str(t01.get("llm_backend", "mock"))

    arm_results = {
        arm: run_agent_carryover_session(
            arm,
            seed=seed,
            session_ticks=session_ticks,
            drive_threshold=drive_threshold,
            llm_backend=llm_backend,
            hdc_dim=hdc_dim,
        )
        for arm in K_HDC_02_ARMS
    }

    diagnostics = evaluate_carryover_diagnostics(arm_results)
    full = arm_results["full_eia"]
    hdc = arm_results["full_eia_hdc"]
    diagnostic_pass = (
        diagnostics.both_arms_run
        and diagnostics.hdc_retrieval_across_ticks
        and session_ticks >= MIN_SESSION_TICKS
    )

    return {
        "milestone": MILESTONE,
        "harness_id": HARNESS_ID,
        "artifact_id": "M-K-HDC-02_2026-09-11",
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
        "session_ticks": session_ticks,
        "hdc_dim": hdc_dim,
        "sources": {
            "hdc_memory": _rel(ADAPTERS / "hdc_memory.py"),
            "shadow_multitick": _rel(REPO / "src" / "eia" / "runtime" / "shadow_multitick.py"),
            "t_agent_01": _rel(AGENT_EIA / "harnesses" / "t_agent_01_llm_eia.py"),
        },
        "arms": {
            arm: {
                "initiative_count": r["initiative_count"],
                "cumulative_initiatives": r["cumulative_initiatives"],
                "eoi_mean": (r["eoi"] or {}).get("eoi_mean"),
                "eoi_persistence": r["eoi_persistence"],
                "tick_retrieval_accuracy": (r.get("tick_retrieval") or {}).get("accuracy"),
                "genesis_delta": r["genesis_delta"],
                "per_tick": r["per_tick"],
            }
            for arm, r in arm_results.items()
        },
        "comparison": {
            "initiative_delta_hdc_minus_full": (
                int(hdc["cumulative_initiatives"]) - int(full["cumulative_initiatives"])
            ),
            "eoi_delta_hdc_minus_full": round(
                float((hdc["eoi"] or {}).get("eoi_mean") or 0.0)
                - float((full["eoi"] or {}).get("eoi_mean") or 0.0),
                6,
            ),
            "retrieval_accuracy": (hdc.get("tick_retrieval") or {}).get("accuracy"),
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
            "Kairologos HDC carryover across 2+ session ticks at X^trigger=0. "
            "Retrieval accuracy tick-to-tick vs full_eia baseline; not proto-AGI."
        ),
    }


def artifact_sha256(payload: dict[str, Any]) -> str:
    body = {k: v for k, v in payload.items() if k != "artifact_sha256"}
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def render_k_hdc_02_markdown(payload: dict[str, Any]) -> str:
    arms = payload.get("arms") or {}
    cmp_ = payload.get("comparison") or {}
    lines = [
        f"# M-K-HDC-02 HDC carryover — {payload.get('date', '')}",
        "",
        f"**Harness:** {payload.get('harness_id')} · **Tier:** C · **session_ticks:** {payload.get('session_ticks')}",
        f"**SHA-256:** `{payload.get('artifact_sha256', '')}`",
        "",
        "## Arms",
        "",
        "| Arm | cumulative initiatives | EOI mean | retrieval acc | EOI persistence |",
        "|-----|------------------------|----------|---------------|-----------------|",
    ]
    for arm_key in K_HDC_02_ARMS:
        row = arms.get(arm_key) or {}
        retr = row.get("tick_retrieval_accuracy")
        retr_s = f"{retr:.2%}" if retr is not None else "—"
        lines.append(
            f"| `{arm_key}` | {row.get('cumulative_initiatives', 0)} | "
            f"{row.get('eoi_mean', 0):.3f} | {retr_s} | {row.get('eoi_persistence', 0):.3f} |"
        )
    lines.extend([
        "",
        f"- initiative Δ (hdc − full): `{cmp_.get('initiative_delta_hdc_minus_full')}`",
        f"- retrieval accuracy: `{cmp_.get('retrieval_accuracy')}`",
        "",
        f"**diagnostic_pass:** `{payload.get('diagnostic_pass')}`",
    ])
    return "\n".join(lines)

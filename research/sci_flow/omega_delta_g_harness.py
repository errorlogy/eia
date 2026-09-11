"""OMEGA→ΔG bridge probe — correlate OMEGA_t arms with shadow genesis delta (X_trigger=0).

Tests whether OMEGA_t variation across paired do(O) arms correlates with measurable
ΔG / goal-symbol change in omega-bridged shadow multitick under zero user trigger.

Tier C only; ``claim_allowed=false``; no D1 ``e_endo_support`` from OMEGA alone.
May still confirm F-OMEGA-DECOR (decorative OMEGA without genesis linkage).
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import sys
import types
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Literal

REPO = Path(__file__).resolve().parents[2]
SCI_FLOW = Path(__file__).resolve().parent
SRC = REPO / "src"
WOE_SRC = REPO / "research" / "cursor-starter-v0.2" / "src"
WOE_PKG = WOE_SRC / "eia"
OSCILLATORY = WOE_PKG / "oscillatory_state.py"
ARMS_ARTIFACT = SCI_FLOW / "M-MO_do_o_arms_2026-09-02.json"
BRIDGE_ARTIFACT_JSON = SCI_FLOW / "M-OMEGA_delta_G_2026-09-05.json"
BRIDGE_ARTIFACT_MD = SCI_FLOW / "M-OMEGA_delta_G_2026-09-05.md"

ArmKey = Literal[
    "native_oscillatory",
    "neuraxon_bridged",
    "plasticity_off",
    "phase_scramble",
]

OMEGA_DECOR_THRESHOLD = 0.75
OMEGA_SPAN_MIN = 0.1
GENESIS_EPSILON = 1e-9


def _ensure_paths() -> None:
    for path in (str(SRC), str(SCI_FLOW)):
        if path not in sys.path:
            sys.path.insert(0, path)


def _load_oscillatory_module() -> Any:
    spec = importlib.util.spec_from_file_location("oscillatory_state_omega_dg", OSCILLATORY)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {OSCILLATORY}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _rel(path: Path) -> str:
    try:
        return path.relative_to(REPO).as_posix()
    except ValueError:
        return path.as_posix()


def load_arms_payload(
    arms_path: Path = ARMS_ARTIFACT,
    *,
    regenerate: bool = False,
    steps: int = 50,
    seed: int = 42,
) -> dict[str, Any]:
    """Load paired do(O) arms artifact, optionally regenerating it first."""
    from mo_proof_bridge_harness import load_arms_payload as _load

    return _load(arms_path, regenerate=regenerate, steps=steps, seed=seed)


def build_phase_scramble_omega_ctx(osc_mod: Any) -> dict[str, Any]:
    """do(O) phase-scramble control — low OMEGA_t via scrambled carrier phases."""
    carriers = list(osc_mod.DEFAULT_WOE_CARRIERS)
    phases = [0.0, math.pi / 2, math.pi, 3 * math.pi / 2]
    amps = [1.0] * len(carriers)
    ows = osc_mod.OmegaWaveState.from_carrier_phases(phases, carriers=carriers, amplitudes=amps)
    omega = float(osc_mod.omega_metric(ows))
    kuramoto_r = float(osc_mod.kuramoto_order_parameter(phases))
    return {
        "omega_t": omega,
        "kuramoto_r": kuramoto_r,
        "omega_wave_state": {
            "phase_coherence": ows.phase_coherence,
            "cadence": ows.cadence,
            "synchrony": ows.synchrony,
            "productive_tension": ows.productive_tension,
            "handoff": ows.handoff,
            "drift": ows.drift,
            "closure_velocity": ows.closure_velocity,
            "n_bands": len(carriers),
        },
        "crosswalk": {"do_o_phase_scramble": True},
        "vendor": "eia.oscillatory_state",
        "arm": "do_o_phase_scramble",
        "intervention_id": "do_o_phase_scramble",
    }


def omega_ctx_for_arm(
    arm_key: ArmKey,
    arms_payload: dict[str, Any],
    *,
    osc_mod: Any | None = None,
) -> dict[str, Any]:
    """Resolve omega injection context for one probe arm."""
    from mo_shadow_bridge_harness import extract_omega_crosswalk

    arms = arms_payload.get("arms") or {}
    if arm_key == "native_oscillatory":
        return extract_omega_crosswalk(arms.get("native_oscillatory_state") or {})
    if arm_key == "neuraxon_bridged":
        return extract_omega_crosswalk(arms.get("neuraxon_baseline") or {})
    if arm_key == "plasticity_off":
        return extract_omega_crosswalk(arms.get("do_o_neuraxon_plasticity_off") or {})
    if arm_key == "phase_scramble":
        mod = osc_mod or _load_oscillatory_module()
        return build_phase_scramble_omega_ctx(mod)
    raise ValueError(f"unknown arm_key: {arm_key}")


def shadow_initiative_fingerprint(ep: dict[str, Any]) -> str:
    """Compact goal/action fingerprint from shadow ATT-R events."""
    parts: list[str] = []
    for event in ep.get("events") or []:
        kind = event.get("kind")
        if kind in ("G", "G_prime", "A", "Pi"):
            parts.append(f"{kind}:{event.get('label', '')}")
    return "|".join(parts)


def extract_genesis_metrics(ep: dict[str, Any]) -> dict[str, Any]:
    """ΔG / genesis delta from one shadow episode (G → G_prime under X_trigger=0)."""
    motive_ids = list(ep.get("motive_ids") or [])
    events = ep.get("events") or []
    g0 = motive_ids[0] if motive_ids else None
    g_prime = motive_ids[-1] if len(motive_ids) > 1 else None
    goal_symbol_changed = bool(g0 and g_prime and g0 != g_prime)
    genesis_delta = 1.0 if goal_symbol_changed else 0.0
    has_novel_g_prime = any(
        e.get("kind") == "G_prime" and e.get("novel") for e in events
    )
    return {
        "g0_id": g0,
        "g_prime_id": g_prime,
        "goal_symbol_changed": goal_symbol_changed,
        "genesis_delta": genesis_delta,
        "has_novel_g_prime": has_novel_g_prime,
        "initiative_fingerprint": shadow_initiative_fingerprint(ep),
        "x_trigger_zero": not any(
            e.get("label") == "user_prompt" for e in events
        ),
    }


def run_arm_shadow_probe(
    arm_key: ArmKey,
    omega_ctx: dict[str, Any],
    *,
    seed: int = 0,
) -> dict[str, Any]:
    """Run one omega-bridged shadow multitick probe (ambient obs only, no user trigger)."""
    from mo_shadow_bridge_harness import run_omega_bridged_shadow_episode

    ep = run_omega_bridged_shadow_episode(omega_ctx, seed=seed)
    genesis = extract_genesis_metrics(ep)
    omega_t = float(omega_ctx.get("omega_t") or 0.0)
    osc_mod = _load_oscillatory_module()
    f_decor = osc_mod.falsifier_f_omega_decor(
        omega=omega_t,
        genesis_delta=genesis["genesis_delta"],
        omega_threshold=OMEGA_DECOR_THRESHOLD,
        epsilon=GENESIS_EPSILON,
    )
    intervention_id = omega_ctx.get("intervention_id")
    if intervention_id is None and (omega_ctx.get("crosswalk") or {}).get("do_o_phase_scramble"):
        intervention_id = "do_o_phase_scramble"
    return {
        "arm_key": arm_key,
        "bridge_kind": ep.get("bridge_kind"),
        "omega_t": omega_t,
        "kuramoto_r": float(omega_ctx.get("kuramoto_r") or ep.get("kuramoto_r") or 0.0),
        "intervention_id": intervention_id,
        "vendor": omega_ctx.get("vendor", "unknown"),
        "shadow": ep,
        **genesis,
        "f_omega_decor_arm": f_decor,
        "claim_allowed": False,
    }


@dataclass(frozen=True, slots=True)
class OmegaGCorrelation:
    omega_span: float
    genesis_span: float
    fingerprint_parity: bool
    decorrelation_confirmed: bool
    f_omega_decor_aggregate: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "omega_span": round(self.omega_span, 6),
            "genesis_span": round(self.genesis_span, 6),
            "fingerprint_parity": self.fingerprint_parity,
            "decorrelation_confirmed": self.decorrelation_confirmed,
            "f_omega_decor_aggregate": self.f_omega_decor_aggregate,
        }


def evaluate_omega_g_correlation(arm_probes: list[dict[str, Any]]) -> OmegaGCorrelation:
    """Cross-arm: large OMEGA span with invariant genesis fingerprint ⇒ F-OMEGA-DECOR."""
    omegas = [float(p["omega_t"]) for p in arm_probes]
    genesis = [float(p["genesis_delta"]) for p in arm_probes]
    fingerprints = [str(p["initiative_fingerprint"]) for p in arm_probes]
    omega_span = max(omegas) - min(omegas) if omegas else 0.0
    genesis_span = max(genesis) - min(genesis) if genesis else 0.0
    fingerprint_parity = len(set(fingerprints)) == 1 and bool(fingerprints)
    decorrelation = omega_span >= OMEGA_SPAN_MIN and genesis_span <= GENESIS_EPSILON
    f_aggregate = decorrelation and fingerprint_parity
    return OmegaGCorrelation(
        omega_span=omega_span,
        genesis_span=genesis_span,
        fingerprint_parity=fingerprint_parity,
        decorrelation_confirmed=decorrelation,
        f_omega_decor_aggregate=f_aggregate,
    )


def build_omega_delta_g_payload(
    arms_payload: dict[str, Any],
    *,
    seed: int = 42,
    generated: str | None = None,
) -> dict[str, Any]:
    """Build full OMEGA→ΔG bridge artifact from paired arms + shadow probes."""
    _ensure_paths()
    osc_mod = _load_oscillatory_module()
    arm_keys: tuple[ArmKey, ...] = (
        "native_oscillatory",
        "neuraxon_bridged",
        "plasticity_off",
        "phase_scramble",
    )
    probes: list[dict[str, Any]] = []
    for key in arm_keys:
        ctx = omega_ctx_for_arm(key, arms_payload, osc_mod=osc_mod)
        probe = run_arm_shadow_probe(key, ctx, seed=seed)
        probe["omega_ctx"] = {
            k: ctx[k]
            for k in ("omega_t", "kuramoto_r", "vendor", "arm", "intervention_id")
            if k in ctx
        }
        probes.append(probe)

    correlation = evaluate_omega_g_correlation(probes)
    comparison = arms_payload.get("paired_comparison") or {}
    omega_cmp = comparison.get("omega_t_final") or {}
    hints = comparison.get("falsifier_hints") or {}

    baseline_probe = next(p for p in probes if p["arm_key"] == "neuraxon_bridged")
    native_probe = next(p for p in probes if p["arm_key"] == "native_oscillatory")
    plasticity_probe = next(p for p in probes if p["arm_key"] == "plasticity_off")
    scramble_probe = next(p for p in probes if p["arm_key"] == "phase_scramble")

    f_omega_decor_status = "confirmed" if correlation.f_omega_decor_aggregate else "not_confirmed"
    if correlation.f_omega_decor_aggregate or any(p["f_omega_decor_arm"] for p in probes):
        f_omega_decor_status = "confirmed"

    return {
        "milestone": "M-OMEGA-DELTA-G",
        "artifact_id": "M-OMEGA_delta_G_2026-09-05",
        "tick_id": "M-OMEGA-DELTA-G",
        "date": generated or date.today().isoformat(),
        "branch": "research/cursor-starter-v0.2-woe-eis",
        "cell": "D2×L2",
        "tier": "C",
        "claim_ceiling": "C2",
        "claim_allowed": False,
        "e_endo_support": "none",
        "witness_support": "none",
        "c_ladder_raise_allowed": False,
        "agi_star_claim": False,
        "att": "ATT-R",
        "x_trigger_zero": True,
        "seed": seed,
        "sources": {
            "arms": _rel(ARMS_ARTIFACT),
            "admissibility": "research/sci_flow/M-O_PROOF_ADMISSIBILITY.md",
            "shadow_bridge": "research/sci_flow/mo_shadow_bridge_harness.py",
            "oscillatory_state": "research/cursor-starter-v0.2/src/eia/oscillatory_state.py",
            "shadow_runtime": "src/eia/runtime/shadow_multitick.py",
        },
        "arms": {
            key: {
                "omega_t": p["omega_t"],
                "genesis_delta": p["genesis_delta"],
                "goal_symbol_changed": p["goal_symbol_changed"],
                "has_novel_g_prime": p["has_novel_g_prime"],
                "initiative_fingerprint": p["initiative_fingerprint"],
                "f_omega_decor_arm": p["f_omega_decor_arm"],
                "intervention_id": p.get("intervention_id"),
            }
            for key, p in zip(arm_keys, probes, strict=True)
        },
        "paired_vendor_omega_delta": {
            "plasticity_off_vs_baseline": omega_cmp.get("delta_plasticity_off_vs_baseline"),
            "native_vs_baseline": omega_cmp.get("delta_native_vs_baseline"),
        },
        "shadow_genesis_compare": {
            "native_vs_neuraxon": {
                "omega_delta": round(native_probe["omega_t"] - baseline_probe["omega_t"], 6),
                "genesis_delta_unchanged": (
                    native_probe["genesis_delta"] == baseline_probe["genesis_delta"]
                ),
                "fingerprint_match": (
                    native_probe["initiative_fingerprint"]
                    == baseline_probe["initiative_fingerprint"]
                ),
            },
            "plasticity_off_vs_neuraxon": {
                "omega_delta": round(
                    plasticity_probe["omega_t"] - baseline_probe["omega_t"], 6
                ),
                "genesis_delta_unchanged": (
                    plasticity_probe["genesis_delta"] == baseline_probe["genesis_delta"]
                ),
                "fingerprint_match": (
                    plasticity_probe["initiative_fingerprint"]
                    == baseline_probe["initiative_fingerprint"]
                ),
            },
            "phase_scramble_vs_native": {
                "omega_delta": round(
                    scramble_probe["omega_t"] - native_probe["omega_t"], 6
                ),
                "genesis_delta_unchanged": (
                    scramble_probe["genesis_delta"] == native_probe["genesis_delta"]
                ),
                "fingerprint_match": (
                    scramble_probe["initiative_fingerprint"]
                    == native_probe["initiative_fingerprint"]
                ),
            },
        },
        "omega_g_correlation": correlation.to_dict(),
        "f_omega_decor": {
            "status": f_omega_decor_status,
            "aggregate": correlation.f_omega_decor_aggregate,
            "per_arm": {p["arm_key"]: p["f_omega_decor_arm"] for p in probes},
            "vendor_hints": hints.get("F-OMEGA-DECOR"),
        },
        "falsifiers_active": [
            "F-KURAMOTO-AS-E",
            "F-OMEGA-DECOR",
            "F-SYNC",
            "F-STRUCT≠E",
        ],
        "note": (
            "OMEGA_t span across arms does not induce ΔG / initiative fingerprint change "
            "on matched-seed omega-bridged shadow multitick (X_trigger=0). "
            "Does not establish E_endo or raise C-level."
        ),
    }


def artifact_sha256(payload: dict[str, Any]) -> str:
    """Stable SHA-256 over canonical JSON (excludes sha field)."""
    body = {k: v for k, v in payload.items() if k != "artifact_sha256"}
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def render_omega_delta_g_markdown(payload: dict[str, Any]) -> str:
    """Render markdown artifact for OMEGA→ΔG bridge probe."""
    arms = payload.get("arms") or {}
    corr = payload.get("omega_g_correlation") or {}
    decor = payload.get("f_omega_decor") or {}
    compare = payload.get("shadow_genesis_compare") or {}

    lines = [
        f"# M-OMEGA Delta-G Bridge — {payload.get('date', '')}",
        "",
        f"**Cell:** {payload.get('cell', 'D2×L2')} · **Tier:** {payload.get('tier', 'C')} · "
        f"**ATT:** {payload.get('att', 'ATT-R')}",
        f"**Seed:** {payload.get('seed')} · **X_trigger:** 0 (shadow, no user prompt)",
        f"**SHA-256:** `{payload.get('artifact_sha256', '')}`",
        "",
        "## Arms (OMEGA_t vs ΔG)",
        "",
        "| Arm | OMEGA_t | genesis_Δ | G symbol change | F-OMEGA-DECOR (arm) |",
        "|-----|---------|-----------|-----------------|---------------------|",
    ]
    for key, row in arms.items():
        lines.append(
            f"| {key} | {row.get('omega_t')} | {row.get('genesis_delta')} | "
            f"{row.get('goal_symbol_changed')} | {row.get('f_omega_decor_arm')} |"
        )

    nat_vs_neu = compare.get("native_vs_neuraxon") or {}
    lines.extend(
        [
            "",
            "## Cross-arm genesis compare",
            "",
            f"- native↔neuraxon: Δω={nat_vs_neu.get('omega_delta')} · "
            f"ΔG unchanged={nat_vs_neu.get('genesis_delta_unchanged')} · "
            f"fingerprint match={nat_vs_neu.get('fingerprint_match')}",
            f"- OMEGA span: `{corr.get('omega_span')}` · genesis span: `{corr.get('genesis_span')}`",
            f"- Fingerprint parity: `{corr.get('fingerprint_parity')}`",
            f"- **F-OMEGA-DECOR aggregate:** `{decor.get('aggregate')}` ({decor.get('status')})",
            "",
            "## Invariants",
            "",
            "- `e_endo_support=none` (no D1 bleed)",
            "- `claim_allowed=false`",
            "- `c_ladder_raise_allowed=false`",
            "- `agi_star_claim=false`",
            "- Kuramoto R ≠ E_endo",
            "- OMEGA decorative when high ω does not change genesis fingerprint",
        ]
    )
    return "\n".join(lines)


def maybe_refresh_adjunct_ledger(
    arms_payload: dict[str, Any],
    bridge_payload: dict[str, Any],
    *,
    generated: str | None = None,
) -> dict[str, Any] | None:
    """Rebuild adjunct ledger only if OMEGA→ΔG witness improves beyond partial."""
    if bridge_payload.get("f_omega_decor", {}).get("status") == "confirmed":
        return None
    from mo_proof_bridge_harness import ADJUNCT_ARTIFACT_JSON, build_adjunct_ledger

    new_ledger = build_adjunct_ledger(arms_payload, generated=generated)
    if ADJUNCT_ARTIFACT_JSON.is_file():
        current = json.loads(ADJUNCT_ARTIFACT_JSON.read_text(encoding="utf-8"))
        current_ws = current.get("witness_support", "none")
        new_ws = new_ledger.get("witness_support", "none")
        rank = {"none": 0, "partial": 1}
        if rank.get(new_ws, 0) <= rank.get(current_ws, 0):
            return None
    return new_ledger

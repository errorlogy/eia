"""K-KUR-02 — paired do(O) scramble: Kuramoto R↑ without ΔG.

Explicit scramble arm on oscillatory O while holding spike/behavior fixed.
Strengthens F-KURAMOTO-AS-E with causal framing: high R must not imply genesis.
"""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import yaml

BRAIN_AI = Path(__file__).resolve().parents[1]
REPO = BRAIN_AI.parents[1]
KAIRO = REPO / "research" / "kairologos_experiments"
ADAPTERS = BRAIN_AI / "adapters"
ARTIFACTS = KAIRO / "artifacts"
ARTIFACT_JSON = ARTIFACTS / "M-K-KUR-02_2026-09-11.json"
ARTIFACT_MD = ARTIFACTS / "M-K-KUR-02_2026-09-11.md"
CONFIG_PATH = BRAIN_AI / "config.yaml"
BRANCH = "main"

KURAMOTO_HIGH = 0.85
GENESIS_EPSILON = 1e-9
OMEGA_DELTA_MIN = 0.02
HARNESS_ID = "K-KUR-02"
MILESTONE = "M-KAIRO-TIER-C"

PAIRED_ARMS: tuple[str, ...] = ("coupled_active", "phase_scramble_control")


def _ensure_paths() -> None:
    for path in (str(ADAPTERS), str(BRAIN_AI / "harnesses"), str(REPO / "src")):
        if path not in sys.path:
            sys.path.insert(0, path)


def load_config(path: Path = CONFIG_PATH) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


@dataclass(frozen=True, slots=True)
class PairedScrambleVerdict:
    omega_changes_under_scramble: bool
    genesis_invariant_under_scramble: bool
    kuramoto_high_in_either_arm: bool
    high_r_without_genesis_delta: bool
    f_kuramoto_as_e_causal: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "omega_changes_under_scramble": self.omega_changes_under_scramble,
            "genesis_invariant_under_scramble": self.genesis_invariant_under_scramble,
            "kuramoto_high_in_either_arm": self.kuramoto_high_in_either_arm,
            "high_r_without_genesis_delta": self.high_r_without_genesis_delta,
            "F-KURAMOTO-AS-E": self.f_kuramoto_as_e_causal,
        }


def run_paired_do_o_probe(
    source_key: str,
    *,
    seed: int,
    n_nodes: int,
    duration_ms: float,
    dt_ms: float,
    prefer_brian2: bool,
    carriers: tuple[float, ...],
    session_ticks: int,
) -> dict[str, Any]:
    """Paired do(O): same spikes/behavior, natural vs phase-scrambled O."""
    _ensure_paths()
    from behavior_metrics import compute_behavior_metrics
    from connectome_export import load_subgraph
    from ot_injection import inject_omega_from_spikes, _load_oscillatory_module
    from spike_arms import run_spike_arm, scramble_spike_phases_for_omega
    from t_brain_04_longitudinal_carryover import run_longitudinal_arm_session
    from t_brain_05_connectome_parity import SOURCE_SEED_OFFSET, source_fallback_info

    src_seed = seed + SOURCE_SEED_OFFSET.get(source_key, 0)
    fallback = source_fallback_info(source_key)
    subgraph = load_subgraph(
        connectome_source=source_key,
        n_nodes=n_nodes,
        seed=src_seed,
        prefer_bundled=(source_key == "bundled_tiny"),
    )
    osc_mod = _load_oscillatory_module()

    spike_payload = run_spike_arm(
        subgraph,
        "coupled_active",
        seed=src_seed,
        duration_ms=duration_ms,
        dt_ms=dt_ms,
        prefer_brian2=prefer_brian2,
    )
    behavior = compute_behavior_metrics(spike_payload)
    arms: dict[str, Any] = {}

    for arm_key in PAIRED_ARMS:
        if arm_key == "phase_scramble_control":
            phases = scramble_spike_phases_for_omega(
                spike_payload,
                subgraph.node_ids,
                carriers=carriers,
                duration_ms=duration_ms,
                seed=src_seed + 99,
            )
            amps = [
                min(1.0, 0.3 + 0.1 * len(spike_payload["spike_times_ms"].get(nid, [])))
                for nid in subgraph.node_ids[: len(carriers)]
            ]
            while len(amps) < len(carriers):
                amps.append(1.0)
            ows = osc_mod.OmegaWaveState.from_carrier_phases(
                phases, carriers=carriers, amplitudes=amps
            )
            omega_ctx = {
                "omega_t": float(osc_mod.omega_metric(ows)),
                "kuramoto_r": float(osc_mod.kuramoto_order_parameter(phases)),
                "arm": arm_key,
                "intervention": "do(O=phase_scramble)",
            }
        else:
            omega_ctx = inject_omega_from_spikes(
                spike_payload, subgraph.node_ids, carriers=carriers, osc_mod=osc_mod
            )
            omega_ctx["arm"] = arm_key
            omega_ctx["intervention"] = "do(O=natural)"

        sess = run_longitudinal_arm_session(
            arm_key,  # type: ignore[arg-type]
            omega_ctx,
            behavior,
            seed=src_seed,
            session_ticks=session_ticks,
        )
        tick0 = sess["ticks"][0]
        arms[arm_key] = {
            "kuramoto_r": omega_ctx["kuramoto_r"],
            "omega_t": omega_ctx["omega_t"],
            "genesis_delta": tick0["genesis"]["genesis_delta"],
            "cumulative_genesis_delta": sess["cumulative_genesis_delta"],
            "has_novel_g_prime": tick0["genesis"]["has_novel_g_prime"],
            "intervention": omega_ctx["intervention"],
            "behavior_hash": behavior.get("behavior_hash"),
        }

    natural = arms["coupled_active"]
    scramble = arms["phase_scramble_control"]
    omega_delta = abs(float(natural["omega_t"]) - float(scramble["omega_t"]))
    genesis_delta_natural = float(natural["genesis_delta"])
    genesis_delta_scramble = float(scramble["genesis_delta"])
    genesis_invariant = abs(genesis_delta_natural - genesis_delta_scramble) <= GENESIS_EPSILON

    kuramoto_natural = float(natural["kuramoto_r"])
    kuramoto_scramble = float(scramble["kuramoto_r"])
    high_r = kuramoto_natural >= KURAMOTO_HIGH or kuramoto_scramble >= KURAMOTO_HIGH
    r_preserved_or_elevated = kuramoto_scramble >= kuramoto_natural - 0.05
    high_r_no_delta_g = (
        genesis_invariant
        and omega_delta >= OMEGA_DELTA_MIN
        and (high_r or r_preserved_or_elevated)
    )

    return {
        "source_key": source_key,
        "connectome_source_tag": subgraph.source,
        "source_fallback": fallback,
        "paired_spike_arm": "coupled_active",
        "arms": arms,
        "causal_contrast": {
            "intervention": "do(O=phase_scramble) vs do(O=natural)",
            "behavior_matched": natural.get("behavior_hash") == scramble.get("behavior_hash"),
            "omega_delta": round(omega_delta, 6),
            "omega_changes": omega_delta >= OMEGA_DELTA_MIN,
            "genesis_delta_natural": genesis_delta_natural,
            "genesis_delta_scramble": genesis_delta_scramble,
            "genesis_invariant": genesis_invariant,
            "kuramoto_r_natural": round(kuramoto_natural, 6),
            "kuramoto_r_scramble": round(kuramoto_scramble, 6),
            "high_r_without_genesis_delta": high_r_no_delta_g,
        },
    }


def build_k_kur_02_payload(
    *,
    seed: int | None = None,
    generated: str | None = None,
    prefer_brian2: bool | None = None,
    session_ticks: int = 2,
    sources: tuple[str, ...] | None = None,
) -> dict[str, Any]:
    _ensure_paths()
    from t_brain_05_connectome_parity import PARITY_SOURCES

    cfg = load_config()
    sim = cfg.get("simulation") or {}
    conn = cfg.get("connectome") or {}
    seed = int(seed if seed is not None else sim.get("seed", 42))
    prefer_brian2 = (
        prefer_brian2 if prefer_brian2 is not None else bool(sim.get("prefer_brian2", False))
    )
    n_nodes = min(int(sim.get("n_nodes", 8)), int(conn.get("max_subgraph_nodes", 500)))
    duration_ms = float(sim.get("duration_ms", 100.0))
    dt_ms = float(sim.get("dt_ms", 1.0))
    carriers = tuple(cfg.get("carriers_hz") or [20, 30, 42, 70])
    source_list = tuple(sources or PARITY_SOURCES)

    probes: list[dict[str, Any]] = []
    omega_changes_count = 0
    genesis_invariant_count = 0
    high_r_no_delta_count = 0

    for source_key in source_list:
        probe = run_paired_do_o_probe(
            source_key,
            seed=seed,
            n_nodes=n_nodes,
            duration_ms=duration_ms,
            dt_ms=dt_ms,
            prefer_brian2=prefer_brian2,
            carriers=carriers,
            session_ticks=session_ticks,
        )
        probes.append(probe)
        cc = probe["causal_contrast"]
        if cc["omega_changes"]:
            omega_changes_count += 1
        if cc["genesis_invariant"]:
            genesis_invariant_count += 1
        if cc["high_r_without_genesis_delta"]:
            high_r_no_delta_count += 1

    n_sources = len(probes)
    verdict = PairedScrambleVerdict(
        omega_changes_under_scramble=omega_changes_count > 0,
        genesis_invariant_under_scramble=genesis_invariant_count == n_sources and n_sources > 0,
        kuramoto_high_in_either_arm=any(
            float(p["arms"]["coupled_active"]["kuramoto_r"]) >= KURAMOTO_HIGH
            or float(p["arms"]["phase_scramble_control"]["kuramoto_r"]) >= KURAMOTO_HIGH
            for p in probes
        ),
        high_r_without_genesis_delta=high_r_no_delta_count > 0,
        f_kuramoto_as_e_causal=(
            genesis_invariant_count == n_sources
            and omega_changes_count > 0
            and high_r_no_delta_count >= max(1, n_sources // 2)
        ),
    )

    diagnostic_pass = (
        n_sources > 0
        and verdict.omega_changes_under_scramble
        and verdict.genesis_invariant_under_scramble
    )

    return {
        "milestone": MILESTONE,
        "harness_id": HARNESS_ID,
        "artifact_id": "M-K-KUR-02_2026-09-11",
        "tick_id": HARNESS_ID,
        "date": generated or date.today().isoformat(),
        "branch": BRANCH,
        "cell": "D2×L2",
        "tier": "C",
        "claim_ceiling": "C2",
        "ceiling": "C2",
        "theory_strand": "kairologos_explore",
        "claim_allowed": False,
        "e_endo_support": "none",
        "witness_support": "none",
        "c_ladder_raise_allowed": False,
        "agi_star_claim": False,
        "att": "ATT-R",
        "x_trigger_zero": True,
        "session_ticks": session_ticks,
        "seed": seed,
        "paired_arms": list(PAIRED_ARMS),
        "connectome_sources": list(source_list),
        "per_source": {p["source_key"]: p for p in probes},
        "scramble_verdict": verdict.to_dict(),
        "falsifiers": {
            "F-KURAMOTO-AS-E": {
                "status": "confirmed_causal" if verdict.f_kuramoto_as_e_causal else "annotation",
                "high_r_without_genesis_rows": high_r_no_delta_count,
                "note": (
                    "Paired do(O=scramble): OMEGA changes but genesis_Δ invariant; "
                    "high Kuramoto R does not imply genesis — causal decorrelation"
                    if verdict.f_kuramoto_as_e_causal
                    else "Annotation — Kuramoto R must not be read as E_endo"
                ),
            }
        },
        "diagnostic_pass": diagnostic_pass,
        "falsifiers_active": ["F-KURAMOTO-AS-E"],
        "claim_invariants": {
            "claim_allowed": False,
            "e_endo_support": "none",
            "tier": "C",
            "ceiling": "C2",
            "theory_strand": "kairologos_explore",
            "agi_star_claim": False,
        },
        "note": (
            "Kairologos Tier C paired do(O) scramble: phase_scramble_control vs "
            "coupled_active on fixed spikes/behavior. Strengthens F-KURAMOTO-AS-E."
        ),
    }


def artifact_sha256(payload: dict[str, Any]) -> str:
    body = {k: v for k, v in payload.items() if k != "artifact_sha256"}
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def render_k_kur_02_markdown(payload: dict[str, Any]) -> str:
    verdict = payload.get("scramble_verdict") or {}
    fals = payload.get("falsifiers") or {}
    lines = [
        f"# M-K-KUR-02 paired do(O) scramble — {payload.get('date', '')}",
        "",
        f"**Harness:** {payload.get('harness_id')} · **Tier:** C · **Theory:** kairologos_explore",
        f"**SHA-256:** `{payload.get('artifact_sha256', '')}`",
        "",
        "## Paired scramble verdict",
        "",
        f"- omega changes under scramble: `{verdict.get('omega_changes_under_scramble')}`",
        f"- genesis invariant: `{verdict.get('genesis_invariant_under_scramble')}`",
        f"- high R without ΔG: `{verdict.get('high_r_without_genesis_delta')}`",
        f"- F-KURAMOTO-AS-E causal: `{verdict.get('F-KURAMOTO-AS-E')}`",
        "",
        "## Falsifiers",
        "",
        f"- F-KURAMOTO-AS-E: `{fals.get('F-KURAMOTO-AS-E', {}).get('status')}` "
        f"({fals.get('F-KURAMOTO-AS-E', {}).get('high_r_without_genesis_rows', 0)} sources)",
        "",
        f"**diagnostic_pass:** `{payload.get('diagnostic_pass')}`",
    ]
    return "\n".join(lines)

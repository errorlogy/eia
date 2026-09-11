"""T-BRAIN-02 — OMEGA_t vs behavioral proxy correlation / diagnostic harness.

Multi-arm synthetic connectome dynamics: activity rate, burstiness, population sync
vs OMEGA_t / Kuramoto R. Tier C only; ``claim_allowed=false``; no D1 bleed.
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
ADAPTERS = BRAIN_AI / "adapters"
ARTIFACTS = BRAIN_AI / "artifacts"
ARTIFACT_JSON = ARTIFACTS / "M-T-BRAIN-02_2026-09-10.json"
ARTIFACT_MD = ARTIFACTS / "M-T-BRAIN-02_2026-09-10.md"
CONFIG_PATH = BRAIN_AI / "config.yaml"
BRANCH = "research/brain-ai-connectome"

BEHAVIOR_SPAN_MIN = 0.01
OMEGA_SPAN_MIN = 0.05
OMEGA_BEHAV_R_MIN = 0.3


def _ensure_paths() -> None:
    for path in (str(ADAPTERS),):
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


@dataclass(frozen=True, slots=True)
class OmegaBehaviorCorrelation:
    omega_span: float
    behavior_span: float
    r_omega_activity: float | None
    r_kuramoto_sync: float | None
    f_omega_decor_arm: bool
    behavioral_variance_ok: bool
    omega_tracks_behavior: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "omega_span": round(self.omega_span, 6),
            "behavior_span": round(self.behavior_span, 6),
            "r_omega_activity": (
                round(self.r_omega_activity, 6) if self.r_omega_activity is not None else None
            ),
            "r_kuramoto_sync": (
                round(self.r_kuramoto_sync, 6) if self.r_kuramoto_sync is not None else None
            ),
            "f_omega_decor_arm": self.f_omega_decor_arm,
            "behavioral_variance_ok": self.behavioral_variance_ok,
            "omega_tracks_behavior": self.omega_tracks_behavior,
        }


def evaluate_omega_behavior_correlation(
    arm_probes: list[dict[str, Any]],
) -> OmegaBehaviorCorrelation:
    """Cross-arm diagnostics: OMEGA_t vs activity; Kuramoto vs population sync."""
    from behavior_metrics import pearson_r

    behavior_arms = [p for p in arm_probes if not p.get("phase_scramble_omega_only")]
    omegas = [float(p["omega_t"]) for p in behavior_arms]
    activities = [float(p["behavior"]["activity_rate_per_node_ms"]) for p in behavior_arms]
    kuramoto = [float(p["kuramoto_r"]) for p in behavior_arms]
    syncs = [float(p["behavior"]["population_sync"]) for p in behavior_arms]

    omega_span = max(omegas) - min(omegas) if omegas else 0.0
    behavior_span = max(activities) - min(activities) if activities else 0.0
    r_oa = pearson_r(omegas, activities)
    r_ks = pearson_r(kuramoto, syncs)

    scramble = next((p for p in arm_probes if p.get("phase_scramble_omega_only")), None)
    coupled = next((p for p in arm_probes if p.get("arm_key") == "coupled_active"), None)
    f_decor = False
    if scramble and coupled:
        beh_match = (
            abs(
                scramble["behavior"]["activity_rate_per_node_ms"]
                - coupled["behavior"]["activity_rate_per_node_ms"]
            )
            < 1e-4
            and scramble["behavior"]["n_spikes"] == coupled["behavior"]["n_spikes"]
        )
        omega_delta = abs(float(scramble["omega_t"]) - float(coupled["omega_t"]))
        f_decor = beh_match and omega_delta >= OMEGA_SPAN_MIN

    beh_ok = behavior_span >= BEHAVIOR_SPAN_MIN
    tracks = r_oa is not None and abs(r_oa) >= OMEGA_BEHAV_R_MIN and beh_ok

    return OmegaBehaviorCorrelation(
        omega_span=omega_span,
        behavior_span=behavior_span,
        r_omega_activity=r_oa,
        r_kuramoto_sync=r_ks,
        f_omega_decor_arm=f_decor,
        behavioral_variance_ok=beh_ok,
        omega_tracks_behavior=tracks,
    )


def build_t_brain_02_payload(
    *,
    seed: int | None = None,
    generated: str | None = None,
    prefer_brian2: bool | None = None,
) -> dict[str, Any]:
    """Build full T-BRAIN-02 artifact payload."""
    _ensure_paths()
    from behavior_metrics import compute_behavior_metrics
    from connectome_export import load_subgraph
    from ot_injection import inject_omega_from_spikes, _load_oscillatory_module
    from spike_arms import ARM_KEYS, run_spike_arm, scramble_spike_phases_for_omega

    cfg = load_config()
    sim = cfg.get("simulation") or {}
    t02 = cfg.get("t_brain_02") or {}
    seed = int(seed if seed is not None else sim.get("seed", 42))
    prefer_brian2 = (
        prefer_brian2 if prefer_brian2 is not None else bool(sim.get("prefer_brian2", False))
    )
    n_nodes = int(sim.get("n_nodes", 8))
    duration_ms = float(sim.get("duration_ms", 100.0))
    dt_ms = float(sim.get("dt_ms", 1.0))
    carriers = tuple(cfg.get("carriers_hz") or [20, 30, 42, 70])

    subgraph = load_subgraph(n_nodes=n_nodes, seed=seed, prefer_bundled=True)
    osc_mod = _load_oscillatory_module()
    arm_probes: list[dict[str, Any]] = []

    coupled_ref: dict[str, Any] | None = None
    for arm_key in ARM_KEYS:
        spike_payload = run_spike_arm(
            subgraph,
            arm_key,
            seed=seed,
            duration_ms=duration_ms,
            dt_ms=dt_ms,
            prefer_brian2=prefer_brian2,
            coupled_reference=coupled_ref,
        )
        if arm_key == "coupled_active":
            coupled_ref = spike_payload
        behavior = compute_behavior_metrics(spike_payload)

        if arm_key == "phase_scramble_control":
            phases = scramble_spike_phases_for_omega(
                spike_payload,
                subgraph.node_ids,
                carriers=carriers,
                duration_ms=duration_ms,
                seed=seed + 99,
            )
            amps = [min(1.0, 0.3 + 0.1 * len(spike_payload["spike_times_ms"].get(nid, [])))
                    for nid in subgraph.node_ids[: len(carriers)]]
            while len(amps) < len(carriers):
                amps.append(1.0)
            ows = osc_mod.OmegaWaveState.from_carrier_phases(phases, carriers=carriers, amplitudes=amps)
            omega_ctx = {
                "omega_t": float(osc_mod.omega_metric(ows)),
                "kuramoto_r": float(osc_mod.kuramoto_order_parameter(phases)),
                "omega_wave_state": {
                    "phase_coherence": ows.phase_coherence,
                    "synchrony": ows.synchrony,
                    "productive_tension": ows.productive_tension,
                },
                "crosswalk": {"phase_scramble_control": True},
                "spike_backend": spike_payload.get("backend"),
            }
        else:
            omega_ctx = inject_omega_from_spikes(
                spike_payload, subgraph.node_ids, carriers=carriers
            )

        arm_probes.append({
            "arm_key": arm_key,
            "intervention_id": arm_key,
            "phase_scramble_omega_only": arm_key == "phase_scramble_control",
            "spike_backend": spike_payload.get("backend"),
            "n_spikes": spike_payload.get("n_spikes"),
            "behavior": behavior,
            "omega_t": omega_ctx.get("omega_t"),
            "kuramoto_r": omega_ctx.get("kuramoto_r"),
            "omega_wave_state": omega_ctx.get("omega_wave_state"),
        })

    correlation = evaluate_omega_behavior_correlation(arm_probes)
    diagnostic_pass = correlation.behavioral_variance_ok and correlation.r_omega_activity is not None

    return {
        "milestone": "M-BRAIN-AI",
        "harness_id": "T-BRAIN-02",
        "artifact_id": "M-T-BRAIN-02_2026-09-10",
        "tick_id": "T-BRAIN-02",
        "date": generated or date.today().isoformat(),
        "branch": BRANCH,
        "cell": "D2×L2",
        "tier": "C",
        "claim_ceiling": "C2",
        "claim_allowed": False,
        "e_endo_support": "none",
        "witness_support": "none",
        "c_ladder_raise_allowed": False,
        "agi_star_claim": False,
        "att": "ATT-R",
        "seed": seed,
        "sources": {
            "t_brain_01": _rel(BRAIN_AI / "harnesses" / "t_brain_01_connectome_ot.py"),
            "behavior_metrics": _rel(BRAIN_AI / "adapters" / "behavior_metrics.py"),
            "spike_arms": _rel(BRAIN_AI / "adapters" / "spike_arms.py"),
            "ot_injection": _rel(BRAIN_AI / "adapters" / "ot_injection.py"),
            "oscillatory_state": "research/cursor-starter-v0.2/src/eia/oscillatory_state.py",
        },
        "arms": {p["arm_key"]: {
            "omega_t": p["omega_t"],
            "kuramoto_r": p["kuramoto_r"],
            "behavior": p["behavior"],
            "spike_backend": p["spike_backend"],
            "phase_scramble_omega_only": p["phase_scramble_omega_only"],
        } for p in arm_probes},
        "omega_behavior_correlation": correlation.to_dict(),
        "diagnostic_pass": diagnostic_pass,
        "f_omega_decor": {
            "status": "confirmed" if correlation.f_omega_decor_arm else "not_confirmed",
            "phase_scramble_control": correlation.f_omega_decor_arm,
        },
        "falsifiers_active": [
            "F-KURAMOTO-AS-E",
            "F-OMEGA-DECOR",
            "F-SYNC",
            "F-BEHAV-OMEGA-MISMATCH",
            "F-STRUCT≠E",
        ],
        "connectome_source": subgraph.source,
        "n_nodes": subgraph.n_nodes,
        "note": (
            "OMEGA_t vs behavioral proxy correlation across synthetic connectome arms. "
            "phase_scramble_control isolates decorative OMEGA shift at matched spike behavior. "
            "Does not establish E_endo, ATT-R closure, or raise C-level. "
            "Real FlyWire/Brian2 path deferred — synthetic MVP sufficient for diagnostic."
        ),
        "future_hooks": t02.get("future_hooks") or [
            "FlyWire offline subgraph export",
            "Brian2 LIF multi-arm parity",
        ],
    }


def artifact_sha256(payload: dict[str, Any]) -> str:
    """Stable SHA-256 over canonical JSON (excludes sha field)."""
    body = {k: v for k, v in payload.items() if k != "artifact_sha256"}
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def render_t_brain_02_markdown(payload: dict[str, Any]) -> str:
    """Render markdown artifact for T-BRAIN-02."""
    arms = payload.get("arms") or {}
    corr = payload.get("omega_behavior_correlation") or {}
    decor = payload.get("f_omega_decor") or {}

    lines = [
        f"# M-T-BRAIN-02 OMEGA vs Behavior — {payload.get('date', '')}",
        "",
        f"**Cell:** {payload.get('cell', 'D2×L2')} · **Tier:** {payload.get('tier', 'C')} · "
        f"**Harness:** {payload.get('harness_id', 'T-BRAIN-02')}",
        f"**Seed:** {payload.get('seed')} · **Branch:** `{payload.get('branch')}`",
        f"**SHA-256:** `{payload.get('artifact_sha256', '')}`",
        "",
        "## Arms (OMEGA_t vs behavior)",
        "",
        "| Arm | OMEGA_t | Kuramoto R | activity_rate | burstiness | pop_sync | regime |",
        "|-----|---------|------------|---------------|------------|----------|--------|",
    ]
    for key, arm in arms.items():
        beh = arm.get("behavior") or {}
        lines.append(
            f"| `{key}` | `{arm.get('omega_t')}` | `{arm.get('kuramoto_r')}` | "
            f"`{beh.get('activity_rate_per_node_ms')}` | `{beh.get('burstiness_cv')}` | "
            f"`{beh.get('population_sync')}` | `{beh.get('regime_label')}` |"
        )

    lines.extend([
        "",
        "## Correlation diagnostics",
        "",
        f"- omega_span: `{corr.get('omega_span')}` · behavior_span: `{corr.get('behavior_span')}`",
        f"- r(OMEGA_t, activity_rate): `{corr.get('r_omega_activity')}`",
        f"- r(Kuramoto R, population_sync): `{corr.get('r_kuramoto_sync')}`",
        f"- omega_tracks_behavior: `{corr.get('omega_tracks_behavior')}`",
        f"- diagnostic_pass: `{payload.get('diagnostic_pass')}`",
        f"- F-OMEGA-DECOR (phase_scramble): `{decor.get('status')}`",
        "",
        "## Invariants",
        "",
        "- `e_endo_support=none` (no D1 bleed)",
        "- `claim_allowed=false`",
        "- `c_ladder_raise_allowed=false`",
        "- `agi_star_claim=false`",
        "- Kuramoto R ≠ E_endo (F-KURAMOTO-AS-E)",
        "- OMEGA vs behavior is observational diagnostic only; no genesis linkage claimed",
    ])
    return "\n".join(lines)

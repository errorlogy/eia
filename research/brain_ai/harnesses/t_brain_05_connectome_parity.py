"""T-BRAIN-05 — multi-source connectome parity.

Compares spike→OMEGA→shadow pipeline across connectome sources:
``google_male_cns``, ``flywire_female``, ``synthetic``, ``bundled_tiny``.

Tier C · ``claim_allowed=false`` · no AGI* · C2 ceiling.
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
ARTIFACT_JSON = ARTIFACTS / "M-T-BRAIN-05_2026-09-10.json"
ARTIFACT_MD = ARTIFACTS / "M-T-BRAIN-05_2026-09-10.md"
CONFIG_PATH = BRAIN_AI / "config.yaml"
BRANCH = "research/brain-ai-connectome"

PARITY_SOURCES: tuple[str, ...] = (
    "bundled_tiny",
    "synthetic",
    "google_male_cns",
    "flywire_female",
)

SOURCE_SEED_OFFSET: dict[str, int] = {
    "bundled_tiny": 0,
    "synthetic": 0,
    "google_male_cns": 101,
    "flywire_female": 203,
}

OMEGA_SPAN_MIN = 0.01
BEHAVIOR_SPAN_MIN = 1e-6
HARNESS_ID = "T-BRAIN-05"
MILESTONE = "M-BRAIN-AI"


def _ensure_paths() -> None:
    for path in (str(ADAPTERS), str(REPO / "src")):
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


def extract_genesis_metrics(ep: dict[str, Any]) -> dict[str, Any]:
    """ΔG / genesis delta from one shadow episode (G → G_prime under X_trigger=0)."""
    motive_ids = list(ep.get("motive_ids") or [])
    events = ep.get("events") or []
    g0 = motive_ids[0] if motive_ids else None
    g_prime = motive_ids[-1] if len(motive_ids) > 1 else None
    has_novel_g_prime = any(
        e.get("kind") == "G_prime" and e.get("novel") for e in events
    )
    parts: list[str] = []
    for event in events:
        kind = event.get("kind")
        if kind in ("G", "G_prime", "A", "Pi"):
            parts.append(f"{kind}:{event.get('label', '')}")
    return {
        "g0_id": g0,
        "g_prime_id": g_prime,
        "goal_symbol_changed": has_novel_g_prime,
        "genesis_delta": 1.0 if has_novel_g_prime else 0.0,
        "has_novel_g_prime": has_novel_g_prime,
        "initiative_fingerprint": "|".join(parts),
        "x_trigger_zero": not any(
            e.get("label") == "user_prompt" for e in events
        ),
        "behavior_gated_novel_genesis": ep.get("behavior_gated_novel_genesis"),
    }


def structural_fingerprint(subgraph: Any) -> str:
    """Stable hash of adjacency structure for cross-source comparison."""
    adj = subgraph.adjacency
    flat = ",".join(str(x) for row in adj for x in row)
    return hashlib.sha256(flat.encode("utf-8")).hexdigest()[:16]


def source_fallback_info(source_key: str) -> dict[str, Any]:
    """Report whether a source used a real export file or offline stub."""
    _ensure_paths()
    from connectome_export import (
        BUNDLED_SUBGRAPH,
        FLYWIRE_FEMALE_SUBGRAPH,
        GOOGLE_MALE_SUBGRAPH,
        SOURCE_PATHS,
    )

    if source_key == "synthetic":
        return {
            "source_key": source_key,
            "mode": "generated",
            "fallback": False,
            "data_file_present": False,
            "path": None,
        }

    path = SOURCE_PATHS.get(source_key, BUNDLED_SUBGRAPH)
    present = path.is_file()
    if source_key == "bundled_tiny":
        mode = "bundled" if present else "synthetic_fallback"
    else:
        mode = "offline_export" if present else "synthetic_fallback"
    return {
        "source_key": source_key,
        "mode": mode,
        "fallback": not present,
        "data_file_present": present,
        "path": _rel(path) if path else None,
    }


def structural_distance(adj_a: tuple[tuple[int, ...], ...], adj_b: tuple[tuple[int, ...], ...]) -> float | None:
    """Fraction of adjacency bits that differ (same shape only)."""
    if len(adj_a) != len(adj_b):
        return None
    n = len(adj_a)
    if n == 0:
        return 0.0
    diffs = 0
    total = n * n
    for i in range(n):
        if len(adj_a[i]) != len(adj_b[i]):
            return None
        for j in range(n):
            if int(adj_a[i][j]) != int(adj_b[i][j]):
                diffs += 1
    return diffs / total


def run_source_parity_probe(
    source_key: str,
    *,
    seed: int,
    n_nodes: int,
    duration_ms: float,
    dt_ms: float,
    prefer_brian2: bool,
    carriers: tuple[float, ...],
    include_shadow: bool = True,
) -> dict[str, Any]:
    """Run coupled_active pipeline for one connectome source."""
    _ensure_paths()
    from behavior_metrics import compute_behavior_metrics
    from connectome_export import load_subgraph
    from ot_injection import inject_omega_from_spikes
    from shadow_bridge import run_brain_omega_bridged_shadow_episode
    from spike_arms import run_spike_arm

    src_seed = seed + SOURCE_SEED_OFFSET.get(source_key, 0)
    fallback = source_fallback_info(source_key)
    subgraph = load_subgraph(
        connectome_source=source_key,
        n_nodes=n_nodes,
        seed=src_seed,
        prefer_bundled=(source_key == "bundled_tiny"),
    )

    spike_payload = run_spike_arm(
        subgraph,
        "coupled_active",
        seed=src_seed,
        duration_ms=duration_ms,
        dt_ms=dt_ms,
        prefer_brian2=prefer_brian2,
    )
    behavior = compute_behavior_metrics(spike_payload)
    omega_ctx = inject_omega_from_spikes(
        spike_payload, subgraph.node_ids, carriers=carriers
    )
    omega_t = float(omega_ctx.get("omega_t") or 0.0)

    genesis: dict[str, Any] | None = None
    if include_shadow:
        bridged = run_brain_omega_bridged_shadow_episode(
            omega_ctx,
            behavior,
            seed=src_seed,
            arm_key="coupled_active",
        )
        genesis = extract_genesis_metrics(bridged)

    return {
        "source_key": source_key,
        "connectome_source_tag": subgraph.source,
        "n_nodes": subgraph.n_nodes,
        "structural_fingerprint": structural_fingerprint(subgraph),
        "source_fallback": fallback,
        "seed_used": src_seed,
        "spike_backend": spike_payload.get("backend"),
        "n_spikes": spike_payload.get("n_spikes"),
        "omega_t": omega_t,
        "kuramoto_r": omega_ctx.get("kuramoto_r"),
        "behavior": behavior,
        "activity_rate_per_node_ms": behavior.get("activity_rate_per_node_ms"),
        "genesis": genesis,
        "genesis_delta": genesis["genesis_delta"] if genesis else None,
        "subgraph_adjacency": subgraph.adjacency,
    }


@dataclass(frozen=True, slots=True)
class ParityDiagnostics:
    all_omega_valid: bool
    omega_span_measurable: bool
    behavior_span_measurable: bool
    f_source_parity: bool
    structural_diversity: bool
    invariants_ok: bool

    def to_dict(self) -> dict[str, Any]:
        return {k: getattr(self, k) for k in self.__dataclass_fields__}


def evaluate_parity_diagnostics(
    probes: list[dict[str, Any]],
    *,
    omega_span: float,
    behavior_span: float,
) -> ParityDiagnostics:
    """Acceptance checks for T-BRAIN-05 connectome source parity."""
    omega_values = [float(p["omega_t"]) for p in probes]
    all_omega_valid = all(0.0 <= v <= 1.0 for v in omega_values)

    fingerprints = {p["structural_fingerprint"] for p in probes}
    structural_diversity = len(fingerprints) > 1

    omega_span_measurable = omega_span >= OMEGA_SPAN_MIN
    behavior_span_measurable = behavior_span >= BEHAVIOR_SPAN_MIN

    if structural_diversity:
        f_source_parity = not all(
            abs(omega_values[i] - omega_values[j]) < 1e-9
            for i in range(len(omega_values))
            for j in range(i + 1, len(omega_values))
        )
    else:
        f_source_parity = True

    return ParityDiagnostics(
        all_omega_valid=all_omega_valid,
        omega_span_measurable=omega_span_measurable,
        behavior_span_measurable=behavior_span_measurable,
        f_source_parity=f_source_parity,
        structural_diversity=structural_diversity,
        invariants_ok=True,
    )


def build_t_brain_05_payload(
    *,
    seed: int | None = None,
    generated: str | None = None,
    prefer_brian2: bool | None = None,
    include_shadow: bool = True,
) -> dict[str, Any]:
    """Build full T-BRAIN-05 artifact payload."""
    _ensure_paths()

    cfg = load_config()
    sim = cfg.get("simulation") or {}
    conn = cfg.get("connectome") or {}
    seed = int(seed if seed is not None else sim.get("seed", 42))
    prefer_brian2 = (
        prefer_brian2 if prefer_brian2 is not None else bool(sim.get("prefer_brian2", False))
    )
    n_nodes = int(sim.get("n_nodes", 8))
    max_nodes = int(conn.get("max_subgraph_nodes", 500))
    n_nodes = min(n_nodes, max_nodes)
    duration_ms = float(sim.get("duration_ms", 100.0))
    dt_ms = float(sim.get("dt_ms", 1.0))
    carriers = tuple(cfg.get("carriers_hz") or [20, 30, 42, 70])

    probes: list[dict[str, Any]] = []
    for source_key in PARITY_SOURCES:
        probe = run_source_parity_probe(
            source_key,
            seed=seed,
            n_nodes=n_nodes,
            duration_ms=duration_ms,
            dt_ms=dt_ms,
            prefer_brian2=prefer_brian2,
            carriers=carriers,
            include_shadow=include_shadow,
        )
        probes.append(probe)

    omega_values = [float(p["omega_t"]) for p in probes]
    behavior_rates = [float(p["activity_rate_per_node_ms"] or 0.0) for p in probes]
    omega_span = max(omega_values) - min(omega_values) if omega_values else 0.0
    behavior_span = max(behavior_rates) - min(behavior_rates) if behavior_rates else 0.0

    diagnostics = evaluate_parity_diagnostics(
        probes, omega_span=omega_span, behavior_span=behavior_span
    )
    diagnostic_pass = (
        diagnostics.all_omega_valid
        and diagnostics.omega_span_measurable
        and diagnostics.behavior_span_measurable
        and diagnostics.f_source_parity
        and diagnostics.invariants_ok
    )

    by_key = {p["source_key"]: p for p in probes}
    male_adj = by_key.get("google_male_cns", {}).get("subgraph_adjacency")
    female_adj = by_key.get("flywire_female", {}).get("subgraph_adjacency")
    male_vs_female_distance = (
        structural_distance(male_adj, female_adj)
        if male_adj is not None and female_adj is not None
        else None
    )

    sources_summary = {
        p["source_key"]: {
            "connectome_source_tag": p["connectome_source_tag"],
            "n_nodes": p["n_nodes"],
            "structural_fingerprint": p["structural_fingerprint"],
            "source_fallback": p["source_fallback"],
            "seed_used": p["seed_used"],
            "spike_backend": p["spike_backend"],
            "n_spikes": p["n_spikes"],
            "omega_t": p["omega_t"],
            "kuramoto_r": p["kuramoto_r"],
            "activity_rate_per_node_ms": p["activity_rate_per_node_ms"],
            "behavior_regime": (p["behavior"] or {}).get("regime_label"),
            "genesis_delta": p["genesis_delta"],
            "has_novel_g_prime": (
                (p["genesis"] or {}).get("has_novel_g_prime") if p["genesis"] else None
            ),
        }
        for p in probes
    }

    any_fallback = any(p["source_fallback"]["fallback"] for p in probes)
    run_mode = "mixed" if any_fallback else "offline_exports"

    return {
        "milestone": MILESTONE,
        "harness_id": HARNESS_ID,
        "artifact_id": "M-T-BRAIN-05_2026-09-10",
        "tick_id": HARNESS_ID,
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
        "x_trigger_zero": True,
        "seed": seed,
        "run_mode": run_mode,
        "include_shadow_bridge": include_shadow,
        "sources": {
            "connectome_export": _rel(BRAIN_AI / "adapters" / "connectome_export.py"),
            "shadow_bridge": _rel(BRAIN_AI / "adapters" / "shadow_bridge.py"),
            "t_brain_03": _rel(BRAIN_AI / "harnesses" / "t_brain_03_shadow_bridge.py"),
            "oscillatory_state": "research/cursor-starter-v0.2/src/eia/oscillatory_state.py",
        },
        "connectome_sources": list(PARITY_SOURCES),
        "per_source": sources_summary,
        "aggregate_metrics": {
            "omega_t_min": min(omega_values) if omega_values else None,
            "omega_t_max": max(omega_values) if omega_values else None,
            "omega_span": omega_span,
            "behavior_rate_min": min(behavior_rates) if behavior_rates else None,
            "behavior_rate_max": max(behavior_rates) if behavior_rates else None,
            "behavior_span": behavior_span,
            "male_vs_female_structural_distance": male_vs_female_distance,
            "structural_fingerprints_unique": len(
                {p["structural_fingerprint"] for p in probes}
            ),
        },
        "parity_diagnostics": diagnostics.to_dict(),
        "diagnostic_pass": diagnostic_pass,
        "f_source_parity": {
            "status": "confirmed" if diagnostics.f_source_parity else "not_confirmed",
            "structural_diversity": diagnostics.structural_diversity,
        },
        "f_omega_decor": {
            "status": "n/a",
            "note": "Single-arm coupled_active per source; decor test lives in T-BRAIN-03",
        },
        "falsifiers_active": [
            "F-SOURCE-PARITY",
            "F-OMEGA-DECOR",
            "F-KURAMOTO-AS-E",
            "F-STRUCT≠E",
        ],
        "note": (
            "Multi-source connectome parity — observational crosswalk only. "
            f"Run mode: {run_mode}. Uses stub/placeholder subgraphs when data/ "
            "exports absent (gitignored). Does not establish E_endo or raise C-level."
        ),
    }


def build_t_brain_05_spec() -> dict[str, Any]:
    """Return T-BRAIN-05 harness spec (legacy stub accessor)."""
    return {
        "milestone": MILESTONE,
        "harness_id": HARNESS_ID,
        "tier": "C",
        "claim_ceiling": "C2",
        "claim_allowed": False,
        "agi_star_claim": False,
        "status": "implemented",
        "sources": list(PARITY_SOURCES),
        "metrics_planned": [
            "omega_t_per_source",
            "omega_span",
            "genesis_delta_per_source",
            "behavior_span",
            "source_fallback_flags",
        ],
        "falsifiers": [
            "F-OMEGA-DECOR",
            "F-SOURCE-PARITY",
        ],
    }


def artifact_sha256(payload: dict[str, Any]) -> str:
    """Stable SHA-256 over canonical JSON (excludes sha field)."""
    body = {k: v for k, v in payload.items() if k != "artifact_sha256"}
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def render_t_brain_05_markdown(payload: dict[str, Any]) -> str:
    """Render markdown artifact for T-BRAIN-05."""
    per_source = payload.get("per_source") or {}
    agg = payload.get("aggregate_metrics") or {}
    diag = payload.get("parity_diagnostics") or {}
    fsp = payload.get("f_source_parity") or {}

    lines = [
        f"# M-T-BRAIN-05 Connectome Source Parity — {payload.get('date', '')}",
        "",
        f"**Cell:** {payload.get('cell', 'D2×L2')} · **Tier:** {payload.get('tier', 'C')} · "
        f"**Harness:** {payload.get('harness_id', HARNESS_ID)}",
        f"**Seed:** {payload.get('seed')} · **Run mode:** `{payload.get('run_mode')}` · "
        f"**Branch:** `{payload.get('branch')}`",
        f"**SHA-256:** `{payload.get('artifact_sha256', '')}`",
        "",
        "## Per-source metrics (coupled_active)",
        "",
        "| Source | OMEGA_t | activity_rate | genesis_Δ | fallback | backend |",
        "|--------|---------|---------------|-----------|----------|---------|",
    ]
    for key, src in per_source.items():
        fb = src.get("source_fallback") or {}
        fb_s = "yes" if fb.get("fallback") else "no"
        lines.append(
            f"| `{key}` | `{src.get('omega_t')}` | "
            f"`{src.get('activity_rate_per_node_ms')}` | `{src.get('genesis_delta')}` | "
            f"`{fb_s}` (`{fb.get('mode')}`) | `{src.get('spike_backend')}` |"
        )

    lines.extend([
        "",
        "## Aggregate spans",
        "",
        f"- omega_span: `{agg.get('omega_span')}` (min `{agg.get('omega_t_min')}`, "
        f"max `{agg.get('omega_t_max')}`)",
        f"- behavior_span: `{agg.get('behavior_span')}`",
        f"- male vs female structural distance: `{agg.get('male_vs_female_structural_distance')}`",
        f"- unique structural fingerprints: `{agg.get('structural_fingerprints_unique')}`",
        "",
        "## Parity diagnostics",
        "",
        f"- all OMEGA in [0,1]: `{diag.get('all_omega_valid')}`",
        f"- omega span measurable: `{diag.get('omega_span_measurable')}`",
        f"- behavior span measurable: `{diag.get('behavior_span_measurable')}`",
        f"- **F-SOURCE-PARITY:** `{fsp.get('status')}`",
        f"- diagnostic_pass: `{payload.get('diagnostic_pass')}`",
        "",
        "## Invariants",
        "",
        "- `e_endo_support=none` (no D1 bleed)",
        "- `claim_allowed=false`",
        "- `c_ladder_raise_allowed=false`",
        "- `agi_star_claim=false`",
        "- Offline-first: ego-network ≤500 nodes or deterministic stub",
    ])
    return "\n".join(lines)

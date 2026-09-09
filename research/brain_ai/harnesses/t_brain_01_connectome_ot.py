"""T-BRAIN-01 — connectome subgraph → spike dynamics → OmegaWaveState / OMEGA_t.

MVP: synthetic or bundled tiny adjacency; Brian2 LIF when installed, else
deterministic synthetic spike trains. Tier C only; ``claim_allowed=false``;
no D1 ``e_endo_support`` bleed; no AGI* claims.
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

import yaml

BRAIN_AI = Path(__file__).resolve().parents[1]
REPO = BRAIN_AI.parents[1]
ADAPTERS = BRAIN_AI / "adapters"
ARTIFACTS = BRAIN_AI / "artifacts"
ARTIFACT_JSON = ARTIFACTS / "M-T-BRAIN-01_2026-09-09.json"
ARTIFACT_MD = ARTIFACTS / "M-T-BRAIN-01_2026-09-09.md"
CONFIG_PATH = BRAIN_AI / "config.yaml"
BRANCH = "research/brain-ai-connectome"


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


def build_t_brain_01_payload(
    *,
    seed: int | None = None,
    generated: str | None = None,
    prefer_brian2: bool | None = None,
) -> dict[str, Any]:
    """Build full T-BRAIN-01 artifact payload."""
    _ensure_paths()
    from brian2_lif_subgraph import brian2_available, run_spike_dynamics
    from connectome_export import load_subgraph
    from ot_injection import inject_omega_from_spikes

    cfg = load_config()
    sim = cfg.get("simulation") or {}
    seed = int(seed if seed is not None else sim.get("seed", 42))
    prefer_brian2 = (
        prefer_brian2 if prefer_brian2 is not None else bool(sim.get("prefer_brian2", True))
    )
    n_nodes = int(sim.get("n_nodes", 8))
    duration_ms = float(sim.get("duration_ms", 100.0))
    dt_ms = float(sim.get("dt_ms", 1.0))
    carriers = tuple(cfg.get("carriers_hz") or [20, 30, 42, 70])

    subgraph = load_subgraph(n_nodes=n_nodes, seed=seed, prefer_bundled=True)
    spike_payload = run_spike_dynamics(
        subgraph,
        seed=seed,
        duration_ms=duration_ms,
        dt_ms=dt_ms,
        prefer_brian2=prefer_brian2,
    )
    omega_ctx = inject_omega_from_spikes(
        spike_payload,
        subgraph.node_ids,
        carriers=carriers,
    )

    brian2_used = spike_payload.get("backend") == "brian2_lif"
    brian2_skipped = prefer_brian2 and not brian2_used and not brian2_available()

    return {
        "milestone": "M-BRAIN-AI",
        "harness_id": "T-BRAIN-01",
        "artifact_id": "M-T-BRAIN-01_2026-09-09",
        "tick_id": "T-BRAIN-01",
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
            "connectome_export": _rel(BRAIN_AI / "adapters" / "connectome_export.py"),
            "brian2_lif": _rel(BRAIN_AI / "adapters" / "brian2_lif_subgraph.py"),
            "ot_injection": _rel(BRAIN_AI / "adapters" / "ot_injection.py"),
            "oscillatory_state": "research/cursor-starter-v0.2/src/eia/oscillatory_state.py",
            "bundled_subgraph": _rel(BRAIN_AI / "data" / "tiny_subgraph.json"),
        },
        "connectome": subgraph.to_dict(),
        "spike_dynamics": {
            "backend": spike_payload.get("backend"),
            "brian2_available": brian2_available(),
            "brian2_used": brian2_used,
            "brian2_skipped": brian2_skipped,
            "duration_ms": duration_ms,
            "dt_ms": dt_ms,
            "n_spikes": spike_payload.get("n_spikes"),
        },
        "omega_crosswalk": omega_ctx,
        "omega_t": omega_ctx.get("omega_t"),
        "kuramoto_r": omega_ctx.get("kuramoto_r"),
        "falsifiers_active": [
            "F-KURAMOTO-AS-E",
            "F-OMEGA-DECOR",
            "F-SYNC",
            "F-STRUCT≠E",
        ],
        "note": (
            "Connectome subgraph spike phases → OmegaWaveState crosswalk (MVP). "
            "Does not establish E_endo, ATT-R closure, or raise C-level."
        ),
    }


def artifact_sha256(payload: dict[str, Any]) -> str:
    """Stable SHA-256 over canonical JSON (excludes sha field)."""
    body = {k: v for k, v in payload.items() if k != "artifact_sha256"}
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def render_t_brain_01_markdown(payload: dict[str, Any]) -> str:
    """Render markdown artifact for T-BRAIN-01."""
    conn = payload.get("connectome") or {}
    spike = payload.get("spike_dynamics") or {}
    omega = payload.get("omega_crosswalk") or {}
    ows = omega.get("omega_wave_state") or {}

    lines = [
        f"# M-T-BRAIN-01 Connectome→O_t — {payload.get('date', '')}",
        "",
        f"**Cell:** {payload.get('cell', 'D2×L2')} · **Tier:** {payload.get('tier', 'C')} · "
        f"**Harness:** {payload.get('harness_id', 'T-BRAIN-01')}",
        f"**Seed:** {payload.get('seed')} · **Branch:** `{payload.get('branch')}`",
        f"**SHA-256:** `{payload.get('artifact_sha256', '')}`",
        "",
        "## Connectome subgraph",
        "",
        f"- Source: `{conn.get('source')}` · nodes: `{conn.get('n_nodes')}`",
        "",
        "## Spike dynamics",
        "",
        f"- Backend: `{spike.get('backend')}`",
        f"- Brian2 available: `{spike.get('brian2_available')}` · used: `{spike.get('brian2_used')}` · "
        f"skipped: `{spike.get('brian2_skipped')}`",
        f"- Spikes: `{spike.get('n_spikes')}` · duration: `{spike.get('duration_ms')}` ms",
        "",
        "## OMEGA crosswalk",
        "",
        f"- OMEGA_t: `{payload.get('omega_t')}` · Kuramoto R: `{payload.get('kuramoto_r')}`",
        f"- phase_coherence: `{ows.get('phase_coherence')}` · synchrony: `{ows.get('synchrony')}` · "
        f"productive_tension: `{ows.get('productive_tension')}`",
        "",
        "## Invariants",
        "",
        "- `e_endo_support=none` (no D1 bleed)",
        "- `claim_allowed=false`",
        "- `c_ladder_raise_allowed=false`",
        "- `agi_star_claim=false`",
        "- Kuramoto R ≠ E_endo (F-KURAMOTO-AS-E)",
        "- Connectome→O_t is observational crosswalk only; no genesis linkage claimed",
    ]
    return "\n".join(lines)

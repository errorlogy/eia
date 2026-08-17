"""Deterministic trace re-execution and comparison."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from eia.audit import CausalTrace, TraceMetadata, TraceNodeKind

VOLATILE_PAYLOAD_KEYS = frozenset({"id", "timestamp", "trace_id", "loop_schedule"})

KEY_NODE_KINDS = (
    TraceNodeKind.INTENTION_GENESIS,
    TraceNodeKind.CONTACT_GOVERNOR,
    TraceNodeKind.EOI_SCORE,
    TraceNodeKind.AUTHENTIC_REASON,
)


class ReplayMetadataError(ValueError):
    """Raised when a trace lacks metadata required for re-execution."""


def get_code_version() -> str:
    """Re-export for backward compatibility."""
    from eia.version import get_code_version as _get_code_version

    return _get_code_version()


def _normalize_value(value: Any) -> Any:
    if isinstance(value, dict):
        return _normalize_payload(value)
    if isinstance(value, list):
        return [_normalize_value(item) for item in value]
    if isinstance(value, float):
        return round(value, 6)
    return value


def _normalize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for key, value in payload.items():
        if key in VOLATILE_PAYLOAD_KEYS:
            continue
        normalized[key] = _normalize_value(value)
    return normalized


def trace_fingerprint(trace: CausalTrace) -> str:
    """Content hash ignoring volatile IDs and timestamps."""
    parts: list[str] = []
    for node in trace.nodes:
        record = {
            "kind": node.kind.value,
            "payload": _normalize_payload(node.payload),
        }
        parts.append(json.dumps(record, sort_keys=True))
    digest = hashlib.sha256("\n".join(parts).encode()).hexdigest()
    return digest[:16]


def _latest_payload(trace: CausalTrace, kind: TraceNodeKind) -> dict[str, Any] | None:
    nodes = [n for n in trace.nodes if n.kind == kind]
    if not nodes:
        return None
    return nodes[-1].payload


def _extract_eoi(trace: CausalTrace) -> float | None:
    payload = _latest_payload(trace, TraceNodeKind.EOI_SCORE)
    if not payload:
        return None
    return float(payload.get("eoi", 0))


def _extract_auth(trace: CausalTrace) -> dict[str, Any] | None:
    payload = _latest_payload(trace, TraceNodeKind.AUTHENTIC_REASON)
    if not payload:
        return None
    return {
        "is_authentic": payload.get("is_authentic"),
        "initiative_class": payload.get("initiative_class"),
        "summary": payload.get("summary"),
    }


def _key_node_summary(trace: CausalTrace) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for kind in KEY_NODE_KINDS:
        payload = _latest_payload(trace, kind)
        if payload is not None:
            summary[kind.value] = _normalize_payload(payload)
    return summary


def require_metadata(trace: CausalTrace, *, trace_path: Path | None = None) -> TraceMetadata:
    """Extract replay metadata or raise a helpful error."""
    if trace.metadata is None:
        hint = (
            "This trace was created before replay metadata was stored. "
            "Re-run the scenario with a current EIA version:\n"
            "  eia run --scenario <scenario.yaml>\n"
            "Then replay with:\n"
            "  eia replay --trace <new_trace.jsonl> --re-execute"
        )
        if trace_path:
            hint = f"Trace: {trace_path}\n{hint}"
        raise ReplayMetadataError(hint)
    missing: list[str] = []
    if trace.metadata.seed is None:
        missing.append("seed")
    if not trace.metadata.scenario_path:
        missing.append("scenario_path")
    if missing:
        raise ReplayMetadataError(
            f"Trace metadata is incomplete (missing: {', '.join(missing)}). "
            "Re-run the scenario to regenerate a replayable trace."
        )
    return trace.metadata


@dataclass
class ReplayComparison:
    """Result of comparing an original trace with a re-executed run."""

    matched: bool
    fingerprint_match: bool
    original_fingerprint: str
    replay_fingerprint: str
    eoi_match: bool
    eoi_original: float | None
    eoi_replay: float | None
    auth_match: bool
    auth_original: dict[str, Any] | None
    auth_replay: dict[str, Any] | None
    key_node_diffs: list[str] = field(default_factory=list)
    summary: str = ""
    replay_trace_path: Path | None = None


def compare_traces(original: CausalTrace, replay: CausalTrace) -> ReplayComparison:
    """Compare original and re-executed traces."""
    orig_fp = trace_fingerprint(original)
    replay_fp = trace_fingerprint(replay)
    fingerprint_match = orig_fp == replay_fp

    eoi_original = _extract_eoi(original)
    eoi_replay = _extract_eoi(replay)
    eoi_match = eoi_original == eoi_replay

    auth_original = _extract_auth(original)
    auth_replay = _extract_auth(replay)
    auth_match = auth_original == auth_replay

    diffs: list[str] = []
    orig_keys = _key_node_summary(original)
    replay_keys = _key_node_summary(replay)
    for kind in KEY_NODE_KINDS:
        key = kind.value
        if orig_keys.get(key) != replay_keys.get(key):
            diffs.append(key)

    matched = fingerprint_match and eoi_match and auth_match and not diffs

    if matched:
        summary = (
            f"MATCH — fingerprint={orig_fp}, EOI={eoi_original:.3f}, "
            f"authentic={auth_original.get('is_authentic') if auth_original else '?'}"
        )
    else:
        parts = ["MISMATCH"]
        if not fingerprint_match:
            parts.append(f"fingerprint {orig_fp} != {replay_fp}")
        if not eoi_match:
            parts.append(f"EOI {eoi_original} != {eoi_replay}")
        if not auth_match:
            parts.append("authentic_reason verdict differs")
        if diffs:
            parts.append(f"key nodes differ: {', '.join(diffs)}")
        summary = " — ".join(parts)

    return ReplayComparison(
        matched=matched,
        fingerprint_match=fingerprint_match,
        original_fingerprint=orig_fp,
        replay_fingerprint=replay_fp,
        eoi_match=eoi_match,
        eoi_original=eoi_original,
        eoi_replay=eoi_replay,
        auth_match=auth_match,
        auth_original=auth_original,
        auth_replay=auth_replay,
        key_node_diffs=diffs,
        summary=summary,
    )


def re_execute_trace(
    trace_path: Path,
    *,
    traces_dir: Path | None = None,
) -> ReplayComparison:
    """Re-run simulator/pipeline from trace metadata and compare traces."""
    from eia.pipeline import run_scenario

    original = CausalTrace.load_jsonl(trace_path)
    metadata = require_metadata(original, trace_path=trace_path)

    scenario_path = Path(metadata.scenario_path)
    if not scenario_path.is_absolute():
        scenario_path = (trace_path.parent / scenario_path).resolve()
        if not scenario_path.exists():
            scenario_path = Path(metadata.scenario_path).resolve()
    if not scenario_path.exists():
        raise ReplayMetadataError(
            f"Scenario file not found: {metadata.scenario_path}\n"
            "Ensure the scenario path in trace metadata is valid."
        )

    out_dir = traces_dir or trace_path.parent / "replay"
    result = run_scenario(
        scenario_path,
        traces_dir=out_dir,
        seed=metadata.seed,
    )
    replay_trace = result["loop"].trace
    comparison = compare_traces(original, replay_trace)
    comparison.replay_trace_path = result["trace_path"]
    return comparison

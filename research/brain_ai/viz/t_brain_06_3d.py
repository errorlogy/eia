"""3D matplotlib visualizations for T-BRAIN-06 integrated EIA modeling results.

Tier C · C2 ceiling · claim_allowed=false · observational framing only.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from matplotlib.colors import Normalize
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 — registers 3D projection

BRAIN_AI = Path(__file__).resolve().parents[1]
REPO = BRAIN_AI.parents[1]
HARNESS_DIR = BRAIN_AI / "harnesses"
ARTIFACTS = BRAIN_AI / "artifacts"
FIGURES = BRAIN_AI / "figures"
DATA = BRAIN_AI / "data"
TINY_SUBGRAPH = DATA / "tiny_subgraph.json"

TITLE = "T-BRAIN-06 EIA Integrated Modeling (C2, claim_allowed=false)"
CAPTION = (
    "Observational connectome-grounded EIA diagnostics — Drosophila CNS substrate; "
    "not mammalian neocortex. No E_endo or AGI* claims."
)

SOURCES: tuple[str, ...] = (
    "bundled_tiny",
    "synthetic",
    "google_male_cns",
    "flywire_female",
)
ARMS: tuple[str, ...] = ("coupled_active", "passive_quiescent")
ARM_LABELS = {
    "coupled_active": "Endogenous (coupled_active)",
    "passive_quiescent": "Passive (passive_quiescent)",
}
SOURCE_LABELS = {
    "bundled_tiny": "bundled_tiny",
    "synthetic": "synthetic",
    "google_male_cns": "google_male_cns",
    "flywire_female": "flywire_female",
}
ARM_COLORS = {
    "coupled_active": "#1f77b4",
    "passive_quiescent": "#ff7f0e",
}
METRICS = ("omega_t", "genesis_delta", "eoi_mean")
METRIC_LABELS = {
    "omega_t": "OMEGA_t",
    "genesis_delta": "genesis_Δ",
    "eoi_mean": "EOI mean",
}

# Embedded fallback from M-T-BRAIN-06_2026-09-11 (seed=42, 2 ticks).
_FALLBACK_PAYLOAD: dict[str, Any] = {
    "harness_id": "T-BRAIN-06",
    "claim_allowed": False,
    "claim_ceiling": "C2",
    "session_ticks": 2,
    "connectome_sources": list(SOURCES),
    "arms_compared": list(ARMS),
    "aggregate_metrics": {
        "omega_span": 0.22617926251815296,
        "mean_endogenous_passive_separation": 2.75,
    },
    "diagnostic_pass": True,
    "per_source": {
        "bundled_tiny": {
            "omega_t_endogenous": 0.39578618733267606,
            "omega_t_passive": 0.24341086111215554,
            "separation": {"separation_score": 2.75},
            "arms": {
                "coupled_active": {
                    "cumulative_genesis_delta": 2.0,
                    "cumulative_eoi": {"eoi_mean": 0.9166666666666666},
                    "ticks": [
                        {"session_tick": 0, "omega_t": 0.39578618733267606, "genesis_delta": 1.0, "eoi_mean": 1.0, "drive_norm": 0.36096404744368116},
                        {"session_tick": 1, "omega_t": None, "genesis_delta": 1.0, "eoi_mean": 0.875, "drive_norm": 0.8648498848049229},
                    ],
                },
                "passive_quiescent": {
                    "cumulative_genesis_delta": 0.0,
                    "cumulative_eoi": {"eoi_mean": 0.0},
                    "ticks": [
                        {"session_tick": 0, "omega_t": 0.24341086111215554, "genesis_delta": 0.0, "eoi_mean": 0.0, "drive_norm": 0.0},
                        {"session_tick": 1, "omega_t": None, "genesis_delta": 0.0, "eoi_mean": 0.0, "drive_norm": 0.0},
                    ],
                },
            },
        },
        "synthetic": {
            "omega_t_endogenous": 0.4064256496884792,
            "omega_t_passive": 0.24341086111215554,
            "separation": {"separation_score": 2.75},
            "arms": {
                "coupled_active": {
                    "cumulative_genesis_delta": 2.0,
                    "cumulative_eoi": {"eoi_mean": 0.9166666666666666},
                    "ticks": [
                        {"session_tick": 0, "omega_t": 0.4064256496884792, "genesis_delta": 1.0, "eoi_mean": 1.0, "drive_norm": 0.36096404744368116},
                        {"session_tick": 1, "omega_t": None, "genesis_delta": 1.0, "eoi_mean": 0.875, "drive_norm": 0.8648498848049229},
                    ],
                },
                "passive_quiescent": {
                    "cumulative_genesis_delta": 0.0,
                    "cumulative_eoi": {"eoi_mean": 0.0},
                    "ticks": [
                        {"session_tick": 0, "omega_t": 0.24341086111215554, "genesis_delta": 0.0, "eoi_mean": 0.0, "drive_norm": 0.0},
                        {"session_tick": 1, "omega_t": None, "genesis_delta": 0.0, "eoi_mean": 0.0, "drive_norm": 0.0},
                    ],
                },
            },
        },
        "google_male_cns": {
            "omega_t_endogenous": 0.621965449850829,
            "omega_t_passive": 0.3551727305097323,
            "separation": {"separation_score": 2.75},
            "arms": {
                "coupled_active": {
                    "cumulative_genesis_delta": 2.0,
                    "cumulative_eoi": {"eoi_mean": 0.9166666666666666},
                    "ticks": [
                        {"session_tick": 0, "omega_t": 0.621965449850829, "genesis_delta": 1.0, "eoi_mean": 1.0, "drive_norm": 0.36096404744368116},
                        {"session_tick": 1, "omega_t": None, "genesis_delta": 1.0, "eoi_mean": 0.875, "drive_norm": 0.8648498848049229},
                    ],
                },
                "passive_quiescent": {
                    "cumulative_genesis_delta": 0.0,
                    "cumulative_eoi": {"eoi_mean": 0.0},
                    "ticks": [
                        {"session_tick": 0, "omega_t": 0.3551727305097323, "genesis_delta": 0.0, "eoi_mean": 0.0, "drive_norm": 0.0},
                        {"session_tick": 1, "omega_t": None, "genesis_delta": 0.0, "eoi_mean": 0.0, "drive_norm": 0.0},
                    ],
                },
            },
        },
        "flywire_female": {
            "omega_t_endogenous": 0.48410375738392103,
            "omega_t_passive": 0.5850000000000001,
            "separation": {"separation_score": 2.75},
            "arms": {
                "coupled_active": {
                    "cumulative_genesis_delta": 2.0,
                    "cumulative_eoi": {"eoi_mean": 0.9166666666666666},
                    "ticks": [
                        {"session_tick": 0, "omega_t": 0.48410375738392103, "genesis_delta": 1.0, "eoi_mean": 1.0, "drive_norm": 0.36096404744368116},
                        {"session_tick": 1, "omega_t": None, "genesis_delta": 1.0, "eoi_mean": 0.875, "drive_norm": 0.8648498848049229},
                    ],
                },
                "passive_quiescent": {
                    "cumulative_genesis_delta": 0.0,
                    "cumulative_eoi": {"eoi_mean": 0.0},
                    "ticks": [
                        {"session_tick": 0, "omega_t": 0.5850000000000001, "genesis_delta": 0.0, "eoi_mean": 0.0, "drive_norm": 0.0},
                        {"session_tick": 1, "omega_t": None, "genesis_delta": 0.0, "eoi_mean": 0.0, "drive_norm": 0.0},
                    ],
                },
            },
        },
    },
}


def _setup_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.size": 10,
            "axes.labelsize": 11,
            "axes.titlesize": 11,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "figure.titlesize": 12,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
        }
    )


def _artifact_candidates() -> list[Path]:
    paths = sorted(ARTIFACTS.glob("M-T-BRAIN-06_*.json"), reverse=True)
    if not paths:
        paths = [ARTIFACTS / f"M-T-BRAIN-06_{date.today().isoformat()}.json"]
    return paths


def load_payload(artifact_path: Path | None = None, run_harness: bool = True) -> dict[str, Any]:
    """Load T-BRAIN-06 JSON artifact, optionally regenerating via harness."""
    candidates = [artifact_path] if artifact_path else _artifact_candidates()
    for path in candidates:
        if path and path.is_file():
            return json.loads(path.read_text(encoding="utf-8"))

    if run_harness:
        if str(HARNESS_DIR) not in sys.path:
            sys.path.insert(0, str(HARNESS_DIR))
        from t_brain_06_eia_integrated import build_t_brain_06_payload

        return build_t_brain_06_payload(seed=42, generated=date.today().isoformat())

    return _FALLBACK_PAYLOAD


def _metric_value(payload: dict[str, Any], source: str, arm: str, metric: str, tick: int = 0) -> float:
    arm_data = payload["per_source"][source]["arms"][arm]
    if metric == "omega_t":
        tick_data = arm_data["ticks"][tick]
        val = tick_data.get("omega_t")
        if val is None:
            return float(arm_data.get("omega_t_tick0") or 0.0)
        return float(val)
    if metric == "genesis_delta":
        if tick == 0:
            return float(arm_data["ticks"][tick]["genesis_delta"])
        return float(arm_data["cumulative_genesis_delta"])
    if metric == "eoi_mean":
        if tick == 0:
            return float(arm_data["ticks"][tick]["eoi_mean"])
        return float(arm_data["cumulative_eoi"]["eoi_mean"])
    raise KeyError(metric)


def _save_figure(fig: plt.Figure, stem: str) -> tuple[Path, Path]:
    FIGURES.mkdir(parents=True, exist_ok=True)
    pdf = FIGURES / f"{stem}.pdf"
    png = FIGURES / f"{stem}.png"
    fig.savefig(pdf, format="pdf")
    fig.savefig(png, format="png", dpi=300)
    plt.close(fig)
    return pdf, png


def spectral_layout_3d(adj: np.ndarray) -> np.ndarray:
    """3D spectral embedding from adjacency (offline, no networkx)."""
    n = adj.shape[0]
    if n < 4:
        theta = np.linspace(0, 2 * np.pi, n, endpoint=False)
        return np.column_stack([np.cos(theta), np.sin(theta), np.zeros(n)])

    deg = adj.sum(axis=1)
    lap = np.diag(deg) - adj
    _, eigvecs = np.linalg.eigh(lap)
    coords = eigvecs[:, 1:4]
    scale = np.abs(coords).max() or 1.0
    return coords / scale


def _load_subgraph() -> tuple[np.ndarray, list[str]]:
    if TINY_SUBGRAPH.is_file():
        data = json.loads(TINY_SUBGRAPH.read_text(encoding="utf-8"))
        adj = np.array(data["adjacency"], dtype=float)
        ids = list(data.get("node_ids", [f"n{i}" for i in range(adj.shape[0])]))
        return adj, ids
    n = 8
    adj = np.zeros((n, n))
    for i in range(n):
        adj[i, (i + 1) % n] = 1.0
        adj[(i + 1) % n, i] = 1.0
    return adj, [f"n{i}" for i in range(n)]


def _node_activity_proxy(adj: np.ndarray, omega_t: float, drive_norm: float) -> np.ndarray:
    deg = adj.sum(axis=1)
    cent = deg / (deg.max() or 1.0)
    return cent * omega_t * (0.5 + 0.5 * drive_norm)


def plot_eia_3d_cube(payload: dict[str, Any]) -> tuple[Path, Path]:
    """Source × tick × OMEGA_t scatter colored by arm, with metric facets."""
    _setup_style()
    session_ticks = int(payload.get("session_ticks", 2))
    omega_span = payload.get("aggregate_metrics", {}).get("omega_span", 0.0)

    fig = plt.figure(figsize=(11, 8))
    fig.suptitle(TITLE, fontsize=12, y=0.98)
    fig.text(0.5, 0.94, CAPTION, ha="center", fontsize=8, color="#444444")

    ax_main = fig.add_subplot(2, 2, 1, projection="3d")
    ax_metric = fig.add_subplot(2, 2, 2, projection="3d")
    ax_sep = fig.add_subplot(2, 2, 3, projection="3d")
    ax_legend = fig.add_subplot(2, 2, 4)
    ax_legend.axis("off")

    source_x = {s: i for i, s in enumerate(SOURCES)}

    for arm in ARMS:
        xs, ys, zs = [], [], []
        for source in SOURCES:
            for tick in range(session_ticks):
                omega = _metric_value(payload, source, arm, "omega_t", tick)
                if tick == 1 and payload["per_source"][source]["arms"][arm]["ticks"][1].get("omega_t") is None:
                    continue
                xs.append(source_x[source])
                ys.append(tick)
                zs.append(omega)
        ax_main.scatter(
            xs, ys, zs,
            c=ARM_COLORS[arm],
            label=ARM_LABELS[arm],
            s=70,
            depthshade=True,
            edgecolors="k",
            linewidths=0.3,
        )

    ax_main.set_xlabel("Connectome source")
    ax_main.set_ylabel("Session tick")
    ax_main.set_zlabel("OMEGA_t")
    ax_main.set_title("Source × Tick × OMEGA_t")
    ax_main.set_xticks(list(source_x.values()))
    ax_main.set_xticklabels([SOURCE_LABELS[s] for s in SOURCES], rotation=20, ha="right")
    ax_main.set_yticks(range(session_ticks))

    metric_idx = {m: i for i, m in enumerate(METRICS)}
    bar_w = 0.18
    for si, source in enumerate(SOURCES):
        for ai, arm in enumerate(ARMS):
            for mi, metric in enumerate(METRICS):
                val = _metric_value(payload, source, arm, metric, tick=0)
                x = si + (ai - 0.5) * bar_w
                y = mi
                ax_metric.bar3d(x, y, 0, bar_w * 0.9, 0.7, val, color=ARM_COLORS[arm], alpha=0.85, shade=True)

    ax_metric.set_xlabel("Connectome source")
    ax_metric.set_ylabel("Metric")
    ax_metric.set_zlabel("Value (tick 0)")
    ax_metric.set_title("Source × Metric × Value (by arm)")
    ax_metric.set_xticks(range(len(SOURCES)))
    ax_metric.set_xticklabels([SOURCE_LABELS[s] for s in SOURCES], rotation=20, ha="right")
    ax_metric.set_yticks(range(len(METRICS)))
    ax_metric.set_yticklabels([METRIC_LABELS[m] for m in METRICS])

    sep_scores = [payload["per_source"][s]["separation"]["separation_score"] for s in SOURCES]
    endo_omega = [payload["per_source"][s]["omega_t_endogenous"] for s in SOURCES]
    passive_omega = [payload["per_source"][s]["omega_t_passive"] for s in SOURCES]
    ax_sep.bar3d(
        np.arange(len(SOURCES)), np.zeros(len(SOURCES)), np.zeros(len(SOURCES)),
        0.35, 0.35, endo_omega,
        color=ARM_COLORS["coupled_active"], alpha=0.9, label=ARM_LABELS["coupled_active"],
    )
    ax_sep.bar3d(
        np.arange(len(SOURCES)) + 0.45, np.zeros(len(SOURCES)), np.zeros(len(SOURCES)),
        0.35, 0.35, passive_omega,
        color=ARM_COLORS["passive_quiescent"], alpha=0.9, label=ARM_LABELS["passive_quiescent"],
    )
    for i, (e, p, sep) in enumerate(zip(endo_omega, passive_omega, sep_scores)):
        ax_sep.text(i + 0.2, 0.5, max(e, p) + 0.03, f"sep={sep:.2f}", fontsize=7, ha="center")

    ax_sep.set_xlabel("Connectome source")
    ax_sep.set_ylabel("")
    ax_sep.set_zlabel("OMEGA_t (tick 0)")
    ax_sep.set_title(f"Endogenous vs passive OMEGA_t (ω span={omega_span:.3f})")
    ax_sep.set_xticks(np.arange(len(SOURCES)) + 0.4)
    ax_sep.set_xticklabels([SOURCE_LABELS[s] for s in SOURCES], rotation=20, ha="right")
    ax_sep.set_yticks([])

    handles = [
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=ARM_COLORS[a], markersize=9, label=ARM_LABELS[a])
        for a in ARMS
    ]
    ax_legend.legend(handles=handles, loc="center", title="Arms", frameon=True)
    ax_legend.text(
        0.5, 0.15,
        f"diagnostic_pass={payload.get('diagnostic_pass')}\n"
        f"mean separation={payload.get('aggregate_metrics', {}).get('mean_endogenous_passive_separation', 'n/a')}",
        ha="center", va="top", fontsize=9, transform=ax_legend.transAxes,
    )

    fig.subplots_adjust(left=0.04, right=0.98, top=0.90, bottom=0.06, wspace=0.25, hspace=0.30)
    return _save_figure(fig, "t_brain_06_eia_3d_cube")


def plot_connectome_3d(payload: dict[str, Any]) -> tuple[Path, Path]:
    """3D connectome subgraph — spectral layout, nodes colored by activity proxy."""
    _setup_style()
    adj, node_ids = _load_subgraph()
    base_pos = spectral_layout_3d(adj)

    fig = plt.figure(figsize=(12, 9))
    fig.suptitle(TITLE, fontsize=12)
    fig.text(0.5, 0.95, CAPTION, ha="center", fontsize=8, color="#444444")

    for idx, source in enumerate(SOURCES):
        ax = fig.add_subplot(2, 2, idx + 1, projection="3d")
        arm = "coupled_active"
        tick0 = payload["per_source"][source]["arms"][arm]["ticks"][0]
        omega = float(tick0["omega_t"] or payload["per_source"][source]["omega_t_endogenous"])
        drive = float(tick0["drive_norm"])
        activity = _node_activity_proxy(adj, omega, drive)

        offset = np.array([idx * 3.5, 0.0, 0.0])
        pos = base_pos + offset

        norm = Normalize(vmin=activity.min(), vmax=activity.max() or 1.0)
        colors = cm.viridis(norm(activity))

        for i in range(adj.shape[0]):
            for j in range(i + 1, adj.shape[0]):
                if adj[i, j] > 0:
                    ax.plot(
                        [pos[i, 0], pos[j, 0]],
                        [pos[i, 1], pos[j, 1]],
                        [pos[i, 2], pos[j, 2]],
                        color="#aaaaaa", linewidth=0.6, alpha=0.5,
                    )

        ax.scatter(
            pos[:, 0], pos[:, 1], pos[:, 2],
            c=colors, s=80 + 120 * activity, depthshade=True, edgecolors="k", linewidths=0.3,
        )
        for i, nid in enumerate(node_ids):
            ax.text(pos[i, 0], pos[i, 1], pos[i, 2] + 0.08, nid, fontsize=6, ha="center")

        ax.set_title(f"{SOURCE_LABELS[source]}\nendo OMEGA_t={omega:.3f}, drive={drive:.2f}")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("z")
        ax.view_init(elev=22, azim=35 + idx * 15)

    fig.text(
        0.5, 0.02,
        "bundled_tiny topology · node color/size ∝ degree×OMEGA_t×drive (proxy; artifact has session-level drive)",
        ha="center", fontsize=8, color="#555555",
    )
    fig.subplots_adjust(top=0.90, bottom=0.08, wspace=0.15, hspace=0.25)
    return _save_figure(fig, "t_brain_06_connectome_3d")


def plot_metrics_3d(payload: dict[str, Any]) -> tuple[Path, Path]:
    """3D grouped bars: 4 sources × 2 arms × cumulative metrics."""
    _setup_style()
    metrics = ("omega_t", "genesis_delta", "eoi_mean")
    metric_labels = [METRIC_LABELS[m] for m in metrics]

    fig = plt.figure(figsize=(10, 7))
    fig.suptitle(TITLE, fontsize=12)
    fig.text(0.5, 0.94, CAPTION, ha="center", fontsize=8, color="#444444")
    ax = fig.add_subplot(111, projection="3d")

    dx, dy = 0.22, 0.55
    for si, source in enumerate(SOURCES):
        for ai, arm in enumerate(ARMS):
            for mi, metric in enumerate(metrics):
                if metric == "omega_t":
                    val = float(payload["per_source"][source]["arms"][arm]["ticks"][0]["omega_t"] or 0.0)
                elif metric == "genesis_delta":
                    val = float(payload["per_source"][source]["arms"][arm]["cumulative_genesis_delta"])
                else:
                    val = float(payload["per_source"][source]["arms"][arm]["cumulative_eoi"]["eoi_mean"])

                x = si + (ai - 0.5) * dx
                y = mi
                ax.bar3d(x, y, 0, dx * 0.9, dy * 0.85, val, color=ARM_COLORS[arm], alpha=0.88, shade=True)

    ax.set_xlabel("Connectome source")
    ax.set_ylabel("Metric")
    ax.set_zlabel("Cumulative / tick-0 value")
    ax.set_title("Sources × Arms × Metrics (2-tick session)")
    ax.set_xticks(range(len(SOURCES)))
    ax.set_xticklabels([SOURCE_LABELS[s] for s in SOURCES], rotation=15, ha="right")
    ax.set_yticks(range(len(metrics)))
    ax.set_yticklabels(metric_labels)

    handles = [
        plt.Line2D([0], [0], color=ARM_COLORS[a], lw=8, label=ARM_LABELS[a]) for a in ARMS
    ]
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.02, 0.98))

    fig.subplots_adjust(top=0.88, bottom=0.08)
    return _save_figure(fig, "t_brain_06_metrics_3d")


def generate_all(payload: dict[str, Any] | None = None) -> dict[str, tuple[Path, Path]]:
    """Generate all T-BRAIN-06 3D figures; return stem → (pdf, png) paths."""
    data = payload or load_payload()
    outputs: dict[str, tuple[Path, Path]] = {}
    outputs["t_brain_06_eia_3d_cube"] = plot_eia_3d_cube(data)
    outputs["t_brain_06_connectome_3d"] = plot_connectome_3d(data)
    outputs["t_brain_06_metrics_3d"] = plot_metrics_3d(data)
    return outputs


def main() -> int:
    outputs = generate_all()
    for stem, (pdf, png) in outputs.items():
        print(f"{stem}: {pdf} | {png}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

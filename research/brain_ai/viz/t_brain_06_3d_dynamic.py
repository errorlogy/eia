"""Time-evolving 3D matplotlib animations for T-BRAIN-06 integrated EIA results.

Tier C · C2 ceiling · claim_allowed=false · observational framing only.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.colors import Normalize
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 — registers 3D projection

from t_brain_06_3d import (
    ARM_COLORS,
    ARM_LABELS,
    ARMS,
    CAPTION,
    FIGURES,
    METRIC_LABELS,
    SOURCE_LABELS,
    SOURCES,
    TITLE,
    _load_subgraph,
    _node_activity_proxy,
    _setup_style,
    load_payload,
    spectral_layout_3d,
)

DEFAULT_FPS = 12
DEFAULT_FRAMES = 36
FAST_FRAMES = 6
FAST_FPS = 6


@dataclass(frozen=True)
class FrameState:
    """Interpolated EIA metrics at one animation frame."""

    tick_progress: float
    tick_label: str
    per_point: dict[tuple[str, str], dict[str, float]]


def _tick_series(payload: dict[str, Any], source: str, arm: str) -> list[dict[str, float]]:
    arm_data = payload["per_source"][source]["arms"][arm]
    series: list[dict[str, float]] = []
    for tick in arm_data["ticks"]:
        omega = tick.get("omega_t")
        if omega is None:
            omega = float(arm_data.get("omega_t_tick0") or 0.0)
        series.append(
            {
                "omega_t": float(omega),
                "genesis_delta": float(tick["genesis_delta"]),
                "eoi_mean": float(tick["eoi_mean"]),
                "drive_norm": float(tick.get("drive_norm", 0.0)),
            }
        )
    return series


def _lerp(a: float, b: float, alpha: float) -> float:
    return a + (b - a) * alpha


def _interpolate_series(
    series: list[dict[str, float]], progress: float
) -> tuple[dict[str, float], float]:
    """Map progress in [0, n_ticks-1] to interpolated metrics."""
    if len(series) <= 1:
        return series[0], 0.0

    progress = progress % (len(series) - 1)
    idx = int(np.floor(progress))
    alpha = progress - idx
    idx = min(idx, len(series) - 2)
    a, b = series[idx], series[idx + 1]
    return (
        {
            "omega_t": _lerp(a["omega_t"], b["omega_t"], alpha),
            "genesis_delta": _lerp(a["genesis_delta"], b["genesis_delta"], alpha),
            "eoi_mean": _lerp(a["eoi_mean"], b["eoi_mean"], alpha),
            "drive_norm": _lerp(a["drive_norm"], b["drive_norm"], alpha),
        },
        idx + alpha,
    )


def build_frame_states(payload: dict[str, Any], n_frames: int) -> list[FrameState]:
    session_ticks = int(payload.get("session_ticks", 2))
    states: list[FrameState] = []
    for fi in range(n_frames):
        progress = fi * (session_ticks - 1) / max(n_frames - 1, 1)
        per_point: dict[tuple[str, str], dict[str, float]] = {}
        max_tick = 0.0
        for source in SOURCES:
            for arm in ARMS:
                metrics, tick_pos = _interpolate_series(
                    _tick_series(payload, source, arm), progress
                )
                per_point[(source, arm)] = metrics
                max_tick = max(max_tick, tick_pos)
        states.append(
            FrameState(
                tick_progress=max_tick,
                tick_label=f"tick {max_tick:.2f}",
                per_point=per_point,
            )
        )
    return states


def _save_animation(
    anim: FuncAnimation,
    stem: str,
    *,
    fps: int,
    dpi: int = 90,
) -> dict[str, Path]:
    FIGURES.mkdir(parents=True, exist_ok=True)
    outputs: dict[str, Path] = {}
    gif_path = FIGURES / f"{stem}.gif"
    anim.save(gif_path, writer=PillowWriter(fps=fps), dpi=dpi)
    outputs["gif"] = gif_path

    if _ffmpeg_available():
        mp4_path = FIGURES / f"{stem}.mp4"
        try:
            anim.save(str(mp4_path), writer="ffmpeg", fps=fps, dpi=dpi)
            outputs["mp4"] = mp4_path
        except (RuntimeError, OSError, ValueError):
            pass
    return outputs


def _ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None


def animate_eia_3d_cube(
    payload: dict[str, Any],
    *,
    n_frames: int = DEFAULT_FRAMES,
    fps: int = DEFAULT_FPS,
    dpi: int = 90,
) -> dict[str, Path]:
    """Animated evidence cube: Source × Tick × OMEGA_t with arm-colored scatter."""
    _setup_style()
    states = build_frame_states(payload, n_frames)
    session_ticks = int(payload.get("session_ticks", 2))
    source_x = {s: i for i, s in enumerate(SOURCES)}

    fig = plt.figure(figsize=(9, 7))
    fig.suptitle(TITLE, fontsize=11, y=0.98)
    fig.text(0.5, 0.94, CAPTION, ha="center", fontsize=7, color="#444444")
    ax = fig.add_subplot(111, projection="3d")

    scatter_by_arm: dict[str, Any] = {}
    for arm in ARMS:
        scatter_by_arm[arm] = ax.scatter(
            [], [], [],
            c=ARM_COLORS[arm],
            label=ARM_LABELS[arm],
            s=70,
            depthshade=True,
            edgecolors="k",
            linewidths=0.3,
        )

    tick_line, = ax.plot([], [], [], color="#888888", linewidth=1.5, alpha=0.6)
    status = ax.text2D(0.02, 0.96, "", transform=ax.transAxes, fontsize=9)

    ax.set_xlabel("Connectome source")
    ax.set_ylabel("Session tick")
    ax.set_zlabel("OMEGA_t")
    ax.set_title("Source × Tick × OMEGA_t (time-evolving)")
    ax.set_xticks(list(source_x.values()))
    ax.set_xticklabels([SOURCE_LABELS[s] for s in SOURCES], rotation=20, ha="right")
    ax.set_yticks(range(session_ticks))
    ax.set_zlim(0.0, 0.75)
    ax.legend(loc="upper right", fontsize=7)

    def _update(frame_idx: int) -> tuple[Any, ...]:
        state = states[frame_idx]
        for arm in ARMS:
            xs, ys, zs = [], [], []
            for source in SOURCES:
                m = state.per_point[(source, arm)]
                xs.append(source_x[source])
                ys.append(state.tick_progress)
                zs.append(m["omega_t"])
            scatter_by_arm[arm]._offsets3d = (xs, ys, zs)

        ref_source = SOURCES[0]
        ref_arm = "coupled_active"
        ref_metrics = state.per_point[(ref_source, ref_arm)]
        tick_line.set_data(
            [source_x[ref_source], source_x[ref_source]],
            [0.0, state.tick_progress],
        )
        tick_line.set_3d_properties([ref_metrics["omega_t"], ref_metrics["omega_t"]])

        status.set_text(
            f"{state.tick_label} · genesis_Δ={ref_metrics['genesis_delta']:.2f} · "
            f"EOI={ref_metrics['eoi_mean']:.2f}"
        )
        ax.view_init(elev=22, azim=25 + frame_idx * 2.5)
        return (*scatter_by_arm.values(), tick_line, status)

    anim = FuncAnimation(fig, _update, frames=n_frames, interval=1000 / fps, blit=False)
    outputs = _save_animation(anim, "t_brain_06_eia_3d_dynamic", fps=fps, dpi=dpi)
    plt.close(fig)
    return outputs


def animate_connectome_3d(
    payload: dict[str, Any],
    *,
    n_frames: int = DEFAULT_FRAMES,
    fps: int = DEFAULT_FPS,
    dpi: int = 90,
) -> dict[str, Path]:
    """Animated connectome: node color/size from activity proxy evolving over ticks."""
    _setup_style()
    states = build_frame_states(payload, n_frames)
    adj, node_ids = _load_subgraph()
    base_pos = spectral_layout_3d(adj)
    source = "bundled_tiny"
    arm = "coupled_active"

    fig = plt.figure(figsize=(8, 7))
    fig.suptitle(TITLE, fontsize=11)
    fig.text(0.5, 0.94, CAPTION, ha="center", fontsize=7, color="#444444")
    ax = fig.add_subplot(111, projection="3d")

    edge_lines = []
    for i in range(adj.shape[0]):
        for j in range(i + 1, adj.shape[0]):
            if adj[i, j] > 0:
                (line,) = ax.plot(
                    [base_pos[i, 0], base_pos[j, 0]],
                    [base_pos[i, 1], base_pos[j, 1]],
                    [base_pos[i, 2], base_pos[j, 2]],
                    color="#aaaaaa",
                    linewidth=0.6,
                    alpha=0.5,
                )
                edge_lines.append(line)

    scat = ax.scatter(
        base_pos[:, 0],
        base_pos[:, 1],
        base_pos[:, 2],
        c=np.zeros(adj.shape[0]),
        cmap="viridis",
        s=80,
        depthshade=True,
        edgecolors="k",
        linewidths=0.3,
    )
    status = ax.text2D(0.02, 0.96, "", transform=ax.transAxes, fontsize=9)
    ax.set_title(f"{SOURCE_LABELS[source]} · {ARM_LABELS[arm]} connectome (animated)")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")

    def _update(frame_idx: int) -> tuple[Any, ...]:
        state = states[frame_idx]
        m = state.per_point[(source, arm)]
        activity = _node_activity_proxy(adj, m["omega_t"], m["drive_norm"])
        norm = Normalize(vmin=0.0, vmax=max(activity.max(), 0.01))
        scat.set_array(activity)
        scat.set_clim(norm.vmin, norm.vmax)
        scat.set_sizes(80 + 120 * activity)
        status.set_text(
            f"{state.tick_label} · OMEGA_t={m['omega_t']:.3f} · drive={m['drive_norm']:.2f}"
        )
        ax.view_init(elev=20, azim=30 + frame_idx * 3)
        return (scat, status, *edge_lines)

    anim = FuncAnimation(fig, _update, frames=n_frames, interval=1000 / fps, blit=False)
    outputs = _save_animation(anim, "t_brain_06_connectome_3d_dynamic", fps=fps, dpi=dpi)
    plt.close(fig)
    return outputs


def animate_trajectory_3d(
    payload: dict[str, Any],
    *,
    n_frames: int = DEFAULT_FRAMES,
    fps: int = DEFAULT_FPS,
    dpi: int = 90,
) -> dict[str, Path]:
    """3D state-space trajectories: (OMEGA_t, genesis_Δ, EOI) per source/arm."""
    _setup_style()
    states = build_frame_states(payload, n_frames)

    fig = plt.figure(figsize=(9, 7))
    fig.suptitle(TITLE, fontsize=11)
    fig.text(0.5, 0.94, CAPTION, ha="center", fontsize=7, color="#444444")
    ax = fig.add_subplot(111, projection="3d")

    lines: dict[tuple[str, str], Any] = {}
    heads: dict[tuple[str, str], Any] = {}
    for source in SOURCES:
        for arm in ARMS:
            key = (source, arm)
            (line,) = ax.plot([], [], [], color=ARM_COLORS[arm], alpha=0.35, linewidth=1.2)
            heads[key] = ax.scatter(
                [], [], [],
                c=ARM_COLORS[arm],
                s=45,
                depthshade=True,
                edgecolors="k",
                linewidths=0.2,
            )
            lines[key] = line

    handles = [
        plt.Line2D([0], [0], color=ARM_COLORS[a], lw=2, label=ARM_LABELS[a]) for a in ARMS
    ]
    ax.legend(handles=handles, loc="upper left", fontsize=7)
    status = ax.text2D(0.02, 0.96, "", transform=ax.transAxes, fontsize=9)

    ax.set_xlabel(METRIC_LABELS["omega_t"])
    ax.set_ylabel(METRIC_LABELS["genesis_delta"])
    ax.set_zlabel(METRIC_LABELS["eoi_mean"])
    ax.set_title("State-space trajectories (OMEGA_t × genesis_Δ × EOI)")
    ax.set_xlim(0.2, 0.65)
    ax.set_ylim(-0.05, 2.2)
    ax.set_zlim(-0.05, 1.05)

    trajectories: dict[tuple[str, str], list[tuple[float, float, float]]] = {}
    for source in SOURCES:
        for arm in ARMS:
            key = (source, arm)
            trajectories[key] = []
            for state in states:
                m = state.per_point[key]
                trajectories[key].append((m["omega_t"], m["genesis_delta"], m["eoi_mean"]))

    def _update(frame_idx: int) -> tuple[Any, ...]:
        state = states[frame_idx]
        for source in SOURCES:
            for arm in ARMS:
                key = (source, arm)
                trail = trajectories[key][: frame_idx + 1]
                pt = trail[-1]
                xs, ys, zs = zip(*trail)
                lines[key].set_data(xs, ys)
                lines[key].set_3d_properties(zs)
                heads[key]._offsets3d = ([pt[0]], [pt[1]], [pt[2]])

        ref = state.per_point[(SOURCES[0], "coupled_active")]
        status.set_text(f"{state.tick_label} · bundled_tiny endogenous reference")
        ax.view_init(elev=18, azim=35 + frame_idx * 2)
        return (*lines.values(), *heads.values(), status)

    anim = FuncAnimation(fig, _update, frames=n_frames, interval=1000 / fps, blit=False)
    outputs = _save_animation(anim, "t_brain_06_trajectory_3d_dynamic", fps=fps, dpi=dpi)
    plt.close(fig)
    return outputs


def generate_all_dynamic(
    payload: dict[str, Any] | None = None,
    *,
    n_frames: int = DEFAULT_FRAMES,
    fps: int = DEFAULT_FPS,
    dpi: int = 90,
    views: tuple[str, ...] = ("cube", "connectome", "trajectory"),
) -> dict[str, dict[str, Path]]:
    """Generate all dynamic T-BRAIN-06 animations."""
    data = payload or load_payload()
    outputs: dict[str, dict[str, Path]] = {}
    if "cube" in views:
        outputs["t_brain_06_eia_3d_dynamic"] = animate_eia_3d_cube(
            data, n_frames=n_frames, fps=fps, dpi=dpi
        )
    if "connectome" in views:
        outputs["t_brain_06_connectome_3d_dynamic"] = animate_connectome_3d(
            data, n_frames=n_frames, fps=fps, dpi=dpi
        )
    if "trajectory" in views:
        outputs["t_brain_06_trajectory_3d_dynamic"] = animate_trajectory_3d(
            data, n_frames=n_frames, fps=fps, dpi=dpi
        )
    return outputs


def main() -> int:
    outputs = generate_all_dynamic()
    for stem, paths in outputs.items():
        parts = " | ".join(f"{k}={v}" for k, v in paths.items())
        print(f"{stem}: {parts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

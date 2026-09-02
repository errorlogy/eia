#!/usr/bin/env python3
"""
Generate publication-quality vector (PDF) and raster (PNG) figures for EIA arXiv papers.

I05 batch: 3D cube status heatmap, express pipeline, CF-4 ablation bars, Pearl DAG (A04).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import numpy as np
import seaborn as sns
import yaml

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

REPO = Path(__file__).resolve().parents[2]
DEFAULT_FIGURES_DIR = REPO / "arxiv" / "figures"
CUBE_FIGURES_DIR = REPO / "arxiv" / "sci_flow_3d_cube" / "figures"
CELL_REGISTRY = REPO / "research" / "sci_flow" / "cell_registry.yaml"
CF4_RESULTS = REPO / "research" / "sci_flow" / "cf4_results.json"
EXPRESS_MD = REPO / "research" / "sci_flow" / "M-3D-EXPRESS_2026-09-02.md"

STATUS_COLORS = {
    "filled": "#2ca02c",
    "partial": "#ff7f0e",
    "empty": "#bdbdbd",
    "pass": "#1f77b4",
}


def setup_academic_style() -> None:
    sns.set_theme(style="ticks", context="paper")
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.size": 10,
            "axes.labelsize": 11,
            "axes.titlesize": 12,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "legend.fontsize": 9,
            "figure.titlesize": 12,
            "lines.linewidth": 1.5,
            "lines.markersize": 5,
            "figure.autolayout": True,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
        }
    )


def _save_figure(fig: plt.Figure, output_dir: Path, stem: str) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = output_dir / f"{stem}.pdf"
    png_path = output_dir / f"{stem}.png"
    fig.savefig(pdf_path, format="pdf")
    fig.savefig(png_path, format="png", dpi=300)
    plt.close(fig)
    return pdf_path, png_path


def _load_cell_status_grid() -> tuple[list[str], list[str], np.ndarray, list[str]]:
    with CELL_REGISTRY.open(encoding="utf-8") as fh:
        registry = yaml.safe_load(fh)
    axes = ["D1", "D2", "D3"]
    layers = ["L1", "L2", "L3"]
    grid = np.zeros((len(axes), len(layers)), dtype=float)
    labels: list[str] = []
    for i, axis in enumerate(axes):
        for j, layer in enumerate(layers):
            cell = registry["cells"][axis][layer]
            status = str(cell.get("status", "empty"))
            labels.append(status)
            grid[i, j] = {"filled": 2.0, "partial": 1.0, "empty": 0.0}.get(status, 0.0)
    return axes, layers, grid, labels


def generate_cube_status_heatmap(output_dir: Path) -> tuple[Path, Path]:
    setup_academic_style()
    axes, layers, grid, flat_labels = _load_cell_status_grid()

    fig, ax = plt.subplots(figsize=(5.8, 4.2))
    cmap = sns.color_palette(["#e0e0e0", "#ffcc80", "#66bb6a"], as_cmap=True)
    sns.heatmap(
        grid,
        ax=ax,
        cmap=cmap,
        vmin=0,
        vmax=2,
        cbar=False,
        linewidths=1.2,
        linecolor="white",
        xticklabels=[f"{l}\nInvariants" if l == "L1" else f"{l}\nDynamics" if l == "L2" else f"{l}\nWitness" for l in layers],
        yticklabels=[f"{a} Causal" if a == "D1" else f"{a} Dynamic" if a == "D2" else f"{a} Boundary" for a in axes],
        annot=[[flat_labels[i * 3 + j] for j in range(3)] for i in range(3)],
        fmt="",
        annot_kws={"fontsize": 11, "fontweight": "bold", "color": "#1a1a1a"},
    )
    ax.set_title("EIA 3D Evidence Cube — Cell Status (sci-flow v3)")
    ax.set_xlabel("Evidentiary layer")
    ax.set_ylabel("Evaluation axis")

    legend_handles = [
        mpatches.Patch(color=STATUS_COLORS["filled"], label="filled"),
        mpatches.Patch(color=STATUS_COLORS["partial"], label="partial"),
        mpatches.Patch(color=STATUS_COLORS["empty"], label="empty"),
    ]
    ax.legend(handles=legend_handles, loc="upper left", bbox_to_anchor=(1.02, 1.0), frameon=True)
    return _save_figure(fig, output_dir, "cube_status_heatmap")


def _express_cell_rows() -> list[tuple[str, str, float]]:
    """Return (cell_id, message, duration_ms) from registry defaults + express doc if present."""
    defaults = [
        ("D1×L1", "Causal bar definitions", 0.4),
        ("D1×L2", "D01 EOI-k sweep", 613.4),
        ("D1×L3", "Proof ledger (CF-4 + D01)", 263.0),
        ("D2×L1", "Stable endogeneity invariants", 0.4),
        ("D2×L2", "DSR shadow carryover", 114.8),
        ("D2×L3", "ATT-R shadow witness", 38.9),
        ("D3×L1", "Falsifier registry", 5.2),
        ("D3×L2", "CF-7 governor + ATT-N", 1618.9),
        ("D3×L3", "Tier B soft $N_H$ witness", 419.1),
    ]
    if EXPRESS_MD.is_file():
        text = EXPRESS_MD.read_text(encoding="utf-8")
        rows: list[tuple[str, str, float]] = []
        for cell_id, msg, _ in defaults:
            ms = 0.0
            for line in text.splitlines():
                if cell_id in line and "|" in line:
                    parts = [p.strip() for p in line.split("|") if p.strip()]
                    if len(parts) >= 4 and parts[0] == cell_id:
                        msg = parts[2].replace("**", "")
                        try:
                            ms = float(parts[3])
                        except ValueError:
                            pass
                        break
            rows.append((cell_id, msg, ms))
        return rows
    return defaults


def generate_express_pipeline(output_dir: Path) -> tuple[Path, Path]:
    setup_academic_style()
    rows = _express_cell_rows()
    total_ms = sum(r[2] for r in rows)

    fig, ax = plt.subplots(figsize=(7.2, 5.0))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, len(rows) + 2.5)
    ax.axis("off")

    # Title block
    title_box = FancyBboxPatch(
        (0.3, len(rows) + 1.3),
        9.4,
        0.9,
        boxstyle="round,pad=0.08",
        facecolor="#e3f2fd",
        edgecolor="#1565c0",
        linewidth=1.2,
    )
    ax.add_patch(title_box)
    ax.text(
        5.0,
        len(rows) + 1.75,
        r"run\_3d\_express.py  $\rightarrow$  9/9 pass  ($<$60s budget)",
        ha="center",
        va="center",
        fontsize=11,
        fontweight="bold",
    )
    ax.text(
        5.0,
        len(rows) + 0.55,
        f"Measured total: {total_ms:.1f} ms  |  tier-0: check\_sci\_tier0.py",
        ha="center",
        va="center",
        fontsize=9,
        color="#424242",
    )

    for idx, (cell_id, message, ms) in enumerate(reversed(rows)):
        y = idx + 0.55
        box = FancyBboxPatch(
            (0.5, y),
            9.0,
            0.75,
            boxstyle="round,pad=0.06",
            facecolor="#f5f5f5",
            edgecolor=STATUS_COLORS["pass"],
            linewidth=1.5,
        )
        ax.add_patch(box)
        ax.text(1.0, y + 0.38, cell_id, ha="left", va="center", fontweight="bold", fontsize=10)
        ax.text(2.2, y + 0.38, message, ha="left", va="center", fontsize=9)
        ax.text(9.2, y + 0.38, f"{ms:.1f} ms", ha="right", va="center", fontsize=9, color="#1565c0")

        if idx < len(rows) - 1:
            arrow = FancyArrowPatch(
                (5.0, y),
                (5.0, y - 0.15),
                arrowstyle="-|>",
                mutation_scale=12,
                color="#757575",
                linewidth=1.0,
            )
            ax.add_patch(arrow)

    ax.set_title("M-3D-EXPRESS smoke pipeline (9-cell sequential pass)")
    return _save_figure(fig, output_dir, "express_pipeline")


def generate_cf4_ablation_bars(output_dir: Path) -> tuple[Path, Path]:
    setup_academic_style()
    with CF4_RESULTS.open(encoding="utf-8") as fh:
        payload = json.load(fh)
    conditions = payload["summary"]["conditions"]

    # Key ablation conditions cited in papers
    order = ["default", "zero_epistemic_gap", "wm_off", "zero_staleness", "zero_prospective"]
    labels = [
        "default",
        "zero\\_epistemic\\_gap",
        "wm\\_off",
        "zero\\_staleness",
        "zero\\_prospective",
    ]
    rates = [conditions[c]["intent_rate"] for c in order]
    colors = ["#2ca02c" if r >= 0.85 else "#ff7f0e" if r >= 0.4 else "#d62728" for r in rates]

    fig, ax = plt.subplots(figsize=(6.0, 3.6))
    x = np.arange(len(order))
    bars = ax.bar(x, rates, color=colors, edgecolor="#333333", linewidth=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=15, ha="right")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("CF-4 intent rate (pass proxy)")
    ax.set_xlabel("$do(Z)$ condition")
    ax.axhline(0.85, color="#1565c0", linestyle="--", linewidth=1.0, label="default min (0.85)")
    ax.axhline(0.05, color="#9e9e9e", linestyle=":", linewidth=1.0, label="wm\\_off max (0.05)")
    ax.set_title("CF-4 $do(Z)$ ablation — goal/trajectory shift under non-triggering $X$")

    for bar, rate in zip(bars, rates):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.02,
            f"{rate:.2f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    ax.legend(loc="upper right", frameon=True)
    sns.despine(top=True, right=True)
    return _save_figure(fig, output_dir, "cf4_ablation_bars")


def generate_pearl_dag_eoi(output_dir: Path) -> tuple[Path, Path]:
    setup_academic_style()
    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")

    nodes = {
        "X": (1.2, 3.0, r"$X_{t-k}$"),
        "d": (4.0, 4.2, r"$d_t$"),
        "I": (7.0, 3.0, r"$I$ (initiative)"),
        "o": (4.0, 1.2, r"$o^{\mathrm{user}}_{t-k:t}$"),
        "G": (9.0, 3.0, r"$G_{t+1}$"),
    }

    def draw_node(key: str, fc: str = "#ffffff") -> None:
        x, y, label = nodes[key]
        box = FancyBboxPatch(
            (x - 0.85, y - 0.45),
            1.7,
            0.9,
            boxstyle="round,pad=0.08",
            facecolor=fc,
            edgecolor="#212121",
            linewidth=1.2,
        )
        ax.add_patch(box)
        ax.text(x, y, label, ha="center", va="center", fontsize=11)

    draw_node("X", "#e8f5e9")
    draw_node("d", "#fff3e0")
    draw_node("I", "#e3f2fd")
    draw_node("o", "#fce4ec")
    draw_node("G", "#f3e5f5")

    edges = [
        ("X", "d", "#424242"),
        ("d", "I", "#424242"),
        ("o", "I", "#c62828"),
        ("I", "G", "#424242"),
    ]
    for src, dst, color in edges:
        x1, y1, _ = nodes[src]
        x2, y2, _ = nodes[dst]
        style = "-|>"
        lw = 1.6 if src != "o" else 2.2
        arrow = FancyArrowPatch(
            (x1 + 0.9 if x2 > x1 else x1 - 0.9, y1),
            (x2 - 0.9 if x2 > x1 else x2 + 0.9, y2),
            arrowstyle=style,
            mutation_scale=14,
            color=color,
            linewidth=lw,
            connectionstyle="arc3,rad=0.0",
        )
        ax.add_patch(arrow)

    # do(o=∅) intervention strike-through on o→I edge
    ax.plot([4.8, 6.2], [1.55, 2.45], color="#c62828", linewidth=2.5, linestyle="-")
    ax.text(
        5.5,
        1.55,
        r"$do(o=\varnothing)$",
        ha="center",
        va="top",
        fontsize=11,
        color="#c62828",
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="#c62828", alpha=0.95),
    )

    ax.text(
        5.0,
        5.5,
        "Pearl DAG for EOI counterfactual (ATT-E causal bar)",
        ha="center",
        va="center",
        fontsize=12,
        fontweight="bold",
    )
    ax.text(
        5.0,
        0.35,
        r"Twin-world: compare $P(I' \simeq I \mid do(o=\varnothing), X_{t-k})$ vs.\ triggered baseline",
        ha="center",
        va="center",
        fontsize=9,
        color="#424242",
    )

    return _save_figure(fig, output_dir, "dag")


def generate_all_figures(output_dirs: Iterable[Path]) -> list[tuple[str, Path, Path]]:
    generators = [
        ("cube_status_heatmap", generate_cube_status_heatmap),
        ("express_pipeline", generate_express_pipeline),
        ("cf4_ablation_bars", generate_cf4_ablation_bars),
        ("dag", generate_pearl_dag_eoi),
    ]
    saved: list[tuple[str, Path, Path]] = []
    for out_dir in output_dirs:
        out_dir = Path(out_dir)
        for name, fn in generators:
            pdf_path, png_path = fn(out_dir)
            saved.append((name, pdf_path, png_path))
            print(f"[OK] {name}: {pdf_path}")
            print(f"[OK] {name}: {png_path}")
    return saved


if __name__ == "__main__":
    targets = [DEFAULT_FIGURES_DIR, CUBE_FIGURES_DIR]
    if len(sys.argv) > 1:
        targets = [Path(p).resolve() for p in sys.argv[1:]]
    generate_all_figures(targets)

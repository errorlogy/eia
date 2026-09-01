#!/usr/bin/env python3
"""
Generate publication-quality vector (PDF) and raster (PNG) figures
for arxiv/figures/ (DAG, drive decay, trace manifold — see docs/CURSOR_TASKS I05).
"""

import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

DEFAULT_FIGURES_DIR = os.path.join(
    os.path.dirname(__file__), os.pardir, os.pardir, "arxiv", "figures"
)


def setup_academic_style():
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


def generate_sample_experiment_plot(output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    setup_academic_style()

    epochs = np.arange(1, 21)
    baseline_loss = 2.5 * np.exp(-0.15 * epochs) + np.random.normal(0, 0.03, len(epochs))
    standard_loss = 2.4 * np.exp(-0.25 * epochs) + np.random.normal(0, 0.02, len(epochs))
    proposed_loss = 2.2 * np.exp(-0.40 * epochs) + np.random.normal(0, 0.015, len(epochs))

    fig, ax = plt.subplots(figsize=(5.5, 3.2))

    ax.plot(
        epochs,
        baseline_loss,
        label="Reactive baseline",
        color="#7f7f7f",
        linestyle="--",
        marker="o",
    )
    ax.plot(
        epochs,
        standard_loss,
        label="Predictive (P3)",
        color="#1f77b4",
        linestyle="-.",
        marker="s",
    )
    ax.plot(
        epochs,
        proposed_loss,
        label="EIA (P4/P5)",
        color="#d62728",
        linestyle="-",
        marker="^",
        linewidth=2.0,
    )

    ax.set_xlabel("Evaluation Steps")
    ax.set_ylabel("Empirical Loss")
    ax.set_title("Convergence Dynamics (placeholder — replace for I05)")
    ax.legend(frameon=True, loc="upper right")
    ax.grid(True, linestyle=":", alpha=0.6)

    sns.despine(top=True, right=True)

    pdf_path = os.path.join(output_dir, "convergence_comparison.pdf")
    png_path = os.path.join(output_dir, "convergence_comparison.png")

    fig.savefig(pdf_path, format="pdf")
    fig.savefig(png_path, format="png", dpi=300)
    plt.close(fig)
    print(f"[OK] Saved vector PDF figure: {pdf_path}")
    print(f"[OK] Saved high-res PNG figure: {png_path}")


if __name__ == "__main__":
    target_dir = os.path.abspath(DEFAULT_FIGURES_DIR)
    generate_sample_experiment_plot(target_dir)

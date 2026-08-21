
"""
Toy ablation model for "stable endogeneity".

This is NOT a proof of AGI or subjectivity. It operationalizes a narrower
engineering construct: persistent internally-generated goal selection under
zero external reward, with bounded drive dynamics, learning-progress gating,
anti-noise-trap suppression, goal persistence, and hierarchical goal unlocking.

Run:
    python endogeneity_stack_sim.py

Outputs:
    endogeneity_stack_results.csv
    endogeneity_ablation.png
"""

from dataclasses import dataclass
from collections import deque, Counter
from pathlib import Path
import numpy as np
import csv

@dataclass
class Goal:
    idx: int
    level: int
    prereq: tuple
    noisy: bool
    lr: float
    empowerment: float
    competence: float = 0.0
    visits: int = 0
    lp_ema: float = 0.0
    pe_ema: float = 1.0

    def available(self, goals):
        return all(goals[p].competence >= 0.72 for p in self.prereq)


def build_goals(rng, levels=5, per_level=5):
    """Procedural hierarchical goal-space with learnable goals and noisy traps."""
    goals = []
    for j in range(per_level):
        noisy = (j == 0)
        goals.append(
            Goal(
                idx=len(goals),
                level=0,
                prereq=(),
                noisy=noisy,
                lr=0.0 if noisy else rng.uniform(0.02, 0.06),
                empowerment=rng.uniform(0.1, 0.4) if noisy else rng.uniform(0.35, 0.9),
            )
        )

    for level in range(1, levels):
        prev = list(range((level - 1) * per_level, level * per_level))
        for j in range(per_level):
            prereq = tuple(rng.choice(prev, 2, replace=False))
            noisy = (j == 0) or (rng.random() < 0.05)
            goals.append(
                Goal(
                    idx=len(goals),
                    level=level,
                    prereq=prereq,
                    noisy=noisy,
                    lr=0.0 if noisy else rng.uniform(0.015, 0.045) / (1 + 0.08 * level),
                    empowerment=rng.uniform(0.1, 0.4) if noisy else rng.uniform(0.4, 0.95),
                )
            )
    return goals


def practice(goal, rng):
    """One internally selected learning episode."""
    prev = goal.competence
    if goal.noisy:
        # Irreducible prediction error: "noisy-TV" style distractor.
        goal.competence = np.clip(
            goal.competence + rng.normal(0, 0.002) - 0.002 * goal.competence,
            0, 0.12
        )
        noise_floor = 0.95
    else:
        delta = goal.lr * (1 - goal.competence) + rng.normal(0, 0.0015)
        goal.competence = np.clip(goal.competence + max(delta, -0.002), 0, 1)
        noise_floor = 0.04

    progress = max(goal.competence - prev, 0)
    goal.lp_ema = 0.92 * goal.lp_ema + 0.08 * progress

    prediction_error = (
        max(0, 1 - goal.competence)
        + noise_floor
        + abs(rng.normal(0, 0.08 if goal.noisy else 0.015))
    )
    goal.pe_ema = 0.95 * goal.pe_ema + 0.05 * prediction_error
    goal.visits += 1


def softmax(scores, temperature):
    x = np.asarray(scores, dtype=float) / temperature
    x = x - np.max(x)
    p = np.exp(x)
    return p / p.sum()


def intrinsic_features(goal):
    novelty = np.exp(-goal.visits / 35)
    pe = goal.pe_ema
    lp = goal.lp_ema

    # Metacognitive estimate of whether uncertainty is reducible.
    if goal.visits < 4:
        learnability = 0.65
    else:
        learnability = np.clip((lp * 80) / (0.15 + pe), 0, 1)

    reducible_uncertainty = (1 - goal.competence) * learnability

    # High error + repeated visits + little learning progress => noisy trap.
    stuck = (
        (1 - learnability)
        * min(1.0, np.log1p(goal.visits) / 4.0)
        * min(1.2, pe)
    )

    return reducible_uncertainty, min(1.0, lp * 40), goal.empowerment, novelty, stuck


def score(goal, mode, drive, previous_goal):
    u_red, lp, emp, novelty, stuck = intrinsic_features(goal)
    persistence = 1.0 if previous_goal == goal.idx else 0.0
    complexity_cost = 0.05 * goal.level

    if mode == "prediction_error":
        # Naive curiosity: high prediction error is intrinsically attractive.
        return (
            1.10 * goal.pe_ema
            + 0.30 * novelty
            + 0.05 * persistence
            - complexity_cost
        )

    if mode == "learning_progress":
        return (
            3.0 * goal.lp_ema
            + 0.55 * novelty
            + 0.25 * u_red
            - 0.75 * stuck
            + 0.08 * persistence
            - complexity_cost
        )

    if mode == "stable_stack":
        features = np.array([u_red, lp, emp, novelty])
        return (
            float(drive @ features)
            - 1.15 * stuck
            + 0.18 * persistence
            - complexity_cost
        )

    raise ValueError(mode)


def run(seed, mode, steps=2500):
    rng = np.random.default_rng(seed)
    goals = build_goals(rng)

    # Endogenous drive field:
    # [epistemic deficit, competence-growth drive, controllability, diversity]
    drive = np.array([0.70, 0.60, 0.35, 0.50], dtype=float)

    recent = deque(maxlen=80)
    previous = None
    choices = []
    drive_norms = []

    for _ in range(steps):
        available = [g.idx for g in goals if g.available(goals)]

        if mode == "stable_stack":
            competences = np.array([goals[i].competence for i in available])
            global_uncertainty = float(np.mean(1 - competences))
            best_lp = min(1.0, max(goals[i].lp_ema for i in available) * 40)

            if len(recent) > 1:
                counts = np.array(list(Counter(recent).values()), dtype=float)
                probs = counts / counts.sum()
                entropy = -np.sum(probs * np.log(probs + 1e-12))
                entropy_norm = entropy / np.log(max(2, len(available)))
            else:
                entropy_norm = 0.0

            target_drive = np.array([
                0.35 + 0.80 * global_uncertainty,
                0.35 + 0.70 * best_lp,
                0.45,
                0.25 + 0.80 * (1 - np.clip(entropy_norm, 0, 1)),
            ])

            # Slow homeostatic/allostatic relaxation.
            drive = np.clip(
                0.985 * drive + 0.015 * target_drive,
                0.15, 1.40
            )

        scores = [score(goals[i], mode, drive, previous) for i in available]
        temperature = 0.16 if mode == "stable_stack" else 0.11
        probs = softmax(scores, temperature)
        chosen = int(rng.choice(available, p=probs))

        practice(goals[chosen], rng)

        if mode == "stable_stack":
            # Satisfaction feedback prevents monotonic runaway of intrinsic drives.
            u_red, lp, emp, novelty, _ = intrinsic_features(goals[chosen])
            satisfaction = np.array([u_red, lp, emp, novelty])
            drive = np.clip(drive - 0.012 * satisfaction, 0.15, 1.40)
            drive_norms.append(float(np.linalg.norm(drive)))

        choices.append(chosen)
        recent.append(chosen)
        previous = chosen

    learnable = [g for g in goals if not g.noisy]
    counts = np.bincount(choices, minlength=len(goals))
    p = counts[counts > 0] / len(choices)
    entropy = -np.sum(p * np.log(p)) / np.log(len(goals))
    switching = np.mean(np.asarray(choices[1:]) != np.asarray(choices[:-1]))

    return {
        "mastered_goals": sum(g.competence >= 0.80 for g in learnable),
        "unlocked_goals": sum(g.available(goals) for g in goals),
        "noisy_trap_fraction": float(np.mean([goals[i].noisy for i in choices])),
        "goal_entropy": float(entropy),
        "max_goal_share": float(counts.max() / len(choices)),
        "switching_rate": float(switching),
        "drive_norm_min": min(drive_norms) if drive_norms else np.nan,
        "drive_norm_max": max(drive_norms) if drive_norms else np.nan,
    }


def experiment(seeds=10, steps=2500):
    modes = ["prediction_error", "learning_progress", "stable_stack"]
    rows = []

    for mode in modes:
        runs = [run(seed, mode, steps) for seed in range(seeds)]
        row = {"mode": mode}
        for key in runs[0]:
            values = np.asarray([r[key] for r in runs], dtype=float)
            if np.all(np.isnan(values)):
                row[key] = np.nan
            else:
                row[key] = float(np.nanmean(values))
        rows.append(row)

    return rows


def main():
    outdir = Path(__file__).resolve().parent
    rows = experiment()

    csv_path = outdir / "endogeneity_stack_results.csv"
    fieldnames = list(rows[0].keys())
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print("Ablation means:")
    for row in rows:
        print(row)

    try:
        import matplotlib.pyplot as plt
        labels = [r["mode"] for r in rows]
        vals = [r["noisy_trap_fraction"] for r in rows]
        fig = plt.figure(figsize=(8, 5))
        ax = fig.add_subplot(111)
        ax.bar(labels, vals)
        ax.set_ylabel("Fraction of actions allocated to noisy traps")
        ax.set_title("Intrinsic-drive ablation")
        ax.tick_params(axis="x", rotation=20)
        fig.tight_layout()
        fig.savefig(outdir / "endogeneity_ablation.png", dpi=160)
        plt.close(fig)
    except Exception as e:
        print("Plot skipped:", e)


if __name__ == "__main__":
    main()

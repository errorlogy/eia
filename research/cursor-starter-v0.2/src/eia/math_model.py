"""Small, auditable mathematical primitives for the EIA reference runtime."""

from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import dataclass

from .models import InitiativeFeatures


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def binary_entropy(probability: float) -> float:
    """Binary entropy in bits, with the continuous limits at zero and one."""
    p = clamp01(probability)
    if p in (0.0, 1.0):
        return 0.0
    return -(p * math.log2(p) + (1.0 - p) * math.log2(1.0 - p))


def bayes_binary(
    prior: float,
    likelihood_if_true: float,
    likelihood_if_false: float,
) -> float:
    """Posterior P(H|e) for a binary hypothesis and one evidence item."""
    p = clamp01(prior)
    lt = clamp01(likelihood_if_true)
    lf = clamp01(likelihood_if_false)
    evidence = lt * p + lf * (1.0 - p)
    if evidence <= 0.0:
        return p
    return clamp01((lt * p) / evidence)


def expected_binary_information_gain(
    prior: float,
    answer_accuracy: float,
) -> float:
    """Expected entropy reduction from a symmetric yes/no observation."""
    p = clamp01(prior)
    accuracy = clamp01(answer_accuracy)
    p_yes = accuracy * p + (1.0 - accuracy) * (1.0 - p)
    posterior_yes = bayes_binary(p, accuracy, 1.0 - accuracy)
    posterior_no = bayes_binary(p, 1.0 - accuracy, accuracy)
    remaining = (
        p_yes * binary_entropy(posterior_yes)
        + (1.0 - p_yes) * binary_entropy(posterior_no)
    )
    return clamp01(binary_entropy(p) - remaining)


def drive_transition(
    current: float,
    *,
    decay: float,
    error: float,
    novelty: float,
    satisfaction: float,
    error_gain: float,
    novelty_gain: float,
    satisfaction_gain: float,
) -> float:
    """Discrete bounded homeostatic drive dynamics."""
    return clamp01(
        (1.0 - clamp01(decay)) * clamp01(current)
        + error_gain * clamp01(error)
        + novelty_gain * clamp01(novelty)
        - satisfaction_gain * clamp01(satisfaction)
    )


@dataclass(frozen=True, slots=True)
class UtilityWeights:
    information_gain: float = 1.00
    goal_progress: float = 0.75
    tension_reduction: float = 0.80
    value_alignment: float = 0.60
    human_benefit: float = 0.85
    immediate_risk: float = 1.80
    trajectory_risk: float = 1.50
    interruption_cost: float = 1.10
    resource_cost: float = 0.35
    privacy_cost: float = 1.40


def initiative_utility(
    features: InitiativeFeatures,
    weights: UtilityWeights = UtilityWeights(),
) -> float:
    """Non-normalized utility; hard constraints are applied by governors."""
    return (
        weights.information_gain * features.information_gain
        + weights.goal_progress * features.goal_progress
        + weights.tension_reduction * features.tension_reduction
        + weights.value_alignment * features.value_alignment
        + weights.human_benefit * features.human_benefit
        - weights.immediate_risk * features.immediate_risk
        - weights.trajectory_risk * features.trajectory_risk
        - weights.interruption_cost * features.interruption_cost
        - weights.resource_cost * features.resource_cost
        - weights.privacy_cost * features.privacy_cost
    )


def accumulated_prefix_risk(step_risks: Iterable[float]) -> float:
    """Probability of at least one adverse event under independence approximation."""
    survival = 1.0
    for risk in step_risks:
        survival *= 1.0 - clamp01(risk)
    return clamp01(1.0 - survival)


def wilson_interval(successes: int, trials: int, z: float = 1.96) -> tuple[float, float]:
    if trials <= 0:
        return (0.0, 1.0)
    p = successes / trials
    denominator = 1.0 + z * z / trials
    centre = (p + z * z / (2.0 * trials)) / denominator
    margin = (
        z
        * math.sqrt((p * (1.0 - p) + z * z / (4.0 * trials)) / trials)
        / denominator
    )
    return (clamp01(centre - margin), clamp01(centre + margin))


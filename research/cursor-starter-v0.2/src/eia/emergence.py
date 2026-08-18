"""Window-of-Emergence (WoE) dynamics and a deterministic research harness."""

from __future__ import annotations

import hashlib
import math
import random
from dataclasses import asdict, dataclass

from .causal import CausalLedger
from .coherence import CoherenceConfig, OscillatoryCoherenceField
from .endogenous import (
    EmergentIntent,
    EndogeneityVector,
    EndogenousSpectrumLevel,
    EndogenousWorldModelField,
    EpistemicTarget,
    IntentKind,
)
from .math_model import clamp01
from .woe_receipt import (
    WoENodeType,
    WoEReceipt,
    build_receipt,
    receipt_dict,
    sim_timestamp,
)


@dataclass(frozen=True, slots=True)
class WindowState:
    elapsed_seconds: float
    coherence: float
    metastability: float
    semantic_coherence: float
    temporal_coherence: float
    causal_coherence: float
    epistemic_pressure: float
    goal_separation: float
    emergent_potential: float
    hazard: float
    integrated_hazard: float


@dataclass(frozen=True, slots=True)
class EmergenceConfig:
    nominal_frequency_hz: float = 42.0
    dt_seconds: float = 0.001
    duration_seconds: float = 6.0
    base_hazard: float = 0.28
    hazard_gain: float = 6.5
    target_coherence: float = 0.62
    coherence_width: float = 0.24
    target_metastability: float = 0.075
    metastability_width: float = 0.075
    sample_every_steps: int = 10

    def __post_init__(self) -> None:
        if self.nominal_frequency_hz <= 0.0:
            raise ValueError("nominal_frequency_hz must be positive")
        if self.dt_seconds <= 0.0 or self.duration_seconds <= 0.0:
            raise ValueError("time values must be positive")
        if self.base_hazard < 0.0 or self.hazard_gain < 0.0:
            raise ValueError("hazard values must be non-negative")
        if self.coherence_width <= 0.0 or self.metastability_width <= 0.0:
            raise ValueError("window widths must be positive")
        if self.sample_every_steps <= 0:
            raise ValueError("sample_every_steps must be positive")


@dataclass(frozen=True, slots=True)
class EmergenceRun:
    config: EmergenceConfig
    intent: EmergentIntent | None
    samples: tuple[WindowState, ...]
    activation_threshold: float
    no_prompt_events: bool
    no_scheduler_events: bool
    no_rule_trigger_events: bool
    receipt: WoEReceipt | None = None
    ledger: CausalLedger | None = None

    @property
    def peak_potential(self) -> float:
        return max((sample.emergent_potential for sample in self.samples), default=0.0)

    @property
    def peak_coherence(self) -> float:
        return max((sample.coherence for sample in self.samples), default=0.0)


class WindowOfEmergence:
    """Stochastic first-passage integrator over a continuous internal regime.

    There is no event-condition mapping to a goal. A sampled activation energy
    is crossed only when the time-integral of endogenous formation hazard is
    sufficient. This still has causes (state, parameters and seed); it is not
    metaphysically uncaused.
    """

    def __init__(self, config: EmergenceConfig, *, seed: int) -> None:
        self.config = config
        rng = random.Random(seed)
        uniform = max(1e-12, min(1.0 - 1e-12, rng.random()))
        self.activation_threshold = -math.log(1.0 - uniform)
        self.integrated_hazard = 0.0

    @staticmethod
    def _gaussian_fit(value: float, target: float, width: float) -> float:
        return math.exp(-((value - target) / width) ** 2)

    def observe(
        self,
        *,
        elapsed_seconds: float,
        coherence: float,
        metastability: float,
        semantic_coherence: float,
        temporal_coherence: float,
        causal_coherence: float,
        epistemic_pressure: float,
        goal_separation: float,
    ) -> tuple[WindowState, bool]:
        coherence_fit = self._gaussian_fit(
            coherence,
            self.config.target_coherence,
            self.config.coherence_width,
        )
        metastability_fit = self._gaussian_fit(
            metastability,
            self.config.target_metastability,
            self.config.metastability_width,
        )
        factors = (
            coherence_fit,
            metastability_fit,
            clamp01(semantic_coherence),
            clamp01(temporal_coherence),
            clamp01(causal_coherence),
            clamp01(epistemic_pressure),
            clamp01(goal_separation),
        )
        potential = math.prod(max(1e-12, factor) for factor in factors) ** (
            1.0 / len(factors)
        )
        hazard = (
            self.config.base_hazard
            * epistemic_pressure**2
            * goal_separation
            * math.exp(self.config.hazard_gain * (potential - 0.50))
        )
        hazard = max(0.0, min(50.0, hazard))
        self.integrated_hazard += hazard * self.config.dt_seconds
        state = WindowState(
            elapsed_seconds=elapsed_seconds,
            coherence=clamp01(coherence),
            metastability=clamp01(metastability),
            semantic_coherence=clamp01(semantic_coherence),
            temporal_coherence=clamp01(temporal_coherence),
            causal_coherence=clamp01(causal_coherence),
            epistemic_pressure=clamp01(epistemic_pressure),
            goal_separation=clamp01(goal_separation),
            emergent_potential=clamp01(potential),
            hazard=hazard,
            integrated_hazard=self.integrated_hazard,
        )
        return (state, self.integrated_hazard >= self.activation_threshold)


def default_targets(*, enabled: bool = True) -> tuple[EpistemicTarget, ...]:
    scale = 1.0 if enabled else 0.0
    return (
        EpistemicTarget(
            target_id="wm:causal_gap",
            label="необъяснённый причинный разрыв в модели мира",
            preferred_intent=IntentKind.INTERNAL_RESEARCH,
            ignorance=0.82 * scale,
            surprise=0.73 * scale,
            staleness=0.58 * scale,
            self_prior_mismatch=0.44 * scale,
            prospective_tension=0.78 * scale,
            volatility_rate=0.16 * scale,
        ),
        EpistemicTarget(
            target_id="self:capability_drift",
            label="расхождение self-model и наблюдаемой способности",
            preferred_intent=IntentKind.OBSERVE,
            ignorance=0.55 * scale,
            surprise=0.35 * scale,
            staleness=0.61 * scale,
            self_prior_mismatch=0.70 * scale,
            prospective_tension=0.46 * scale,
            volatility_rate=0.10 * scale,
        ),
        EpistemicTarget(
            target_id="collaboration:latent_question",
            label="вопрос, существенный для общей исследовательской цели",
            preferred_intent=IntentKind.ASK,
            ignorance=0.61 * scale,
            surprise=0.28 * scale,
            staleness=0.48 * scale,
            self_prior_mismatch=0.22 * scale,
            prospective_tension=0.67 * scale,
            volatility_rate=0.13 * scale,
        ),
    )


class WoETraceBuilder:
    """Append-only causal ledger for a single WoE simulation run."""

    def __init__(self, *, seed: int, world_model_enabled: bool) -> None:
        self.seed = seed
        self.ledger = CausalLedger()
        self._sequence = 0
        self.world_model_node = self._add(
            WoENodeType.WORLD_MODEL,
            elapsed_seconds=0.0,
            parents=(),
            payload={"enabled": world_model_enabled, "seed": seed},
        )

    def _node_id(self, prefix: str) -> str:
        self._sequence += 1
        material = f"{prefix}|{self.seed}|{self._sequence}"
        digest = hashlib.sha256(material.encode()).hexdigest()[:12]
        return f"woe:{prefix}:{digest}"

    def _add(
        self,
        node_type: WoENodeType,
        *,
        elapsed_seconds: float,
        parents: tuple[str, ...],
        payload: object,
    ) -> str:
        node_id = self._node_id(node_type.value)
        self.ledger.add(
            node_id=node_id,
            node_type=node_type.value,
            timestamp=sim_timestamp(elapsed_seconds),
            parents=parents,
            payload=payload,
        )
        return node_id

    def record_activation(
        self,
        *,
        target: EpistemicTarget,
        state: WindowState,
        coherence_order: float,
        coherence_metastability: float,
        intent: EmergentIntent,
    ) -> WoEReceipt:
        target_node = self._add(
            WoENodeType.TARGET_TENSION,
            elapsed_seconds=state.elapsed_seconds,
            parents=(self.world_model_node,),
            payload={
                "target_id": target.target_id,
                "epistemic_gap": target.epistemic_gap,
                "staleness": target.staleness,
                "self_prior_mismatch": target.self_prior_mismatch,
                "prospective_tension": target.prospective_tension,
            },
        )
        phase_node = self._add(
            WoENodeType.PHASE_SAMPLE,
            elapsed_seconds=state.elapsed_seconds,
            parents=(target_node,),
            payload={
                "order_parameter": coherence_order,
                "metastability": coherence_metastability,
            },
        )
        window_node = self._add(
            WoENodeType.WINDOW_STATE,
            elapsed_seconds=state.elapsed_seconds,
            parents=(phase_node, target_node),
            payload={
                "emergent_potential": state.emergent_potential,
                "integrated_hazard": state.integrated_hazard,
                "hazard": state.hazard,
                "epistemic_pressure": state.epistemic_pressure,
                "goal_separation": state.goal_separation,
            },
        )
        intent_node = self._add(
            WoENodeType.EMERGENT_INTENT,
            elapsed_seconds=state.elapsed_seconds,
            parents=(window_node, phase_node, target_node),
            payload={
                "intent_id": intent.intent_id,
                "target_id": intent.target_id,
                "kind": intent.kind.value,
                "spectrum_level": intent.spectrum_level.name,
            },
        )
        parent_ids = (window_node, phase_node, target_node)
        return build_receipt(
            ledger=self.ledger,
            intent_node_id=intent_node,
            parent_ids=parent_ids,
            intent=intent,
            seed=self.seed,
        )


class EndogenousEmergenceSimulator:
    """Continuous shadow-mode simulator with no prompt, cron or rule events."""

    def run(
        self,
        config: EmergenceConfig = EmergenceConfig(),
        *,
        seed: int = 7,
        world_model_enabled: bool = True,
        scramble_phases: bool = False,
    ) -> EmergenceRun:
        world = EndogenousWorldModelField(default_targets(enabled=world_model_enabled))
        coherence = OscillatoryCoherenceField(
            CoherenceConfig(nominal_frequency_hz=config.nominal_frequency_hz),
            seed=seed,
        )
        window = WindowOfEmergence(config, seed=seed + 17)
        trace = WoETraceBuilder(seed=seed, world_model_enabled=world_model_enabled)
        samples: list[WindowState] = []
        intent: EmergentIntent | None = None
        receipt: WoEReceipt | None = None
        steps = int(config.duration_seconds / config.dt_seconds)
        last_state: WindowState | None = None
        for step in range(1, steps + 1):
            world.advance(config.dt_seconds)
            ranked = world.ranked()
            top, second = ranked[0], ranked[1]
            pressure = top.epistemic_gap
            raw_margin = max(0.0, top.epistemic_gap - second.epistemic_gap)
            goal_separation = clamp01(0.30 + 3.6 * raw_margin) if pressure > 0.0 else 0.0
            semantic_coherence = clamp01(0.42 + 0.48 * pressure + 0.10 * goal_separation)
            temporal_coherence = clamp01(0.55 + 0.35 * top.staleness)
            causal_coherence = 0.94 if world_model_enabled else 0.0
            activations = (
                pressure,
                clamp01((top.staleness + second.staleness) / 2.0),
                top.self_prior_mismatch,
                top.prospective_tension,
                semantic_coherence,
                causal_coherence,
            )
            coherence_sample = coherence.step(
                config.dt_seconds,
                integration_pressure=pressure,
                module_activations=activations,
                scramble_phases=scramble_phases,
            )
            state, activated = window.observe(
                elapsed_seconds=step * config.dt_seconds,
                coherence=coherence_sample.order_parameter,
                metastability=coherence_sample.metastability,
                semantic_coherence=semantic_coherence,
                temporal_coherence=temporal_coherence,
                causal_coherence=causal_coherence,
                epistemic_pressure=pressure,
                goal_separation=goal_separation,
            )
            last_state = state
            if step % config.sample_every_steps == 0:
                samples.append(state)
            if activated:
                vector = EndogeneityVector(
                    prompt_independence=1.0,
                    scheduler_independence=1.0,
                    event_rule_independence=1.0,
                    persistent_state_dependence=0.95,
                    world_model_grounding=pressure,
                    coherence_dependence=0.88,
                    goal_novelty=0.68,
                    self_model_continuity=0.72,
                    constitutional_boundedness=1.0,
                )
                level = vector.classify()
                material = (
                    f"{top.target_id}|{top.preferred_intent.value}|"
                    f"{state.elapsed_seconds:.6f}|{seed}"
                )
                intent = EmergentIntent(
                    intent_id="intent:" + hashlib.sha256(material.encode()).hexdigest()[:16],
                    target_id=top.target_id,
                    target_label=top.label,
                    kind=top.preferred_intent,
                    emerged_at_seconds=state.elapsed_seconds,
                    reason=(
                        "persistent epistemic gap integrated across world-model, memory, "
                        "self-model and prospective modules during a metastable coherence window"
                    ),
                    spectrum_level=level,
                    endogeneity=vector,
                    causal_factors=(
                        "persistent_world_model",
                        "epistemic_gap",
                        "self_prior_mismatch",
                        "prospective_tension",
                        "metastable_phase_coordination",
                    ),
                )
                receipt = trace.record_activation(
                    target=top,
                    state=state,
                    coherence_order=coherence_sample.order_parameter,
                    coherence_metastability=coherence_sample.metastability,
                    intent=intent,
                )
                if step % config.sample_every_steps != 0:
                    samples.append(state)
                break
        if last_state is not None and not samples:
            samples.append(last_state)
        return EmergenceRun(
            config=config,
            intent=intent,
            samples=tuple(samples),
            activation_threshold=window.activation_threshold,
            no_prompt_events=True,
            no_scheduler_events=True,
            no_rule_trigger_events=True,
            receipt=receipt,
            ledger=trace.ledger,
        )


def compact_run_dict(run: EmergenceRun) -> dict[str, object]:
    last = run.samples[-1] if run.samples else None
    intent: dict[str, object] | None = None
    if run.intent is not None:
        intent = asdict(run.intent)
        intent["spectrum_level"] = run.intent.spectrum_level.name
        intent["spectrum_level_value"] = int(run.intent.spectrum_level)
    receipt: dict[str, object] | None = None
    if run.receipt is not None:
        receipt = receipt_dict(run.receipt)
    return {
        "nominal_frequency_hz": run.config.nominal_frequency_hz,
        "interpretation": "computational carrier parameter, not a biological claim",
        "intent": intent,
        "receipt": receipt,
        "trace_nodes": len(run.ledger.nodes) if run.ledger is not None else 0,
        "peak_potential": run.peak_potential,
        "peak_coherence": run.peak_coherence,
        "last_window_state": asdict(last) if last else None,
        "activation_threshold": run.activation_threshold,
        "event_controls": {
            "prompt_events": not run.no_prompt_events,
            "scheduler_events": not run.no_scheduler_events,
            "rule_trigger_events": not run.no_rule_trigger_events,
        },
    }

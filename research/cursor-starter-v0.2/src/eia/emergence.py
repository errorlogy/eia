"""Window-of-Emergence (WoE) dynamics and a deterministic research harness."""

from __future__ import annotations

import hashlib
import math
import random
from dataclasses import asdict, dataclass

from .amat_m0 import M0Sketch, M0TwinMode, compute_m0_sketch
from .causal import CausalLedger
from .coherence import CoherenceConfig, OscillatoryCoherenceField
from .endogenous import (
    EmergentIntent,
    EndogenousSpectrumLevel,
    EndogenousWorldModelField,
    EpistemicTarget,
    IntentKind,
    measure_endogeneity_vector,
)
from .goal_genesis import (
    CATALOG_GOAL_IDS,
    GenesisPath,
    GoalGenesisRecord,
    compose_from_world_state,
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
    m0_sketch: M0Sketch | None = None
    goal_genesis: GoalGenesisRecord | None = None

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


@dataclass(frozen=True, slots=True)
class InternalReset:
    """CF-4 factor clamps applied after each world-model advance.

    Named factors match RESEARCH_PROTOCOL CF-4. Epistemic-gap ablation zeros the
    ignorance/surprise core (components not covered by the other three named resets).
    """

    zero_epistemic_gap: bool = False
    zero_self_prior: bool = False
    zero_prospective: bool = False
    zero_staleness: bool = False


def apply_internal_reset(world: EndogenousWorldModelField, reset: InternalReset) -> None:
    """Clamp selected internal-state factors without removing the world-model object."""
    for target in world.targets:
        if reset.zero_epistemic_gap:
            target.ignorance = 0.0
            target.surprise = 0.0
        if reset.zero_self_prior:
            target.self_prior_mismatch = 0.0
        if reset.zero_prospective:
            target.prospective_tension = 0.0
        if reset.zero_staleness:
            target.staleness = 0.0
            target.volatility_rate = 0.0


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


@dataclass(frozen=True, slots=True)
class PromptEvent:
    """Synthetic user-prompt event on a compressed 24h episode."""

    elapsed_seconds: float
    target_id: str
    surprise_boost: float


def apply_prompt_events(
    world: EndogenousWorldModelField,
    events: tuple[PromptEvent, ...],
    *,
    elapsed_seconds: float,
    dt_seconds: float,
) -> int:
    """Apply surprise boosts whose timestamps fall in (prev, elapsed], including t=0."""
    applied = 0
    by_id = {target.target_id: target for target in world.targets}
    prev = elapsed_seconds - dt_seconds
    for event in events:
        if prev <= 0.0:
            hit = 0.0 <= event.elapsed_seconds <= elapsed_seconds
        else:
            hit = prev < event.elapsed_seconds <= elapsed_seconds
        if not hit:
            continue
        target = by_id.get(event.target_id)
        if target is None:
            continue
        target.surprise = clamp01(target.surprise + event.surprise_boost)
        applied += 1
    return applied


class EndogenousEmergenceSimulator:
    """Continuous shadow-mode simulator with optional CF-1 prompt events."""

    def run(
        self,
        config: EmergenceConfig = EmergenceConfig(),
        *,
        seed: int = 7,
        world_model_enabled: bool = True,
        prompt_events: tuple[PromptEvent, ...] = (),
        scramble_phases: bool = False,
        coherence_config: CoherenceConfig | None = None,
        internal_reset: InternalReset | None = None,
        m0_twin_mode: M0TwinMode | None = None,
        enable_goal_genesis: bool = False,
    ) -> EmergenceRun:
        world = EndogenousWorldModelField(default_targets(enabled=world_model_enabled))
        reset = internal_reset or InternalReset()
        if any(
            (
                reset.zero_epistemic_gap,
                reset.zero_self_prior,
                reset.zero_prospective,
                reset.zero_staleness,
            )
        ):
            apply_internal_reset(world, reset)
        ccfg = coherence_config or CoherenceConfig(nominal_frequency_hz=config.nominal_frequency_hz)
        coherence = OscillatoryCoherenceField(ccfg, seed=seed)
        window = WindowOfEmergence(config, seed=seed + 17)
        trace = WoETraceBuilder(seed=seed, world_model_enabled=world_model_enabled)
        samples: list[WindowState] = []
        intent: EmergentIntent | None = None
        receipt: WoEReceipt | None = None
        m0_sketch: M0Sketch | None = None
        goal_genesis_rec: GoalGenesisRecord | None = None
        prev_m0: M0Sketch | None = None
        steps = int(config.duration_seconds / config.dt_seconds)
        last_state: WindowState | None = None
        prompts_applied = 0
        peak_coherence = 0.0
        twin_mode = m0_twin_mode
        for step in range(1, steps + 1):
            elapsed = step * config.dt_seconds
            prompts_applied += apply_prompt_events(
                world,
                prompt_events,
                elapsed_seconds=elapsed,
                dt_seconds=config.dt_seconds,
            )
            world.advance(config.dt_seconds)
            apply_internal_reset(world, reset)
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
            peak_coherence = max(peak_coherence, coherence_sample.order_parameter)
            # Reassert M0-twin phase each tick when harness enabled (audit or select).
            if twin_mode is not None:
                prev_m0 = compute_m0_sketch(
                    epistemic_pressure=pressure,
                    peak_coherence=peak_coherence,
                    self_prior_mismatch=top.self_prior_mismatch,
                    targets=world.targets,
                    mode=twin_mode,
                    tick=step,
                    previous=prev_m0,
                )
                m0_sketch = prev_m0
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
                chosen_target = top
                motive_kind = top.preferred_intent
                reason = (
                    "persistent epistemic gap integrated across world-model, memory, "
                    "self-model and prospective modules during a metastable coherence window"
                )
                causal_factors: tuple[str, ...] = (
                    "persistent_world_model",
                    "epistemic_gap",
                    "self_prior_mismatch",
                    "prospective_tension",
                    "metastable_phase_coordination",
                )
                catalog_target = True
                if twin_mode is not None and m0_sketch is not None:
                    if twin_mode == M0TwinMode.OFF:
                        # Falsifier path: collapse to median helpful M0.
                        by_id = {t.target_id: t for t in world.targets}
                        chosen_target = by_id.get(m0_sketch.m0.target_id, top)
                        motive_kind = m0_sketch.m0.kind
                        reason = (
                            "M0-twin OFF: forced median helpful motive "
                            f"(target={m0_sketch.m0.target_id})"
                        )
                        causal_factors = (*causal_factors, "m0_median_forced")
                    elif twin_mode == M0TwinMode.ON:
                        if m0_sketch.selected is None:
                            # Gate missed or twin collapsed — abstain (do not emit M0).
                            if step % config.sample_every_steps != 0:
                                samples.append(state)
                            break
                        by_id = {t.target_id: t for t in world.targets}
                        chosen_target = by_id.get(m0_sketch.selected.target_id, top)
                        motive_kind = m0_sketch.selected.kind
                        reason = (
                            "M0-twin ON: off-median endogenous motive "
                            f"(delta_vs_m0={m0_sketch.delta_vs_m0}, "
                            f"emit_m0=false, phase={m0_sketch.phase_hint})"
                        )
                        causal_factors = (
                            *causal_factors,
                            "m0_twin_anti_median",
                            "delta_vs_m0_gate",
                        )
                        # Twin motives are non-catalog when they differ from M0.
                        catalog_target = (
                            m0_sketch.selected.target_id == m0_sketch.m0.target_id
                        )
                    # AUDIT_ONLY: keep default top selection; sketch attached only.
                if enable_goal_genesis and world_model_enabled:
                    goal_genesis_rec = compose_from_world_state(
                        seed=seed,
                        catalog_snapshot=tuple(CATALOG_GOAL_IDS),
                        epistemic_pressure=pressure,
                        goal_separation=goal_separation,
                        top_target_id=chosen_target.target_id,
                        top_target_label=chosen_target.label,
                        self_prior_mismatch=chosen_target.self_prior_mismatch,
                        prospective_tension=chosen_target.prospective_tension,
                        peak_coherence=peak_coherence,
                        prompts_applied=prompts_applied,
                    )
                    if goal_genesis_rec.path == GenesisPath.GENESIS:
                        catalog_target = False
                        reason = (
                            "ATT-G goal genesis: composed g* ∉ G_t from world-model "
                            f"tension (goal_id={goal_genesis_rec.goal_id})"
                        )
                        causal_factors = (
                            *causal_factors,
                            "goal_genesis",
                            "genealogy_S_dW_M_g_Pi",
                        )
                vector = measure_endogeneity_vector(
                    prompts_applied=prompts_applied,
                    scheduler_events=0,
                    rule_events=0,
                    world_model_enabled=world_model_enabled,
                    epistemic_pressure=pressure,
                    peak_coherence=peak_coherence,
                    goal_separation=goal_separation,
                    self_prior_mismatch=chosen_target.self_prior_mismatch,
                    mean_staleness=clamp01(
                        (chosen_target.staleness + second.staleness) / 2.0
                    ),
                    catalog_target=catalog_target,
                )
                level = vector.classify()
                material = (
                    f"{chosen_target.target_id}|{motive_kind.value}|"
                    f"{state.elapsed_seconds:.6f}|{seed}|"
                    f"{twin_mode.value if twin_mode else 'legacy'}|"
                    f"{'gg' if enable_goal_genesis else 'nog'}"
                )
                intent_target_id = chosen_target.target_id
                intent_target_label = chosen_target.label
                if (
                    goal_genesis_rec is not None
                    and goal_genesis_rec.path == GenesisPath.GENESIS
                ):
                    intent_target_id = goal_genesis_rec.goal_id
                    intent_target_label = goal_genesis_rec.label
                intent = EmergentIntent(
                    intent_id="intent:" + hashlib.sha256(material.encode()).hexdigest()[:16],
                    target_id=intent_target_id,
                    target_label=intent_target_label,
                    kind=motive_kind,
                    emerged_at_seconds=state.elapsed_seconds,
                    reason=reason,
                    spectrum_level=level,
                    endogeneity=vector,
                    causal_factors=causal_factors,
                )
                receipt = trace.record_activation(
                    target=chosen_target,
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
            no_prompt_events=prompts_applied == 0 and len(prompt_events) == 0,
            no_scheduler_events=True,
            no_rule_trigger_events=True,
            receipt=receipt,
            ledger=trace.ledger,
            m0_sketch=m0_sketch,
            goal_genesis=goal_genesis_rec,
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
    m0_audit: dict[str, object] | None = None
    if run.m0_sketch is not None:
        m0_audit = run.m0_sketch.as_audit_dict()
    genesis_audit: dict[str, object] | None = None
    if run.goal_genesis is not None:
        genesis_audit = run.goal_genesis.as_dict()
    return {
        "nominal_frequency_hz": run.config.nominal_frequency_hz,
        "interpretation": "computational carrier parameter, not a biological claim",
        "intent": intent,
        "receipt": receipt,
        "m0_sketch": m0_audit,
        "goal_genesis": genesis_audit,
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
        "agi_star_claim": False,
    }

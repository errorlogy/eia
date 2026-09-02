# Neuraxon Game of Life Neuron Components v3.34
# Based on the Paper "Neuraxon: A New Neural Growth & Computation Blueprint" by David Vivancos https://vivancos.com/  & Dr. Jose Sanchez  https://josesanchezgarcia.com/ for Qubic Science https://qubic.org/
# https://www.researchgate.net/publication/397331336_Neuraxon
# Play the Lite Version of the Game of Life at https://huggingface.co/spaces/DavidVivancos/NeuraxonLife
import random
import math
import numpy as np
from collections import deque
from typing import List, Dict, Tuple, Optional

# Import local modules
from .enums import SynapseType
from config import NetworkParameters, SYNAPSE_SILENCING_ACTIVITY_THRESHOLD
from utils import _variate
from logger import get_data_logger

class DendriticBranch:
    """
    Models a single dendritic compartment of a Neuraxon.
    Now includes individualized threshold and decay properties.
    """
    def __init__(self, branch_id: int, parent_neuron_id: int, params: NetworkParameters):
        self.branch_id = branch_id
        self.parent_neuron_id = parent_neuron_id
        self.params = params
        self.branch_potential = 0.0
        
        # INDIVIDUALIZED: Each branch has slight variations in geometry/physics
        self.branch_threshold = _variate(params.branch_threshold)
        self.plateau_decay = _variate(params.plateau_decay)
        
        self.plateau_potential = 0.0
        self.local_spike_history = deque(maxlen=10)
    
    def integrate_inputs(self, synaptic_inputs: List[float], dt: float) -> float:
        """
        Integrates incoming synaptic signals for this branch.
        """
        if not synaptic_inputs:
            # Use localized plateau_decay
            self.plateau_potential += dt / self.plateau_decay * (-self.plateau_potential)
            self.branch_potential += dt / (self.params.membrane_time_constant * 0.5) * (-self.branch_potential)
            return self.branch_potential + self.plateau_potential
        
        branch_signal = math.tanh(sum(synaptic_inputs))
        
        # Use localized branch_threshold
        if abs(branch_signal) > self.branch_threshold:
            self.plateau_potential = branch_signal * 0.8
            
        tau_branch = max(1.0, self.params.membrane_time_constant * 0.3)
        self.branch_potential += dt / tau_branch * (branch_signal - self.branch_potential)
        
        self.local_spike_history.append(1.0 if abs(self.branch_potential) > self.branch_threshold else 0.0)
        
        return self.branch_potential + self.plateau_potential
    
    def get_local_ca_influx(self) -> float:
        return sum(self.local_spike_history) / len(self.local_spike_history) if len(self.local_spike_history) >= 3 else 0.0
    
    def to_dict(self) -> dict:
        # Save individualized parameters
        return {
            'branch_id': self.branch_id, 
            'branch_potential': self.branch_potential, 
            'plateau_potential': self.plateau_potential, 
            'branch_threshold': self.branch_threshold,
            'plateau_decay': self.plateau_decay,
            'local_spike_history': list(self.local_spike_history) # Save spike history v 2.03
        }

class Synapse:
    """
    Implements the Neuraxon synapse with individualized temporal dynamics and weights.
    Time constants and learning rates are now specific to this synapse instance.
    """
    def __init__(self, pre_id: int, post_id: int, params: NetworkParameters):
        self.pre_id = pre_id
        self.post_id = post_id
        self.is_afferent = False
        self.params = params
        
        self.w_fast = random.uniform(params.w_fast_init_min, params.w_fast_init_max)
        self.w_slow = random.uniform(params.w_slow_init_min, params.w_slow_init_max)
        self.w_meta = random.uniform(params.w_meta_init_min, params.w_meta_init_max)
        
        # INDIVIDUALIZED: Synaptic Time Constants & Plasticity Properties
        self.tau_fast = _variate(params.tau_fast)
        self.tau_slow = _variate(params.tau_slow)
        self.tau_meta = _variate(params.tau_meta)
        self.tau_ltp = _variate(params.tau_ltp)
        self.tau_ltd = _variate(params.tau_ltd)
        self.learning_rate = _variate(params.learning_rate)
        self.plasticity_threshold = _variate(params.plasticity_threshold)
        
        self.is_silent = random.random() < 0.1
        self.is_modulatory = random.random() < 0.2
        self.integrity = 1.0
        self.axonal_delay = random.uniform(0, params.max_axonal_delay)
        
        self.pre_trace = 0.0
        self.post_trace = 0.0
        self.pre_trace_ltd = 0.0
        
        self.learning_rate_mod = 1.0
        self.associative_strength = 0.0
        self.neighbor_synapses = []

        # --- Neuraxon v2.0: ChronoPlasticity (Eqs 5-7) ---
        self.chrono_fast_trace = 0.0
        self.chrono_slow_trace = 0.0
        self.chrono_omega = 0.5
        # --- Neuraxon v2.0: AGMP eligibility (Eq 8) ---
        self.eligibility = 0.0
        # --- Neuraxon v2.0: Dendritic branch assignment ---
        self.branch_id = random.randint(0, max(0, getattr(params, 'num_dendritic_branches', 3) - 1))
        self.branch_index = 0
        self.potential_delta_w = 0.0
        self.synapse_type = self._determine_type()
        
        # NEW: Track previous weights for evolution logging
        self._prev_w_fast = self.w_fast
        self._prev_w_slow = self.w_slow
        self._prev_w_meta = self.w_meta
    
    def mark_as_afferent(self):
        """Mark as afferent synapse and strengthen."""
        self.is_afferent = True
        self.w_fast *= self.params.afferent_synapse_strength
        self.w_slow *= self.params.afferent_synapse_strength
        self.is_silent = random.random() > self.params.afferent_synapse_reliability
    
    def _determine_type(self) -> SynapseType:
        if self.is_silent: return SynapseType.SILENT
        if self.is_modulatory: return SynapseType.METABOTROPIC
        return SynapseType.IONOTROPIC_FAST if abs(self.w_fast) >= abs(self.w_slow) else SynapseType.IONOTROPIC_SLOW

    def update_chrono_traces(self, pre_state: int):
        """Neuraxon v2.0: Update fast/slow chrono traces (Algorithm 1, Eqs 5-6)."""
        if not getattr(self.params, 'chrono_enabled', False):
            return
        a_f = getattr(self.params, 'chrono_alpha_f', 0.95)
        a_s = getattr(self.params, 'chrono_alpha_s', 0.99)
        l_f = getattr(self.params, 'chrono_lambda_f', 0.15)
        l_s = getattr(self.params, 'chrono_lambda_s', 0.08)
        raw = max(-50.0, min(50.0, float(pre_state)))
        self.chrono_fast_trace = a_f * self.chrono_fast_trace + (1.0 - a_f) * raw * l_f
        self.chrono_slow_trace = a_s * self.chrono_slow_trace + (1.0 - a_s) * raw * l_s
        clip = getattr(self.params, 'chrono_trace_clip', 6.0)
        self.chrono_fast_trace = max(-clip, min(clip, self.chrono_fast_trace))
        self.chrono_slow_trace = max(-clip, min(clip, self.chrono_slow_trace))

    def update_eligibility(self, pre_state: int, post_state: int, params):
        """Neuraxon v2.0: AGMP eligibility trace (Algorithm 1, Eq 8)."""
        if not getattr(params, 'agmp_enabled', False):
            return
        lam_e = getattr(params, 'agmp_lambda_e', 0.95)
        self.eligibility = lam_e * self.eligibility + (1.0 - lam_e) * (1.0 if (pre_state == 1 and post_state == 1) else 0.0)
        self.eligibility = max(-1.0, min(1.0, self.eligibility))
    
    def compute_input(self, pre_state: int, current_time: float) -> Tuple[float, float]:
        if self.is_silent: return 0.0, 0.0
        # v4.1: Skip computation when pre is neutral (state==0) — common case
        if pre_state == 0: return 0.0, 0.0
        delay_factor = max(0.0, 1.0 - self.axonal_delay / 10.0)
        if self.is_afferent:
            delay_factor = max(0.5, delay_factor)
        # v3.31: CRITICAL FIX — Include w_meta in effective weight
        # v4.1: Cache meta_influence_gain on first access
        try:
            meta_gain = self._cached_meta_gain
        except AttributeError:
            meta_gain = getattr(self.params, 'meta_influence_gain', 0.25)
            self._cached_meta_gain = meta_gain
        w = self.w_fast + self.w_slow + self.w_meta * meta_gain
        signal = w * pre_state
        return signal * delay_factor, signal * (1.0 - delay_factor)
    
    def calculate_delta_w(self, pre_state: int, post_state: int, neuromodulators: Dict[str, float], dt: float) -> float:
        # v4.1: Fast path — when both pre and post are neutral, only decay traces
        if pre_state == 0 and post_state == 0:
            self.pre_trace *= (1.0 - dt / self.tau_ltp)
            self.pre_trace_ltd *= (1.0 - dt / self.tau_ltd)
            self.post_trace *= (1.0 - dt / self.tau_ltp)
            self._pending_delta_w = 0.0
            return 0.0
        # Use localized tau_ltp / tau_ltd
        self.pre_trace += (-self.pre_trace / self.tau_ltp + (1 if pre_state == 1 else 0)) * dt
        self.pre_trace_ltd += (-self.pre_trace_ltd / self.tau_ltd + (1 if pre_state == 1 else 0)) * dt
        self.post_trace += (-self.post_trace / self.tau_ltp + (1 if post_state == 1 else 0)) * dt
        
        da = neuromodulators.get('dopamine', 0.5)
        ach = neuromodulators.get('acetylcholine', 0.5)
        
        da_threshold = self.params.dopamine_low_affinity_threshold
        if da > da_threshold:
            da_high = min(1.0, (da - da_threshold) / da_threshold)
        else:
            da_high = 0.0
        da_low = 1.0 if da > self.params.dopamine_high_affinity_threshold else 0.0
        self._last_da_high = da_high  # v3.31: Store for meta DA-boost in apply_update
        
        # ACh gain: If high, consolidates learning faster (Paper Claim: Consolidate what has been learned)
        ach_gain = 1.0 + (ach if ach > 0.5 else 0.0)
        self.learning_rate_mod = (1.0 + (da_high * 0.5) + (da_low * 0.2)) * ach_gain
        
        ### HOTFIX5: threshold logging restored at log_level >= 3
        _hf5_logger = get_data_logger()
        if _hf5_logger.log_level >= 3:
            if da_high > 0 and pre_state == 1 and post_state == 1:
                _hf5_logger.log_neuromodulator_event(
                    tick=0, modulator='dopamine', level=da,
                    crossed_threshold='low_affinity', effect='ltp_enabled')
            if da_low > 0 and pre_state == 1 and post_state == -1:
                _hf5_logger.log_neuromodulator_event(
                    tick=0, modulator='dopamine', level=da,
                    crossed_threshold='high_affinity', effect='ltd_enabled')

        # Track for weight evolution logging
        self._pending_delta_w = 0.0
        
        if pre_state == 1 and post_state == 1:
            # v3.31: LTP = DA-gated component + Hebbian component (reduced Hebbian from 0.3→0.18)
            # BIOINSPIRED: Basic Hebbian LTP occurs at coincident firing even without
            # explicit reward — DA modulates magnitude, not gating entirely.
            # Results96F showed LTP/LTD ratio of 0.082 — far too low for learning.
            hebbian_frac = getattr(self.params, 'hebbian_ltp_rate', 0.18)
            da_component = self.learning_rate * self.learning_rate_mod * da_high * self.pre_trace
            hebbian_component = self.learning_rate * hebbian_frac * self.pre_trace * self.post_trace
            delta = da_component + hebbian_component
            self._pending_delta_w = delta
            ### HOTFIX5: LTP logging restored at log_level >= 3
            _hf5_l = get_data_logger()
            if delta > 0.0001 and _hf5_l.log_level >= 3:
                _hf5_l.log_plasticity_event(tick=0, event_type='LTP',
                                            pre_id=self.pre_id, post_id=self.post_id,
                                            delta_w=delta)
            return delta
        elif pre_state == 1 and post_state <= 0:
            # v3.31: LTD slightly increased from v3.3 — neutral 0.08→0.12 to counter LTP overcorrection
            # Results96F: 92.4% of all plasticity events were LTD — far too dominant.
            # Root cause: neutral state is ~50% of all states, and was scaled at 0.3 × full LTD.
            # FIX: Neutral scale → 0.08, inhibitory scale → 0.6 (from 1.0/0.3)
            ach_forgetting_mult = 1.5 if ach > 0.6 else 1.0
            
            ltd_neutral = getattr(self.params, 'ltd_neutral_scale', 0.12)
            ltd_inhib = getattr(self.params, 'ltd_inhibitory_scale', 0.6)
            ltd_scale = (ltd_inhib if post_state == -1 else ltd_neutral) * ach_forgetting_mult
            delta = -self.learning_rate * self.learning_rate_mod * da_low * self.pre_trace_ltd * ltd_scale
            self._pending_delta_w = delta
            ### HOTFIX5: LTD logging restored at log_level >= 3
            _hf5_l = get_data_logger()
            if delta < -0.0001 and _hf5_l.log_level >= 3:
                _hf5_l.log_plasticity_event(tick=0, event_type='LTD',
                                            pre_id=self.pre_id, post_id=self.post_id,
                                            delta_w=delta)
            return delta
        self._pending_delta_w = 0.0
        return 0.0
    
    def apply_update(self, dt: float, neuromodulators: Dict[str, float], neighbor_deltas: List[float] = None):
        ### HOTFIX5: old_w tracking restored for log_level >= 3
        _hf5_logger = get_data_logger()
        _hf5_log3 = _hf5_logger.log_level >= 3
        if _hf5_log3:
            old_w_fast = self.w_fast
            old_w_slow = self.w_slow
            old_w_meta = self.w_meta

        delta_w = self.potential_delta_w
        own_delta_w = delta_w  # Store for associativity logging
        neighbor_contribution = 0.0
        ach = neuromodulators.get('acetylcholine', 0.5)
        
        if neighbor_deltas:
            # ACh Modulation: Prioritize neighbors/directions (Paper Claim)
            associativity_gain = 1.0 + (ach * 0.5)
            neighbor_contribution = self.params.associativity_strength * associativity_gain * sum(
                dw / (i + 1) for i, dw in enumerate(neighbor_deltas[:3]))
            delta_w += neighbor_contribution
        
        # v3.31: Differentiate fast vs slow timescale drivers
        # Results96F: w_fast/w_slow correlation = 0.94 — they moved in lockstep
        # FIX: w_fast tracks pre_trace (immediate stimulus), w_slow tracks post_trace (response)
        h_fast = self.pre_trace  # Fast: driven by presynaptic activity
        post_frac = self.params.w_slow_post_trace_fraction if hasattr(self.params, 'w_slow_post_trace_fraction') else 0.85  ### HOTFIX4: cached
        h_slow = (1.0 - post_frac) * self.pre_trace + post_frac * self.post_trace  # Slow: response-driven
        
        # Use localized tau_fast, tau_slow, tau_meta with saturation prevention
        # NEW v2.31: Apply hard ceiling/floor to prevent weight saturation
        max_w = self.params.max_weight_magnitude
        min_w = self.params.min_weight_magnitude
        
        # v3.31: Use configurable delta shares for better differentiation
        fast_share = getattr(self.params, 'w_fast_delta_share', 0.5)
        slow_share = getattr(self.params, 'w_slow_delta_share', 0.02)
        
        new_w_fast = self.w_fast + dt / self.tau_fast * (-self.w_fast + h_fast + delta_w * fast_share)
        self.w_fast = max(min_w, min(max_w, new_w_fast))
        
        new_w_slow = self.w_slow + dt / self.tau_slow * (-self.w_slow + h_slow + delta_w * slow_share)
        self.w_slow = max(min_w, min(max_w, new_w_slow))
        
        # v3.31: Meta weight with DA-gated reward boost
        # BIOINSPIRED: Metabotropic receptor upregulation is reward-modulated.
        # When dopamine is high (reward), meta accumulates faster → synapses that
        # were active during rewarding experiences develop stronger meta weights →
        # those pathways become preferentially weighted for future behavior.
        # This creates the action-meta correlation the Paper describes.
        serotonin = neuromodulators.get('serotonin', 0.5)
        stabilizer = (1.0 if serotonin > 0.5 else 0.5) * (1.2 if ach > 0.6 else 1.0)
        meta_gain = getattr(self.params, 'meta_target_gain', 0.30)
        meta_accum = getattr(self.params, 'meta_accumulation_rate', 0.35)
        meta_clamp = getattr(self.params, 'meta_clamp_max', 1.0)
        meta_da_boost = getattr(self.params, 'meta_da_boost', 2.0)
        
        # DA boost: when dopamine is high, meta accumulates faster
        last_da = getattr(self, '_last_da_high', 0.0)
        da_multiplier = 1.0 + last_da * (meta_da_boost - 1.0)  # Range [1.0, meta_da_boost]
        
        # Meta target: accumulated slow patterns + instantaneous learning signal, boosted by reward
        meta_target = (delta_w * meta_gain + self.w_slow * meta_accum) * stabilizer * da_multiplier
        
        # v3.31: Reduced decay term — multiply decay by 0.7 to let meta accumulate more
        # The equation dw/dt = (1/tau) * (-w + target) decays w toward target.
        # If target is episodic (nonzero only during learning), w decays to 0 between episodes.
        # Reducing the decay coefficient lets meta retain accumulated value longer.
        decay_coeff = 0.7  # < 1.0 means slower decay toward zero between learning episodes
        new_w_meta = self.w_meta + dt / self.tau_meta * (-self.w_meta * decay_coeff + meta_target)
        self.w_meta = max(-meta_clamp, min(meta_clamp, new_w_meta))
        
        activity = abs(self.w_fast) + abs(self.w_slow)
        self.integrity = min(1.0, self.integrity + 0.001 * dt * activity) if activity >= 0.01 else self.integrity - self.params.synapse_death_prob * dt

        ### HOTFIX5: weight evolution + associativity logging restored at log_level >= 3
        if _hf5_log3:
            total_change = (abs(self.w_fast - old_w_fast) +
                           abs(self.w_slow - old_w_slow) +
                           abs(self.w_meta - old_w_meta))
            if total_change > 0.01:
                _hf5_logger.log_weight_evolution_event(
                    tick=0, synapse_pre_id=self.pre_id, synapse_post_id=self.post_id,
                    w_fast_old=old_w_fast, w_fast_new=self.w_fast,
                    w_slow_old=old_w_slow, w_slow_new=self.w_slow,
                    w_meta_old=old_w_meta, w_meta_new=self.w_meta)
            if abs(neighbor_contribution) > 0.001:
                _hf5_logger.log_associativity_event(
                    tick=0, synapse_pre_id=self.pre_id, synapse_post_id=self.post_id,
                    own_delta_w=own_delta_w, neighbor_contribution=neighbor_contribution,
                    final_delta_w=delta_w)

        # Track previous silent state
        was_silent = self.is_silent

        if self.is_silent and self.pre_trace > 0.5 and random.random() < 0.01:  # silent → active
            self.is_silent = False
            ### HOTFIX5: silent synapse active logging restored at log_level >= 3
            _hf5_l = get_data_logger()
            if _hf5_l.log_level >= 3:
                _hf5_l.log_silent_synapse_event(
                    tick=0, pre_id=self.pre_id, post_id=self.post_id,
                    became_active=True, trigger="pre_trace_threshold")

        # v3.32 FIX: Active → silent transition.
        # BIOINSPIRED: Synapses with prolonged inactivity undergo functional silencing
        # (AMPA receptor internalization). Mirrors LTD-driven silent synapse formation
        # observed in hippocampal circuits (Paper Section 5 — complex signaling).
        if not self.is_silent and not was_silent:
            activity = abs(self.w_fast) + abs(self.w_slow)
            if activity < SYNAPSE_SILENCING_ACTIVITY_THRESHOLD and self.integrity < 0.3 and random.random() < 0.008:
                self.is_silent = True
                ### HOTFIX5: silent synapse inactive logging restored at log_level >= 3
                _hf5_l = get_data_logger()
                if _hf5_l.log_level >= 3:
                    _hf5_l.log_silent_synapse_event(
                        tick=0, pre_id=self.pre_id, post_id=self.post_id,
                        became_active=False, trigger="inactivity_silencing")

        if _hf5_log3: self.synapse_type = self._determine_type()  ### HOTFIX5: restore at level 3
    
    def get_modulatory_effect(self) -> float:
        return self.w_meta * 0.5 if self.is_modulatory else 0.0
    
    def to_dict(self) -> dict:
        self.synapse_type = self._determine_type()  # HOTFIX4: refresh only when serializing
        return {
            'pre_id': self.pre_id, 'post_id': self.post_id, 
            'w_fast': self.w_fast, 'w_slow': self.w_slow, 'w_meta': self.w_meta, 
            'is_silent': self.is_silent, 'is_modulatory': self.is_modulatory, 
            'integrity': self.integrity, 'axonal_delay': self.axonal_delay, 
            'learning_rate_mod': self.learning_rate_mod, 'synapse_type': self.synapse_type.value, 
            'potential_delta_w': self.potential_delta_w,            
            'tau_fast': self.tau_fast, 'tau_slow': self.tau_slow, 'tau_meta': self.tau_meta,
            'tau_ltp': self.tau_ltp, 'tau_ltd': self.tau_ltd,
            'learning_rate': self.learning_rate, 'plasticity_threshold': self.plasticity_threshold,
            'pre_trace': self.pre_trace,# Updated Save states in v 2.03
        'post_trace': self.post_trace,# Updated Save states in v 2.03
        'pre_trace_ltd': self.pre_trace_ltd,# Updated Save # Updated Save states in v 2.1
        'associative_strength': self.associative_strength, # Updated Save states in v 2.1
         # NEW: Save neighbor synapse references as (pre_id, post_id) tuples
        'neighbor_synapse_ids': [(ns.pre_id, ns.post_id) for ns in self.neighbor_synapses], # Updated Save states in v 2.1
        }

class ITUCircle:
    """
    Implements an Intelligent Tissue Unit (ITU) circle, a concept from the Aigarth hybridization (Section 8 of the Neuraxon paper).
    This class manages a group of neurons that are subject to evolutionary pressures. It calculates
    a collective fitness score and applies mutation and selection (pruning) to its member neurons.
    """
    def __init__(self, circle_id: int, neurons: list, params: NetworkParameters):
        self.circle_id = circle_id
        self.neurons = neurons
        self.params = params
        self.fitness_history = []
        self.mutation_rate = 0.01
        for n in neurons: n.circle_id = circle_id
    
    def compute_fitness(self, network_activity: List[float], temporal_sync: float, energy_efficiency: float) -> float:
        """Calculates the fitness of this ITU based on its performance on multiple objectives."""
        fitness = self.params.fitness_pattern_weight * (np.mean(network_activity) if network_activity else 0.0) + self.params.fitness_temporal_weight * temporal_sync + self.params.fitness_energy_weight * energy_efficiency
        self.fitness_history.append(fitness)
        return fitness
    
    def mutate(self):
        """Applies small, random changes (mutations) to the parameters of the neurons in the circle."""
        for neuron in self.neurons:
            if random.random() < self.mutation_rate:
                # Mutating intrinsic properties allows the evolution of different dynamic behaviors.
                neuron.natural_frequency = max(0.1, min(5.0, neuron.natural_frequency + random.uniform(-0.2, 0.2)))
                neuron.intrinsic_timescale *= random.uniform(0.9, 1.1)
                if hasattr(neuron.params, 'firing_threshold_excitatory'):
                    neuron.params.firing_threshold_excitatory *= random.uniform(0.95, 1.05)
                
                # NEW: Log mutation event
                logger = get_data_logger()
                if logger.log_level >= 2:
                    logger.log_itu_evolution_event(
                        0, self.circle_id, 'mutation',
                        self.fitness_history[-1] if self.fitness_history else 0.0,
                        self.fitness_history[-1] if self.fitness_history else 0.0,
                        1
                    )
    
    def prune_unfit_neurons(self) -> List[int]:
        """
        Implements selection by "pruning" (deactivating) neurons whose fitness is consistently low
        compared to the circle's average. This is a form of structural optimization.
        """
        pruned_ids = []
        avg_fitness = np.mean(self.fitness_history[-10:]) if len(self.fitness_history) > 10 else 0.5
        for neuron in self.neurons:
            if neuron.fitness_score < avg_fitness * 0.3 and random.random() < 0.001:
                neuron.is_active = False
                pruned_ids.append(neuron.id)
        
        # NEW: Log pruning events
        if pruned_ids:
            logger = get_data_logger()
            if logger.log_level >= 2:
                logger.log_itu_evolution_event(
                    0, self.circle_id, 'pruning',
                    avg_fitness, avg_fitness,
                    len(pruned_ids)
                )
        
        return pruned_ids


# =============================================================================
# MSTH: Multi-Scale Temporal Homeostasis (Neuraxon v2.0 Section 5)
# =============================================================================

class MSTHState:
    """
    Four coordinated regulatory loops (Neuraxon v2.0):
      Ultra-fast (~5ms): emergency suppression / runaway prevention
      Fast (~2s): rapid Ca2+/homeostatic control of excitability
      Medium (~5min): synaptic scaling / gain normalisation
      Slow (~1-24h): structural adjustments and long-horizon stability
    """
    def __init__(self, params):
        self.params = params
        self.ultrafast_activity = 0.0
        self.fast_excitability = 0.0
        self.medium_gain = 1.0
        self.slow_structural = 0.0

    def update(self, current_state_abs: float, dt: float) -> dict:
        p = self.params
        uf_tau = getattr(p, 'msth_ultrafast_tau', 5.0)
        f_tau = getattr(p, 'msth_fast_tau', 2000.0)
        m_tau = getattr(p, 'msth_medium_tau', 300000.0)
        s_tau = getattr(p, 'msth_slow_tau', 3600000.0)
        target = getattr(p, 'target_firing_rate', 0.2)

        alpha_uf = dt / uf_tau
        self.ultrafast_activity = (1.0 - alpha_uf) * self.ultrafast_activity + alpha_uf * current_state_abs
        ultrafast_suppress = self.ultrafast_activity > getattr(p, 'msth_ultrafast_ceiling', 2.0)

        alpha_f = dt / f_tau
        self.fast_excitability = (1.0 - alpha_f) * self.fast_excitability + alpha_f * current_state_abs
        fast_threshold_shift = getattr(p, 'msth_fast_gain', 0.1) * (self.fast_excitability - target)

        alpha_m = dt / m_tau
        target_dev = current_state_abs - target
        self.medium_gain += alpha_m * (-getattr(p, 'msth_medium_gain', 0.001) * target_dev * self.medium_gain)
        self.medium_gain = max(0.5, min(2.0, self.medium_gain))

        alpha_s = dt / s_tau
        self.slow_structural = (1.0 - alpha_s) * self.slow_structural + alpha_s * abs(target_dev)

        return {
            'ultrafast_suppress': ultrafast_suppress,
            'fast_threshold_shift': fast_threshold_shift,
            'medium_gain': self.medium_gain,
            'slow_structural_pressure': self.slow_structural,
        }

    def to_dict(self) -> dict:
        return {
            'ultrafast_activity': self.ultrafast_activity,
            'fast_excitability': self.fast_excitability,
            'medium_gain': self.medium_gain,
            'slow_structural': self.slow_structural,
        }


# =============================================================================
# RECEPTOR SUBTYPE (Neuraxon v2.0 Algorithm 2)
# =============================================================================

class ReceptorSubtype:
    """Nonlinear receptor activation with Hill-like sigmoid."""
    def __init__(self, name: str, parent_modulator: str,
                 threshold: float, gain: float, is_tonic: bool, slope: float = 0.0):
        self.name = name
        self.parent_modulator = parent_modulator
        self.threshold = threshold
        self.gain = gain
        self.is_tonic = is_tonic
        self.slope = float(slope)
        self.activation = 0.0

    def compute_activation(self, concentration: float) -> float:
        k = self.slope if self.slope > 0.0 else (20.0 if self.is_tonic else 10.0)
        exponent = -k * (concentration - self.threshold)
        exponent = max(-50.0, min(50.0, exponent))
        self.activation = self.gain / (1.0 + math.exp(exponent))
        return self.activation

    def to_dict(self) -> dict:
        return {
            'name': self.name, 'parent_modulator': self.parent_modulator,
            'threshold': self.threshold, 'gain': self.gain, 'slope': self.slope,
            'is_tonic': self.is_tonic, 'activation': self.activation,
        }


# =============================================================================
# OSCILLATOR BANK (Neuraxon v2.0 Algorithm 2 - Multi-band PAC)
# =============================================================================

class OscillatorBank:
    """Multi-band oscillator (infraslow-gamma) with Phase-Amplitude Coupling."""
    DEFAULT_BANDS = {
        'infraslow': 0.05, 'slow': 0.5, 'theta': 6.0,
        'alpha': 10.0, 'gamma': 40.0,
    }

    def __init__(self, coupling: float = 0.15, bands=None):
        self.coupling = coupling
        self.bands = {}
        for name, freq in (bands or self.DEFAULT_BANDS).items():
            self.bands[name] = {
                'freq': freq,
                'phase': random.uniform(0.0, 2.0 * math.pi),
                'amplitude': 1.0,
            }

    def update(self, dt: float):
        for b in self.bands.values():
            b['phase'] = (b['phase'] + 2.0 * math.pi * b['freq'] * dt / 1000.0) % (2.0 * math.pi)

    def get_drive(self, neuron_id: int, total_neurons: int) -> float:
        phi = 2.0 * math.pi * neuron_id / max(total_neurons, 1)
        theta_phase = self.bands['theta']['phase']
        gamma_phase = self.bands['gamma']['phase']
        slow_phase = self.bands['slow']['phase']
        infra_phase = self.bands['infraslow']['phase']
        gate_theta = max(0.0, math.cos(theta_phase + phi))
        gamma_sig = self.bands['gamma']['amplitude'] * gate_theta * math.sin(gamma_phase + 2.0 * phi)
        slow_sig = self.bands['slow']['amplitude'] * math.sin(slow_phase + 0.3 * phi)
        infra_sig = self.bands['infraslow']['amplitude'] * math.sin(infra_phase)
        return self.coupling * (gamma_sig + 0.5 * slow_sig + 0.3 * infra_sig)

    def to_dict(self) -> dict:
        return {'coupling': self.coupling, 'bands': self.bands}


# =============================================================================
# NEUROMODULATOR SYSTEM (Neuraxon v2.0 Algorithm 5)
# =============================================================================

class NeuromodulatorSystem:
    """4 neuromodulators with tonic/phasic, 9 receptor subtypes, crosstalk."""
    def __init__(self, params):
        self.params = params
        self.levels = {
            'DA':  {'tonic': getattr(params, 'dopamine_baseline', 0.15),       'phasic': 0.0},
            '5HT': {'tonic': getattr(params, 'serotonin_baseline', 0.12),      'phasic': 0.0},
            'ACh': {'tonic': getattr(params, 'acetylcholine_baseline', 0.12),   'phasic': 0.0},
            'NA':  {'tonic': getattr(params, 'norepinephrine_baseline', 0.12),  'phasic': 0.0},
        }
        st = float(getattr(params, 'receptor_slope_tonic', 4.0))
        sp = float(getattr(params, 'receptor_slope_phasic', 3.0))
        self.receptors = {
            'D1':     ReceptorSubtype('D1',     'DA',  0.35, 1.0, False, sp),
            'D2':     ReceptorSubtype('D2',     'DA',  0.25, 1.0, True,  st),
            '5HT1A':  ReceptorSubtype('5HT1A',  '5HT', 0.05, 1.0, True,  st),
            '5HT2A':  ReceptorSubtype('5HT2A',  '5HT', 0.30, 1.0, False, sp),
            '5HT4':   ReceptorSubtype('5HT4',   '5HT', 0.20, 1.0, False, sp),
            'M1':     ReceptorSubtype('M1',     'ACh', 0.30, 1.0, False, sp),
            'M2':     ReceptorSubtype('M2',     'ACh', 0.10, 1.0, True,  st),
            'beta1':  ReceptorSubtype('beta1',  'NA',  0.20, 1.0, False, sp),
            'alpha2': ReceptorSubtype('alpha2', 'NA',  0.08, 1.0, True,  st),
        }

    def get_flat_levels(self) -> dict:
        return {
            'dopamine':       self.levels['DA']['tonic']  + self.levels['DA']['phasic'],
            'serotonin':      self.levels['5HT']['tonic'] + self.levels['5HT']['phasic'],
            'acetylcholine':  self.levels['ACh']['tonic'] + self.levels['ACh']['phasic'],
            'norepinephrine': self.levels['NA']['tonic']  + self.levels['NA']['phasic'],
        }

    def set_level(self, name: str, value: float):
        mapping = {'dopamine': 'DA', 'serotonin': '5HT',
                   'acetylcholine': 'ACh', 'norepinephrine': 'NA'}
        key = mapping.get(name, name)
        if key in self.levels:
            self.levels[key]['tonic'] = max(0.0, min(1.0, value))

    def update(self, network_activity: dict, dt: float):
        p = self.params
        mean_act = network_activity.get('mean_activity', 0.0)
        exc_frac = network_activity.get('excitatory_fraction', 0.0)
        change_rate = network_activity.get('state_change_rate', 0.0)
        tau_ton = getattr(p, 'tau_tonic', 5000.0)
        tau_pha = getattr(p, 'tau_phasic', 200.0)
        rr = getattr(p, 'neuromod_release_rate', 0.02)

        for key, bl_attr in [('DA', 'dopamine_baseline'), ('5HT', 'serotonin_baseline'),
                             ('ACh', 'acetylcholine_baseline'), ('NA', 'norepinephrine_baseline')]:
            baseline = getattr(p, bl_attr, 0.12)
            self.levels[key]['tonic'] += dt / tau_ton * (baseline - self.levels[key]['tonic'])
            self.levels[key]['phasic'] += dt / tau_pha * (0.0 - self.levels[key]['phasic'])

        self.levels['DA']['phasic']  += rr * change_rate * dt
        self.levels['5HT']['tonic'] += rr * mean_act * dt
        self.levels['ACh']['phasic'] += rr * exc_frac * dt
        self.levels['NA']['phasic']  += rr * change_rate * dt

        # Crosstalk (Algorithm 5)
        self.levels['ACh']['phasic'] *= max(0.0, 1.0 - 0.1 * self.levels['DA']['phasic'])
        self.levels['5HT']['tonic'] += 0.02 * (self.levels['NA']['tonic'] + self.levels['NA']['phasic']) * dt

        for key in self.levels:
            for comp in ('tonic', 'phasic'):
                self.levels[key][comp] = max(0.0, min(2.0, self.levels[key][comp]))

    def compute_receptor_activations(self) -> dict:
        activations = {}
        cap = float(getattr(self.params, 'receptor_concentration_cap', 1.0))
        for rname, receptor in self.receptors.items():
            parent = receptor.parent_modulator
            conc = self.levels[parent]['tonic'] if receptor.is_tonic else (
                self.levels[parent]['tonic'] + self.levels[parent]['phasic'])
            if cap > 0.0:
                conc = max(0.0, min(cap, float(conc)))
            else:
                conc = max(0.0, float(conc))
            activations[rname] = receptor.compute_activation(conc)
        return activations

    def to_dict(self) -> dict:
        return {'levels': self.levels, 'receptors': {k: v.to_dict() for k, v in self.receptors.items()}}
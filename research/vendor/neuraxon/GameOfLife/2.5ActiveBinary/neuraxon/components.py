# Neuraxon Game of Life Neuron Components
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
from config import NetworkParameters
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
    
    def compute_input(self, pre_state: int, current_time: float) -> Tuple[float, float]:
        if self.is_silent: return 0.0, 0.0
        delay_factor = max(0.0, 1.0 - self.axonal_delay / 10.0)
        if self.is_afferent:
            delay_factor = max(0.5, delay_factor)
        w = self.w_fast + self.w_slow
        return w * pre_state * delay_factor, w * pre_state * (1.0 - delay_factor)
    
    def calculate_delta_w(self, pre_state: int, post_state: int, neuromodulators: Dict[str, float], dt: float) -> float:
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
        
        # ACh gain: If high, consolidates learning faster (Paper Claim: Consolidate what has been learned)
        ach_gain = 1.0 + (ach if ach > 0.5 else 0.0)
        self.learning_rate_mod = (1.0 + (da_high * 0.5) + (da_low * 0.2)) * ach_gain
        
        # NEW: Log threshold crossings
        logger = get_data_logger()
        if logger.log_level >= 2:
            if da_high > 0 and pre_state == 1 and post_state == 1:
                logger.log_neuromodulator_event(
                    tick=0,
                    modulator='dopamine',
                    level=da,
                    crossed_threshold='low_affinity',
                    effect='ltp_enabled'
                )
            if da_low > 0 and pre_state == 1 and post_state == -1:
                logger.log_neuromodulator_event(
                    tick=0,
                    modulator='dopamine', 
                    level=da,
                    crossed_threshold='high_affinity',
                    effect='ltd_enabled'
                )
        
        # Track for weight evolution logging
        self._pending_delta_w = 0.0
        
        if pre_state == post_state:
            # LTP occurs when both neurons fire the same signal (correlated)
            delta = self.learning_rate * self.learning_rate_mod * da_high * self.pre_trace
            self._pending_delta_w = delta
            # FIX v2.2505: Log LTP event when delta is significant
            if delta > 0.0001 and logger.log_level >= 2:
                logger.log_plasticity_event(tick=0, event_type='LTP', 
                                            pre_id=self.pre_id, post_id=self.post_id,
                                            delta_w=delta)
            return delta
        elif pre_state != post_state:
            # LTD occurs when signals are anti-correlated (opposite signs)
            ltd_scale = 1.0  # Full strength for anti-correlated firing
            delta = -self.learning_rate * self.learning_rate_mod * da_low * self.pre_trace_ltd * ltd_scale
            self._pending_delta_w = delta
            # FIX v2.2505: Log LTD event when delta is significant
            if delta < -0.0001 and logger.log_level >= 2:
                logger.log_plasticity_event(tick=0, event_type='LTD',
                                            pre_id=self.pre_id, post_id=self.post_id,
                                            delta_w=delta)
            return delta
        self._pending_delta_w = 0.0
        return 0.0
    
    def apply_update(self, dt: float, neuromodulators: Dict[str, float], neighbor_deltas: List[float] = None):
        # Store old weights for evolution logging
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
        
        h_fast = self.pre_trace
        h_slow = 0.5 * self.pre_trace + 0.5 * self.post_trace
        
        # Use localized tau_fast, tau_slow, tau_meta with saturation prevention
        # NEW v2.31: Apply hard ceiling/floor to prevent weight saturation
        max_w = self.params.max_weight_magnitude
        min_w = self.params.min_weight_magnitude
        
        new_w_fast = self.w_fast + dt / self.tau_fast * (-self.w_fast + h_fast + delta_w * 0.3)
        self.w_fast = max(min_w, min(max_w, new_w_fast))
        
        new_w_slow = self.w_slow + dt / self.tau_slow * (-self.w_slow + h_slow + delta_w * 0.1)
        self.w_slow = max(min_w, min(max_w, new_w_slow))
        
        serotonin = neuromodulators.get('serotonin', 0.5)
        # ACh Modulation: Collaborate in stabilizing what dopamine has done (Paper Claim)
        # Acts alongside Serotonin to lock in changes to the metabotropic weight
        stabilizer = (1.0 if serotonin > 0.5 else 0.5) * (1.2 if ach > 0.6 else 1.0)
        meta_target = delta_w * 0.05 * stabilizer
        new_w_meta = self.w_meta + dt / self.tau_meta * (-self.w_meta + meta_target)
        self.w_meta = max(-0.5, min(0.5, new_w_meta))
        
        activity = abs(self.w_fast) + abs(self.w_slow)
        self.integrity = min(1.0, self.integrity + 0.001 * dt * activity) if activity >= 0.01 else self.integrity - self.params.synapse_death_prob * dt

        # NEW: Log weight evolution if significant change
        logger = get_data_logger()
        if logger.log_level >= 2:
            total_change = (abs(self.w_fast - old_w_fast) + 
                           abs(self.w_slow - old_w_slow) + 
                           abs(self.w_meta - old_w_meta))
            if total_change > 0.01:  # Threshold for logging
                logger.log_weight_evolution_event(
                    tick=0,  # Will be set by network
                    synapse_pre_id=self.pre_id,
                    synapse_post_id=self.post_id,
                    w_fast_old=old_w_fast, w_fast_new=self.w_fast,
                    w_slow_old=old_w_slow, w_slow_new=self.w_slow,
                    w_meta_old=old_w_meta, w_meta_new=self.w_meta
                )
            
            # Log associativity if neighbor contribution was significant
            if abs(neighbor_contribution) > 0.001:
                logger.log_associativity_event(
                    tick=0,
                    synapse_pre_id=self.pre_id,
                    synapse_post_id=self.post_id,
                    own_delta_w=own_delta_w,
                    neighbor_contribution=neighbor_contribution,
                    final_delta_w=delta_w
                )

        # Track previous silent state
        was_silent = self.is_silent

        if self.is_silent and self.pre_trace > 0.5 and random.random() < 0.01:
            self.is_silent = False
            # NEW: Log the event
            logger = get_data_logger()
            if logger.log_level >= 2:
                logger.log_silent_synapse_event(
                    tick=0,  # Will need to pass tick from network
                    pre_id=self.pre_id,
                    post_id=self.post_id,
                    became_active=True,
                    trigger="pre_trace_threshold"
                )

        self.synapse_type = self._determine_type()
    
    def get_modulatory_effect(self) -> float:
        return self.w_meta * 0.5 if self.is_modulatory else 0.0
    
    def to_dict(self) -> dict:        
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
                if hasattr(neuron.params, 'firing_threshold'):
                    neuron.params.firing_threshold *= random.uniform(0.95, 1.05)
                
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
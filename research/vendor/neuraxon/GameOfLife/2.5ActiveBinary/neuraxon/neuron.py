# Neuraxon Game of Life Neuron
# Based on the Paper "Neuraxon: A New Neural Growth & Computation Blueprint" by David Vivancos https://vivancos.com/  & Dr. Jose Sanchez  https://josesanchezgarcia.com/ for Qubic Science https://qubic.org/
# https://www.researchgate.net/publication/397331336_Neuraxon
# Play the Lite Version of the Game of Life at https://huggingface.co/spaces/DavidVivancos/NeuraxonLife
import math
import random
import numpy as np
from collections import deque
from typing import List, Dict, Tuple

# Import local modules
from config import NetworkParameters
from utils import _variate
from logger import get_data_logger
from .enums import NeuronType, BinaryState
from .components import DendriticBranch

class Neuraxon:
    """
    The core computational unit of the model.
    Now fully individualized: Membrane properties, thresholds, adaptation rates,
    and metabolic costs are random variations of the NetworkParameters.
    """
    def __init__(self, neuron_id: int, neuron_type: NeuronType, params: NetworkParameters):
        self.id = neuron_id
        self.type = neuron_type
        self.params = params
        
        # --- Core Neuron Properties (Individualized) ---
        self.membrane_time_constant = _variate(params.membrane_time_constant)
        self.firing_threshold = _variate(params.firing_threshold)
        self.adaptation_rate = _variate(params.adaptation_rate)
        self.spontaneous_firing_rate = _variate(params.spontaneous_firing_rate)
        self.neuron_health_decay = _variate(params.neuron_health_decay)
        
        # --- Energy Metabolism (Individualized) ---
        self.energy_baseline = _variate(params.energy_baseline)
        self.firing_energy_cost = _variate(params.firing_energy_cost)
        self.plasticity_energy_cost = _variate(params.plasticity_energy_cost)
        self.metabolic_rate = _variate(params.metabolic_rate)
        self.recovery_rate = _variate(params.recovery_rate)

        # Core state variables
        # Start neurons closer to resting potential (zero)
        self.membrane_potential = random.uniform(
            0.0,
            self.firing_threshold * 0.35
        )

        self.binary_state = BinaryState.INHIBITORY.value
        self.adaptation = 0.0
        self.autoreceptor = 0.0
        self.health = 1.0
        self.is_active = True
        
        self.dendritic_branches = [DendriticBranch(i, neuron_id, params) for i in range(params.num_dendritic_branches)]
        self.energy_level = self.energy_baseline # Start with individualized baseline
        
        self.last_firing_time = -1000.0
        # v2.39: Phase clustering for synchronization
        phase_cluster_prob = getattr(params, 'phase_clustering_init', 0.65)
        if random.random() < phase_cluster_prob:
            num_clusters = 3 + (neuron_id % 4)
            cluster_center = (neuron_id % num_clusters) * (2 * math.pi / num_clusters)
            self.phase = (cluster_center + random.gauss(0, 0.4)) % (2 * math.pi)
        else:
            self.phase = random.random() * 2 * math.pi
        freq_min = getattr(params, 'natural_freq_range_min', 0.7)
        freq_max = getattr(params, 'natural_freq_range_max', 1.4)
        self.natural_frequency = random.uniform(freq_min, freq_max)
        self._prev_phase_change = 0.0
        self.state_history = deque(maxlen=50)
        self.intrinsic_timescale = self.membrane_time_constant # Use individualized constant
        
        self.circle_id = None
        self.fitness_score = 0.0
        
        # NEW: Track for subthreshold logging
        self._prev_membrane_potential = 0.0
    
    def _nonlinear_dendritic_integration(self, synaptic_inputs: List[float], modulatory_inputs: List[float], dt: float) -> Tuple[float, List[float]]:
        branch_outputs = []
        total_synaptic = 0.0
        for i, branch in enumerate(self.dendritic_branches):
            branch_syn_inputs = synaptic_inputs[i::len(self.dendritic_branches)]
            branch_out = branch.integrate_inputs(branch_syn_inputs, dt)
            branch_outputs.append(branch_out)
            total_synaptic += branch_out
        return total_synaptic * (1.0 + sum(modulatory_inputs) * 0.2), branch_outputs
    
    #v2.40 update
    def _update_phase_oscillator(self, dt: float, global_osc: float, neighbor_phases: dict = None):
        # Natural frequency evolution
        d_phase = 2 * math.pi * self.natural_frequency * dt
        
        # Global coupling (WEAK - just sets rhythm)
        global_coupling = self.params.phase_coupling_strength * math.sin(global_osc - self.phase) * dt
        
        # Local Kuramoto coupling (STRONG - drives synchronization)
        local_coupling = 0.0
        if neighbor_phases and len(neighbor_phases) > 0:
            total_weight = 0.0
            weighted_sin_sum = 0.0
            for neighbor_id, (neighbor_phase, weight) in neighbor_phases.items():
                phase_diff = neighbor_phase - self.phase
                weighted_sin_sum += weight * math.sin(phase_diff)
                total_weight += weight
            if total_weight > 0.01:
                local_coupling = (self.params.phase_coupling_local_strength * 
                                weighted_sin_sum / total_weight * dt)
        
        # Update with momentum
        total_change = d_phase + global_coupling + local_coupling
        smoothed_change = (self.params.phase_coupling_momentum * self._prev_phase_change + 
                        (1 - self.params.phase_coupling_momentum) * total_change)
        self._prev_phase_change = smoothed_change
        self.phase = (self.phase + smoothed_change) % (2 * math.pi)
    
    def _update_energy(self, activity: float, plasticity_cost: float, dt: float):
        if not self.is_active: return
        # Use individualized metabolic parameters
        consumption = self.metabolic_rate * (self.firing_energy_cost * activity + self.plasticity_energy_cost * plasticity_cost) * dt
        
        # NEW v2.30: Energy-aware recovery boost for metabolically stressed neurons
        # BIOINSPIRED: Neurons in metabolic crisis prioritize ATP regeneration
        # This mimics increased mitochondrial activity under low-ATP conditions
        base_recovery = self.recovery_rate * (1.0 - activity) * dt
        
        if self.energy_level < self.params.critical_energy_level:
            # Boost recovery when energy is critically low
            # Scale boost by how far below critical threshold we are
            energy_deficit_ratio = 1.0 - (self.energy_level / self.params.critical_energy_level)
            recovery_multiplier = 1.0 + (self.params.energy_recovery_boost - 1.0) * energy_deficit_ratio
            recovery = base_recovery * recovery_multiplier
        else:
            recovery = base_recovery
        
        self.energy_level = max(0.0, min(self.energy_baseline * 1.5, self.energy_level + recovery - consumption))
        
        if self.energy_level < 10.0:
            self.health -= self.neuron_health_decay * dt * 2.0
            self.membrane_potential *= 0.9
    
    def _update_intrinsic_timescale(self, dt: float):
        """Update intrinsic timescale based on autocorrelation."""
        # This method is called early in update() to prepare for timescale updates
        # The actual autocorrelation-based update happens in _update_autocorrelation()
        # after state_history is updated
        pass
    
    def _update_autocorrelation(self):
        if len(self.state_history) >= 10:
            states = list(self.state_history)
            # Check if data has variance (avoid zero std)
            states_a = states[:-1]
            states_b = states[1:]
            if np.std(states_a) < 1e-10 or np.std(states_b) < 1e-10:
                return
            try:
                autocorr = np.corrcoef(states_a, states_b)[0, 1]
                if not np.isnan(autocorr):
                    # ACW estimate: timescale weighted by autocorrelation strength
                    # Higher autocorr = longer memory window
                    acw = self.intrinsic_timescale * (1.0 + abs(autocorr))
                    self.intrinsic_timescale = acw
                    # Cap after autocorrelation update
                    self.intrinsic_timescale = min(self.intrinsic_timescale, self.params.max_intrinsic_timescale)
            except:
                pass
    
    def update(self, synaptic_inputs: List[float], modulatory_inputs: List[float], external_input: float, neuromodulators: Dict[str, float], dt: float, global_osc: float, neighbor_phases: List[float] = None):
        """v2.39: Added neighbor_phases for Kuramoto coupling."""
        if not self.is_active or self.energy_level <= 0: return

        phase_coupling_strength = self.params.phase_coupling_strength
        
        self._update_intrinsic_timescale(dt)
        
        # CRITICAL FIX: Cap intrinsic timescale AFTER update, not before
        # This ensures the cap is always enforced regardless of ACW calculation
        self.intrinsic_timescale = min(self.intrinsic_timescale, self.params.max_intrinsic_timescale)
        
        # v2.39: Use Kuramoto coupling method
        self._update_phase_oscillator(dt, global_osc, neighbor_phases)
        
        total_synaptic, branch_outputs = self._nonlinear_dendritic_integration(synaptic_inputs, modulatory_inputs, dt)
        
        acetylcholine = neuromodulators.get('acetylcholine', 0.5)
        norepi = neuromodulators.get('norepinephrine', 0.5)
        
        # ACh Modulation: Maintain persistence of state despite environmental fluctuations (Paper Claim)
        # High ACh suppresses noise (spontaneous firing), focusing the neuron on inputs/memory
        noise_suppression = 0.4 if acetylcholine > 0.6 else 1.0
        
        # Calculate total input strength for classification and gating
        total_input_strength = abs(total_synaptic) + abs(external_input)
        has_strong_input = total_input_strength > self.params.sensory_gating_threshold
        
        # Spontaneous probability with sensory gating
        base_spont_prob = self.spontaneous_firing_rate * dt * (1.0 + math.cos(self.phase) * 0.3) * noise_suppression
        if self.params.sensory_gating_enabled and has_strong_input:
            spont_prob = base_spont_prob * self.params.sensory_gating_suppression
        else:
            spont_prob = base_spont_prob
        
        is_spontaneous_firing = False
        spontaneous = 0.0

        if random.random() < spont_prob:
            is_spontaneous_firing = True
            if self.params.spontaneous_as_current:
                # v2.92: Balanced spontaneous current - 60% inhibitory, 40% excitatory
                # BIOINSPIRED: Cortical spontaneous activity explores full state space
                # Paper claim: trinary states capture "excitatory, neutral, and inhibitory dynamics"
                spontaneous = random.choice([-1.0]*6 + [1.0]*4) * self.params.spontaneous_current_magnitude
            else:
                # Legacy: force threshold
                if random.random() < 0.5:
                    self.membrane_potential = self.firing_threshold + 0.01
                else:
                    spontaneous = random.choice([-1.0, 1.0]) * 2.0
                
        threshold_mod = (acetylcholine - 0.5) * 0.5 + sum(modulatory_inputs) * 0.3
        gain = 1.0 + (norepi - 0.5) * 0.4
        
        membrane_bias = getattr(self.params, 'membrane_bias', 0.0)
        
        drive = (total_synaptic + external_input + spontaneous + membrane_bias) * gain
        
        tau_eff = max(1.0, self.intrinsic_timescale)
        prev_state = self.binary_state
        
        # Membrane decay
        if hasattr(self.params, 'resting_potential_decay'):
            resting_decay = self.params.resting_potential_decay * dt
            self.membrane_potential *= (1.0 - resting_decay)
        
        # Store previous potential for subthreshold logging
        prev_potential = self.membrane_potential
        
        # Use individualized adaptation_rate indirectly via adaptation variable dynamics
        self.membrane_potential += dt / tau_eff * (drive - self.membrane_potential - self.adaptation)
        
        # Adaptation dynamics
        adaptation_target = 0.25 * self.binary_state + 0.08 * self.binary_state
        self.adaptation += dt / 40.0 * (-self.adaptation + adaptation_target)
        
        # Autoreceptor tracks activity level
        activity_for_autoreceptor = self.binary_state
        self.autoreceptor += dt / 150.0 * (-self.autoreceptor + 0.35 * activity_for_autoreceptor)
        
        # Energy-Aware Firing Threshold
        
        # Calculate energy factor: 1.0 when energy is high, <1.0 when depleted
        energy_ratio = self.energy_level / (self.energy_baseline * self.params.energy_threshold_floor)
        energy_factor = min(1.0, max(0.3, energy_ratio))  # Clamp between 0.3 and 1.0
        
        # Energy-dependent threshold scaling: low energy raises effective threshold
        threshold_energy_mod = (1.0 - energy_factor) * self.params.energy_threshold_coupling * self.firing_threshold
        
        # Apply all threshold modulations
        autoreceptor_effect = 0.22 * self.autoreceptor
        theta = self.firing_threshold - threshold_mod + autoreceptor_effect + threshold_energy_mod
        
        # Determine binary state based on sign (Active Binary {1, -1})
        # Using 0.0 as the decision boundary instead of a positive threshold
        if self.membrane_potential >= 0.0:
            self.binary_state = 1
        else:
            self.binary_state = -1
        
        self.state_history.append(self.binary_state)
        self._update_autocorrelation()
        activity_level = self.binary_state
        
        # === SPIKE CLASSIFICATION AND LOGGING ===
        logger = get_data_logger()
        if self.binary_state > 0 and self.params.spike_classification_enabled:
            # Calculate relative contributions
            input_contribution = abs(total_synaptic) + abs(external_input)
            spont_contribution = abs(spontaneous)
            
            is_driven = (input_contribution > self.params.driven_input_threshold or 
                        (not is_spontaneous_firing and input_contribution > 0.01))
            is_truly_spontaneous = is_spontaneous_firing and spont_contribution > input_contribution
            
            if logger.log_level >= 2:
                if is_truly_spontaneous:
                    # Log as spontaneous - this was triggered by spontaneous current
                    logger.log_spontaneous_event(0, self.id, self.membrane_potential)
                else:
                    # Log as driven - this was triggered by synaptic/external input
                    # FIX: Actually call log_driven_firing to increment counter!
                    logger.log_driven_firing(0)
        
        # NEW: Log subthreshold integration events Updated Save states in v 2.1
        logger = get_data_logger()
        if logger.log_level >= 2:
            # If we're inactive but close to threshold
            if self.binary_state == -1:
                distance_to_threshold = theta - self.membrane_potential
                
                # Log if within 30% of threshold
                if distance_to_threshold < abs(theta) * 0.3:
                    logger.log_subthreshold_event(
                        0, self.id, self.membrane_potential, 
                        theta, distance_to_threshold
                    )
        
        # NEW: Log significant autoreceptor effects Updated Save states in v 2.1
        if abs(self.autoreceptor) > 0.1:
            logger = get_data_logger()
            if logger.log_level >= 2:
                threshold_effect = -0.1 * self.autoreceptor
                logger.log_autoreceptor_event(0, self.id, self.autoreceptor, threshold_effect)
        
        # NEW: Log threshold modulation events (when crossing state boundaries) Updated Save states in v 2.1
        if prev_state != self.binary_state:
            logger = get_data_logger()
            if logger.log_level >= 2:
                ach_contrib = (neuromodulators.get('acetylcholine', 0.5) - 0.5) * 0.5
                autoreceptor_contrib = -0.1 * self.autoreceptor
                logger.log_threshold_modulation_event(
                    0, self.id, self.firing_threshold,
                    theta, ach_contrib, autoreceptor_contrib
                )
        
        # NEW: Log Dendritic Spikes Updated Save states in v 2.1
        # Check recent activity in branches to log events
        logger = get_data_logger()
        if logger.log_level >= 2:
            for branch in self.dendritic_branches:
                # If the most recent history indicates a spike (1.0)
                if branch.local_spike_history and branch.local_spike_history[-1] > 0.9:
                    # Avoid spamming: only log if it's a fresh spike (previous was 0) or probabalistically
                    if len(branch.local_spike_history) < 2 or branch.local_spike_history[-2] < 0.1:
                        logger.log_dendritic_spike_event(0, self.id, branch.branch_id, 
                                                       branch.branch_potential, branch.plateau_potential, 
                                                       branch.get_local_ca_influx())
        
        # Use individualized health decay
        self.health = min(1.0, self.health + 0.0005 * dt) if activity_level >= 0.01 else self.health - self.neuron_health_decay * dt
        
        self._update_energy(activity_level, abs(self.binary_state - prev_state) * 0.1, dt)
        
        if self.type == NeuronType.HIDDEN and (self.health < self.params.neuron_death_threshold or self.energy_level < 1.0):
            if random.random() < 0.001: self.is_active = False
    
    def set_state(self, state: int):
        if state in [0, 1]:
            self.binary_state = state
            self.membrane_potential = state * self.firing_threshold
    
    def to_dict(self) -> dict:
        """Serializes the neuron's state and its individualized parameters."""
        return {
            'id': self.id, 'type': self.type.value,
            'membrane_potential': self.membrane_potential, 'binary_state': self.binary_state,
            'adaptation': self.adaptation, 'health': self.health, 
            'is_active': self.is_active, 'energy_level': self.energy_level, 
            'phase': self.phase, 'natural_frequency': self.natural_frequency, 
            'intrinsic_timescale': self.intrinsic_timescale, 
            'circle_id': self.circle_id, 'fitness_score': self.fitness_score, 
            'dendritic_branches': [b.to_dict() for b in self.dendritic_branches],            
            'membrane_time_constant': self.membrane_time_constant,
            'firing_threshold': self.firing_threshold,
            'adaptation_rate': self.adaptation_rate,
            'spontaneous_firing_rate': self.spontaneous_firing_rate,
            'neuron_health_decay': self.neuron_health_decay,
            'energy_baseline': self.energy_baseline,
            'firing_energy_cost': self.firing_energy_cost,
            'plasticity_energy_cost': self.plasticity_energy_cost,
            'metabolic_rate': self.metabolic_rate,
            'recovery_rate': self.recovery_rate,
            'state_history': list(self.state_history), # Updated Save states in v 2.03
            'autoreceptor': self.autoreceptor, # Updated Save states in v 2.03
            'last_firing_time': self.last_firing_time  # Updated Save states in v 2.1
        }
# Neuraxon Game of Life Neuron Network
# Based on the Paper "Neuraxon: A New Neural Growth & Computation Blueprint" by David Vivancos https://vivancos.com/  & Dr. Jose Sanchez  https://josesanchezgarcia.com/ for Qubic Science https://qubic.org/
# https://www.researchgate.net/publication/397331336_Neuraxon
# Play the Lite Version of the Game of Life at https://huggingface.co/spaces/DavidVivancos/NeuraxonLife
import math
import random
import cmath
import numpy as np
from collections import defaultdict, deque
from dataclasses import asdict
from typing import List, Dict, Optional, Tuple

# Import local modules
from config import NetworkParameters
from logger import get_data_logger
from .enums import NeuronType, BinaryState
from .neuron import Neuraxon
from .components import Synapse, ITUCircle

class NeuraxonNetwork:
    """
    The main class that orchestrates the entire network simulation. It manages the collections
    of neurons and synapses, global signals like neuromodulators and oscillators, and executes
    the simulation steps, including all forms of plasticity and evolution.
    """
    def __init__(self, params: Optional[NetworkParameters] = None):
        self.params = params or NetworkParameters()
        self.input_neurons: List[Neuraxon] = []
        self.hidden_neurons: List[Neuraxon] = []
        self.output_neurons: List[Neuraxon] = []
        self.all_neurons: List[Neuraxon] = []
        self.synapses: List[Synapse] = []
        self.itu_circles: List[ITUCircle] = [] # A list of evolutionary units.
        
        # Initialize global neuromodulator levels.
        self.neuromodulators = {mod: getattr(self.params, f'{mod}_baseline') for mod in ['dopamine', 'serotonin', 'acetylcholine', 'norepinephrine']}
        self.modulator_grid = np.full((10, 10, 4), 0.5) # A spatial grid for modeling modulator diffusion.
        
        self.time = 0.0
        self.step_count = 0
        self.total_energy_consumed = 0.0
        
        # v2.39: Phase coherence tracking
        self.phase_coherence_history = deque(maxlen=100)
        self.last_phase_coherence = 0.0
        
        # Initialize random phase offsets for the three global oscillators.
        self.oscillator_phase_offsets = (random.random() * 2 * math.pi, random.random() * 2 * math.pi, random.random() * 2 * math.pi)
        self.activation_history = deque(maxlen=1000)
        self.branching_ratio = 1.0 # A measure of network criticality. A value near 1.0 is often optimal.
        
        # NEW v2.2503: Track excitatory fraction history for adaptive threshold homeostasis
        self.active_fraction_history = deque(maxlen=200)
        self.last_adaptive_threshold_tick = 0
        
        # Construct the network.
        self._initialize_neurons()
        self._initialize_synapses()
        self._initialize_itu_circles()
    
    def _initialize_neurons(self):
        """Creates the populations of input, hidden, and output neurons."""
        nid = 0
        for _ in range(self.params.num_input_neurons):
            n = Neuraxon(nid, NeuronType.INPUT, self.params)
            self.input_neurons.append(n)
            self.all_neurons.append(n)
            nid += 1
        for _ in range(self.params.num_hidden_neurons):
            n = Neuraxon(nid, NeuronType.HIDDEN, self.params)
            self.hidden_neurons.append(n)
            self.all_neurons.append(n)
            nid += 1
        for _ in range(self.params.num_output_neurons):
            n = Neuraxon(nid, NeuronType.OUTPUT, self.params)
            self.output_neurons.append(n)
            self.all_neurons.append(n)
            nid += 1
    
    def _initialize_synapses(self):
        """
        Generates the initial synaptic connectivity using a Watts-Strogatz small-world model.
        """
        num_neurons = len(self.all_neurons)
        if num_neurons <= 1: return
        
        k = max(2, min(num_neurons - 1, int(self.params.small_world_k)))
        rewire_p = max(0.0, min(1.0, float(self.params.small_world_rewire_prob)))
        existing = set()
        neuron_degrees = defaultdict(int)
        
        # Step 1: Regular ring lattice
        for idx, pre in enumerate(self.all_neurons):
            for offset in range(1, k // 2 + 1):
                j = (idx + offset) % num_neurons
                post = self.all_neurons[j]
                
                # Step 2: Rewiring
                if random.random() < rewire_p:
                    if self.params.preferential_attachment:
                        candidates = []; weights = []
                        for _ in range(10): 
                            j_new = random.randrange(num_neurons)
                            cand = self.all_neurons[j_new]
                            if cand.id != pre.id:
                                candidates.append(cand)
                                weights.append(neuron_degrees[cand.id] + 1)
                        if candidates: post = random.choices(candidates, weights=weights, k=1)[0]
                        else:
                            for _ in range(6):
                                j_new = random.randrange(num_neurons)
                                cand = self.all_neurons[j_new]
                                if cand.id != pre.id:
                                    post = cand
                                    break
                    else: # Simple random rewiring.
                        for _ in range(6):
                            j_new = random.randrange(num_neurons)
                            cand = self.all_neurons[j_new]
                            if cand.id != pre.id:
                                post = cand
                                break
                
                # Create synapse
                if pre.id == post.id or (pre.type == NeuronType.OUTPUT and post.type == NeuronType.INPUT) or (pre.id, post.id) in existing: continue
                syn = Synapse(pre.id, post.id, self.params)
                self.synapses.append(syn)
                if pre.type == NeuronType.INPUT:
                    syn.mark_as_afferent()
                existing.add((pre.id, post.id))
                neuron_degrees[pre.id] += 1
                neuron_degrees[post.id] += 1
                
        # Step 3: Random connections
        for pre in self.all_neurons:
            for post in self.all_neurons:
                if pre.id == post.id or (pre.type == NeuronType.OUTPUT and post.type == NeuronType.INPUT) or (pre.id, post.id) in existing: continue
                if random.random() < self.params.connection_probability * 0.25:
                    syn = Synapse(pre.id, post.id, self.params)
                    self.synapses.append(syn)
                    if pre.type == NeuronType.INPUT:
                        syn.mark_as_afferent()
                    existing.add((pre.id, post.id))
                    neuron_degrees[pre.id] += 1
                    neuron_degrees[post.id] += 1
                    
        for s in self.synapses:
            s.neighbor_synapses = [ns for ns in self.synapses if ns.pre_id == s.pre_id and ns.post_id != s.post_id]
    
    def _initialize_itu_circles(self):
        """Groups hidden neurons into ITUs for the Aigarth evolutionary process."""
        if len(self.hidden_neurons) < self.params.itu_circle_radius * 2: return
        num_circles = max(1, len(self.hidden_neurons) // self.params.itu_circle_radius)
        neurons_per_circle = len(self.hidden_neurons) // num_circles
        for circle_idx in range(num_circles):
            start = circle_idx * neurons_per_circle
            end = start + neurons_per_circle
            self.itu_circles.append(ITUCircle(circle_idx, self.hidden_neurons[start:end], self.params))
    
    def _global_oscillatory_drive(self) -> float:
        """Generates a complex, global oscillatory signal."""
        t = self.time
        low = math.sin(2.0 * math.pi * self.params.oscillator_low_freq * t + self.oscillator_phase_offsets[0])
        mid = math.sin(2.0 * math.pi * self.params.oscillator_mid_freq * t + self.oscillator_phase_offsets[1])
        high = math.sin(2.0 * math.pi * self.params.oscillator_high_freq * t + self.oscillator_phase_offsets[2])
        return self.params.oscillator_strength * (low * 0.5 + low * mid * 0.3 + mid * high * 0.2)
    
    def _update_neuromodulator_diffusion(self, dt: float):
        """Simulates the spatial diffusion of neuromodulators across the environment grid."""
        for i, mod in enumerate(['dopamine', 'serotonin', 'acetylcholine', 'norepinephrine']):
            grid = self.modulator_grid[:, :, i]
            laplacian = np.zeros_like(grid)
            laplacian[1:-1, 1:-1] = grid[2:, 1:-1] + grid[:-2, 1:-1] + grid[1:-1, 2:] + grid[1:-1, :-2] - 4 * grid[1:-1, 1:-1]
            self.modulator_grid[:, :, i] += self.params.diffusion_rate * laplacian * dt
            base = getattr(self.params, f'{mod}_baseline')
            
            # --- Antagonistic Decay Dynamics (Paper Claim) ---
            # DA and 5-HT are antagonists. To each natural decay, the opposite one can be added.
            decay_factor = 1.0
            if mod == 'dopamine':
                antagonist = self.neuromodulators.get('serotonin', 0.12)
                if antagonist > 0.5: decay_factor += (antagonist - 0.5)
            elif mod == 'serotonin':
                antagonist = self.neuromodulators.get('dopamine', 0.12)
                if antagonist > 0.5: decay_factor += (antagonist - 0.5)
            
            local_decay = self.params.neuromod_decay_rate  # new update v2.47 3.0
            if mod == 'norepinephrine':
                local_decay *= 3.0   
            self.neuromodulators[mod] += (base - self.neuromodulators[mod]) * local_decay * decay_factor * dt / 100.0

    
    def _apply_homeostatic_plasticity(self):
        """A slow-acting plasticity rule that adjusts neuron excitability."""
        if self.step_count % 100 != 0: return 
        
        # NEW v2.2503: Apply network-wide adaptive threshold homeostasis
        self._apply_adaptive_threshold_homeostasis()
        
        
        logger = get_data_logger()
        
        for neuron in self.all_neurons:
            if neuron.type == NeuronType.HIDDEN and len(neuron.state_history) > 0:
                recent_activity = sum(neuron.state_history) / len(neuron.state_history)
                old_threshold = neuron.params.firing_threshold
                
                if recent_activity > self.params.target_firing_rate * 1.2:
                    neuron.params.firing_threshold += self.params.homeostatic_plasticity_rate
                elif recent_activity < self.params.target_firing_rate * 0.8:
                    neuron.params.firing_threshold -= self.params.homeostatic_plasticity_rate
                
                # NEW: Log if threshold changed
                new_threshold = neuron.params.firing_threshold
                if old_threshold != new_threshold and logger.log_level >= 2:
                    logger.log_homeostatic_event(
                        self.step_count, 
                        neuron.id, 
                        old_threshold, 
                        new_threshold, 
                        recent_activity
                    )
    
    def _apply_adaptive_threshold_homeostasis(self):
        """
        IMPROVED v2.2507: Criticality-seeking threshold homeostasis.
        
        Bioinspired Rationale (Paper Section 7):
        Biological neural networks maintain criticality through homeostatic scaling
        of intrinsic excitability. When activity is too low (subcritical), neurons
        become more excitable; when too high (supercritical), they become less excitable.
        
        This implementation directly targets branching ratio σ→1.0 using proportional
        control, mimicking the continuous adjustment seen in biological homeostasis.
        
        Changes from v2.2503:
        - Targets branching ratio directly instead of just excitatory fraction
        - Uses proportional control (stronger correction when further from target)
        - More frequent checks (every 20 ticks vs 50)
        - Larger adjustment magnitude with bounds
        - Also modulates oscillator strength as secondary drive
        """
        if not self.params.adaptive_threshold_enabled:
            return
        
        # More frequent checking for responsive homeostasis
        check_interval = max(20, self.params.adaptive_threshold_check_interval // 2)
        if self.step_count - self.last_adaptive_threshold_tick < check_interval:
            return
        
        self.last_adaptive_threshold_tick = self.step_count
        
        # Need sufficient history for reliable branching ratio
        if len(self.activation_history) < 15:
            return
        
        active_neurons = [n for n in self.all_neurons if n.is_active]
        if not active_neurons:
            return
        
        # === COMPUTE NETWORK STATE (BINARY FRACTIONS) ===
        states = [n.binary_state for n in active_neurons]
        total = len(states)
        active_count = sum(1 for s in states if s == 1)
        
        active_fraction = active_count / total
        
        # Use avalanche-based sigma (branching ratio) as primary criticality signal
        sigma = self.branching_ratio
        
        # === DETERMINE ADJUSTMENT DIRECTION AND MAGNITUDE ===
        adjustment = 0.0
        reason = "none"
        
        # Check for fraction-based adjustments
        if active_fraction < self.params.min_active_fraction:
            # Too few active - lower thresholds to increase activity
            adjustment = -self.params.adaptive_threshold_adjustment * 1.5
            reason = f"low_active_{active_fraction:.3f}"
        elif active_fraction > self.params.max_active_fraction:
            # Too many active - raise thresholds to reduce activity
            adjustment = self.params.adaptive_threshold_adjustment * 1.5
            reason = f"high_active_{active_fraction:.3f}"
        else:
            # Original criticality-based adjustment continues below...
            sigma_error = 1.0 - sigma
            
            base_adjustment = self.params.adaptive_threshold_adjustment
            proportional_gain = min(2.0, 1.0 + abs(sigma_error))
            adjustment_magnitude = base_adjustment * proportional_gain
            
            # === ALSO CHECK: Active Fraction as Secondary Signal ===
            self.active_fraction_history.append(active_fraction)
            
            # Determine adjustment direction based on sigma
            if sigma < 0.85:  # Subcritical - network too quiet
                adjustment = -adjustment_magnitude
                reason = f"subcritical_sigma_{sigma:.3f}_act_{active_fraction:.3f}"
                
                if sigma < 0.7:
                    self.params.oscillator_strength = min(0.40, 
                        self.params.oscillator_strength + 0.005)
            
            elif sigma > 1.15:  # Supercritical - network too active
                adjustment = adjustment_magnitude
                reason = f"supercritical_sigma_{sigma:.3f}_act_{active_fraction:.3f}"
                
                if sigma > 1.3:
                    self.params.oscillator_strength = max(0.10,
                        self.params.oscillator_strength - 0.005)
        
        # === APPLY GLOBAL THRESHOLD ADJUSTMENT ===
        if adjustment != 0.0:
            neurons_adjusted = 0
            for neuron in active_neurons:
                # Threshold: range [0.25, 1.2]
                new_threshold = neuron.firing_threshold + adjustment
                neuron.firing_threshold = max(0.25, min(1.2, new_threshold))
                
                neurons_adjusted += 1
            
            # === LOG THE HOMEOSTATIC EVENT ===
            logger = get_data_logger()
            if logger.log_level >= 2:
                logger.log_homeostatic_event(
                    tick=self.step_count,
                    neuron_id=-1,  # -1 indicates network-wide adjustment
                    old_value=sigma,  # Using sigma as reference
                    new_value=sigma + adjustment,  # Direction indicator
                    activity=active_fraction
                )
    
    def _apply_synaptic_weight_homeostasis(self):
        """
        NEW v2.31: Synaptic scaling for weight homeostasis.
        
        BIOINSPIRED RATIONALE (Turrigiano et al., 1998; Turrigiano & Nelson, 2004):
        Biological synapses undergo "synaptic scaling" - a homeostatic mechanism where
        total synaptic strength is multiplicatively normalized to prevent runaway
        excitation while preserving the relative differences between weights
        (which encode learned information).
        
        This addresses the weight drift problem identified in HF52/HF53 analysis:
        - HF52: Δw = 0.294, weights approaching saturation (0.82-0.90)
        - HF53: Δw = 0.441 (50% worse after energy patch)
        
        The mechanism works in three stages:
        1. DETECTION: Monitor per-neuron outgoing weight distribution
        2. SOFT SCALING: When mean |weight| exceeds threshold, apply multiplicative scaling
        3. DRIFT CORRECTION: Apply small bias toward zero to counteract systematic drift
        
        Key property: Multiplicative scaling preserves relative weight ratios,
        so learned patterns (which depend on relative strengths) are maintained.
        """
        if not self.params.weight_homeostasis_enabled:
            return
        
        # Apply at regular intervals (not every step for efficiency)
        if self.step_count % self.params.weight_homeostasis_interval != 0:
            return
        
        if not self.synapses:
            return
        
        # === STAGE 1: COMPUTE GLOBAL WEIGHT STATISTICS ===
        all_w_fast = [s.w_fast for s in self.synapses if s.integrity > 0]
        all_w_slow = [s.w_slow for s in self.synapses if s.integrity > 0]
        
        if not all_w_fast:
            return
        
        mean_abs_w_fast = sum(abs(w) for w in all_w_fast) / len(all_w_fast)
        mean_abs_w_slow = sum(abs(w) for w in all_w_slow) / len(all_w_slow)
        mean_w_fast = sum(all_w_fast) / len(all_w_fast)  # Signed mean (for drift detection)
        mean_w_slow = sum(all_w_slow) / len(all_w_slow)
        
        # === STAGE 2: PER-NEURON SYNAPTIC SCALING ===
        # Group synapses by presynaptic neuron (outgoing weights)
        neuron_synapses = defaultdict(list)
        for s in self.synapses:
            if s.integrity > 0:
                neuron_synapses[s.pre_id].append(s)
        
        scaling_events = 0
        
        for pre_id, synapses in neuron_synapses.items():
            if not synapses:
                continue
            
            # Calculate mean absolute weight for this neuron's outgoing synapses
            local_w_fast = [s.w_fast for s in synapses]
            local_w_slow = [s.w_slow for s in synapses]
            
            local_mean_fast = sum(abs(w) for w in local_w_fast) / len(local_w_fast)
            local_mean_slow = sum(abs(w) for w in local_w_slow) / len(local_w_slow)
            
            # Check if scaling needed (weights approaching saturation)
            needs_scaling_fast = local_mean_fast > self.params.weight_saturation_threshold
            needs_scaling_slow = local_mean_slow > self.params.weight_saturation_threshold
            
            if needs_scaling_fast or needs_scaling_slow:
                scaling_events += 1
                
                for s in synapses:
                    # SOFT MULTIPLICATIVE SCALING
                    # Scale factor approaches target/current ratio gradually
                    # This preserves relative weight differences (learned patterns)
                    
                    if needs_scaling_fast and abs(s.w_fast) > 0.01:
                        # Compute scaling factor to move toward target
                        current_scale = abs(s.w_fast) / local_mean_fast
                        target_scale = self.params.weight_homeostasis_target / local_mean_fast
                        
                        # Soft scaling: gradually approach target
                        scale_factor = 1.0 - self.params.weight_homeostasis_rate * (1.0 - target_scale)
                        scale_factor = max(0.8, min(1.0, scale_factor))  # Limit scaling per step
                        
                        s.w_fast *= scale_factor
                    
                    if needs_scaling_slow and abs(s.w_slow) > 0.01:
                        current_scale = abs(s.w_slow) / local_mean_slow
                        target_scale = self.params.weight_homeostasis_target / local_mean_slow
                        
                        scale_factor = 1.0 - self.params.weight_homeostasis_rate * (1.0 - target_scale)
                        scale_factor = max(0.8, min(1.0, scale_factor))
                        
                        s.w_slow *= scale_factor
        
        # === STAGE 3: GLOBAL DRIFT CORRECTION ===
        # If mean weight is systematically positive (drift), apply small correction
        # This counteracts the LTP > LTD imbalance seen in HF53 (ratio 1.29)
        
        drift_correction = self.params.weight_drift_correction
        
        # Detect systematic drift direction
        if abs(mean_w_fast) > 0.1:  # Significant drift detected
            drift_sign = 1.0 if mean_w_fast > 0 else -1.0
            for s in self.synapses:
                if s.integrity > 0:
                    # Apply small bias opposite to drift direction
                    s.w_fast -= drift_sign * drift_correction * abs(s.w_fast)
        
        if abs(mean_w_slow) > 0.1:
            drift_sign = 1.0 if mean_w_slow > 0 else -1.0
            for s in self.synapses:
                if s.integrity > 0:
                    s.w_slow -= drift_sign * drift_correction * abs(s.w_slow)
        
        # === LOGGING ===
        logger = get_data_logger()
        if logger.log_level >= 2 and scaling_events > 0:
            # Log as homeostatic event (repurposing existing infrastructure)
            logger.log_homeostatic_event(
                tick=self.step_count,
                neuron_id=-1,  # -1 indicates network-wide event
                old_value=mean_abs_w_fast,
                new_value=self.params.weight_homeostasis_target,
                activity=scaling_events / max(1, len(neuron_synapses))
            )

    def _get_neighbor_phases(self, neuron_id: int) -> dict:
        """v2.40: Get phases of synaptically connected neighbors for Kuramoto coupling.
        Returns dict of {neighbor_id: (phase, weight)} for weighted coupling."""
        neighbor_phases = {}
        neuron_map = {n.id: n for n in self.all_neurons}
        for syn in self.synapses:
            if syn.is_silent or syn.integrity < 0.1:
                continue
            weight = abs(syn.w_fast) + abs(syn.w_slow) * 0.5
            if weight < 0.05:
                continue
            if syn.post_id == neuron_id and syn.pre_id in neuron_map:
                pre_n = neuron_map[syn.pre_id]
                if pre_n.is_active:
                    if syn.pre_id in neighbor_phases:
                        # Accumulate weight if multiple synapses
                        _, old_weight = neighbor_phases[syn.pre_id]
                        neighbor_phases[syn.pre_id] = (pre_n.phase, old_weight + weight)
                    else:
                        neighbor_phases[syn.pre_id] = (pre_n.phase, weight)
            elif syn.pre_id == neuron_id and syn.post_id in neuron_map:
                post_n = neuron_map[syn.post_id]
                if post_n.is_active:
                    if syn.post_id in neighbor_phases:
                        _, old_weight = neighbor_phases[syn.post_id]
                        neighbor_phases[syn.post_id] = (post_n.phase, old_weight + weight)
                    else:
                        neighbor_phases[syn.post_id] = (post_n.phase, weight)
        return neighbor_phases
    
    def _compute_phase_coherence(self) -> float:
        """v2.39: Compute Kuramoto order parameter R for phase coherence."""
        active = [n for n in self.all_neurons if n.is_active]
        if len(active) < 2:
            return 0.0
        complex_sum = sum(cmath.exp(1j * n.phase) for n in active)
        return abs(complex_sum) / len(active)

    def _compute_branching_ratio(self):
        """Calculates the branching ratio (sigma): A(t) / A(t-1)."""
        if len(self.activation_history) < 2:
            self.branching_ratio = 1.0
            return 1.0
        
        # Get the two most recent time steps
        a_prev = self.activation_history[-2]
        a_now  = self.activation_history[-1]
        
        # Calculate instantaneous ratio (add small epsilon to avoid div/0)
        sigma_inst = a_now / (a_prev + 1e-9)
        
        # Apply EWMA smoothing (0.95 keep, 0.05 update) for stability
        # Clamping between 0.1 and 10.0 prevents massive spikes during quiet periods
        self.branching_ratio = 0.95 * self.branching_ratio + 0.05 * max(0.1, min(10.0, sigma_inst))
        
        return self.branching_ratio
    
    def _get_sensory_input_dict(self) -> Dict[int, float]:
        """Generate external inputs from clamped input neuron states."""
        external_inputs = {}
        for inp_neuron in self.input_neurons:
            if inp_neuron.is_active and inp_neuron.binary_state != 0:
                input_signal = inp_neuron.binary_state * self.params.sensory_input_gain
                for syn in self.synapses:
                    if syn.pre_id == inp_neuron.id and syn.is_afferent:
                        external_inputs[syn.post_id] = external_inputs.get(syn.post_id, 0.0) + input_signal
        return external_inputs
    
    def simulate_step(self, external_inputs: Optional[Dict[int, float]] = None):
        """Executes one full, orchestrated simulation step for the entire network."""
        sensory_inputs = self._get_sensory_input_dict()
        external_inputs = external_inputs or {}
        for nid, val in sensory_inputs.items():
            external_inputs[nid] = external_inputs.get(nid, 0.0) + val
        
        dt = max(self.params.min_dt, min(self.params.max_dt, self.params.dt / (1.0 + np.var(list(self.activation_history)[-10:]) if len(self.activation_history) > 10 else self.params.dt)))
        
        osc_drive = self._global_oscillatory_drive()
        
        syn_inputs = {n.id: [] for n in self.all_neurons}
        mod_inputs = {n.id: [] for n in self.all_neurons}
        delayed_inputs = defaultdict(list)
        for s in self.synapses:
            if s.integrity <= 0: continue
            pre = self.all_neurons[s.pre_id]
            if not pre.is_active: continue
            immediate, delayed = s.compute_input(pre.binary_state, self.time)
            syn_inputs[s.post_id].append(immediate)
            if delayed > 0: delayed_inputs[s.post_id].append((delayed, self.time + s.axonal_delay))
            me = s.get_modulatory_effect()
            if me != 0: mod_inputs[s.post_id].append(me)
        
        for post_id, delays in list(delayed_inputs.items()):
            for value, delivery_time in delays:
                if abs(delivery_time - self.time) < dt:
                    syn_inputs[post_id].append(value)
                    delayed_inputs[post_id].remove((value, delivery_time))

        step_activity_sum = 0.0
        active_neuron_count = 0

        for n in self.all_neurons:
            if not n.is_active: continue
            ext = external_inputs.get(n.id, 0.0) + osc_drive
            neighbor_phases = self._get_neighbor_phases(n.id)
            n.update(syn_inputs[n.id], mod_inputs[n.id], ext, self.neuromodulators, dt, osc_drive, neighbor_phases)
            
            # Aggregate activity for this specific tick
            step_activity_sum += n.binary_state
            active_neuron_count += 1
        
        # Calculate average network activity for this tick (0.0 to 1.0)
        # Using average is better than sum because it handles population changes (deaths) gracefully
        current_step_activity = step_activity_sum / max(1, active_neuron_count)
        self.activation_history.append(current_step_activity)

        for s in self.synapses:
            if s.integrity <= 0: continue
            pre = self.all_neurons[s.pre_id]
            post = self.all_neurons[s.post_id]
            if pre.is_active and post.is_active:
                s.potential_delta_w = s.calculate_delta_w(pre.binary_state, post.binary_state, self.neuromodulators, dt)
                
        for s in self.synapses:
            if s.integrity <= 0: continue
            pre = self.all_neurons[s.pre_id]
            post = self.all_neurons[s.post_id]
            if pre.is_active and post.is_active:
                neighbor_deltas = [ns.potential_delta_w for ns in s.neighbor_synapses]
                s.apply_update(dt, self.neuromodulators, neighbor_deltas)        
        for n in self.all_neurons:
            if n.is_active:
                activity = n.binary_state
                self.total_energy_consumed += n.firing_energy_cost * activity * dt
                        
        self._update_neuromodulator_diffusion(dt)
        for k in ('dopamine', 'serotonin', 'acetylcholine', 'norepinephrine'):
            self.neuromodulators[k] = max(0.0, min(2.0, self.neuromodulators[k] + osc_drive * (0.02 if k == 'dopamine' else 0.01 if k in ('serotonin', 'acetylcholine') else 0.0)))
        self._apply_homeostatic_plasticity()
        
        # NEW v2.31: Apply synaptic weight homeostasis after plasticity updates
        self._apply_synaptic_weight_homeostasis()
        
        self._apply_structural_plasticity()
        
        if self.step_count % self.params.evolution_interval == 0: self._evolve_itu_circles()
        
        self._compute_branching_ratio()
        self.time += dt
        self.step_count += 1
    
    def _apply_structural_plasticity(self):
        """Modifies the network's topology over time."""
        self.synapses = [s for s in self.synapses if s.integrity > self.params.synapse_integrity_threshold]
        
        if random.random() < self.params.synapse_formation_prob:
            act = [n for n in self.all_neurons if n.is_active and n.energy_level > 20.0]
            if len(act) >= 2:
                if self.params.preferential_attachment:
                    degrees = [sum(1 for s in self.synapses if s.pre_id == n.id or s.post_id == n.id) for n in act]
                    pre = random.choices(act, weights=[d+1 for d in degrees], k=1)[0]
                    post = random.choices(act, weights=[d+1 for d in degrees], k=1)[0]
                else:
                    pre = random.choice(act)
                    post = random.choice(act)
                if pre.id != post.id and not (pre.type == NeuronType.OUTPUT and post.type == NeuronType.INPUT) and not any(ss.pre_id == pre.id and ss.post_id == post.id for ss in self.synapses):
                    self.synapses.append(Synapse(pre.id, post.id, self.params))
                    
        for n in self.hidden_neurons:
            if (n.health < self.params.neuron_death_threshold or n.energy_level < 5.0) and random.random() < 0.001:
                n.is_active = False
    

    def _circle_metrics(self, circle):
        active = [n for n in circle.neurons if n.is_active]
        if not active:
            return 0.0, 0.0, 0.0

        # pattern/activity term
        activity = sum(n.binary_state for n in active) / len(active)

        # phase order parameter (this matches what you log in get_energy_status)
        phases = [n.phase for n in active]
        if len(phases) >= 2:
            sync = abs(sum(cmath.exp(1j * p) for p in phases) / len(phases))
        else:
            sync = 0.0

        # approximate per-tick energy spent by this circle
        spent = sum(n.firing_energy_cost * n.binary_state for n in active) + 1e-9
        efficiency = activity / spent

        return activity, sync, efficiency
    
    def _evolve_itu_circles(self):
        """
        Executes one evolutionary cycle for all ITUs in the network.
        UPDATED: Uses real physics metrics instead of proxies.
        """
        for circle in self.itu_circles:
            # Calculate REAL metrics using the new helper
            activity_val, temporal_sync, energy_efficiency = self._circle_metrics(circle)
            
            # Note: compute_fitness expects a list for network_activity for the pattern weight,
            # but usually just takes the mean. We pass the calculated scalar relative to the circle.
            # To keep signature valid with existing circle.compute_fitness logic:
            network_activity_proxy = [activity_val] 
            
            fitness = circle.compute_fitness(network_activity_proxy, temporal_sync, energy_efficiency)
            
            for n in circle.neurons: 
                n.fitness_score = fitness
            
            # Apply mutation and selection.
            circle.mutate()
            pruned_ids = circle.prune_unfit_neurons()            
    
    def set_input_states(self, states: List[int]):
        """Clamps the input neurons to the given binary states."""
        for i, s in enumerate(states[:len(self.input_neurons)]):
            self.input_neurons[i].set_state(s)
    
    def get_output_states(self) -> List[int]:
        """Returns the current binary states of all active output neurons."""
        return [n.binary_state for n in self.output_neurons if n.is_active]
    
    def get_energy_status(self) -> Dict[str, float]:
        """Returns a summary of the network's current energy state."""
        import cmath
        
        active_neurons = [n for n in self.all_neurons if n.is_active]
        total_energy = sum(n.energy_level for n in active_neurons)
        avg_energy = total_energy / max(1, len(active_neurons))
                
        energy_spent = sum(max(0, n.energy_baseline - n.energy_level) for n in active_neurons)
        energy_spent += self.step_count * 0.01 * len(active_neurons)
        recent_activity = sum(self.activation_history) if self.activation_history else 0
        efficiency = recent_activity / max(1, energy_spent) if energy_spent > 0 else 0.0
        
        phases = [n.phase for n in active_neurons]
        if len(phases) >= 2:
            complex_phases = [cmath.exp(1j * p) for p in phases]
            order_param = abs(sum(complex_phases) / len(complex_phases))
            temporal_sync = order_param
        else:
            temporal_sync = 0.0
        
        return {
            'total_energy': total_energy, 
            'average_energy': avg_energy, 
            'efficiency': efficiency,
            'branching_ratio': self.branching_ratio,
            'temporal_sync': temporal_sync
        }
            
   
    def to_dict(self) -> dict:
        """Serializes the entire network state into a single dictionary."""
        return {'parameters': asdict(self.params), 'neurons': {'input': [n.to_dict() for n in self.input_neurons], 'hidden': [n.to_dict() for n in self.hidden_neurons], 'output': [n.to_dict() for n in self.output_neurons]}, 'synapses': [s.to_dict() for s in self.synapses], 'neuromodulators': self.neuromodulators, 'time': self.time, 'step_count': self.step_count, 'energy_consumed': self.total_energy_consumed, 
        'branching_ratio': self.branching_ratio, 
        'modulator_grid': self.modulator_grid.tolist(),  # Updated Save states in v 2.1
        'oscillator_phase_offsets': self.oscillator_phase_offsets,  # Updated Save states in v 2.1
          'itu_circles': [{
            'circle_id': c.circle_id,
            'fitness_history': c.fitness_history,  # Updated Save states in v 2.1
            'mutation_rate': c.mutation_rate  # Updated Save states in v 2.1
        } for c in self.itu_circles],
        'activation_history': list(self.activation_history)    # Updated Save states in v 2.03
         }


def _rebuild_net_from_dict(d: dict) -> NeuraxonNetwork:
    """A utility function to reconstruct a complete NeuraxonNetwork object from a dictionary."""
    params = NetworkParameters(**d['parameters'])
    net = NeuraxonNetwork(params)
    
    # Helper function to apply saved state to a list of neurons.
    def _apply(neu_list, src_list, off=0):
        for nd in src_list:
            idx = nd['id'] - off
            if 0 <= idx < len(neu_list):
                n = neu_list[idx]
                n.membrane_potential = nd['membrane_potential']
                n.binary_state = nd.get('binary_state', nd.get('trinary_state', 0))
                n.health = nd['health']
                n.is_active = nd['is_active']
                n.energy_level = nd.get('energy_level', params.energy_baseline)
                n.phase = nd.get('phase', random.random() * 2 * math.pi)
                n.fitness_score = nd.get('fitness_score', 0.0)
                
                # Individualized neuron parameters
                n.membrane_time_constant = nd.get('membrane_time_constant', params.membrane_time_constant)
                n.firing_threshold = nd.get('firing_threshold', nd.get('firing_threshold_excitatory', params.firing_threshold))
                n.adaptation_rate = nd.get('adaptation_rate', params.adaptation_rate)
                n.spontaneous_firing_rate = nd.get('spontaneous_firing_rate', params.spontaneous_firing_rate)
                n.neuron_health_decay = nd.get('neuron_health_decay', params.neuron_health_decay)
                n.energy_baseline = nd.get('energy_baseline', params.energy_baseline)
                n.firing_energy_cost = nd.get('firing_energy_cost', params.firing_energy_cost)
                n.plasticity_energy_cost = nd.get('plasticity_energy_cost', params.plasticity_energy_cost)
                n.metabolic_rate = nd.get('metabolic_rate', params.metabolic_rate)
                n.recovery_rate = nd.get('recovery_rate', params.recovery_rate)
                n.intrinsic_timescale = nd.get('intrinsic_timescale', n.membrane_time_constant)
                n.adaptation = nd.get('adaptation', 0.0)
                n.autoreceptor = nd.get('autoreceptor', 0.0)
                # ADD: Restore last firing time
                n.last_firing_time = nd.get('last_firing_time', -1000.0)
                
                # ADD: Restore state_history
                if 'state_history' in nd:
                    n.state_history = deque(nd['state_history'], maxlen=50)
                
                # Dendritic branches
                if 'dendritic_branches' in nd:
                    for i, bd in enumerate(nd['dendritic_branches']):
                        if i < len(n.dendritic_branches):
                            b = n.dendritic_branches[i]
                            b.branch_potential = bd['branch_potential']
                            b.plateau_potential = bd['plateau_potential']
                            b.branch_threshold = bd.get('branch_threshold', params.branch_threshold)
                            b.plateau_decay = bd.get('plateau_decay', params.plateau_decay)
                            # ADD: Restore local_spike_history
                            if 'local_spike_history' in bd:
                                b.local_spike_history = deque(bd['local_spike_history'], maxlen=10)
                            
    # Apply the saved state to each neuron population.
    _apply(net.input_neurons, d['neurons']['input'], 0)
    _apply(net.hidden_neurons, d['neurons']['hidden'], len(net.input_neurons))
    _apply(net.output_neurons, d['neurons']['output'], len(net.input_neurons) + len(net.hidden_neurons))
    
    # Reconstruct all synapses from the saved data.
    net.synapses = []
    for sd in d['synapses']:
        s = Synapse(sd['pre_id'], sd['post_id'], params)
        s.w_fast = sd['w_fast']
        s.w_slow = sd['w_slow']
        s.w_meta = sd['w_meta']
        s.is_silent = sd['is_silent']
        s.is_modulatory = sd['is_modulatory']
        s.integrity = sd['integrity']
        s.axonal_delay = sd.get('axonal_delay', random.uniform(0, params.max_axonal_delay))
        s.learning_rate_mod = sd.get('learning_rate_mod', 1.0)
        s.potential_delta_w = sd.get('potential_delta_w', 0.0)
        
        # Individualized synapse parameters
        s.tau_fast = sd.get('tau_fast', params.tau_fast)
        s.tau_slow = sd.get('tau_slow', params.tau_slow)
        s.tau_meta = sd.get('tau_meta', params.tau_meta)
        s.tau_ltp = sd.get('tau_ltp', params.tau_ltp)
        s.tau_ltd = sd.get('tau_ltd', params.tau_ltd)
        s.learning_rate = sd.get('learning_rate', params.learning_rate)
        s.plasticity_threshold = sd.get('plasticity_threshold', params.plasticity_threshold)
        
        # ADD: Restore synaptic traces
        s.pre_trace = sd.get('pre_trace', 0.0)
        s.post_trace = sd.get('post_trace', 0.0)
        s.pre_trace_ltd = sd.get('pre_trace_ltd', 0.0)
         # ADD: Restore associative strength
        s.associative_strength = sd.get('associative_strength', 0.0)
        # Temporarily store neighbor IDs for second pass
        s._saved_neighbor_ids = sd.get('neighbor_synapse_ids', None)
        net.synapses.append(s)
    # Build a lookup dictionary for fast synapse retrieval (Updated Save states in v 2.1)
    synapse_lookup = {(s.pre_id, s.post_id): s for s in net.synapses}
    
    # Second pass: Restore neighbor_synapses relationships (Updated Save states in v 2.1)
    for s in net.synapses:
        if hasattr(s, '_saved_neighbor_ids') and s._saved_neighbor_ids is not None:
            # Restore from saved IDs
            s.neighbor_synapses = []
            for (pre_id, post_id) in s._saved_neighbor_ids:
                neighbor = synapse_lookup.get((pre_id, post_id))
                if neighbor is not None:
                    s.neighbor_synapses.append(neighbor)
            delattr(s, '_saved_neighbor_ids')  # Clean up temporary attribute
        else:
            # Fallback: Rebuild from scratch (backward compatibility)
            s.neighbor_synapses = [ns for ns in net.synapses 
                                   if ns.pre_id == s.pre_id and ns.post_id != s.post_id]
        
    # Restore the rest of the global network state.
    net.neuromodulators = d['neuromodulators']
    net.time = d['time']
    net.step_count = d['step_count']
    net.total_energy_consumed = d.get('energy_consumed', 0.0)
    net.branching_ratio = d.get('branching_ratio', 1.0)
    
    # ADD: Restore activation_history v2.1
    if 'activation_history' in d:
        net.activation_history = deque(d['activation_history'], maxlen=1000)
     # ADD: Restore modulator diffusion grid v2.1
    if 'modulator_grid' in d:
        net.modulator_grid = np.array(d['modulator_grid'])
    
    # ADD: Restore oscillator phase offsets v2.1
    if 'oscillator_phase_offsets' in d:
        net.oscillator_phase_offsets = tuple(d['oscillator_phase_offsets'])
    
    # ADD: Restore ITU circles v2.1
    if 'itu_circles' in d and isinstance(d['itu_circles'], list):
        for i, circle_data in enumerate(d['itu_circles']):
            if i < len(net.itu_circles):
                if isinstance(circle_data, dict):
                    net.itu_circles[i].fitness_history = circle_data.get('fitness_history', [])
                    net.itu_circles[i].mutation_rate = circle_data.get('mutation_rate', 0.01)
    return net
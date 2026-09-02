# Neuraxon Game of Life Neuron (Nxon 2.0 compliant)
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
from .enums import NeuronType, TrinaryState
from .components import DendriticBranch, MSTHState

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
        self.firing_threshold_excitatory = _variate(params.firing_threshold_excitatory)
        # Ensure inhibitory is negative and varied correctly
        self.firing_threshold_inhibitory = params.firing_threshold_inhibitory * random.uniform(0.8, 1.2)
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
        # v2.36: Start neurons closer to resting potential (zero) - biologically neurons
        # spend most time near resting potential, not near threshold
        self.membrane_potential = random.uniform(
            self.firing_threshold_inhibitory * 0.35,  # v2.36: Narrower range, closer to zero
            self.firing_threshold_excitatory * 0.35
        )

        self.trinary_state = TrinaryState.NEUTRAL.value
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

        # --- Neuraxon v2.0: CTSN Complement (Algorithm 1 Step 3) ---
        self.complement_h = 0.0
        self.state_tilde = 0.0

        # --- Neuraxon v2.0: DSN Dynamic Decay (Algorithm 1 Step 2) ---
        k = max(int(getattr(params, 'dsn_kernel_size', 4)), 1)
        self.dsn_input_buffer = [0.0] * k
        self.dsn_alpha = 0.5
        base_kernel = getattr(params, 'dsn_kernel_weights', None) or []
        if len(base_kernel) != k:
            base_kernel = [(i + 1.0) for i in range(k)]
            s = sum(abs(x) for x in base_kernel) or 1.0
            base_kernel = [float(x) / s for x in base_kernel]
        self.dsn_kernel_weights = [float(x) for x in base_kernel]

        # --- Neuraxon v2.0: CTSN learnable phi parameters ---
        self.ctsn_phi_gain = float(getattr(params, 'ctsn_phi_gain', 0.5))
        self.ctsn_phi_bias = float(getattr(params, 'ctsn_phi_bias', 0.0))
        self._ctsn_last_x = 0.0
        self._ctsn_last_phi = 0.0

        # --- Neuraxon v2.0: MSTH ---
        self.msth = MSTHState(params)

        # --- Neuraxon v2.0: AGMP astrocyte ---
        self.astrocyte_state = 0.0

        # --- Neuraxon v2.0: Firing rate average for homeostasis ---
        self.firing_rate_avg = getattr(params, 'target_firing_rate', 0.2)

        
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
            # v3.35/RC6-FIX: Reduced penalty multiplier 2.0→1.2 (was creating death spiral).
            # BIOINSPIRED: Metabolic stress damages neurons but not at catastrophic rate;
            # cellular stress-response (UPR, heat-shock proteins) provides partial protection.
            self.health -= self.neuron_health_decay * dt * 1.2
            self.membrane_potential *= 0.95  # Gentler potential damping (was 0.9)
            self.health = max(-0.5, self.health)  # Enforce floor here too
        elif self.energy_level > self.params.critical_energy_level:
            # v3.35/RC6-FIX NEW: Energy-conditional health recovery.
            # BIOINSPIRED: Adequate ATP drives mitochondrial biogenesis and
            # protein synthesis, actively repairing neuronal structure.
            # Recovery is slow but steady when metabolically healthy.
            self.health = min(1.0, self.health + 0.001 * dt)

    
    def _update_intrinsic_timescale(self, dt: float):
        """Update intrinsic timescale based on autocorrelation."""
        # This method is called early in update() to prepare for timescale updates
        # The actual autocorrelation-based update happens in _update_autocorrelation()
        # after state_history is updated
        pass
    
    def _update_autocorrelation(self):
        ### HOTFIX4: Throttled — was running np.std+np.corrcoef per neuron per tick (4750 numpy calls/tick!)
        ### Now runs ~2% of the time (every ~50 ticks per neuron on average)
        if len(self.state_history) < 50 or random.random() > 0.02:
            return
        try:
            states = list(self.state_history)
            states_a = states[:-1]
            states_b = states[1:]
            # Pure Python variance check (faster than numpy on 50 elements)
            mean_a = sum(states_a) / len(states_a)
            var_a = sum((x - mean_a) ** 2 for x in states_a)
            if var_a < 1e-8:
                return
            mean_b = sum(states_b) / len(states_b)
            var_b = sum((x - mean_b) ** 2 for x in states_b)
            if var_b < 1e-8:
                return
            # Pure Python Pearson correlation (avoids numpy small-array overhead)
            cov = sum((a - mean_a) * (b - mean_b) for a, b in zip(states_a, states_b))
            autocorr = cov / (max(1e-10, (var_a * var_b) ** 0.5))
            acw = self.intrinsic_timescale * (1.0 + abs(autocorr))
            self.intrinsic_timescale = min(acw, self.params.max_intrinsic_timescale)
        except:
            pass
    
    def _compute_dsn_alpha(self, current_input: float) -> float:
        """Neuraxon v2.0: alpha_t = Sigmoid(CausalConv1D(X_{t-k+1:t})) (Algorithm 1 Steps 5-6)."""
        if not getattr(self.params, 'dsn_enabled', False):
            return 0.5
        self.dsn_input_buffer.pop(0)
        self.dsn_input_buffer.append(float(current_input))
        kernel = getattr(self, 'dsn_kernel_weights', []) or []
        if len(kernel) != len(self.dsn_input_buffer):
            k = max(int(getattr(self.params, 'dsn_kernel_size', 4)), 1)
            kernel = [(i + 1.0) for i in range(k)]
            s = sum(abs(x) for x in kernel) or 1.0
            kernel = [float(x) / s for x in kernel]
            self.dsn_kernel_weights = kernel
        conv_out = sum(w * x for w, x in zip(kernel, self.dsn_input_buffer)) + float(getattr(self.params, 'dsn_bias', 0.0))
        exponent = max(-50.0, min(50.0, -conv_out))
        self.dsn_alpha = 1.0 / (1.0 + math.exp(exponent))
        return self.dsn_alpha

    def _update_complement(self, x_t: float):
        """Neuraxon v2.0: h_t, s_tilde(t) = s(t) + h(t) (Algorithm 1 Steps 7-8)."""
        if not getattr(self.params, 'ctsn_enabled', False):
            self.complement_h = 0.0
            return
        rho = float(getattr(self.params, 'ctsn_rho', 0.9))
        phi = math.tanh(float(self.ctsn_phi_gain) * float(x_t) + float(self.ctsn_phi_bias))
        self._ctsn_last_x = float(x_t)
        self._ctsn_last_phi = float(phi)
        self.complement_h = rho * self.complement_h + (1.0 - rho) * phi

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
                # v3.34 RC1-FIX: Balanced spontaneous current — 50% inhibitory, 50% excitatory
                # BIOINSPIRED: Cortical spontaneous activity explores the FULL trinary
                # state space symmetrically. In vivo, balanced E/I networks produce
                # approximately equal rates of spontaneous excitatory and inhibitory
                # postsynaptic events (Haider et al. 2006, J Neurosci). The prior 60/40
                # inhibitory bias compounded with membrane_negative_bias to lock outputs
                # into -1 from initialization (RC1 diagnostic: 97.5% SW quadrant).
                spontaneous = random.choice([-1.0, 1.0]) * self.params.spontaneous_current_magnitude
            else:
                # Legacy: force threshold
                if random.random() < 0.5:
                    self.membrane_potential = self.firing_threshold_excitatory + 0.01
                else:
                    spontaneous = random.choice([-1.0, 1.0]) * 2.0
                
        threshold_mod = (acetylcholine - 0.5) * 0.5 + sum(modulatory_inputs) * 0.3
        gain = 1.0 + (norepi - 0.5) * 0.4
        
        # v3.34 RC1-FIX: Bias now 0.0 from config; kept in formula for backward compat
        negative_bias = getattr(self.params, 'membrane_negative_bias', -0.06)
        
        drive = (total_synaptic + external_input + spontaneous + negative_bias * 2.0) * gain
        
        tau_eff = max(1.0, self.intrinsic_timescale)
        prev_state = self.trinary_state
        
        # v3.34 RC1-FIX: Fully symmetric membrane decay
        # BIOINSPIRED: Passive membrane leak conductance is direction-agnostic —
        # both depolarisation and hyperpolarisation decay toward resting potential
        # at the same rate, governed by the membrane time constant and leak channels.
        # The prior asymmetry (positive 1.1×, negative 0.85×) created a ratchet effect
        # that trapped membrane potential in the negative range, contributing to RC1.
        # Paper claim: neutral state enables "swift transitions based on subsequent inputs"
        if hasattr(self.params, 'resting_potential_decay'):
            resting_decay = self.params.resting_potential_decay * dt
            # v3.34: Symmetric decay for both positive and negative potentials
            self.membrane_potential *= (1.0 - resting_decay)
        
        # Store previous potential for subthreshold logging
        prev_potential = self.membrane_potential
        
        # Use individualized adaptation_rate indirectly via adaptation variable dynamics
        self.membrane_potential += dt / tau_eff * (-self.membrane_potential + drive - self.adaptation)
        
        # v2.37b: BIOINSPIRED - Asymmetric adaptation
        # Adaptation after excitatory firing is STRONGER than after inhibitory
        # This creates natural tendency toward E/I balance
        # Real neurons show strong adaptation after firing, reducing subsequent excitability
        # This creates refractory-like periods that increase neutral state time
        adaptation_target = 0.25 * abs(self.trinary_state) + 0.08 * (1 if self.trinary_state != 0 else 0)
        self.adaptation += dt / 40.0 * (-self.adaptation + adaptation_target)
        # v2.38: FIXED autoreceptor to track ACTIVITY level, not state sign
        # BIOINSPIRED: D2 autoreceptors detect released neurotransmitter from ANY firing
        # Both excitatory AND inhibitory firing should increase autoreceptor
        # This creates proper negative feedback: high activity → high autoreceptor → harder to fire
        # Previous bug: tracked trinary_state sign, causing correlation issues
        activity_for_autoreceptor = abs(self.trinary_state)  # 0 or 1
        self.autoreceptor += dt / 150.0 * (-self.autoreceptor + 0.35 * activity_for_autoreceptor)
        
        # NEW v2.30: Energy-Aware Firing Threshold
        # BIOINSPIRED: ATP depletion impairs Na+/K+-ATPase pump efficiency
        # This raises the effective firing threshold, making low-energy neurons less excitable
        # Creates natural metabolic recovery windows while maintaining network criticality
        
        # Calculate energy factor: 1.0 when energy is high, <1.0 when depleted
        energy_ratio = self.energy_level / (self.energy_baseline * self.params.energy_threshold_floor)
        energy_factor = min(1.0, max(0.3, energy_ratio))  # Clamp between 0.3 and 1.0
        
        # Energy-dependent threshold scaling: low energy raises effective threshold
        # energy_factor=1.0 -> no change; energy_factor=0.3 -> threshold raised by ~3.3x coupling factor
        threshold_energy_mod = (1.0 - energy_factor) * self.params.energy_threshold_coupling * self.firing_threshold_excitatory
        
        # Apply all threshold modulations
        # Note: threshold_energy_mod ADDS to threshold (making firing harder when energy is low)
        # 
        # Use individualized firing thresholds with CORRECTED autoreceptor feedback
        # 
        # FIX v2.32: Autoreceptor provides NEGATIVE feedback (D2-like mechanism)
        # BEFORE: -0.1 * autoreceptor → high activity LOWERED threshold (positive feedback - WRONG)
        # AFTER:  +0.15 * autoreceptor → high activity RAISES threshold (negative feedback - CORRECT)
        #
        # Bioinspired: D2 autoreceptors detect released dopamine and INHIBIT further release
        # Similarly, our autoreceptor senses activity and should DAMPEN further firing
        # v2.36: Increased autoreceptor effect for stronger negative feedback
        autoreceptor_effect = 0.22 * self.autoreceptor
        theta_exc = self.firing_threshold_excitatory - threshold_mod + autoreceptor_effect + threshold_energy_mod
        # v3.34 RC1-FIX: Symmetric autoreceptor negative feedback on inhibitory threshold
        # BIOINSPIRED: D2-type autoreceptors sense released neurotransmitter from ANY
        # firing and dampen further activity equally regardless of sign. The prior 0.5×
        # factor let inhibitory firing escape negative feedback, sustaining -1 lock-in.
        theta_inh = self.firing_threshold_inhibitory - threshold_mod - autoreceptor_effect - threshold_energy_mod * 0.5
        
        # v2.92: Symmetric hysteresis for balanced state transitions
        # Paper claim: neutral state provides "responsiveness without immediate action"
        hysteresis_exc = 0.025 if self.trinary_state == 0 else 0.0
        hysteresis_inh = 0.025 if self.trinary_state == 0 else 0.0
        
        if self.membrane_potential > (theta_exc + hysteresis_exc): 
            self.trinary_state = TrinaryState.EXCITATORY.value
        elif self.membrane_potential < (theta_inh - hysteresis_inh): 
            self.trinary_state = TrinaryState.INHIBITORY.value
        else: 
            self.trinary_state = TrinaryState.NEUTRAL.value
        
        self.state_history.append(self.trinary_state)

        # === NEURAXON v2.0 PIPELINE INTEGRATION ===
        if getattr(self.params, 'dsn_enabled', False) and self.type != NeuronType.INPUT:
            raw_input = total_synaptic + external_input + spontaneous
            alpha_t = self._compute_dsn_alpha(raw_input)
            self.membrane_potential = alpha_t * self.membrane_potential + (1.0 - alpha_t) * raw_input

        msth_signals = self.msth.update(abs(self.trinary_state), dt)
        if msth_signals['ultrafast_suppress']:
            self.membrane_potential *= 0.5

        self._update_complement(self.membrane_potential)
        self.state_tilde = self.membrane_potential + self.complement_h

        fr_alpha = getattr(self.params, 'firing_rate_alpha', 0.01)
        self.firing_rate_avg += fr_alpha * (abs(self.trinary_state) - self.firing_rate_avg) * dt

        if getattr(self.params, 'agmp_enabled', False):
            lam_a = getattr(self.params, 'agmp_lambda_a', 0.999)
            self.astrocyte_state = lam_a * self.astrocyte_state + (1.0 - lam_a) * abs(self.state_tilde)


        self._update_autocorrelation()
        activity_level = abs(self.trinary_state)
        
        ### HOTFIX5: ALL 5 logging blocks restored, guarded by log_level >= 3.
        ### Single get_data_logger() call cached; zero overhead at levels 0-2.
        _hf5_logger = get_data_logger()
        if _hf5_logger.log_level >= 3:
            # --- 1. Spike classification ---
            if abs(self.trinary_state) > 0 and self.params.spike_classification_enabled:
                input_contribution = abs(total_synaptic) + abs(external_input)
                spont_contribution = abs(spontaneous)
                is_driven = (input_contribution > self.params.driven_input_threshold or
                            (not is_spontaneous_firing and input_contribution > 0.01))
                is_truly_spontaneous = is_spontaneous_firing and spont_contribution > input_contribution
                if is_truly_spontaneous:
                    _hf5_logger.log_spontaneous_event(0, self.id, self.membrane_potential)
                else:
                    _hf5_logger.log_driven_firing(0)

            # --- 2. Subthreshold integration ---
            if self.trinary_state == 0:
                distance_to_exc = theta_exc - self.membrane_potential
                distance_to_inh = self.membrane_potential - theta_inh
                if distance_to_exc < abs(theta_exc) * 0.3:
                    _hf5_logger.log_subthreshold_event(
                        0, self.id, self.membrane_potential, theta_exc, distance_to_exc)
                elif distance_to_inh < abs(theta_inh) * 0.3:
                    _hf5_logger.log_subthreshold_event(
                        0, self.id, self.membrane_potential, theta_inh, distance_to_inh)

            # --- 3. Autoreceptor effects ---
            if abs(self.autoreceptor) > 0.1:
                threshold_effect = -0.1 * self.autoreceptor
                _hf5_logger.log_autoreceptor_event(0, self.id, self.autoreceptor, threshold_effect)

            # --- 4. Threshold modulation (state transitions) ---
            if prev_state != self.trinary_state:
                ach_contrib = (neuromodulators.get('acetylcholine', 0.5) - 0.5) * 0.5
                autoreceptor_contrib = -0.1 * self.autoreceptor
                _hf5_logger.log_threshold_modulation_event(
                    0, self.id, self.firing_threshold_excitatory,
                    theta_exc, ach_contrib, autoreceptor_contrib)

            # --- 5. Dendritic spikes ---
            for branch in self.dendritic_branches:
                if branch.local_spike_history and branch.local_spike_history[-1] > 0.9:
                    if len(branch.local_spike_history) < 2 or branch.local_spike_history[-2] < 0.1:
                        _hf5_logger.log_dendritic_spike_event(
                            0, self.id, branch.branch_id,
                            branch.branch_potential, branch.plateau_potential,
                            branch.get_local_ca_influx())

        # Use individualized health decay
        # v3.35/RC6-FIX: Increased recovery rate (0.0005→0.003) to match decay magnitude.
        # BIOINSPIRED: Neurotrophic factors (BDNF/NGF) actively repair active neurons.
        # Added health floor at -0.5: structural proteins maintain minimum integrity.
        if activity_level >= 0.01:
            self.health = min(1.0, self.health + 0.003 * dt)
        else:
            self.health -= self.neuron_health_decay * dt
        self.health = max(-0.5, self.health)

        
        self._update_energy(activity_level, abs(self.trinary_state - prev_state) * 0.1, dt)
        
        if self.type == NeuronType.HIDDEN and (self.health < self.params.neuron_death_threshold or self.energy_level < 1.0):
            if random.random() < 0.001: self.is_active = False
    
    def set_state(self, state: int):
        if state in [-1, 0, 1]:
            self.trinary_state = state
            # Use individualized threshold for clamping
            self.membrane_potential = state * self.firing_threshold_excitatory
    
    def to_dict(self) -> dict:
        """Serializes the neuron's state and its individualized parameters."""
        return {
            'id': self.id, 'type': self.type.value, 
            'membrane_potential': self.membrane_potential, 'trinary_state': self.trinary_state, 
            'adaptation': self.adaptation, 'health': self.health, 
            'is_active': self.is_active, 'energy_level': self.energy_level, 
            'phase': self.phase, 'natural_frequency': self.natural_frequency, 
            'intrinsic_timescale': self.intrinsic_timescale, 
            'circle_id': self.circle_id, 'fitness_score': self.fitness_score, 
            'dendritic_branches': [b.to_dict() for b in self.dendritic_branches],            
            'membrane_time_constant': self.membrane_time_constant,
            'firing_threshold_excitatory': self.firing_threshold_excitatory,
            'firing_threshold_inhibitory': self.firing_threshold_inhibitory,
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
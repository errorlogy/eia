"""
Neuraxon v2.0: A New Neural Growth & Computation Blueprint
Based on Vivancos & Sanchez (2026)
Hybridized with Aigarth Intelligent Tissue

v2.0 features:
  (i)    Receptor subtypes with nonlinear activation curves (tonic/phasic)
  (ii)   Multi-band oscillator bank with cross-frequency coupling (PAC)
  (iii)  Nonlinear dendritic branch integration
  (iv)   Temporal STDP traces with differential dopamine gating
  (v)    Associative neighbour plasticity
  (vi)   Watts-Strogatz small-world topology
  (vii)  Full neuromodulator system with activity-driven release & crosstalk
  (viii) Energy tracking
  (ix)   Aigarth hybridisation with evolutionary mutation and selection
  (x)    ChronoPlastic synaptic time warping (learned omega_t)
  (xi)   DSN-style dynamic decay (alpha_t via causal conv)
  (xii)  CTSN complemented trinary state (s_tilde = s + h)
  (xiii) AGMP astrocyte-gated plasticity (eligibility x modulator x astrocyte)
  (xiv)  Homeostatic plasticity (synaptic scaling + intrinsic plasticity)
  (xv)   Multi-Scale Temporal Homeostasis (MSTH) - 4 regulatory loops
  (xvi)  Pattern storage & recall application layer

Algorithm 1 pipeline per step: Time Warping -> Dynamic Decay -> CTSN -> AGMP
"""

import json
import random
import math
import copy
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import random

# =============================================================================
# NETWORK PARAMETERS
# =============================================================================

@dataclass
class NetworkParameters:
    """Default network parameters with biologically plausible ranges."""
    network_name: str = "Neuraxon v2.0 Net"

    # --- Network Architecture ---
    num_input_neurons: int = 5
    num_hidden_neurons: int = 20
    num_output_neurons: int = 5
    num_dendritic_branches: int = 3
    dendritic_spike_threshold: float = 0.4
    dendritic_supralinear_gamma: float = 1.3

    # Watts-Strogatz small-world parameters
    ws_k: int = 6
    ws_beta: float = 0.3

    # --- Neuron Parameters ---
    membrane_time_constant: float = 20.0
    firing_threshold_excitatory: float = 0.4
    firing_threshold_inhibitory: float = -0.4
    adaptation_tau: float = 100.0
    autoreceptor_tau: float = 200.0
    spontaneous_firing_rate: float = 0.02
    neuron_health_decay: float = 0.001

    # Homeostatic plasticity (Eq 1)
    target_firing_rate: float = 0.2
    homeostatic_rate: float = 0.0005
    firing_rate_alpha: float = 0.01
    threshold_mod_k: float = 0.3

    # --- MSTH: Multi-Scale Temporal Homeostasis (Section 5) ---
    msth_ultrafast_tau: float = 5.0
    msth_ultrafast_ceiling: float = 2.0
    msth_fast_tau: float = 2000.0
    msth_fast_gain: float = 0.1
    msth_medium_tau: float = 300000.0
    msth_medium_gain: float = 0.001
    msth_slow_tau: float = 3600000.0
    msth_slow_gain: float = 0.0001

    # --- DSN Dynamic Decay ---
    dsn_kernel_size: int = 4
    dsn_enabled: bool = True
    dsn_bias: float = 0.0
    # Optional: provide explicit causal-conv kernel weights (length = dsn_kernel_size).
    # If None/empty, a default triangular kernel is created in __post_init__.
    dsn_kernel_weights: Optional[List[float]] = None
    # --- DSN Learning (optional) ---
    dsn_learn_enabled: bool = False
    dsn_learn_lr: float = 0.01
    # Target alpha is computed as sigmoid(dsn_target_bias - dsn_target_sensitivity * |ΔX|)
    dsn_target_sensitivity: float = 4.0
    dsn_target_bias: float = 2.0
    # Safety clip for learned kernels (applied before re-normalisation)
    dsn_kernel_clip: float = 5.0

    # --- CTSN Complement ---
    ctsn_rho: float = 0.9
    ctsn_enabled: bool = True
    # Learnable filter proxy: phi_h(X(t)) ~ tanh(gain * X(t) + bias)
    ctsn_phi_gain: float = 0.5
    ctsn_phi_bias: float = 0.0
    # --- CTSN Learning (optional) ---
    ctsn_learn_enabled: bool = False
    ctsn_learn_lr: float = 0.005
    ctsn_phi_gain_clip: float = 5.0
    ctsn_phi_bias_clip: float = 5.0

    # --- Synapse Parameters ---
    tau_fast: float = 5.0
    tau_slow: float = 50.0
    tau_meta: float = 1000.0
    tau_stdp: float = 20.0
    w_fast_init_min: float = -0.8
    w_fast_init_max: float = 0.8
    w_slow_init_min: float = -0.4
    w_slow_init_max: float = 0.4
    w_meta_init_min: float = -0.3
    w_meta_init_max: float = 0.3

    # --- ChronoPlasticity (Eqs 5-7) ---
    chrono_alpha_f: float = 0.95
    chrono_alpha_s: float = 0.99
    chrono_lambda_f: float = 0.15
    chrono_lambda_s: float = 0.08
    chrono_enabled: bool = True

    # --- Chrono Stability (recommended) ---
    # Prevent omega_t saturating at 0/1 and keep traces bounded.
    chrono_trace_clip: float = 10.0
    chrono_gate_norm: float = 10.0
    chrono_raw_clip: float = 8.0
    chrono_omega_min: float = 0.05
    chrono_omega_max: float = 0.95
    chrono_omega_smoothing: float = 0.2

    # --- AGMP (Eqs 8-10) ---
    agmp_lambda_e: float = 0.95
    agmp_lambda_a: float = 0.999
    agmp_eta: float = 0.005
    agmp_enabled: bool = True

    # --- Plasticity ---
    learning_rate: float = 0.01
    stdp_window: float = 20.0
    associative_alpha: float = 0.005
    synapse_integrity_threshold: float = 0.1
    synapse_formation_prob: float = 0.05
    synapse_death_prob: float = 0.01
    neuron_death_threshold: float = 0.1

    # --- Neuromodulator Baselines ---
    dopamine_baseline: float = 0.15
    serotonin_baseline: float = 0.15
    acetylcholine_baseline: float = 0.15
    norepinephrine_baseline: float = 0.15
    tau_tonic: float = 5000.0
    tau_phasic: float = 200.0
    neuromod_release_rate: float = 0.02
    # --- Receptor activation shaping (avoid saturation) ---
    # Concentration is clipped to [0, receptor_concentration_cap] before receptor nonlinearities.
    receptor_concentration_cap: float = 1.0
    # Logistic slope for tonic vs phasic receptors (lower values = less saturation).
    receptor_slope_tonic: float = 4.0
    receptor_slope_phasic: float = 3.0


    # --- Oscillator Bank ---
    oscillator_coupling: float = 0.1

    # --- Aigarth ---
    aigarth_pop_size: int = 10
    aigarth_itu_size: int = 12
    aigarth_tick_cap: int = 20
    aigarth_mutation_wf_prob: float = 0.3
    aigarth_mutation_ws_prob: float = 0.1
    aigarth_mutation_wm_prob: float = 0.05

    # --- Simulation ---
    dt: float = 1.0
    simulation_steps: int = 100

    def __post_init__(self):
        # Ensure DSN kernel weights exist and match dsn_kernel_size.
        k = max(int(self.dsn_kernel_size), 1)
        if not self.dsn_kernel_weights:
            # Default triangular / recency-weighted causal kernel.
            w = [(i + 1.0) for i in range(k)]
        else:
            w = list(self.dsn_kernel_weights)[:k]
            if len(w) < k:
                w = w + [w[-1]] * (k - len(w))
        s = float(sum(abs(x) for x in w)) if w else 1.0
        if s <= 0:
            s = 1.0
        # Normalise (keep sign if user provided signed weights).
        self.dsn_kernel_weights = [float(x) / s for x in w]


# =============================================================================
# ENUMS
# =============================================================================

class NeuronType(Enum):
    INPUT = "input"
    HIDDEN = "hidden"
    OUTPUT = "output"

class SynapseType(Enum):
    IONOTROPIC_FAST = "ionotropic_fast"
    IONOTROPIC_SLOW = "ionotropic_slow"
    METABOTROPIC = "metabotropic"
    SILENT = "silent"

class TrinaryState(Enum):
    INHIBITORY = -1
    NEUTRAL = 0
    EXCITATORY = 1


# =============================================================================
# RECEPTOR SUBTYPE  (Algorithm 2)
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
# OSCILLATOR BANK  (Algorithm 2)
# =============================================================================

class OscillatorBank:
    """Multi-band oscillator (infraslow-gamma) with PAC."""

    DEFAULT_BANDS = {
        'infraslow': 0.05, 'slow': 0.5, 'theta': 6.0,
        'alpha': 10.0, 'gamma': 40.0,
    }

    def __init__(self, coupling: float = 0.15, bands: Optional[Dict[str, float]] = None):
        self.coupling = coupling
        self.bands: Dict[str, Dict[str, float]] = {}
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
# NEUROMODULATOR SYSTEM  (Algorithm 5)
# =============================================================================

class NeuromodulatorSystem:
    """4 neuromodulators with tonic/phasic, 9 receptor subtypes, crosstalk."""

    def __init__(self, params: NetworkParameters):
        self.params = params
        self.levels: Dict[str, Dict[str, float]] = {
            'DA':  {'tonic': params.dopamine_baseline,       'phasic': 0.0},
            '5HT': {'tonic': params.serotonin_baseline,      'phasic': 0.0},
            'ACh': {'tonic': params.acetylcholine_baseline,   'phasic': 0.0},
            'NA':  {'tonic': params.norepinephrine_baseline,  'phasic': 0.0},
        }
        st = float(params.receptor_slope_tonic)
        sp = float(params.receptor_slope_phasic)
        self.receptors: Dict[str, ReceptorSubtype] = {
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

    def get_flat_levels(self) -> Dict[str, float]:
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

    def update(self, network_activity: Dict[str, float], dt: float):
        p = self.params
        mean_act = network_activity.get('mean_activity', 0.0)
        exc_frac = network_activity.get('excitatory_fraction', 0.0)
        change_rate = network_activity.get('state_change_rate', 0.0)

        for key, bl_attr in [('DA', 'dopamine_baseline'), ('5HT', 'serotonin_baseline'),
                             ('ACh', 'acetylcholine_baseline'), ('NA', 'norepinephrine_baseline')]:
            baseline = getattr(p, bl_attr)
            self.levels[key]['tonic'] += dt / p.tau_tonic * (baseline - self.levels[key]['tonic'])
            self.levels[key]['phasic'] += dt / p.tau_phasic * (0.0 - self.levels[key]['phasic'])

        rr = p.neuromod_release_rate
        self.levels['DA']['phasic']  += rr * change_rate * dt
        self.levels['5HT']['tonic'] += rr * mean_act * dt
        self.levels['ACh']['phasic'] += rr * exc_frac * dt
        self.levels['NA']['phasic']  += rr * change_rate * dt

        # Crosstalk
        self.levels['ACh']['phasic'] *= max(0.0, 1.0 - 0.1 * self.levels['DA']['phasic'])
        self.levels['5HT']['tonic'] += 0.02 * (self.levels['NA']['tonic'] + self.levels['NA']['phasic']) * dt

        for key in self.levels:
            for comp in ('tonic', 'phasic'):
                self.levels[key][comp] = max(0.0, min(2.0, self.levels[key][comp]))

    def compute_receptor_activations(self) -> Dict[str, float]:
        activations: Dict[str, float] = {}
        for rname, receptor in self.receptors.items():
            parent = receptor.parent_modulator
            conc = self.levels[parent]['tonic'] if receptor.is_tonic else (
                self.levels[parent]['tonic'] + self.levels[parent]['phasic'])
            cap = float(getattr(self.params, 'receptor_concentration_cap', 1.0))
            if cap > 0.0:
                conc = max(0.0, min(cap, float(conc)))
            else:
                conc = max(0.0, float(conc))
            activations[rname] = receptor.compute_activation(conc)
        return activations

    def to_dict(self) -> dict:
        return {'levels': self.levels, 'receptors': {k: v.to_dict() for k, v in self.receptors.items()}}


# =============================================================================
# SYNAPSE  (Algorithm 3 + ChronoPlasticity from Algorithm 1 steps 1-4)
# =============================================================================

class Synapse:
    """Triple-weight synapse with ChronoPlasticity, STDP+DA gating, AGMP."""

    def __init__(self, pre_id: int, post_id: int, branch_id: int,
                 params: NetworkParameters):
        self.pre_id = pre_id
        self.post_id = post_id
        self.branch_id = branch_id
        self.params = params

        # Dendritic position index (assigned by network; used for neighbour distances d_ij)
        self.branch_index: int = 0

        self.w_fast = random.uniform(params.w_fast_init_min, params.w_fast_init_max)
        self.w_slow = random.uniform(params.w_slow_init_min, params.w_slow_init_max)
        self.w_meta = random.uniform(params.w_meta_init_min, params.w_meta_init_max)

        self.is_silent = random.random() < 0.1
        self.is_modulatory = random.random() < 0.2
        self.integrity = 1.0

        self.pre_trace = 0.0
        self.post_trace = 0.0
        self.recent_delta_w = 0.0

        # ChronoPlasticity (Eqs 5-7)
        self.chrono_fast_trace = 0.0
        self.chrono_slow_trace = 0.0
        self.chrono_omega = 0.5

        # AGMP eligibility (Eq 8)
        self.eligibility = 0.0

        self.synapse_type = self._determine_type()

    def _determine_type(self) -> SynapseType:
        if self.is_silent: return SynapseType.SILENT
        elif self.is_modulatory: return SynapseType.METABOTROPIC
        elif abs(self.w_fast) > abs(self.w_slow): return SynapseType.IONOTROPIC_FAST
        else: return SynapseType.IONOTROPIC_SLOW

    # ===== ALGORITHM 1 STEP 1: Synaptic Time Warping (Eqs 5-7) =====
    def update_chrono_traces(self, pre_state: int):
        """Learned warp factor omega_t controls slow trace decay.

        Note: In short runs with constant s_pre, Eq 5 can produce large steady-state traces
        (e.g., ~±20 for alpha_f=0.95). To prevent omega_t saturating at 0/1 and to keep
        Chrono traces numerically well-behaved, we apply:
          - bounded gating via tanh(z / gate_norm) in the omega_t controller
          - raw pre-sigmoid clipping
          - omega clamping and optional EMA smoothing
          - trace clipping
        """
        if not self.params.chrono_enabled:
            return
        p = self.params
        # Preserve trinary sign (paper uses s_pre ∈ {-1,0,1})
        s_pre = float(max(-1, min(1, int(pre_state))))

        # ---- Eq 7 (stabilized): omega_t = sigmoid(g([s_pre, z_{t-1}])) ----
        # Use a bounded view of the slow trace so large |z| does not pin omega_t.
        gate_norm = float(getattr(p, 'chrono_gate_norm', 10.0))
        if gate_norm <= 0:
            z_gate = self.chrono_slow_trace
        else:
            z_gate = math.tanh(self.chrono_slow_trace / gate_norm)

        raw = 2.0 * s_pre + 1.5 * z_gate - 1.0

        raw_clip = float(getattr(p, 'chrono_raw_clip', 8.0))
        if raw_clip > 0:
            raw = max(-raw_clip, min(raw_clip, raw))

        new_omega = 1.0 / (1.0 + math.exp(-raw))

        # Clamp away from 0/1 to avoid alpha_s**omega -> 1.0 (no decay) at omega=0.
        o_min = float(getattr(p, 'chrono_omega_min', 0.05))
        o_max = float(getattr(p, 'chrono_omega_max', 0.95))
        if o_max < o_min:
            o_min, o_max = o_max, o_min
        new_omega = max(o_min, min(o_max, new_omega))

        # Optional smoothing (EMA) to avoid abrupt flips.
        beta = float(getattr(p, 'chrono_omega_smoothing', 0.2))
        beta = max(0.0, min(1.0, beta))
        self.chrono_omega = (1.0 - beta) * self.chrono_omega + beta * new_omega

        # ---- Eq 5: f_t = alpha_f * f_{t-1} + s_pre ----
        self.chrono_fast_trace = p.chrono_alpha_f * self.chrono_fast_trace + s_pre

        # ---- Eq 6: z_t = alpha_s**omega_t * z_{t-1} + s_pre ----
        alpha_s_warped = p.chrono_alpha_s ** self.chrono_omega
        self.chrono_slow_trace = alpha_s_warped * self.chrono_slow_trace + s_pre

        # Clip traces to keep Chrono contributions bounded and avoid pathological omega_t.
        tclip = float(getattr(p, 'chrono_trace_clip', 10.0))
        if tclip > 0:
            self.chrono_fast_trace = max(-tclip, min(tclip, self.chrono_fast_trace))
            self.chrono_slow_trace = max(-tclip, min(tclip, self.chrono_slow_trace))

    def compute_input(self, pre_state: int) -> float:
        """Algorithm 1 line 4: warped multi-trace synaptic current."""
        if self.is_silent:
            return 0.0
        w_total = self.w_fast + self.w_slow
        base = w_total * pre_state
        if not self.params.chrono_enabled:
            return base
        p = self.params
        chrono_extra = (p.chrono_lambda_f * self.w_fast * self.chrono_fast_trace +
                        p.chrono_lambda_s * self.w_slow * self.chrono_slow_trace)
        return base + chrono_extra

    # ===== STDP + DA gating + associative (Algorithm 3) =====
    def update(self, pre_state: int, post_state: int,
               receptor_activations: Dict[str, float],
               neighbour_delta_ws: List[Tuple[float, float]], dt: float):
        p = self.params
        tau = p.tau_stdp

        self.update_chrono_traces(pre_state)

        # STDP traces
        self.pre_trace += (-self.pre_trace / tau + (1.0 if pre_state == 1 else 0.0)) * dt
        self.post_trace += (-self.post_trace / tau + (1.0 if post_state == 1 else 0.0)) * dt

        A_plus = self.pre_trace * (1.0 if post_state == 1 else 0.0)
        A_minus = self.post_trace * (1.0 if pre_state == 1 else 0.0)

        # Differential DA gating
        d1_act = receptor_activations.get('D1', 0.5)
        d2_act = receptor_activations.get('D2', 0.5)
        delta_w = p.learning_rate * A_plus * d1_act - p.learning_rate * A_minus * d2_act

        # Trinary-specific rules
        if pre_state == 1 and post_state == 1:
            delta_w += p.learning_rate * 0.5 * d1_act
        if pre_state == 1 and post_state == -1:
            delta_w -= p.learning_rate * 0.5 * d2_act
        if pre_state == 0 and post_state == 0:
            delta_w *= 0.1

        # Associative neighbour plasticity
        for neighbour_dw, distance in neighbour_delta_ws:
            if distance > 0:
                delta_w += p.associative_alpha * neighbour_dw / distance

        self.recent_delta_w = delta_w

        # Weight updates
        self.w_fast += dt / p.tau_fast * (-self.w_fast + 0.3 * delta_w)
        self.w_fast = max(-1.0, min(1.0, self.w_fast))

        self.w_slow += dt / p.tau_slow * (-self.w_slow + 0.1 * delta_w)
        self.w_slow = max(-1.0, min(1.0, self.w_slow))

        # Meta weight - 5-HT modulated
        ht2a = receptor_activations.get('5HT2A', 0.0)
        ht1a = receptor_activations.get('5HT1A', 0.0)
        serotonin_factor = 0.5 * ht2a + 0.1 * (1.0 - ht1a)
        self.w_meta += dt / p.tau_meta * (-self.w_meta + 0.05 * delta_w * serotonin_factor)
        self.w_meta = max(-0.5, min(0.5, self.w_meta))

        # Integrity
        if abs(self.w_fast) < 0.01 and abs(self.w_slow) < 0.01:
            self.integrity -= p.synapse_death_prob * dt
        else:
            self.integrity = min(1.0, self.integrity + 0.001 * dt)

        # Unsilence
        if self.is_silent and pre_state == 1 and post_state == 1:
            if random.random() < 0.05:
                self.is_silent = False
                self.synapse_type = self._determine_type()

    # ===== AGMP eligibility (Eq 8) =====
    def update_eligibility(self, pre_state: int, post_output: int, params: NetworkParameters):
        if not params.agmp_enabled:
            return
        psi = 0.0
        if pre_state == 1 and post_output == 1: psi = 1.0
        elif pre_state == 1 and post_output == -1: psi = -0.5
        elif pre_state == -1 and post_output == 1: psi = -0.3
        self.eligibility = params.agmp_lambda_e * self.eligibility + psi

    def get_modulatory_effect(self) -> float:
        return self.w_meta if self.is_modulatory else 0.0

    def to_dict(self) -> dict:
        return {
            'pre_id': self.pre_id, 'post_id': self.post_id, 'branch_id': self.branch_id,
            'branch_index': getattr(self, 'branch_index', 0),
            'w_fast': self.w_fast, 'w_slow': self.w_slow, 'w_meta': self.w_meta,
            'is_silent': self.is_silent, 'is_modulatory': self.is_modulatory,
            'integrity': self.integrity, 'synapse_type': self.synapse_type.value,
            'pre_trace': self.pre_trace, 'post_trace': self.post_trace,
            'chrono_fast_trace': self.chrono_fast_trace, 'chrono_slow_trace': self.chrono_slow_trace,
            'chrono_omega': self.chrono_omega, 'eligibility': self.eligibility,
        }


# =============================================================================
# MSTH: Multi-Scale Temporal Homeostasis (Section 5)
# =============================================================================

class MSTHState:
    """
    Four coordinated regulatory loops:
      Ultra-fast (~5ms): emergency suppression / runaway prevention
      Fast (~2s): rapid Ca2+/homeostatic control of excitability
      Medium (~5min): synaptic scaling / gain normalisation
      Slow (~1-24h): structural adjustments and long-horizon stability
    """

    def __init__(self, params: NetworkParameters):
        self.params = params
        self.ultrafast_activity = 0.0
        self.fast_excitability = 0.0
        self.medium_gain = 1.0
        self.slow_structural = 0.0

    def update(self, current_state_abs: float, dt: float) -> dict:
        p = self.params

        # Ultra-fast (~5ms): track bursts
        alpha_uf = dt / p.msth_ultrafast_tau
        self.ultrafast_activity = (1.0 - alpha_uf) * self.ultrafast_activity + alpha_uf * current_state_abs
        ultrafast_suppress = self.ultrafast_activity > p.msth_ultrafast_ceiling

        # Fast (~2s): calcium-like homeostatic excitability
        alpha_f = dt / p.msth_fast_tau
        self.fast_excitability = (1.0 - alpha_f) * self.fast_excitability + alpha_f * current_state_abs
        fast_threshold_shift = p.msth_fast_gain * (self.fast_excitability - p.target_firing_rate)

        # Medium (~5min): synaptic gain
        alpha_m = dt / p.msth_medium_tau
        target_dev = current_state_abs - p.target_firing_rate
        self.medium_gain += alpha_m * (-p.msth_medium_gain * target_dev * self.medium_gain)
        self.medium_gain = max(0.5, min(2.0, self.medium_gain))

        # Slow (~1h+): structural pressure
        alpha_s = dt / p.msth_slow_tau
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
# NEURAXON UNIT  (Algorithm 4 + Algorithm 1 pipeline)
# =============================================================================

class Neuraxon:
    """
    Bio-inspired trinary neuron. Full Algorithm 1 pipeline:
      Step 1: Synaptic time warping  (handled in Synapse)
      Step 2: DSN dynamic decay
      Step 3: CTSN complemented state
      Step 4: Trinary readout on s_tilde
      Step 5: AGMP  (handled in Network)
    Plus: dendritic integration, MSTH, homeostasis, spontaneous firing.
    """

    def __init__(self, neuron_id: int, neuron_type: NeuronType,
                 params: NetworkParameters):
        self.id = neuron_id
        self.type = neuron_type
        self.params = params

        self.state = 0.0
        self.trinary_state = 0
        self.adaptation = 0.0
        self.autoreceptor = 0.0

        # CTSN
        self.complement_h = 0.0
        self.state_tilde = 0.0

        # DSN
        self.dsn_input_buffer: List[float] = [0.0] * params.dsn_kernel_size
        self.dsn_alpha = 0.5

        # DSN kernel (learnable per-neuron; initialised from params)
        base_kernel = params.dsn_kernel_weights or []
        if len(base_kernel) != params.dsn_kernel_size:
            # Fallback to default triangular kernel (mirrors params.__post_init__)
            k = max(int(params.dsn_kernel_size), 1)
            base_kernel = [(i + 1.0) for i in range(k)]
            s = sum(abs(x) for x in base_kernel) or 1.0
            base_kernel = [float(x) / s for x in base_kernel]
        self.dsn_kernel_weights: List[float] = [float(x) for x in base_kernel]
        self._dsn_last_x: float = 0.0

        # CTSN phi parameters (learnable per-neuron; initialised from params)
        self.ctsn_phi_gain: float = float(params.ctsn_phi_gain)
        self.ctsn_phi_bias: float = float(params.ctsn_phi_bias)
        self._ctsn_last_x: float = 0.0
        self._ctsn_last_phi: float = 0.0

        # Dendritic
        self.branch_potentials = [0.0] * params.num_dendritic_branches

        # Homeostatic
        self.firing_rate_avg = params.target_firing_rate

        # MSTH
        self.msth = MSTHState(params)

        # AGMP astrocyte
        self.astrocyte_state = 0.0

        # Health
        self.health = 1.0
        self.is_active = True
        self.prev_state = 0

        self.state_history: List[int] = []
        self.potential_history: List[float] = []

    @property
    def membrane_potential(self) -> float:
        return self.state
    @membrane_potential.setter
    def membrane_potential(self, value: float):
        self.state = value

    def dendritic_integration(self, inputs_by_branch: Dict[int, List[float]]) -> float:
        """Algorithm 4 lines 4-15: nonlinear dendritic branches."""
        p = self.params
        total = 0.0
        for b in range(p.num_dendritic_branches):
            branch_inputs = inputs_by_branch.get(b, [])
            sigma_b = sum(branch_inputs)
            self.branch_potentials[b] = sigma_b
            if abs(sigma_b) > p.dendritic_spike_threshold:
                sign = 1.0 if sigma_b > 0 else -1.0
                total += sign * (abs(sigma_b) ** p.dendritic_supralinear_gamma)
            else:
                total += sigma_b
        return total

    def _compute_dsn_alpha(self, current_input: float) -> float:
        """Algorithm 1 lines 5-6: alpha_t = Sigmoid(CausalConv1D(X_{t-k+1:t}))"""
        if not self.params.dsn_enabled:
            return 0.5

        # Maintain causal buffer of the driving input stream X(t)
        self.dsn_input_buffer.pop(0)
        self.dsn_input_buffer.append(float(current_input))

        # CausalConv1D: dot(kernel, buffer) + bias
        kernel = getattr(self, 'dsn_kernel_weights', []) or []
        if len(kernel) != len(self.dsn_input_buffer):
            # Fallback: re-initialise to a safe triangular kernel
            k = max(int(self.params.dsn_kernel_size), 1)
            kernel = [(i + 1.0) for i in range(k)]
            s = sum(abs(x) for x in kernel) or 1.0
            kernel = [float(x) / s for x in kernel]
            self.dsn_kernel_weights = kernel

        conv_out = sum(w * x for w, x in zip(kernel, self.dsn_input_buffer)) + float(self.params.dsn_bias)

        # Paper form: alpha_t = sigmoid(conv_out)
        exponent = max(-50.0, min(50.0, -conv_out))
        self.dsn_alpha = 1.0 / (1.0 + math.exp(exponent))

        # Optional online learning for DSN kernel weights (minimal, local rule)
        # Goal: make alpha_t high when input stream is stable, low when it changes abruptly.
        if self.params.dsn_learn_enabled and self.type != NeuronType.INPUT:
            buf = self.dsn_input_buffer
            if len(buf) >= 2:
                delta_x = abs(buf[-1] - buf[-2])
            else:
                delta_x = abs(buf[-1]) if buf else 0.0

            # target_alpha = sigmoid(bias - sensitivity * |ΔX|)
            t = float(self.params.dsn_target_bias) - float(self.params.dsn_target_sensitivity) * float(delta_x)
            t_exp = max(-50.0, min(50.0, -t))
            target_alpha = 1.0 / (1.0 + math.exp(t_exp))

            err = (self.dsn_alpha - target_alpha)
            dalpha = self.dsn_alpha * (1.0 - self.dsn_alpha)  # d sigmoid
            common = err * dalpha

            lr = float(self.params.dsn_learn_lr)
            clip = float(self.params.dsn_kernel_clip)

            new_kernel = []
            for w, x in zip(kernel, buf):
                nw = float(w) - lr * common * float(x)
                # Safety clip before renormalisation
                nw = max(-clip, min(clip, nw))
                new_kernel.append(nw)

            # Renormalise (L1 over absolute values) for stability
            s = sum(abs(x) for x in new_kernel) or 1.0
            new_kernel = [float(x) / s for x in new_kernel]
            self.dsn_kernel_weights = new_kernel

        return self.dsn_alpha

    def _update_complement(self, x_t: float):
        """Algorithm 1 lines 7-8: h_t, s_tilde(t) = s(t) + h(t)

        Paper note: phi_h(X(t)) is a lightweight learnable filter. Here we implement a
        parameterised proxy: tanh(gain * X(t) + bias).
        """
        if not self.params.ctsn_enabled:
            self.complement_h = 0.0
            return
        rho = float(self.params.ctsn_rho)
        phi = math.tanh(float(self.ctsn_phi_gain) * float(x_t) + float(self.ctsn_phi_bias))
        self._ctsn_last_x = float(x_t)
        self._ctsn_last_phi = float(phi)
        self.complement_h = rho * self.complement_h + (1.0 - rho) * phi

    def update(self, inputs_by_branch: Dict[int, List[float]],
               modulatory_inputs: List[float], external_input: float,
               osc_drive: float, receptor_activations: Dict[str, float], dt: float):
        """Full Neuraxon update: Alg 4 + Alg 1 Steps 2-4 + MSTH."""
        if not self.is_active:
            return
        p = self.params

        # Dendritic integration (Alg 4 line 17)
        D = self.dendritic_integration(inputs_by_branch)
        total_input_mag = abs(D) + abs(external_input)

        # Homeostatic rate tracking (Alg 4 line 19)
        self.firing_rate_avg += p.firing_rate_alpha * (
            abs(self.trinary_state) - self.firing_rate_avg) * dt

        # MSTH update (Section 5)
        msth_signals = self.msth.update(abs(self.trinary_state), dt)

        # NA-modulated gain + spontaneous (Alg 4 lines 21-22)
        beta1_act = receptor_activations.get('beta1', 0.0)
        alpha2_act = receptor_activations.get('alpha2', 0.0)
        g_NA = 1.0 + 0.5 * beta1_act + 0.2 * alpha2_act
        spontaneous = 0.0
        spont_rate = p.spontaneous_firing_rate + 0.3 * alpha2_act
        if random.random() < spont_rate * dt:
            spontaneous = random.gauss(0.0, 0.3)

        # === ALG 1 STEP 2: DSN Dynamic Decay ===
        D_scaled = D * msth_signals['medium_gain']
        raw_input = g_NA * D_scaled + external_input + osc_drive - self.adaptation + spontaneous
        alpha_t = self._compute_dsn_alpha(raw_input)
        self.state = alpha_t * self.state + (1.0 - alpha_t) * raw_input

        # MSTH ultra-fast: emergency suppression
        if msth_signals['ultrafast_suppress']:
            self.state *= 0.5

        # === ALG 1 STEP 3: CTSN Complement ===
        self._update_complement(raw_input)
        self.state_tilde = self.state + self.complement_h

        # Saturated Modulation + Homeostasis (Eq 1 / Alg 4 lines 25-29)
        raw_mod = sum(modulatory_inputs)
        raw_mod += 0.3 * receptor_activations.get('M1', 0.0) - 0.2 * receptor_activations.get('M2', 0.0)
        delta_theta_meta = p.threshold_mod_k * math.tanh(raw_mod)
        delta_theta_homeo = p.homeostatic_rate * (self.firing_rate_avg - p.target_firing_rate)
        delta_theta_fast = msth_signals['fast_threshold_shift']

        theta_eff1 = p.firing_threshold_excitatory - delta_theta_meta + delta_theta_homeo + delta_theta_fast - 0.1 * self.autoreceptor
        theta_eff2 = p.firing_threshold_inhibitory - delta_theta_meta + delta_theta_homeo + delta_theta_fast + 0.1 * self.autoreceptor

        # === ALG 1 STEP 4: Trinary readout on s_tilde ===
        self.prev_state = self.trinary_state
        if self.state_tilde > theta_eff1:
            self.trinary_state = 1
        elif self.state_tilde < theta_eff2:
            self.trinary_state = -1
        else:
            self.trinary_state = 0

        # Optional online learning for CTSN phi parameters (minimal, local rule)
        # Uses homeostatic error as a proxy learning signal to shape phi_h(X(t)).
        if p.ctsn_learn_enabled and p.ctsn_enabled and self.type != NeuronType.INPUT:
            e = float(p.target_firing_rate) - float(self.firing_rate_avg)
            rho = float(p.ctsn_rho)
            x = float(getattr(self, '_ctsn_last_x', raw_input))
            phi = float(getattr(self, '_ctsn_last_phi', math.tanh(self.ctsn_phi_gain * x + self.ctsn_phi_bias)))

            dphi = 1.0 - phi * phi  # d/dz tanh(z)
            scale = (1.0 - rho)
            lr = float(p.ctsn_learn_lr)

            self.ctsn_phi_gain += lr * e * scale * dphi * x
            self.ctsn_phi_bias += lr * e * scale * dphi

            gclip = float(p.ctsn_phi_gain_clip)
            bclip = float(p.ctsn_phi_bias_clip)
            self.ctsn_phi_gain = max(-gclip, min(gclip, self.ctsn_phi_gain))
            self.ctsn_phi_bias = max(-bclip, min(bclip, self.ctsn_phi_bias))

        # Adaptation (Alg 4 line 31)
        self.adaptation += dt / p.adaptation_tau * (-self.adaptation + 0.1 * abs(self.trinary_state))
        # Autoreceptor (Alg 4 line 32)
        self.autoreceptor += dt / p.autoreceptor_tau * (-self.autoreceptor + 0.2 * self.trinary_state)
        # AGMP astrocyte (Eq 9)
        if p.agmp_enabled:
            self.astrocyte_state = p.agmp_lambda_a * self.astrocyte_state + (1.0 - p.agmp_lambda_a) * abs(self.state_tilde)

        # Health
        if abs(self.state) / 2.0 < 0.01:
            self.health -= p.neuron_health_decay * dt
        else:
            self.health = min(1.0, self.health + 0.0005 * dt)
        if self.type == NeuronType.HIDDEN and self.health < p.neuron_death_threshold:
            if random.random() < 0.001:
                self.is_active = False

        self.state_history.append(self.trinary_state)
        self.potential_history.append(self.state)
        if len(self.state_history) > 1000:
            self.state_history.pop(0)
            self.potential_history.pop(0)

    def set_state(self, state: int):
        if state in (-1, 0, 1):
            # Mirror the non-input update path: preserve previous trinary for change-rate tracking.
            self.prev_state = self.trinary_state
            self.trinary_state = state
            self.state = state * self.params.firing_threshold_excitatory
            self.state_tilde = self.state + self.complement_h

    def to_dict(self) -> dict:
        return {
            'id': self.id, 'type': self.type.value,
            'membrane_potential': self.state, 'trinary_state': self.trinary_state,
            'prev_state': getattr(self, 'prev_state', 0),
            'adaptation': self.adaptation, 'autoreceptor': self.autoreceptor,
            'complement_h': self.complement_h, 'state_tilde': self.state_tilde,
            'dsn_alpha': getattr(self, 'dsn_alpha', 0.5),
            'dsn_input_buffer': getattr(self, 'dsn_input_buffer', []),
            'dsn_kernel_weights': getattr(self, 'dsn_kernel_weights', []),
            'ctsn_phi_gain': getattr(self, 'ctsn_phi_gain', self.params.ctsn_phi_gain),
            'ctsn_phi_bias': getattr(self, 'ctsn_phi_bias', self.params.ctsn_phi_bias),
            'firing_rate_avg': self.firing_rate_avg, 'astrocyte_state': self.astrocyte_state,
            'msth': self.msth.to_dict(), 'health': self.health, 'is_active': self.is_active,
        }


# =============================================================================
# NEURAXON NETWORK  (Algorithm 6)
# =============================================================================

class NeuraxonNetwork:
    """Complete Neuraxon v2.0 network with all subsystems."""

    def __init__(self, params: Optional[NetworkParameters] = None):
        self.params = params or NetworkParameters()
        self.input_neurons: List[Neuraxon] = []
        self.hidden_neurons: List[Neuraxon] = []
        self.output_neurons: List[Neuraxon] = []
        self.all_neurons: List[Neuraxon] = []
        self.synapses: List[Synapse] = []

        self.neuromod_system = NeuromodulatorSystem(self.params)
        self.oscillators = OscillatorBank(coupling=self.params.oscillator_coupling)
        self.neuromodulators: Dict[str, float] = self.neuromod_system.get_flat_levels()

        self.time = 0.0
        self.step_count = 0
        self.energy_usage = 0.0

        self._initialize_neurons()
        self._initialize_synapses_watts_strogatz()

    def _initialize_neurons(self):
        nid = 0
        for _ in range(self.params.num_input_neurons):
            self.input_neurons.append(Neuraxon(nid, NeuronType.INPUT, self.params))
            self.all_neurons.append(self.input_neurons[-1]); nid += 1
        for _ in range(self.params.num_hidden_neurons):
            self.hidden_neurons.append(Neuraxon(nid, NeuronType.HIDDEN, self.params))
            self.all_neurons.append(self.hidden_neurons[-1]); nid += 1
        for _ in range(self.params.num_output_neurons):
            self.output_neurons.append(Neuraxon(nid, NeuronType.OUTPUT, self.params))
            self.all_neurons.append(self.output_neurons[-1]); nid += 1

    def _initialize_synapses_watts_strogatz(self):
        N = len(self.all_neurons)
        if N == 0: return
        k = min(self.params.ws_k, N - 1)
        half_k = max(k // 2, 1)
        beta = self.params.ws_beta
        B = self.params.num_dendritic_branches
        edge_set = set()

        for i in range(N):
            for j in range(1, half_k + 1):
                for target in [(i + j) % N, (i - j) % N]:
                    pre_type = self.all_neurons[i].type
                    post_type = self.all_neurons[target].type
                    pre_id = self.all_neurons[i].id
                    post_id = self.all_neurons[target].id
                    if pre_type == NeuronType.OUTPUT and post_type == NeuronType.INPUT:
                        continue
                    if pre_id != post_id:
                        edge_set.add((pre_id, post_id))

        edges_list = list(edge_set)
        for pre_id, post_id in edges_list:
            if random.random() < beta:
                edge_set.discard((pre_id, post_id))
                new_target = random.randint(0, N - 1)
                new_post_id = self.all_neurons[new_target].id
                new_post_type = self.all_neurons[new_target].type
                pre_idx = next(i for i, n in enumerate(self.all_neurons) if n.id == pre_id)
                pre_type = self.all_neurons[pre_idx].type
                if (new_post_id != pre_id and (pre_id, new_post_id) not in edge_set and
                        not (pre_type == NeuronType.OUTPUT and new_post_type == NeuronType.INPUT)):
                    edge_set.add((pre_id, new_post_id))
                else:
                    edge_set.add((pre_id, post_id))

        for pre_id, post_id in edge_set:
            branch = random.randint(0, B - 1)
            self.synapses.append(Synapse(pre_id, post_id, branch, self.params))

        self._assign_branch_positions()

    def _assign_branch_positions(self):
        """Assign a stable position index along each (post_id, branch_id) dendrite.

        This implements d_ij for Algorithm 3 neighbour plasticity, so that nearby synapses
        on the same dendrite have stronger associative coupling.
        """
        groups: Dict[Tuple[int, int], List[Synapse]] = {}
        for syn in self.synapses:
            groups.setdefault((syn.post_id, syn.branch_id), []).append(syn)

        for syns in groups.values():
            syns_sorted = sorted(syns, key=lambda s: (s.pre_id, s.post_id))
            for pos, syn in enumerate(syns_sorted):
                syn.branch_index = pos

    def _compute_network_activity(self) -> Dict[str, float]:
        active = [n for n in self.all_neurons if n.is_active]
        if not active:
            return {'mean_activity': 0.0, 'excitatory_fraction': 0.0, 'state_change_rate': 0.0}
        states = [n.trinary_state for n in active]
        return {
            'mean_activity': sum(abs(s) for s in states) / len(states),
            'excitatory_fraction': sum(1 for s in states if s == 1) / len(states),
            'state_change_rate': sum(1 for n in active if n.trinary_state != n.prev_state) / len(active),
        }

    def _neuron_by_id(self, nid: int) -> Optional[Neuraxon]:
        return self.all_neurons[nid] if 0 <= nid < len(self.all_neurons) else None

    def simulate_step(self, external_inputs: Optional[Dict[int, float]] = None):
        """
        One full network step implementing Algorithm 1 pipeline:
          Step 1: Synaptic Time Warping (in Synapse.compute_input)
          Step 2: DSN Dynamic Decay (in Neuraxon.update)
          Step 3: CTSN Complement (in Neuraxon.update)
          Step 4: Trinary Readout (in Neuraxon.update)
          Step 5: AGMP Astrocyte-Gated Plasticity (below)
        """
        external_inputs = external_inputs or {}
        p = self.params; dt = p.dt

        # Neuromodulator + oscillator update
        activity = self._compute_network_activity()
        self.neuromod_system.update(activity, dt)
        R = self.neuromod_system.compute_receptor_activations()
        self.neuromodulators = self.neuromod_system.get_flat_levels()
        self.oscillators.update(dt)
        N = len(self.all_neurons)

        # Collect inputs by dendritic branch (Step 1 happens in compute_input)
        branch_inputs: Dict[int, Dict[int, List[float]]] = {
            n.id: {b: [] for b in range(p.num_dendritic_branches)} for n in self.all_neurons}
        mod_inputs: Dict[int, List[float]] = {n.id: [] for n in self.all_neurons}

        for syn in self.synapses:
            if syn.integrity <= 0: continue
            pre = self._neuron_by_id(syn.pre_id)
            if pre is None or not pre.is_active: continue
            inp = syn.compute_input(pre.trinary_state)
            branch_inputs[syn.post_id][syn.branch_id].append(inp)
            me = syn.get_modulatory_effect()
            if me != 0.0:
                mod_inputs[syn.post_id].append(me)

        # Update neurons (*** INPUT NEURONS SKIP ODE — hold their set state ***)
        for neuron in self.all_neurons:
            if not neuron.is_active: continue
            if neuron.type == NeuronType.INPUT:
                # Mirror Neuraxon.update() bookkeeping so state_change_rate is meaningful for inputs too.
                neuron.prev_state = neuron.trinary_state
                ext = external_inputs.get(neuron.id, 0.0)
                if ext != 0.0:
                    neuron.set_state(int(max(-1, min(1, round(ext)))))
                continue  # <-- CRITICAL: inputs are NOT updated by the ODE
            ext = external_inputs.get(neuron.id, 0.0)
            osc = self.oscillators.get_drive(neuron.id, N)
            neuron.update(branch_inputs[neuron.id], mod_inputs[neuron.id], ext, osc, R, dt)

        # Update synapses
        branch_synapses: Dict[Tuple[int, int], List[Synapse]] = {}
        for syn in self.synapses:
            branch_synapses.setdefault((syn.post_id, syn.branch_id), []).append(syn)

        for syn in self.synapses:
            if syn.integrity <= 0: continue
            pre = self._neuron_by_id(syn.pre_id)
            post = self._neuron_by_id(syn.post_id)
            if pre is None or post is None or not pre.is_active or not post.is_active: continue
            neighbours = [(o.recent_delta_w, abs(o.branch_index - syn.branch_index) + 1.0)
                          for o in branch_synapses.get((syn.post_id, syn.branch_id), []) if o is not syn]
            syn.update(pre.trinary_state, post.trinary_state, R, neighbours, dt)

            # === ALG 1 STEP 5: AGMP ===
            if p.agmp_enabled:
                syn.update_eligibility(pre.trinary_state, post.trinary_state, p)
                m_t = self.neuromod_system.levels['DA']['phasic']
                a_t = post.astrocyte_state
                delta_agmp = p.agmp_eta * m_t * a_t * syn.eligibility
                syn.w_fast = max(-1.0, min(1.0, syn.w_fast + delta_agmp * 0.3))
                syn.w_slow = max(-1.0, min(1.0, syn.w_slow + delta_agmp * 0.1))

        # Homeostatic synaptic scaling
        for neuron in self.all_neurons:
            if not neuron.is_active or neuron.type == NeuronType.INPUT: continue
            scale = 1.0 + p.homeostatic_rate * (p.target_firing_rate - neuron.firing_rate_avg) * neuron.msth.medium_gain
            for syn in self.synapses:
                if syn.post_id == neuron.id and syn.integrity > 0:
                    syn.w_fast = max(-1.0, min(1.0, syn.w_fast * scale))
                    syn.w_slow = max(-1.0, min(1.0, syn.w_slow * scale))

        self._apply_structural_plasticity()
        active_count = sum(1 for n in self.all_neurons if n.is_active and n.trinary_state != 0)
        self.energy_usage += 0.01 * active_count * dt
        self.time += dt
        self.step_count += 1

    def _apply_structural_plasticity(self):
        p = self.params
        self.synapses = [s for s in self.synapses if s.integrity > p.synapse_integrity_threshold]
        for n in self.hidden_neurons:
            if n.is_active and n.health < p.neuron_death_threshold:
                if random.random() < 0.001: n.is_active = False
        avg_slow = 0.0
        ah = [n for n in self.hidden_neurons if n.is_active]
        if ah: avg_slow = sum(n.msth.slow_structural for n in ah) / len(ah)
        if random.random() < p.synapse_formation_prob * (1.0 + avg_slow):
            active_neurons = [n for n in self.all_neurons if n.is_active]
            if len(active_neurons) >= 2:
                pre = random.choice(active_neurons)
                post = random.choice(active_neurons)
                if (pre.id != post.id and
                        not (pre.type == NeuronType.OUTPUT and post.type == NeuronType.INPUT) and
                        not any(s.pre_id == pre.id and s.post_id == post.id for s in self.synapses)):
                    self.synapses.append(Synapse(pre.id, post.id,
                                                 random.randint(0, p.num_dendritic_branches - 1), p))

        # Recompute dendritic positions for neighbour plasticity after structural changes
        self._assign_branch_positions()

    def set_input_states(self, states: List[int]):
        for i, state in enumerate(states[:len(self.input_neurons)]):
            self.input_neurons[i].set_state(state)

    def get_output_states(self) -> List[int]:
        return [n.trinary_state for n in self.output_neurons if n.is_active]

    def get_all_states(self) -> Dict[str, List[int]]:
        return {
            'input': [n.trinary_state for n in self.input_neurons],
            'hidden': [n.trinary_state for n in self.hidden_neurons if n.is_active],
            'output': [n.trinary_state for n in self.output_neurons if n.is_active],
        }

    def modulate(self, neuromodulator: str, level: float):
        self.neuromod_system.set_level(neuromodulator, level)
        self.neuromodulators = self.neuromod_system.get_flat_levels()

    def get_energy(self) -> float:
        return self.energy_usage

    def to_dict(self) -> dict:
        return {
            'version': '2.0', 'parameters': asdict(self.params),
            'neurons': {
                'input': [n.to_dict() for n in self.input_neurons],
                'hidden': [n.to_dict() for n in self.hidden_neurons],
                'output': [n.to_dict() for n in self.output_neurons],
            },
            'synapses': [s.to_dict() for s in self.synapses],
            'neuromodulator_system': self.neuromod_system.to_dict(),
            'oscillators': self.oscillators.to_dict(),
            'neuromodulators': self.neuromodulators,
            'time': self.time, 'step_count': self.step_count, 'energy_usage': self.energy_usage,
        }


# =============================================================================
# AIGARTH ITU  (Algorithm 7)
# =============================================================================

class AigarthITU:
    def __init__(self, size: int, num_inputs: int, num_outputs: int, params: NetworkParameters):
        self.size = size; self.num_inputs = num_inputs; self.num_outputs = num_outputs
        self.params = params; self.neurons: List[Neuraxon] = []
        num_hidden = size - num_inputs - num_outputs
        assert num_hidden >= 0
        nid = 0
        for _ in range(num_inputs):
            self.neurons.append(Neuraxon(nid, NeuronType.INPUT, params)); nid += 1
        for _ in range(num_hidden):
            self.neurons.append(Neuraxon(nid, NeuronType.HIDDEN, params)); nid += 1
        for _ in range(num_outputs):
            self.neurons.append(Neuraxon(nid, NeuronType.OUTPUT, params)); nid += 1
        self.circle_weights = [random.choice([-1, 0, 1]) for _ in range(size)]
        self.input_skew = random.uniform(-0.5, 0.5)
        self.fitness = 0.0

    def feedforward(self, input_vec: List[int], tick_cap: int = 20) -> List[int]:
        for i, val in enumerate(input_vec[:self.num_inputs]):
            self.neurons[i].set_state(val)
        prev_outputs = None
        for tick in range(tick_cap):
            for j in range(self.num_inputs, self.size):
                left = (j - 1) % self.size; right = (j + 1) % self.size
                sigma = (self.circle_weights[left] * self.neurons[left].trinary_state +
                         self.circle_weights[right] * self.neurons[right].trinary_state + self.input_skew)
                self.neurons[j].trinary_state = 1 if sigma > 0.5 else (-1 if sigma < -0.5 else 0)
            outputs = [self.neurons[self.size - self.num_outputs + i].trinary_state for i in range(self.num_outputs)]
            if outputs == prev_outputs: break
            prev_outputs = outputs[:]
        return [self.neurons[self.size - self.num_outputs + i].trinary_state for i in range(self.num_outputs)]

    def mutate(self):
        if self.size == 0: return
        idx = random.randint(0, self.size - 1)
        self.circle_weights[idx] += random.choice([-1, 1])
        if abs(self.circle_weights[idx]) > 1:
            self.circle_weights[idx] = max(-1, min(1, self.circle_weights[idx]))
            if self.size > self.num_inputs + self.num_outputs:
                si = (idx + 1) % self.size
                if self.neurons[si].type == NeuronType.HIDDEN:
                    new_nid = max(n.id for n in self.neurons) + 1
                    nn = Neuraxon(new_nid, NeuronType.HIDDEN, self.params)
                    nn.state = self.neurons[si].state
                    self.neurons.insert(si + 1, nn)
                    self.circle_weights.insert(si + 1, random.choice([-1, 0, 1]))
                    self.size += 1
        to_rm = [i for i in range(self.num_inputs, self.size - self.num_outputs)
                 if self.circle_weights[i] == 0 and self.neurons[i].health < 0.3
                 and self.neurons[i].type == NeuronType.HIDDEN]
        for i in reversed(to_rm):
            self.neurons.pop(i); self.circle_weights.pop(i); self.size -= 1


class NeuraxonAigarthHybrid:
    def __init__(self, params: NetworkParameters):
        self.params = params
        self.population = [AigarthITU(params.aigarth_itu_size, params.num_input_neurons,
                                      params.num_output_neurons, params) for _ in range(params.aigarth_pop_size)]

    def evaluate_fitness(self, dataset):
        for itu in self.population:
            score = 0.0
            for inp, expected in dataset:
                output = itu.feedforward(inp, self.params.aigarth_tick_cap)
                score += sum(1 for a, b in zip(output, expected) if a == b) / max(len(expected), 1)
            itu.fitness = score / max(len(dataset), 1)

    def evolve(self, dataset, seasons=5, episodes=10):
        for _ in range(seasons):
            for _ in range(episodes):
                self.evaluate_fitness(dataset)
                self.population.sort(key=lambda x: x.fitness, reverse=True)
                half = len(self.population) // 2
                for i in range(half, len(self.population)):
                    child = copy.deepcopy(self.population[i % half])
                    child.mutate()
                    for neuron in child.neurons:
                        if random.random() < self.params.aigarth_mutation_wf_prob:
                            neuron.state += random.gauss(0, 0.15)
                    self.population[i] = child
        self.evaluate_fitness(dataset)
        self.population.sort(key=lambda x: x.fitness, reverse=True)

    def best(self): return self.population[0]


# =============================================================================
# APPLICATION LAYER  (Algorithm 8)
# =============================================================================

class NeuraxonApplication:
    def __init__(self, params=None):
        self.params = params or NetworkParameters()
        self.network = NeuraxonNetwork(self.params)
        self.patterns: Dict[str, List[int]] = {}

    def present_pattern(self, pattern, steps=10):
        self.network.set_input_states(pattern)
        for _ in range(steps):
            self.network.simulate_step()

    def store_pattern(self, name, pattern, steps=20):
        self.patterns[name] = pattern
        self.present_pattern(pattern, steps)

    def recall_pattern(self, name, steps=20, mask_fraction=0.5):
        if name not in self.patterns: return []
        partial = [0 if random.random() < mask_fraction else v for v in self.patterns[name]]
        self.present_pattern(partial, steps)
        return self.network.get_output_states()

    def train_sequence(self, sequence, repetitions=5, steps_per=10):
        for _ in range(repetitions):
            for pattern in sequence:
                self.present_pattern(pattern, steps_per)

    def get_network(self): return self.network


# =============================================================================
# JSON SAVE / LOAD
# =============================================================================

def save_network(network: NeuraxonNetwork, filename: str):
    with open(filename, 'w') as f:
        json.dump(network.to_dict(), f, indent=2)
    print(f"Network saved to {filename}")

def load_network(filename: str) -> NeuraxonNetwork:
    with open(filename, 'r') as f:
        data = json.load(f)
    param_data = data.get('parameters', {})
    defaults = asdict(NetworkParameters())
    for key, val in defaults.items():
        if key not in param_data: param_data[key] = val
    params = NetworkParameters(**param_data)
    network = NeuraxonNetwork(params)

    def _restore(nlist, dlist):
        for nd in dlist:
            for n in nlist:
                if n.id == nd['id']:
                    n.state = nd.get('membrane_potential', 0.0)
                    n.trinary_state = nd.get('trinary_state', 0)
                    n.prev_state = nd.get('prev_state', n.trinary_state)
                    # Restore DSN internal state for continuity (optional in older saves)
                    n.dsn_alpha = nd.get('dsn_alpha', getattr(n, 'dsn_alpha', 0.5))
                    buf = nd.get('dsn_input_buffer', None)
                    if isinstance(buf, list) and len(buf) > 0:
                        k = max(int(params.dsn_kernel_size), 1)
                        buf = [float(x) for x in buf][-k:]
                        if len(buf) < k:
                            buf = [0.0] * (k - len(buf)) + buf
                        n.dsn_input_buffer = buf
                    # Restore per-neuron DSN kernel weights (optional in older saves)
                    kw = nd.get('dsn_kernel_weights', None)
                    if isinstance(kw, list) and len(kw) > 0:
                        k = max(int(params.dsn_kernel_size), 1)
                        kw = [float(x) for x in kw][-k:]
                        if len(kw) < k:
                            kw = [0.0] * (k - len(kw)) + kw
                        # Renormalise L1 abs for stability
                        s = sum(abs(x) for x in kw) or 1.0
                        n.dsn_kernel_weights = [float(x) / s for x in kw]
                    else:
                        n.dsn_kernel_weights = list(params.dsn_kernel_weights or [])

                    # Restore per-neuron CTSN phi parameters (optional in older saves)
                    n.ctsn_phi_gain = float(nd.get('ctsn_phi_gain', params.ctsn_phi_gain))
                    n.ctsn_phi_bias = float(nd.get('ctsn_phi_bias', params.ctsn_phi_bias))
                    n.health = nd.get('health', 1.0)
                    n.is_active = nd.get('is_active', True)
                    n.adaptation = nd.get('adaptation', 0.0)
                    n.autoreceptor = nd.get('autoreceptor', 0.0)
                    n.complement_h = nd.get('complement_h', 0.0)
                    n.firing_rate_avg = nd.get('firing_rate_avg', params.target_firing_rate)
                    n.astrocyte_state = nd.get('astrocyte_state', 0.0)
                    md = nd.get('msth', {})
                    if md:
                        n.msth.ultrafast_activity = md.get('ultrafast_activity', 0.0)
                        n.msth.fast_excitability = md.get('fast_excitability', 0.0)
                        n.msth.medium_gain = md.get('medium_gain', 1.0)
                        n.msth.slow_structural = md.get('slow_structural', 0.0)
                    break

    _restore(network.input_neurons, data['neurons'].get('input', []))
    _restore(network.hidden_neurons, data['neurons'].get('hidden', []))
    _restore(network.output_neurons, data['neurons'].get('output', []))

    network.synapses = []
    for sd in data.get('synapses', []):
        syn = Synapse(sd['pre_id'], sd['post_id'],
                      sd.get('branch_id', random.randint(0, params.num_dendritic_branches-1)), params)
        for attr in ['w_fast','w_slow','w_meta','is_silent','is_modulatory','integrity',
                     'pre_trace','post_trace','chrono_fast_trace','chrono_slow_trace','chrono_omega','eligibility']:
            if attr in sd: setattr(syn, attr, sd[attr])
        if 'synapse_type' in sd:
            try:
                syn.synapse_type = SynapseType(sd['synapse_type'])
            except Exception:
                pass
        if 'branch_index' in sd:
            try:
                syn.branch_index = int(sd['branch_index'])
            except Exception:
                syn.branch_index = 0
        network.synapses.append(syn)

    # Ensure dendritic positions are valid for neighbour plasticity
    if hasattr(network, '_assign_branch_positions'):
        network._assign_branch_positions()

    nm = data.get('neuromodulator_system', {})
    if 'levels' in nm:
        for k in network.neuromod_system.levels:
            if k in nm['levels']: network.neuromod_system.levels[k] = nm['levels'][k]
    elif 'neuromodulators' in data:
        lm = {'dopamine':'DA','serotonin':'5HT','acetylcholine':'ACh','norepinephrine':'NA'}
        for name, key in lm.items():
            if name in data['neuromodulators']:
                network.neuromod_system.levels[key]['tonic'] = data['neuromodulators'][name]

        # Restore oscillator bank state (phases/amplitudes) if present
    osc = data.get('oscillators', None)
    if isinstance(osc, dict):
        try:
            if 'coupling' in osc: network.oscillators.coupling = float(osc['coupling'])
            if 'bands' in osc and isinstance(osc['bands'], dict):
                # Shallow replace; keeps expected structure {'freq','phase','amplitude'} per band
                network.oscillators.bands = osc['bands']
        except Exception:
            pass

    # Restore receptor activations (optional; they will be recomputed anyway)
    if isinstance(nm, dict) and 'receptors' in nm and isinstance(nm['receptors'], dict):
        for rname, rd in nm['receptors'].items():
            if rname in network.neuromod_system.receptors and isinstance(rd, dict):
                try:
                    network.neuromod_system.receptors[rname].activation = float(rd.get('activation', network.neuromod_system.receptors[rname].activation))
                except Exception:
                    pass

    network.neuromodulators = network.neuromod_system.get_flat_levels()
    network.time = data.get('time', 0.0)
    network.step_count = data.get('step_count', 0)
    network.energy_usage = data.get('energy_usage', 0.0)
    print(f"Network loaded from {filename}")
    return network


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":
    random.seed(10)
    print("=" * 70)
    print("NEURAXON v2.0 — Bio-Inspired Neural Network")
    print("Pipeline: Time Warping -> Dynamic Decay -> CTSN -> AGMP")
    print("=" * 70)

    params = NetworkParameters()
    params = NetworkParameters()
    params.dsn_learn_enabled = True
    params.ctsn_learn_enabled = True

    # (optional) tune learning rates
    params.dsn_learn_lr = 0.002
    params.ctsn_learn_lr = 0.001

    # Reduce Chrono strength
    params.chrono_trace_clip = 6.0
    params.chrono_lambda_f *= 0.5
    params.chrono_lambda_s *= 0.5


    # Make MSTH less suppressive (depending on implementation)
    params.msth_ultrafast_tau *= 0.5   # faster recovery
    # or if you have a threshold/scale for ultrafast suppression, reduce its sensitivity

    network = NeuraxonNetwork(params)
    print(f"\n1. Network: {len(network.input_neurons)}in / {len(network.hidden_neurons)}hid / "
          f"{len(network.output_neurons)}out, {len(network.synapses)} synapses")

    print("\n2. Setting inputs [1, -1, 0, 1, -1]")
    network.set_input_states([1, -1, 0, 1, -1])

    print("\n3. Simulating 50 steps...")
    for step in range(50):
        network.simulate_step()
        if step % 10 == 0:
            s = network.get_all_states()
            ha = sum(1 for x in s['hidden'] if x != 0)
            print(f"   Step {step:3d}: In={s['input']} HidActive={ha}/{len(s['hidden'])} "
                  f"Out={s['output']} E={network.energy_usage:.3f}")

    h0 = network.hidden_neurons[0]; s0 = network.synapses[0]
    print(f"\n4. MSTH (hidden[0]): uf={h0.msth.ultrafast_activity:.4f} "
          f"fast={h0.msth.fast_excitability:.4f} med_gain={h0.msth.medium_gain:.4f} "
          f"slow={h0.msth.slow_structural:.6f}")
    print(f"5. Chrono (syn[0]): omega={s0.chrono_omega:.4f} f_trace={s0.chrono_fast_trace:.4f} "
          f"z_trace={s0.chrono_slow_trace:.4f} elig={s0.eligibility:.4f}")
    print(f"6. CTSN (hidden[0]): s={h0.state:.4f} h={h0.complement_h:.4f} s_tilde={h0.state_tilde:.4f}")

    print("\n7. Neuromodulation: DA -> 0.8")
    network.modulate('dopamine', 0.8)
    for _ in range(10): network.simulate_step()
    R = network.neuromod_system.compute_receptor_activations()
    print(f"   D1={R['D1']:.3f} D2={R['D2']:.3f} 5HT1A={R['5HT1A']:.3f} "
          f"5HT2A={R['5HT2A']:.3f} M1={R['M1']:.3f} M2={R['M2']:.3f} "
          f"b1={R['beta1']:.3f} a2={R['alpha2']:.3f}")
    print(f"   Outputs: {network.get_output_states()}")

    print("\n8. Application layer...")
    app = NeuraxonApplication(params)
    app.store_pattern("A", [1, 1, -1, -1, 1], steps=50)
    app.store_pattern("B", [-1, -1, 1, 1, -1], steps=50)
    print(f"   Recall A: {app.recall_pattern('A', steps=30, mask_fraction=0.3)}")
    print(f"   Recall B: {app.recall_pattern('B', steps=30, mask_fraction=0.3)}")

    print("\n9. Aigarth hybrid...")
    dataset = [([1,0,0,0,0],[1,0,0,0,0]),([0,1,0,0,0],[0,1,0,0,0]),
               ([0,0,1,0,0],[0,0,1,0,0]),([-1,0,0,0,0],[-1,0,0,0,0])]
    hybrid = NeuraxonAigarthHybrid(params)
    hybrid.evolve(dataset, seasons=3, episodes=10)
    print(f"   Best fitness: {hybrid.best().fitness:.3f}")

    print("\n10. Signal propagation test [1,1,1,1,1]...")
    net2 = NeuraxonNetwork(params)
    net2.set_input_states([1, 1, 1, 1, 1])
    for step in range(30):
        net2.simulate_step()
        if step % 5 == 0:
            s = net2.get_all_states()
            print(f"   Step {step:3d}: Active={sum(1 for n in net2.all_neurons if n.trinary_state!=0)}/{len(net2.all_neurons)} Out={s['output']}")
    
    print("\n11. Kernels")
    n0 = net2.hidden_neurons[0]
    print("DSN kernel:", getattr(n0, "dsn_kernel_weights", None))
    print("CTSN gain/bias:", getattr(n0, "ctsn_phi_gain", None), getattr(n0, "ctsn_phi_bias", None))

    print("\n11. Save/load...")
    save_network(network, "neuraxon_v2_network.json")
    loaded = load_network("neuraxon_v2_network.json")
    print(f"   Synapses: {len(loaded.synapses)}, Energy: {loaded.energy_usage:.4f}")

    print("\n" + "=" * 70)
    print("All Neuraxon v2.0 systems operational.")
    print("=" * 70)
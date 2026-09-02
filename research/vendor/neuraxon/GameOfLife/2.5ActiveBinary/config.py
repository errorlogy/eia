# Neuraxon Game of Life Config
# Based on the Paper "Neuraxon: A New Neural Growth & Computation Blueprint" by David Vivancos https://vivancos.com/  & Dr. Jose Sanchez  https://josesanchezgarcia.com/ for Qubic Science https://qubic.org/
# https://www.researchgate.net/publication/397331336_Neuraxon
# Play the Lite Version of the Game of Life at https://huggingface.co/spaces/DavidVivancos/NeuraxonLife
import random
from dataclasses import dataclass, field
from typing import Set, Dict, Optional, List, Set

# ============================================================================
# GLOBAL CONSTANTS
# ============================================================================

# Constants for terrain types.
T_SEA = 0
T_LAND = 1
T_ROCK = 2

# A list of colors reserved for UI or special objects to ensure agent colors are distinct.
RESERVED_COLORS = [(20, 120, 255), (40, 180, 60), (130, 130, 130), (220, 40, 40)]

# ============================================================================
# SESSION AND NAMING HELPERS
# ============================================================================

def _generate_session_id() -> str:
    """Generate a 10-digit random session ID."""
    return "".join([str(random.randint(0, 9)) for _ in range(10)])

def _base26_name(n: int) -> str:
    """Generates a unique, human-readable name from an integer (e.g., 0->'A', 26->'AA')."""
    letters = []
    n0 = n
    while True:
        n, r = divmod(n0, 26)
        letters.append(chr(ord('A') + r))
        if n == 0: break
        n0 = n - 1
    return ''.join(reversed(letters))

# ============================================================================
# GLOBAL SESSION VARIABLES
# ============================================================================

_session_id: Optional[str] = None
_global_name_counter: int = 0  # Tracks the next available name index (A=0, B=1, ..., Z=25, AA=26, etc.)
_used_names: Set[str] = set()  # All names ever used in this session
_clan_history: Dict[int, Dict] = {}  # clan_id -> {members: set, merged_from: list, created_at_round: int}
_next_clan_id: int = 1
_current_round: int = 1
_game_id: str = ""
_next_nxer_id: int = 0  # Globally unique NxEr ID counter

def _get_next_global_name() -> str:
    """Get the next unique uppercase name (A, B, ..., Z, AA, AB, ...)."""
    global _global_name_counter, _used_names
    name = _base26_name(_global_name_counter)
    _global_name_counter += 1
    _used_names.add(name)
    return name

def _reset_session_globals():
    """Reset all session globals for a fresh start."""
    global _session_id, _global_name_counter, _used_names, _clan_history, _next_clan_id, _current_round, _game_id, _next_nxer_id
    _session_id = _generate_session_id()
    _global_name_counter = 0
    _used_names = set()
    _clan_history = {}
    _next_clan_id = 1
    _current_round = 1
    _game_id = "".join([str(random.randint(0, 9)) for _ in range(9)])
    _next_nxer_id = 0

# ============================================================================
# NETWORK PARAMETERS
# ============================================================================

@dataclass
class NetworkParameters:
    """
    A dataclass holding all configurable parameters for the Neuraxon network and the simulation environment.
    """
    # --- General Network Architecture ---
    network_name: str = "Neuraxon NxEr"
    # UPDATED: 3 original + Hunger, Sight, Smell
    num_input_neurons: int = 6  
    num_hidden_neurons: int = 10 
    # UPDATED: 4 original + Give Food
    num_output_neurons: int = 5 
    
    # --- Temporal Dynamics & Simulation ---
    dt: float = 1.0 
    min_dt: float = 0.1 
    max_dt: float = 2.0  
    activity_threshold: float = 0.5 
    simulation_steps: int = 30 

    # --- Network Topology ---
    connection_probability: float = 0.15 
    small_world_k: int = 6  
    small_world_rewire_prob: float = 0.15 
    preferential_attachment: bool = True 
    
    # --- Core Neuron Properties (Neuraxon) ---
    membrane_time_constant: float = 20.0 
    # Binary threshold for activation
    firing_threshold: float = 0.45
    adaptation_rate: float = 0.08  # v2.36: Raised from 0.02 - stronger spike-frequency adaptation
    spontaneous_firing_rate: float = 0.006
    neuron_health_decay: float = 0.001 
    
    # --- Membrane Potential Dynamics (NEW v2.36) ---
    resting_potential_decay: float = 0.05  # v2.92: Balanced decay for symmetric state persistence
    
    # --- Membrane Bias ---
    membrane_bias: float = 0.0
    
    # --- Dendritic Branch Properties ---
    num_dendritic_branches: int = 3 
    branch_threshold: float = 0.72  # v2.36: Raised - dendritic spikes require more accumulated input 
    plateau_decay: float = 500.0 

    # --- Synaptic Properties & Plasticity (Section 3) ---
    tau_fast: float = 5.0  
    tau_slow: float = 50.0  
    tau_meta: float = 1000.0 
    tau_ltp: float = 15.0 
    tau_ltd: float = 35.0 
    
    # --- Synaptic Weight Initialization Ranges ---
    w_fast_init_min: float = -1.0
    w_fast_init_max: float = 1.0
    w_slow_init_min: float = -0.5
    w_slow_init_max: float = 0.5
    w_meta_init_min: float = -0.3
    w_meta_init_max: float = 0.3
    
    # --- Learning and Plasticity Rules (Section 4) ---
    learning_rate: float = 0.01 
    stdp_window: float = 20.0 
    learning_rate_mod: float = 1.0 
    plasticity_threshold: float = 0.5 
    associativity_strength: float = 0.1 
    
    # --- Structural Plasticity ---
    synapse_integrity_threshold: float = 0.1 
    synapse_formation_prob: float = 0.02 
    synapse_death_prob: float = 0.01 
    neuron_death_threshold: float = 0.1 
    
    # --- Neuromodulation (Section 1 & 8) ---
    dopamine_baseline: float = 0.15
    dopamine_high_affinity_threshold: float = 0.01
    dopamine_low_affinity_threshold: float = 0.25   
    serotonin_baseline: float = 0.12
    serotonin_high_affinity_threshold: float = 0.01
    serotonin_low_affinity_threshold: float = 1.0
    acetylcholine_baseline: float = 0.12
    acetylcholine_high_affinity_threshold: float = 0.01
    acetylcholine_low_affinity_threshold: float = 1.0
    norepinephrine_baseline: float = 0.12
    norepinephrine_high_affinity_threshold: float = 0.01
    norepinephrine_low_affinity_threshold: float = 1.0
    neuromod_decay_rate: float = 0.06
    diffusion_rate: float = 0.05
    dopamine_reward_magnitude: float = 0.25 
    
    # --- Oscillators & Synchronization (Section 7) ---
    oscillator_low_freq: float = 0.05  
    oscillator_mid_freq: float = 0.5   
    oscillator_high_freq: float = 4.0  
    oscillator_strength: float = 0.10  # v2.36: Reduced from 0.25 - less tonic drive, more stimulus-dependent 
    
    # --- Energy Metabolism ---
    energy_baseline: float = 100.0 
    firing_energy_cost: float = 5.0  
    
    # --- Synaptic Weight Homeostasis (NEW in v2.31) ---
    # BIOINSPIRED: Models synaptic scaling (Turrigiano & Nelson, 2004)
    # Biological neurons maintain stable total synaptic drive through
    # multiplicative scaling that preserves relative weight differences
    weight_homeostasis_enabled: bool = True  # Enable synaptic scaling
    weight_homeostasis_interval: int = 50  # Apply scaling every N steps
    weight_saturation_threshold: float = 0.75  # Mean |weight| triggering scaling
    weight_homeostasis_target: float = 0.5  # Target mean |weight| after scaling
    weight_homeostasis_rate: float = 0.02  # How fast to approach target (soft scaling)
    weight_drift_correction: float = 0.005  # Per-step drift toward zero for Δw balance
    max_weight_magnitude: float = 0.95  # Hard ceiling to prevent saturation
    min_weight_magnitude: float = -0.95  # Hard floor to prevent saturation
    ltp_ltd_balance_target: float = 1.0  # Target LTP/LTD ratio
    ltp_ltd_correction_rate: float = 0.01  # Rate of correcting LTP/LTD imbalance
    plasticity_energy_cost: float = 10.0 
    metabolic_rate: float = 1.0 
    recovery_rate: float = 0.5 
    
    # --- Energy-Aware Threshold Homeostasis (NEW in v2.30) ---
    # BIOINSPIRED: Models ATP depletion effects on ion channel dynamics
    # In biology, low ATP impairs Na+/K+-ATPase, raising effective firing threshold
    energy_threshold_coupling: float = 0.5  # How strongly energy affects threshold (0=none, 1=strong)
    energy_threshold_floor: float = 0.3  # Minimum energy fraction before threshold scaling activates
    energy_recovery_boost: float = 2.0  # Enhanced recovery rate multiplier for low-energy neurons
    critical_energy_level: float = 30.0  # Energy level below which recovery boost activates
    
    # --- Homeostasis ---
    target_firing_rate: float = 0.1 
    homeostatic_plasticity_rate: float = 0.001 
    
    # --- Adaptive Network-Wide Threshold Homeostasis (REBALANCED v2.36) ---
    adaptive_threshold_enabled: bool = True
    adaptive_threshold_check_interval: int = 12  # v2.36: More frequent checks
    adaptive_threshold_adjustment: float = 0.06
    min_active_fraction: float = 0.15
    max_active_fraction: float = 0.35
    target_active_fraction: float = 0.25
    
    # --- Aigarth Hybridization (Section 8) ---
    itu_circle_radius: int = 8 
    evolution_interval: int = 1000 
    fitness_temporal_weight: float = 0.4 
    fitness_energy_weight: float = 0.3
    fitness_pattern_weight: float = 0.3
    
    # --- Phase Synchronization Parameters (v2.40 Kuramoto Model) ---
    phase_coupling_strength: float = 0.08  # REDUCED global coupling
    phase_coupling_local_strength: float = 1.0  # STRONG local Kuramoto coupling  reduced fro 1.5 
    max_axonal_delay: float = 10.0
    phase_clustering_init: float = 0.85  # 85% neurons start clustered
    natural_freq_range_min: float = 0.85  # Narrow frequency range
    natural_freq_range_max: float = 1.15  # Spread of 0.3 (was 1.5)
    phase_coupling_momentum: float = 0.6  # Smooth phase transitions
    
    # --- Sensory-Motor Coupling (NEW in v2.35) ---
    sensory_input_gain: float = 0.9  # v2.36: Reduced - sensory shouldn't overwhelm network
    afferent_synapse_strength: float = 1.1  # v2.36: Reduced from 1.5
    afferent_synapse_reliability: float = 0.95
    sensory_gating_enabled: bool = True
    sensory_gating_threshold: float = 0.45  # v2.36: Raised - stronger gating
    sensory_gating_suppression: float = 0.25  # v2.36: Stronger suppression during driven input
    max_intrinsic_timescale: float = 80.0  # Reduced from 100 for stricter bound
    spontaneous_as_current: bool = True
    spontaneous_current_magnitude: float = 1.2  # Reduced from 1.5
    
    # --- Spike Classification Thresholds (UPDATED v2.38) ---
    # Used to determine if a spike was driven vs spontaneous
    # BIOINSPIRED: Even small synaptic inputs should count as "driven"
    # v2.38: Lowered threshold to capture weak but real synaptic drive
    driven_input_threshold: float = 0.05  # v2.38: Reduced from 0.2 for better classification
    spike_classification_enabled: bool = True
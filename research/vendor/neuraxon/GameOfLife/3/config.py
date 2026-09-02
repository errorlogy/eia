# Neuraxon Game of Life Config  v.3.35
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

# ============================================================================
# CIRCADIAN / DAY-NIGHT CYCLE CONSTANTS (NEW v3.0)
# ============================================================================
# BIOINSPIRED: Circadian rhythms are fundamental to all biological life.
# The suprachiasmatic nucleus (SCN) orchestrates 24-hour cycles affecting:
# - Melatonin/serotonin balance (sleep-wake regulation)
# - Dopamine release patterns (reward sensitivity varies by time of day)
# - Metabolic rate (lower at night, higher during day)
# - Core body temperature (drops at night, rises during day)

CIRCADIAN_CYCLE_TICKS = 600  # Default: 10 minutes real-time = 1 day cycle at 60 tps
DAWN_PHASE = 0.0              # 0.0 = start of day
NOON_PHASE = 0.25             # Peak activity
DUSK_PHASE = 0.5              # Transition to night
MIDNIGHT_PHASE = 0.75         # Deepest night

# Temperature constants (in abstract units, ~35-40 maps to biological 35-40°C)
TEMP_BASELINE = 37.0          # Normal body temperature
TEMP_MIN = 34.0               # Hypothermia threshold
TEMP_MAX = 41.0               # Hyperthermia threshold
TEMP_NIGHT_DROP = 1.5         # Temperature drops at night (circadian)
TEMP_ACTIVITY_GAIN = 0.3      # Heat from movement/activity
TEMP_SOCIAL_GAIN = 0.2        # Heat from proximity to others
TEMP_FOOD_GAIN = 0.5          # Thermogenic effect of eating
TEMP_DECAY_RATE = 0.02        # Return to baseline rate

# Proprioceptron constants
ROCK_HIT_MEMORY = 5           # How many recent rock hits to track
ROCK_HIT_THRESHOLD = 3        # Hits before forced direction change

# v3.2: Resting metabolism constants
# v3.3: Kept but referenced from NxEr attribute for inheritance
RESTING_METABOLISM_MULTIPLIER_DEFAULT = 0.3
RESTING_TEMP_DROP_RATE = 0.08  # v3.3: Slightly faster drop when resting

# v3.3: Temperature dynamics rebalance — data showed temp stuck at ~37.74
# with near-zero circadian correlation. Gains must exceed decay for variance.
TEMP_ACTIVITY_GAIN_V32 = 0.8   # v3.31: Kept from v3.3
TEMP_FOOD_GAIN_V32 = 1.0       # v3.31: Kept from v3.3
TEMP_DECAY_RATE_V32 = 0.008    # v3.31: Kept from v3.3

# v3.31: RESTING_METABOLISM_MULT alias for backward compat (game_loop uses this)
RESTING_METABOLISM_MULT = 0.3

# v3.31: Resting metabolism constants (BIOINSPIRED: torpor/sleep energy conservation)
RESTING_METABOLISM_MULTIPLIER = 0.3
RESTING_TEMP_DROP_RATE = 0.1  # Body temp drops slowly when resting
RESTING_FOOD_THRESHOLD = 0.2  # Min food fraction to enter voluntary rest

# v3.31: FIX - Temperature constants rebalanced further from results-97 analysis
# Results-97: temp_circadian_corr STILL ≈0, circadian_phase vs body_temp r=-0.106
# Root cause: night drop and day warming still too weak relative to decay
TEMP_ACTIVITY_GAIN = 0.8       # v3.3: Up from 0.5 — must outpace decay
TEMP_SOCIAL_GAIN = 0.4         # v3.3: Up from 0.3
TEMP_FOOD_GAIN = 1.0           # v3.3: Up from 0.7
TEMP_DECAY_RATE = 0.008        # v3.3: Down from 0.015 — slower homeostasis
TEMP_BASELINE_VARIANCE = 1.0   # v3.3: Up from 0.5 — more individual variation
TEMP_NIGHT_DROP = 4.0          # v3.31: Up from 2.5 — much stronger circadian drop
TEMP_DAY_WARMING = 1.5         # v3.31: NEW — explicit day warming constant

# v3.32: Temporal correlation rolling window (ticks) for temperature–circadian correlation
TEMP_CIRCADIAN_CORR_WINDOW = 50  # ~8% of a 600-tick circadian cycle — enough phase variation
# v3.32: Silencing threshold — active synapses with activity below this AND low integrity can become silent
SYNAPSE_SILENCING_ACTIVITY_THRESHOLD = 0.005  # Below this total |w_fast|+|w_slow|, eligible for silencing

@dataclass
class NetworkParameters:
    """
    A dataclass holding all configurable parameters for the Neuraxon network and the simulation environment.
    """
    # --- General Network Architecture ---
    network_name: str = "Neuraxon NxEr"
    # UPDATED v3.1: 6 original + DayNight, Temperature, Proprioception = 9 inputs
    # Input neurons (trinary -1/0/1):
    #   0: Movement result (-1=blocked, 0=moved, 1=food found)
    #   1: Terrain encounter (-1=rock, 0=empty, 1=nxer present)
    #   2: Terrain type (-1=rock, 0=sea, 1=land)
    #   3: Hunger (-1=starving, 0=normal, 1=satiated) 
    #   4: Sight (-1=enemy/nothing, 0=clan/neutral, 1=food)
    #   5: Smell (-1=nothing, 0=nxer nearby, 1=food nearby)
    #   6: DayNight (-1=night, 0=transition dawn/dusk, 1=day)
    #   7: Temperature (-1=cold/hypothermic, 0=normal, 1=hot/hyperthermic)
    #   8: Proprioception (-1=repeatedly blocked, 0=normal, 1=clear path history)
    num_input_neurons: int = 9  
    num_hidden_neurons: int = 10 
    # UPDATED v3.1: 5 original + Resting = 6 outputs
    # Output neurons (trinary -1/0/1):
    #   0: Move X (-1=west, 0=stay, 1=east)
    #   1: Move Y (-1=north, 0=stay, 1=south)
    #   2: Social (-1=aggressive/steal, 0=neutral, 1=friendly)
    #   3: Mate intent (-1=reject, 0=neutral, 1=seek mate)
    #   4: Give food (-1=take, 0=neutral, 1=give to clan)
    #   5: Resting (-1=force active/wake, 0=normal, 1=rest/sleep)
    num_output_neurons: int = 6 
    
    # v3.2: Resting/Metabolism parameters
    resting_metabolism_multiplier: float = 0.3
    resting_temp_drop_rate: float = 0.1
    temp_activity_gain_v32: float = 0.5
    temp_food_gain_v32: float = 0.7
    temp_decay_rate_v32: float = 0.015
    
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
    # v2.92: REBALANCED thresholds for bio-inspired trinary distribution
    # BIOINSPIRED: Target ~20-25% excitatory, 30-40% neutral, 35-45% inhibitory
    # Paper claim: neutral state acts as "buffer enabling rapid transitions"
    firing_threshold_excitatory: float = 0.45  # v2.92: Lowered from 0.60 for easier excitation
    firing_threshold_inhibitory: float = -0.40  # v2.92: Raised from -0.25 to reduce inhibitory bias
    adaptation_rate: float = 0.08  # v2.36: Raised from 0.02 - stronger spike-frequency adaptation
    # v2.92: Moderate spontaneous rate for balanced trinary exploration
    # BIOINSPIRED: Cortical spontaneous activity explores state space
    # Paper claim: "spontaneous firing sustains intrinsic activity"
    spontaneous_firing_rate: float = 0.006  # v2.92: Slightly increased for state exploration
    neuron_health_decay: float = 0.001 
    
    # --- Membrane Potential Dynamics (NEW v2.36) ---
    resting_potential_decay: float = 0.05  # v2.92: Balanced decay for symmetric state persistence
    
    # v3.34 RC1-FIX: Set to 0.0 — the constant negative bias was the primary driver of
    # output locking into inhibitory state (97.5% SW quadrant, ~40% outputs at -1).
    # BIOINSPIRED: Biological resting potential is maintained by Na+/K+-ATPase pump
    # equilibrium, not by a tonic inhibitory current. The resting_potential_decay
    # parameter already models passive return to resting potential via leak channels.
    membrane_negative_bias: float = 0.0  # v3.34: Was -0.06; removed — see RC1 diagnostics
    
    # --- Dendritic Branch Properties ---
    num_dendritic_branches: int = 3 
    branch_threshold: float = 0.72  # v2.36: Raised - dendritic spikes require more accumulated input 
    plateau_decay: float = 500.0 

    # --- Synaptic Properties & Plasticity (Section 3) ---
    tau_fast: float = 5.0  
    tau_slow: float = 50.0  
    tau_meta: float = 150.0   # v3.31: Down from 200 — faster meta tracking (was 1000 in v3.2)
    tau_ltp: float = 15.0 
    tau_ltd: float = 35.0 
    
    # v3.31: Meta-plasticity dynamics (Paper Section 3 multi-timescale)
    # BIOINSPIRED: Metabotropic receptors integrate over seconds-minutes, not hours
    meta_target_gain: float = 0.30        # v3.31: Up from 0.25 — stronger meta signal
    meta_accumulation_rate: float = 0.35  # v3.31: Up from 0.3 — more w_slow→meta flow
    meta_clamp_max: float = 1.0           # v3.31: Up from 0.8 — full [-1,1] range
    
    # v3.31: NEW — Meta-behavior coupling (CRITICAL FIX)
    # Results-97: w_meta not in compute_input → zero behavioral effect for 80% of synapses
    meta_influence_gain: float = 0.25     # v3.31: How much w_meta contributes to effective weight
    meta_da_boost: float = 2.0            # v3.31: DA multiplier for meta accumulation during reward
    
    # --- Synaptic Weight Initialization Ranges ---
    w_fast_init_min: float = -1.0
    w_fast_init_max: float = 1.0
    w_slow_init_min: float = -0.5
    w_slow_init_max: float = 0.5
    w_meta_init_min: float = -0.3
    w_meta_init_max: float = 0.3
    
    # v3.31: LTP/LTD rebalance — Results-97 overcorrected to 70.6% LTP, target ~55-60%
    hebbian_ltp_rate: float = 0.18        # v3.31: Down from 0.3 — less pure Hebbian LTP
    ltd_neutral_scale: float = 0.12       # v3.31: Up from 0.08 — slightly more neutral LTD
    ltd_inhibitory_scale: float = 0.6     # v3.31: Kept from v3.3
    # v3.31: Slow weight differentiation
    w_slow_post_trace_fraction: float = 0.85 # v3.31: Up from 0.8 — more post-trace in w_slow
    w_fast_delta_share: float = 0.5       # v3.31: NEW — fraction of delta_w going to w_fast
    w_slow_delta_share: float = 0.02      # v3.31: NEW — fraction of delta_w going to w_slow (was 0.03)
    
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
    # v3.33: Enzymatic clearance (MAO/COMT analog) — Michaelis-Menten per-transporter
    # BIOINSPIRED: Each monoamine has a distinct reuptake transporter with different kinetics:
    #   NET (norepinephrine transporter): fast clearance
    #   DAT (dopamine transporter): moderate
    #   SERT (serotonin transporter): slow (SSRIs block this)
    #   AChE (acetylcholinesterase): fastest enzymatic degradation
    reuptake_vmax_ne: float = 0.08
    reuptake_vmax_da: float = 0.05
    reuptake_vmax_5ht: float = 0.03
    reuptake_vmax_ach: float = 0.10
    reuptake_km: float = 0.5  # Half-saturation constant (shared, Michaelis-Menten)
    # v3.33: Autoreceptor negative feedback strength
    # BIOINSPIRED: Presynaptic autoreceptors (5-HT1A, α2-adrenergic, D2-short)
    # detect high extracellular concentration and suppress further vesicle release
    autoreceptor_strength: float = 1.0  # Scaling exponent for feedback (1.0 = quadratic)
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
    
    # --- Circadian Rhythm Parameters (NEW v3.0) ---
    # BIOINSPIRED: Configurable day/night cycle
    circadian_cycle_ticks: int = 2400  # Ticks per full day/night cycle
    circadian_enabled: bool = True     # Toggle circadian effects
    
    # Neuromodulator circadian modulation strengths
    circadian_serotonin_amplitude: float = 0.3   # Night: +serotonin (sleep)
    circadian_dopamine_amplitude: float = 0.25  # Day: +dopamine (activity)
    circadian_norepinephrine_amplitude: float = 0.2  # Day: +NE (alertness)
    circadian_acetylcholine_amplitude: float = 0.15  # Day: +ACh (attention)
    
    # Metabolic circadian effects
    circadian_metabolic_day_multiplier: float = 1.2   # Higher metabolism during day
    circadian_metabolic_night_multiplier: float = 0.7 # Lower metabolism at night
    
    # --- Temperature Parameters (NEW v3.0) ---
    # BIOINSPIRED: Body temperature affects enzyme kinetics, neural firing rates
    temperature_enabled: bool = True
    temperature_baseline: float = 37.0
    temperature_min: float = 34.0
    temperature_max: float = 41.0
    temperature_neural_sensitivity: float = 0.1  # How much temp affects firing
    temperature_metabolic_q10: float = 2.0  # Q10 coefficient for metabolism
    
    # --- Proprioceptron Parameters (UPDATED v3.1) ---
    proprioceptron_rock_memory: int = 5
    proprioceptron_force_turn_threshold: int = 3
    proprioceptron_clear_path_threshold: int = 5  # Consecutive successful moves for "clear path" signal
    
    # --- Brain-Instinct Balance (NEW v3.1) ---
    # BIOINSPIRED: Balance between learned brain outputs and instinctive survival behaviors
    brain_movement_base_weight: float = 0.7  # How much brain controls movement vs instinct
    brain_rest_override_threshold: float = 0.3  # Food level below which rest is overridden
    circadian_rest_tendency: float = 0.7  # Base probability of resting during night phase
    
    # --- Temperature Behavioral Thresholds (NEW v3.1) ---
    temp_cold_threshold: float = 35.5  # Below this = hypothermic signal
    temp_hot_threshold: float = 38.5   # Above this = hyperthermic signal
    temp_movement_bonus: float = 0.15  # Extra movement when cold (to generate heat)
    
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
    # BIOINSPIRED: Cortical neurons maintain ~20-25% average firing rate for optimal information
    # processing. The neutral state is the computational "buffer" where integration occurs.
    adaptive_threshold_enabled: bool = True
    adaptive_threshold_check_interval: int = 12  # v2.36: More frequent checks
    adaptive_threshold_adjustment: float = 0.06  # v2.37b: Even stronger correction  
    min_excitatory_fraction: float = 0.15  # v2.36: Floor for maintaining some activity
    max_excitatory_fraction: float = 0.28  # v2.37b: Slightly lower
    target_excitatory_fraction: float = 0.22  # v2.36: NEW - optimal target for criticality
    min_inhibitory_fraction: float = 0.10  # v2.37b: NEW - minimum inhibitory for E/I balance
    target_inhibitory_fraction: float = 0.10  # v2.36: NEW - ensures inhibitory presence
    
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
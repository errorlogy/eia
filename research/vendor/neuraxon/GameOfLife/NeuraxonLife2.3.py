# Neuraxon Game of Life v.2.38 (Research Version): Plausible Spontaneous/Driven Fix
# Based on the Paper "Neuraxon: A New Neural Growth & Computation Blueprint" by David Vivancos https://vivancos.com/  & Dr. Jose Sanchez  https://josesanchezgarcia.com/
# https://www.researchgate.net/publication/397331336_Neuraxon
# Play the Lite Version of the Game of Life at https://huggingface.co/spaces/DavidVivancos/NeuraxonLife
# New features in V2.2:  Enhance Full Feldged Inheritance
# New features in v2.21: New Nxrs Naming convention for Long Game Tracking Through sesions
# New features in v2.22: Extra Loging enabled up to 10000 timesteps configurable
# New features in v2.23: God mode disabled and improved biological parameters
# New features in v2.24: Sparse comrpesing some Timeseries data to reduce memory usage and improve performance
# New features in v2.25: Log Mode 3 enabled for deep detailed timeseries at non agragated Nxer level
# New features in v2.2501: "metric mismatch" in ITU evolution fitness
# New features in v2.2502: upgraded branching ratio measurement
# New features in v2.2503: Excitability rebalancing for criticality (Proposal 1) up to 0.45 
# New features in v2.2504: Reduced adaptation rate to 0.02 to reduce the impact of inputs on the network
# New features in v2.2505: dopamine_low_affinity_threshold Lowered
# New features in v2.2506: LTP/LTD recording update
# New features in v2.2507: adaptive_threshold_homeostasis update
# New features in v2.2508: norepinephrine update
# New features in v2.26: acetylcholine update (Consolidation, Associativity, Persistence)
# New features in v2.27: Serotonin update (Behavioral modulation: Serenity vs Impulse/Risk-taking)
# New features in v2.28: Dopamine update (Behavioral modulation: Novelty Seeking vs Interaction with other clans)
# New features in v2.29: Global NeuroModulator updates
# New features in v2.30: Energy-Aware Firing Threshold
# New features in v2.31: Synaptic Weight Homeostasis
# New features in v2.32: Autoreceptor Negative Feedback Fix
# New features in v2.33: code and performance optimizations
# New features in v2.34: Inherit Synaptic Weights update
# New features in v2.35: Properly caps intrinsic timescale
# New features in v2.36: Bioinspired Trinary State Rebalancing
# New features in v2.37: E/I Balance Fix
# New features in v2.38: Biologically Plausible Spontaneous/Driven Activity Ratio

import os, sys, time, json, math, random, pathlib
from dataclasses import dataclass, asdict, field
from enum import Enum
from typing import List, Dict, Tuple, Optional, Set,Any
from datetime import datetime
import numpy as np
import random
from copy import deepcopy
from collections import deque, defaultdict
from os import environ
import cmath
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
try:
    import pygame
except Exception as e:
    raise RuntimeError("This program requires pygame. Install with: pip install pygame") from e



# ============================================================================
# GLOBAL SESSION AND NAMING VARIABLES (NEW in V2.21)
# ============================================================================
_session_id: Optional[str] = None
_global_name_counter: int = 0  # Tracks the next available name index (A=0, B=1, ..., Z=25, AA=26, etc.)
_used_names: Set[str] = set()  # All names ever used in this session
_clan_history: Dict[int, Dict] = {}  # clan_id -> {members: set, merged_from: list, created_at_round: int}
_next_clan_id: int = 1
_current_round: int = 1
_game_id: str = ""
_next_nxer_id: int = 0  # Globally unique NxEr ID counter

def _generate_session_id() -> str:
    """Generate a 10-digit random session ID."""
    return "".join([str(random.randint(0, 9)) for _ in range(10)])

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
# DATALOGGER CLASS
# ============================================================================

class DataLogger:
    """
    Comprehensive data logger for validating the Neuraxon research paper.
    
    Level 1: Basic logging (summary statistics, final states)
    Level 2: Detailed logging (time-series of all variables, plasticity events, etc.) Default
    Level 3: Deep detailed logging

    Data is kept in memory during gameplay and only saved:
    - At the end of the game (game over / all NxErs died)
    - When user explicitly saves the game
    - When user loads a game (saves current state first)
    """
    
    
    def __init__(self, log_level: int = 2, max_history_length: int = 10000):
        self.log_level = max(1, min(3, log_level))
        self.max_history_length = max_history_length
        self.reset()
    
    def _compress_series(self, data_list: list) -> list:
        """
        Compresses a list into [index, value] pairs. 
        Only stores the entry when the value changes.
        Example: [0, 0, 0, 5, 5] -> [[0, 0], [3, 5]]
        """
        if not data_list:
            return []
        
        compressed = [[0, data_list[0]]]
        last_val = data_list[0]
        
        for idx, val in enumerate(data_list[1:], 1):
            if val != last_val:
                compressed.append([idx, val])
                last_val = val
        return compressed

    def reset(self):
        """Reset all logged data."""
        self.start_time = time.time()
        self.game_metadata = {
            'start_timestamp': datetime.now().isoformat(),
            'log_level': self.log_level,
            'version': '2.05'
        }
        
        self.summary = {
            'total_ticks': 0,
            'total_neurons_created': 0,
            'total_neurons_died': 0,
            'total_synapses_created': 0,
            'total_synapses_pruned': 0,
            'total_plasticity_events': 0,
            'total_ltp_events': 0,
            'total_ltd_events': 0,
            'peak_network_activity': 0.0,
            'average_branching_ratio': 0.0,
            'branching_ratio_samples': 0,
            'neuromodulator_peaks': {
                'dopamine': 0.0,
                'serotonin': 0.0,
                'acetylcholine': 0.0,
                'norepinephrine': 0.0
            },
            # NEW summary stats
            'total_silent_synapse_activations': 0,
            'total_spontaneous_events': 0,
            'total_dendritic_spikes': 0,
            'total_homeostatic_adjustments': 0,
            'peak_phase_coherence': 0.0,
            # NEW: Updated Save states in v 2.1
            'total_threshold_modulations': 0,
            'total_associativity_events': 0,
            'total_metabotropic_activations': 0,
            'total_ionotropic_activations': 0,
            'peak_autocorrelation_window': 0.0,
            'mean_weight_change_rate': 0.0,
            'total_subthreshold_integrations': 0,
        }
        
        self.nxer_summary = {
            'total_born': 0,
            'total_died': 0,
            'max_food_found': 0.0,
            'max_time_lived': 0.0,
            'max_mates': 0,
            'max_explored': 0
        }
        
        # --- Event Lists (Unconditional Init to prevent AttributeError) ---
        self.plasticity_events = []
        self.structural_events = []
        self.neuron_snapshots = []
        self.synapse_snapshots = []
        self.nxer_events = []
        self.itu_fitness_history = []
        self.io_patterns = []
        
        self.silent_synapse_events = []
        self.spontaneous_events = []
        self.homeostatic_events = []
        self.dendritic_spike_events = []
        self.autoreceptor_events = []
        self.neuromodulator_events = []
        self.phase_reset_events = []
        
        # NEW: Additional event lists for paper validation
        self.weight_evolution_events = []
        self.threshold_modulation_events = []
        self.associativity_events = []
        self.subthreshold_events = []
        
        self.tracked_neuron_ids = []
        self.neuron_time_series = {}
        self.tracked_synapse_ids = []
        self.synapse_time_series = {}
        
        self.snapshot_interval = 100
        self.last_snapshot_tick = -1
        self.detailed_snapshot_interval = 500
        
        if self.log_level >= 2:
            self._init_level2_data()
    
    def _init_level2_data(self):
        self.time_series = {
            'ticks': [],
            'timestamps': [],
            'network_activity': [],
            'branching_ratio': [],
            'total_energy': [],
            'average_energy': [],
            'energy_efficiency': [],
            'temporal_sync': [],
            'dopamine': [],
            'serotonin': [],
            'acetylcholine': [],
            'norepinephrine': [],
            'oscillator_drive': [],
            
            # NEW: Oscillator components for CFC analysis
            'oscillator_low': [],
            'oscillator_mid': [],
            'oscillator_high': [],
            
            # NEW: Cross-frequency coupling metrics
            'phase_coherence': [],
            'cfc_low_mid': [],
            'cfc_mid_high': [],
            
            # NEW: Trinary state distributions
            'excitatory_fraction': [],
            'inhibitory_fraction': [],
            'neutral_fraction': [],
            
            # NEW: Autoreceptor dynamics
            'autoreceptor_mean': [],
            'autoreceptor_std': [],
            
            # NEW: Adaptation dynamics
            'adaptation_mean': [],
            
            # NEW: Spontaneous activity metrics
            'spontaneous_firing_count': [],
            'driven_firing_count': [],
            
            # NEW: Synapse health metrics
            'silent_synapse_count': [],
            'active_synapse_count': [],
            'modulatory_synapse_count': [],
            'mean_synapse_integrity': [],
            
            # NEW: Dendritic metrics (averaged across network)
            'mean_plateau_potential': [],
            'mean_branch_potential': [],
            'dendritic_spike_count': [],
            
            # NEW: Intrinsic timescale distribution
            'mean_intrinsic_timescale': [],
            'timescale_heterogeneity': [],
            
            # NEW: Membrane potential statistics
            'membrane_potential_mean': [],
            'membrane_potential_std': [],
            
            # ============================================================
            # NEW: Synaptic Weight Evolution
            # ============================================================
            # Multi-timescale weight tracking (w_fast, w_slow, w_meta)
            'mean_w_fast': [],
            'mean_w_slow': [],
            'mean_w_meta': [],
            'std_w_fast': [],
            'std_w_slow': [],
            'std_w_meta': [],
            
            # Synaptic trace dynamics
            'mean_pre_trace': [],
            'mean_post_trace': [],
            'mean_pre_trace_ltd': [],
            'std_pre_trace': [],
            
            # Weight change rates
            'mean_delta_w': [],
            'ltp_rate': [],  # LTP events per tick
            'ltd_rate': [],  # LTD events per tick
            
            # ============================================================
            # NEW: Plasticity and Associativity
            # ============================================================
            # Associativity contribution from neighboring synapses
            'mean_associativity_contribution': [],
            'associativity_event_count': [],
            
            # Learning rate modulation by neuromodulators
            'mean_learning_rate_mod': [],
            'std_learning_rate_mod': [],
            
            # ============================================================
            # NEW: Self-Generated Activity / ACW
            # ============================================================
            # Autocorrelation Window (ACW) - critical for intrinsic timescales
            'mean_autocorrelation_window': [],
            'std_autocorrelation_window': [],
            'autocorrelation_coefficient_mean': [],
            
            # ============================================================
            # NEW: Threshold Modulation
            # ============================================================
            # Effective threshold tracking (after neuromodulation + autoreceptor)
            'mean_threshold_excitatory_effective': [],
            'mean_threshold_inhibitory_effective': [],
            'threshold_modulation_by_ach': [],
            'threshold_modulation_by_autoreceptor': [],
            
            # Ionotropic vs Metabotropic channel contributions
            'ionotropic_contribution_mean': [],
            'metabotropic_contribution_mean': [],
            
            # ============================================================
            # NEW: Neuromodulator Spatial Dynamics
            # ============================================================
            # Modulator grid spatial statistics
            'modulator_grid_entropy': [],
            'modulator_grid_gradient_magnitude': [],
            'dopamine_spatial_variance': [],
            'serotonin_spatial_variance': [],
            
            # ============================================================
            # NEW: Silent Synapse Dynamics
            # ============================================================
            'silent_synapse_fraction': [],
            'silent_to_active_transitions': [],
            'active_to_silent_transitions': [],
            
            # ============================================================
            # NEW: Complex Signaling / Subthreshold
            # ============================================================
            'subthreshold_integration_count': [],
            'near_threshold_fraction': [],  # Neurons close to firing
            
            # ============================================================
            # NEW: Extended Oscillator Metrics
            # ============================================================
            # Phase-Amplitude Coupling (PAC) detailed metrics
            'pac_theta_gamma': [],
            'pac_delta_theta': [],
            'mean_phase_velocity': [],
            
            # ============================================================
            # NEW:  Aigarth/ITU Metrics
            # ============================================================
            'itu_mean_fitness': [],
            'itu_fitness_variance': [],
            'itu_mutation_events': [],
            'itu_pruning_events': [],
        }
        self.per_nxer_time_series: Dict[int, Dict[str, List]] = {}
    
    def _ensure_nxer_series(self, nxer_id: int, nxer_name: str):
        """Initialize time series structure for a specific NxEr if not exists."""
        if nxer_id not in self.per_nxer_time_series:
            self.per_nxer_time_series[nxer_id] = {
                'name': nxer_name,
                'ticks': [],
                'alive': [],
                'food': [],
                'pos_x': [],
                'pos_y': [],
                'network_activity': [],
                'branching_ratio': [],
                'total_energy': [],
                'average_energy': [],
                'dopamine': [],
                'serotonin': [],
                'acetylcholine': [],
                'norepinephrine': [],
                'membrane_potential_mean': [],
                'membrane_potential_std': [],
                'excitatory_fraction': [],
                'inhibitory_fraction': [],
                'neutral_fraction': [],
                'mean_w_fast': [],
                'mean_w_slow': [],
                'mean_w_meta': [],
                'phase_coherence': [],
                'fitness_score': [],
                'food_found': [],
                'explored': [],
                'mates_performed': [],
            }
    def _log_nxer_individual(self, tick: int, a: 'NxEr'):
        """Log individual NxEr's data independently."""
        if not a.alive:
            return  # Don't log dead NxErs at all
        self._ensure_nxer_series(a.id, a.name)
        series = self.per_nxer_time_series[a.id]
        
        series['ticks'].append(tick)
        series['alive'].append(a.alive)
        series['food'].append(a.food)
        series['pos_x'].append(a.pos[0])
        series['pos_y'].append(a.pos[1])
        series['fitness_score'].append(a.stats.fitness_score)
        series['food_found'].append(a.stats.food_found)
        series['explored'].append(a.stats.explored)
        series['mates_performed'].append(a.stats.mates_performed)
        
        if not a.alive:
            # Append zeros for dead NxEr's network data
            for key in ['network_activity', 'branching_ratio', 'total_energy', 'average_energy',
                        'dopamine', 'serotonin', 'acetylcholine', 'norepinephrine',
                        'membrane_potential_mean', 'membrane_potential_std',
                        'excitatory_fraction', 'inhibitory_fraction', 'neutral_fraction',
                        'mean_w_fast', 'mean_w_slow', 'mean_w_meta', 'phase_coherence']:
                series[key].append(0.0)
            return
        
        net = a.net
        active_neurons = [n for n in net.all_neurons if n.is_active]
        active_synapses = [s for s in net.synapses if s.integrity > 0]
        
        if not active_neurons:
            for key in ['network_activity', 'branching_ratio', 'total_energy', 'average_energy',
                        'dopamine', 'serotonin', 'acetylcholine', 'norepinephrine',
                        'membrane_potential_mean', 'membrane_potential_std',
                        'excitatory_fraction', 'inhibitory_fraction', 'neutral_fraction',
                        'mean_w_fast', 'mean_w_slow', 'mean_w_meta', 'phase_coherence']:
                series[key].append(0.0)
            return
        
        # Network activity
        activity = sum(abs(n.trinary_state) for n in active_neurons) / len(active_neurons)
        series['network_activity'].append(activity)
        series['branching_ratio'].append(net.branching_ratio)
        
        # Energy
        total_energy = sum(n.energy_level for n in active_neurons)
        series['total_energy'].append(total_energy)
        series['average_energy'].append(total_energy / len(active_neurons))
        
        # Neuromodulators
        series['dopamine'].append(net.neuromodulators.get('dopamine', 0.0))
        series['serotonin'].append(net.neuromodulators.get('serotonin', 0.0))
        series['acetylcholine'].append(net.neuromodulators.get('acetylcholine', 0.0))
        series['norepinephrine'].append(net.neuromodulators.get('norepinephrine', 0.0))
        
        # Membrane potentials
        membrane_potentials = [n.membrane_potential for n in active_neurons]
        series['membrane_potential_mean'].append(np.mean(membrane_potentials))
        series['membrane_potential_std'].append(np.std(membrane_potentials))
        
        # Trinary states
        states = [n.trinary_state for n in active_neurons]
        series['excitatory_fraction'].append(sum(1 for s in states if s == 1) / len(states))
        series['inhibitory_fraction'].append(sum(1 for s in states if s == -1) / len(states))
        series['neutral_fraction'].append(sum(1 for s in states if s == 0) / len(states))
        
        # Synaptic weights
        if active_synapses:
            series['mean_w_fast'].append(np.mean([s.w_fast for s in active_synapses]))
            series['mean_w_slow'].append(np.mean([s.w_slow for s in active_synapses]))
            series['mean_w_meta'].append(np.mean([s.w_meta for s in active_synapses]))
        else:
            series['mean_w_fast'].append(0.0)
            series['mean_w_slow'].append(0.0)
            series['mean_w_meta'].append(0.0)
        
        # Phase coherence
        phases = [n.phase for n in active_neurons]
        if len(phases) >= 2:
            import cmath
            complex_phases = [cmath.exp(1j * p) for p in phases]
            phase_coherence = abs(sum(complex_phases) / len(complex_phases))
        else:
            phase_coherence = 0.0
        series['phase_coherence'].append(phase_coherence)
    
    def set_level(self, level: int):
        new_level = max(1, min(3, level))
        if new_level != self.log_level:
            self.log_level = new_level
            self.game_metadata['log_level'] = self.log_level
            if new_level >= 2 and not hasattr(self, 'time_series'):
                self._init_level2_data()
    
    def log_tick(self, tick: int, nxers: dict = None):
        self.summary['total_ticks'] = tick
        
        all_nxers = list((nxers or {}).values()) if nxers else []
        alive_nxers = [a for a in all_nxers if a.alive]
        
        if alive_nxers:
            all_active_neurons = []
            for a in alive_nxers:
                all_active_neurons.extend([n for n in a.net.all_neurons if n.is_active])
            
            if all_active_neurons:
                activity = sum(abs(n.trinary_state) for n in all_active_neurons) / len(all_active_neurons)
                self.summary['peak_network_activity'] = max(self.summary['peak_network_activity'], activity)
            
            branching_ratios = [a.net.branching_ratio for a in alive_nxers if a.net.branching_ratio > 0]
            if branching_ratios:
                avg_br = sum(branching_ratios) / len(branching_ratios)
                self.summary['average_branching_ratio'] = (
                    (self.summary['average_branching_ratio'] * self.summary['branching_ratio_samples'] + 
                    avg_br) / (self.summary['branching_ratio_samples'] + 1)
                )
                self.summary['branching_ratio_samples'] += 1
            
            for mod in ['dopamine', 'serotonin', 'acetylcholine', 'norepinephrine']:
                levels = [a.net.neuromodulators.get(mod, 0.0) for a in alive_nxers]
                avg_level = sum(levels) / len(levels) if levels else 0.0
                self.summary['neuromodulator_peaks'][mod] = max(self.summary['neuromodulator_peaks'][mod], avg_level)
        
        if self.log_level >= 2:
            self._log_tick_level2(tick, alive_nxers)
            # Only log individual NxEr time series at level 3
            if self.log_level >= 3:
                for a in alive_nxers:
                    self._log_nxer_individual(tick, a)
    
    def _log_tick_level2(self, tick: int, alive_nxers: list):
        """Capture detailed time series data each tick from ALL alive NxErs."""
        import numpy as np
        import cmath
        
        # Trim old data if needed
        if len(self.time_series['ticks']) >= self.max_history_length:
            trim_count = self.max_history_length // 10
            for key in self.time_series:
                if isinstance(self.time_series[key], list) and len(self.time_series[key]) > trim_count:
                    self.time_series[key] = self.time_series[key][trim_count:]
        
        # Basic timing
        self.time_series['ticks'].append(tick)
        self.time_series['timestamps'].append(time.time() - self.start_time)
        
        if not alive_nxers:
            # Append zeros/defaults if no alive NxErs
            for key in self.time_series:
                if key not in ['ticks', 'timestamps']:
                    self.time_series[key].append(0.0)
            return
        
        # Collect all active neurons and synapses across ALL alive NxErs
        all_active_neurons = []
        all_active_synapses = []
        all_networks = []
        
        for a in alive_nxers:
            net = a.net
            all_networks.append(net)
            all_active_neurons.extend([n for n in net.all_neurons if n.is_active])
            all_active_synapses.extend([s for s in net.synapses if s.integrity > 0])
        
        if not all_active_neurons:
            for key in self.time_series:
                if key not in ['ticks', 'timestamps']:
                    self.time_series[key].append(0.0)
            return
        
        # === EXISTING METRICS (now aggregated) ===
        activity = sum(abs(n.trinary_state) for n in all_active_neurons) / len(all_active_neurons)
        self.time_series['network_activity'].append(activity)
        
        # Branching ratio (average across networks)
        branching_ratios = [net.branching_ratio for net in all_networks]
        self.time_series['branching_ratio'].append(np.mean(branching_ratios))
        
        # Energy status (aggregate)
        total_energy = sum(n.energy_level for n in all_active_neurons)
        avg_energy = total_energy / len(all_active_neurons)
        
        # Efficiency calculation
        energy_spent = sum(max(0, n.energy_baseline - n.energy_level) for n in all_active_neurons)
        total_steps = sum(net.step_count for net in all_networks)
        energy_spent += total_steps * 0.01 * len(all_active_neurons) / max(1, len(all_networks))
        total_activation = sum(sum(net.activation_history) if net.activation_history else 0 for net in all_networks)
        efficiency = total_activation / max(1, energy_spent) if energy_spent > 0 else 0.0
        
        self.time_series['total_energy'].append(total_energy)
        self.time_series['average_energy'].append(avg_energy)
        self.time_series['energy_efficiency'].append(efficiency)
        
        # Temporal sync (phase coherence across ALL neurons)
        phases = [n.phase for n in all_active_neurons]
        if len(phases) >= 2:
            complex_phases = [cmath.exp(1j * p) for p in phases]
            temporal_sync = abs(sum(complex_phases) / len(complex_phases))
        else:
            temporal_sync = 0.0
        self.time_series['temporal_sync'].append(temporal_sync)
        
        # Neuromodulators (average across all networks)
        for mod in ['dopamine', 'serotonin', 'acetylcholine', 'norepinephrine']:
            levels = [net.neuromodulators.get(mod, 0.0) for net in all_networks]
            self.time_series[mod].append(np.mean(levels))
        
        # Oscillator drive (average)
        osc_drives = [net._global_oscillatory_drive() for net in all_networks]
        self.time_series['oscillator_drive'].append(np.mean(osc_drives))
        
        # === OSCILLATOR COMPONENTS (use first network's time as reference) ===
        ref_net = all_networks[0]
        t = ref_net.time
        low = math.sin(2.0 * math.pi * ref_net.params.oscillator_low_freq * t + ref_net.oscillator_phase_offsets[0])
        mid = math.sin(2.0 * math.pi * ref_net.params.oscillator_mid_freq * t + ref_net.oscillator_phase_offsets[1])
        high = math.sin(2.0 * math.pi * ref_net.params.oscillator_high_freq * t + ref_net.oscillator_phase_offsets[2])
        self.time_series['oscillator_low'].append(low)
        self.time_series['oscillator_mid'].append(mid)
        self.time_series['oscillator_high'].append(high)
        
        # === CROSS-FREQUENCY COUPLING ===
        cfc_low_mid = abs(low) * abs(mid)
        cfc_mid_high = abs(mid) * abs(high)
        self.time_series['cfc_low_mid'].append(cfc_low_mid)
        self.time_series['cfc_mid_high'].append(cfc_mid_high)
        
        # Phase coherence
        if len(phases) >= 2:
            complex_phases = [cmath.exp(1j * p) for p in phases]
            phase_coherence = abs(sum(complex_phases) / len(complex_phases))
            if phase_coherence > 0.4:
                prev_coherence = self.time_series['phase_coherence'][-2] if len(self.time_series['phase_coherence']) > 1 else 0.0
                if prev_coherence <= 0.4:
                    self.log_phase_event(tick, "high_synchronization", phase_coherence, {'active_count': len(all_active_neurons)})
        else:
            phase_coherence = 0.0
        self.time_series['phase_coherence'].append(phase_coherence)
        
        # === TRINARY STATE DISTRIBUTIONS ===
        states = [n.trinary_state for n in all_active_neurons]
        excitatory_frac = sum(1 for s in states if s == 1) / len(states)
        inhibitory_frac = sum(1 for s in states if s == -1) / len(states)
        neutral_frac = sum(1 for s in states if s == 0) / len(states)
        self.time_series['excitatory_fraction'].append(excitatory_frac)
        self.time_series['inhibitory_fraction'].append(inhibitory_frac)
        self.time_series['neutral_fraction'].append(neutral_frac)
        
        # === AUTORECEPTOR DYNAMICS ===
        autoreceptors = [n.autoreceptor for n in all_active_neurons]
        self.time_series['autoreceptor_mean'].append(np.mean(autoreceptors))
        self.time_series['autoreceptor_std'].append(np.std(autoreceptors))
        
        # === ADAPTATION DYNAMICS ===
        adaptations = [n.adaptation for n in all_active_neurons]
        self.time_series['adaptation_mean'].append(np.mean(adaptations))
        
        # === MEMBRANE POTENTIAL STATISTICS ===
        membrane_potentials = [n.membrane_potential for n in all_active_neurons]
        self.time_series['membrane_potential_mean'].append(np.mean(membrane_potentials))
        self.time_series['membrane_potential_std'].append(np.std(membrane_potentials))
        
        # === INTRINSIC TIMESCALE DISTRIBUTION ===
        timescales = [n.intrinsic_timescale for n in all_active_neurons]
        self.time_series['mean_intrinsic_timescale'].append(np.mean(timescales))
        self.time_series['timescale_heterogeneity'].append(np.std(timescales) / max(0.01, np.mean(timescales)))
        
        # === SYNAPSE STATISTICS ===
        silent_count = sum(1 for s in all_active_synapses if s.is_silent)
        modulatory_count = sum(1 for s in all_active_synapses if s.is_modulatory)
        self.time_series['silent_synapse_count'].append(silent_count)
        self.time_series['active_synapse_count'].append(len(all_active_synapses) - silent_count)
        self.time_series['modulatory_synapse_count'].append(modulatory_count)
        
        if all_active_synapses:
            self.time_series['mean_synapse_integrity'].append(np.mean([s.integrity for s in all_active_synapses]))
        else:
            self.time_series['mean_synapse_integrity'].append(0.0)
        
        # === DENDRITIC METRICS ===
        all_branch_potentials = []
        all_plateau_potentials = []
        dendritic_spike_count = 0
        for n in all_active_neurons:
            for b in n.dendritic_branches:
                all_branch_potentials.append(b.branch_potential)
                all_plateau_potentials.append(b.plateau_potential)
                if abs(b.branch_potential) > b.branch_threshold:
                    dendritic_spike_count += 1
        
        self.time_series['mean_branch_potential'].append(np.mean(all_branch_potentials) if all_branch_potentials else 0.0)
        self.time_series['mean_plateau_potential'].append(np.mean(all_plateau_potentials) if all_plateau_potentials else 0.0)
        self.time_series['dendritic_spike_count'].append(dendritic_spike_count)
        
        # === SPONTANEOUS VS DRIVEN FIRING ===
        self.time_series['spontaneous_firing_count'].append(0)
        self.time_series['driven_firing_count'].append(0)
        
        # === SYNAPTIC WEIGHT EVOLUTION ===
        if all_active_synapses:
            w_fast_vals = [s.w_fast for s in all_active_synapses]
            w_slow_vals = [s.w_slow for s in all_active_synapses]
            w_meta_vals = [s.w_meta for s in all_active_synapses]
            
            self.time_series['mean_w_fast'].append(np.mean(w_fast_vals))
            self.time_series['mean_w_slow'].append(np.mean(w_slow_vals))
            self.time_series['mean_w_meta'].append(np.mean(w_meta_vals))
            self.time_series['std_w_fast'].append(np.std(w_fast_vals))
            self.time_series['std_w_slow'].append(np.std(w_slow_vals))
            self.time_series['std_w_meta'].append(np.std(w_meta_vals))
            
            pre_traces = [s.pre_trace for s in all_active_synapses]
            post_traces = [s.post_trace for s in all_active_synapses]
            pre_traces_ltd = [s.pre_trace_ltd for s in all_active_synapses]
            
            self.time_series['mean_pre_trace'].append(np.mean(pre_traces))
            self.time_series['mean_post_trace'].append(np.mean(post_traces))
            self.time_series['mean_pre_trace_ltd'].append(np.mean(pre_traces_ltd))
            self.time_series['std_pre_trace'].append(np.std(pre_traces))
            
            delta_w_vals = [abs(s.potential_delta_w) for s in all_active_synapses]
            self.time_series['mean_delta_w'].append(np.mean(delta_w_vals))
            
            lr_mods = [s.learning_rate_mod for s in all_active_synapses]
            self.time_series['mean_learning_rate_mod'].append(np.mean(lr_mods))
            self.time_series['std_learning_rate_mod'].append(np.std(lr_mods))
            
            ionotropic_contrib = [abs(s.w_fast) + abs(s.w_slow) for s in all_active_synapses if not s.is_modulatory]
            metabotropic_contrib = [abs(s.w_meta) for s in all_active_synapses if s.is_modulatory]
            
            self.time_series['ionotropic_contribution_mean'].append(
                np.mean(ionotropic_contrib) if ionotropic_contrib else 0.0)
            self.time_series['metabotropic_contribution_mean'].append(
                np.mean(metabotropic_contrib) if metabotropic_contrib else 0.0)
        else:
            for key in ['mean_w_fast', 'mean_w_slow', 'mean_w_meta', 
                    'std_w_fast', 'std_w_slow', 'std_w_meta',
                    'mean_pre_trace', 'mean_post_trace', 'mean_pre_trace_ltd', 'std_pre_trace',
                    'mean_delta_w', 'mean_learning_rate_mod', 'std_learning_rate_mod',
                    'ionotropic_contribution_mean', 'metabotropic_contribution_mean']:
                self.time_series[key].append(0.0)
        
        # === PLASTICITY AND ASSOCIATIVITY ===
        if all_active_synapses:
            associativity_contribs = []
            for s in all_active_synapses:
                if s.neighbor_synapses:
                    neighbor_deltas = [ns.potential_delta_w for ns in s.neighbor_synapses[:3]]
                    if neighbor_deltas:
                        contrib = ref_net.params.associativity_strength * sum(
                            dw / (i + 1) for i, dw in enumerate(neighbor_deltas))
                        associativity_contribs.append(abs(contrib))
            
            self.time_series['mean_associativity_contribution'].append(
                np.mean(associativity_contribs) if associativity_contribs else 0.0)
            self.time_series['associativity_event_count'].append(
                sum(1 for c in associativity_contribs if c > 0.001))
        else:
            self.time_series['mean_associativity_contribution'].append(0.0)
            self.time_series['associativity_event_count'].append(0)
        
        self.time_series['ltp_rate'].append(0)
        self.time_series['ltd_rate'].append(0)
        
        # === AUTOCORRELATION WINDOWS ===
        acw_estimates = []
        autocorr_coeffs = []
        
        for n in all_active_neurons:
            if len(n.state_history) >= 10:
                states = list(n.state_history)
                states_a = states[:-1]
                states_b = states[1:]
                if np.std(states_a) < 1e-10 or np.std(states_b) < 1e-10:
                    continue
                try:
                    autocorr = np.corrcoef(states_a, states_b)[0, 1]
                    if not np.isnan(autocorr):
                        autocorr_coeffs.append(autocorr)
                        acw = n.intrinsic_timescale * (1.0 + abs(autocorr))
                        acw_estimates.append(acw)
                except:
                    pass
        
        if acw_estimates:
            mean_acw = np.mean(acw_estimates)
            self.time_series['mean_autocorrelation_window'].append(mean_acw)
            self.time_series['std_autocorrelation_window'].append(np.std(acw_estimates))
            self.summary['peak_autocorrelation_window'] = max(
                self.summary['peak_autocorrelation_window'], mean_acw)
        else:
            self.time_series['mean_autocorrelation_window'].append(0.0)
            self.time_series['std_autocorrelation_window'].append(0.0)
        
        self.time_series['autocorrelation_coefficient_mean'].append(
            np.mean(autocorr_coeffs) if autocorr_coeffs else 0.0)
        
        # === THRESHOLD MODULATION ===
        ach_levels = [net.neuromodulators.get('acetylcholine', 0.5) for net in all_networks]
        ach = np.mean(ach_levels)
        
        theta_exc_effectives = []
        theta_inh_effectives = []
        ach_mods = []
        autoreceptor_mods = []
        
        for n in all_active_neurons:
            threshold_mod = (ach - 0.5) * 0.5
            ach_mods.append(threshold_mod)
            
            autoreceptor_mod = -0.1 * n.autoreceptor
            autoreceptor_mods.append(autoreceptor_mod)
            
            theta_exc_eff = n.firing_threshold_excitatory - threshold_mod + autoreceptor_mod
            theta_inh_eff = n.firing_threshold_inhibitory - threshold_mod - autoreceptor_mod
            
            theta_exc_effectives.append(theta_exc_eff)
            theta_inh_effectives.append(theta_inh_eff)
        
        self.time_series['mean_threshold_excitatory_effective'].append(np.mean(theta_exc_effectives))
        self.time_series['mean_threshold_inhibitory_effective'].append(np.mean(theta_inh_effectives))
        self.time_series['threshold_modulation_by_ach'].append(np.mean(ach_mods))
        self.time_series['threshold_modulation_by_autoreceptor'].append(np.mean(autoreceptor_mods))
        
        # === NEUROMODULATOR SPATIAL DYNAMICS ===
        try:
            all_grid_entropies = []
            all_grad_magnitudes = []
            all_da_variances = []
            all_ser_variances = []
            
            for net in all_networks:
                grid_flat = net.modulator_grid.flatten()
                grid_normalized = (grid_flat - grid_flat.min()) / (grid_flat.max() - grid_flat.min() + 1e-10)
                hist, _ = np.histogram(grid_normalized, bins=20, density=True)
                hist = hist[hist > 0]
                grid_entropy = -np.sum(hist * np.log(hist + 1e-10)) / np.log(20)
                all_grid_entropies.append(grid_entropy)
                
                grad_y = np.diff(net.modulator_grid, axis=0)
                grad_x = np.diff(net.modulator_grid, axis=1)
                grad_magnitude = np.sqrt(np.mean(grad_y**2) + np.mean(grad_x**2))
                all_grad_magnitudes.append(grad_magnitude)
                
                all_da_variances.append(np.var(net.modulator_grid[:, :, 0]))
                all_ser_variances.append(np.var(net.modulator_grid[:, :, 1]))
            
            self.time_series['modulator_grid_entropy'].append(np.mean(all_grid_entropies))
            self.time_series['modulator_grid_gradient_magnitude'].append(np.mean(all_grad_magnitudes))
            self.time_series['dopamine_spatial_variance'].append(np.mean(all_da_variances))
            self.time_series['serotonin_spatial_variance'].append(np.mean(all_ser_variances))
        except Exception:
            self.time_series['modulator_grid_entropy'].append(0.0)
            self.time_series['modulator_grid_gradient_magnitude'].append(0.0)
            self.time_series['dopamine_spatial_variance'].append(0.0)
            self.time_series['serotonin_spatial_variance'].append(0.0)
        
        # === SILENT SYNAPSE DYNAMICS ===
        if all_active_synapses:
            silent_count = sum(1 for s in all_active_synapses if s.is_silent)
            silent_fraction = silent_count / len(all_active_synapses)
            self.time_series['silent_synapse_fraction'].append(silent_fraction)
        else:
            self.time_series['silent_synapse_fraction'].append(0.0)
        
        self.time_series['silent_to_active_transitions'].append(0)
        self.time_series['active_to_silent_transitions'].append(0)
        
        # === SUBTHRESHOLD INTEGRATION ===
        subthreshold_count = 0
        near_threshold_count = 0
        
        for n in all_active_neurons:
            if n.trinary_state == 0:
                theta_exc = n.firing_threshold_excitatory
                theta_inh = n.firing_threshold_inhibitory
                
                if n.membrane_potential > theta_exc * 0.8 or n.membrane_potential < theta_inh * 0.8:
                    near_threshold_count += 1
                    subthreshold_count += 1
        
        self.time_series['subthreshold_integration_count'].append(subthreshold_count)
        self.time_series['near_threshold_fraction'].append(
            near_threshold_count / len(all_active_neurons) if all_active_neurons else 0.0)
        
        # === EXTENDED OSCILLATOR/PAC METRICS ===
        t = ref_net.time
        
        delta = math.sin(2.0 * math.pi * 0.02 * t)
        theta_osc = math.sin(2.0 * math.pi * 0.08 * t)
        gamma = math.sin(2.0 * math.pi * 5.0 * t)
        
        pac_theta_gamma = abs(theta_osc) * abs(gamma)
        pac_delta_theta = abs(delta) * abs(theta_osc)
        
        self.time_series['pac_theta_gamma'].append(pac_theta_gamma)
        self.time_series['pac_delta_theta'].append(pac_delta_theta)
        
        if len(all_active_neurons) >= 2:
            phase_velocities = [n.natural_frequency * 2 * math.pi for n in all_active_neurons]
            self.time_series['mean_phase_velocity'].append(np.mean(phase_velocities))
        else:
            self.time_series['mean_phase_velocity'].append(0.0)
        
        # === ITU/AIGARTH METRICS ===
        all_itu_circles = []
        for net in all_networks:
            all_itu_circles.extend(net.itu_circles)
        
        if all_itu_circles:
            fitness_vals = []
            for circle in all_itu_circles:
                if circle.fitness_history:
                    fitness_vals.append(circle.fitness_history[-1])
            
            if fitness_vals:
                self.time_series['itu_mean_fitness'].append(np.mean(fitness_vals))
                self.time_series['itu_fitness_variance'].append(np.var(fitness_vals))
            else:
                self.time_series['itu_mean_fitness'].append(0.0)
                self.time_series['itu_fitness_variance'].append(0.0)
        else:
            self.time_series['itu_mean_fitness'].append(0.0)
            self.time_series['itu_fitness_variance'].append(0.0)
        
        self.time_series['itu_mutation_events'].append(0)
        self.time_series['itu_pruning_events'].append(0)
        
        # Take snapshots at intervals
        if tick - self.last_snapshot_tick >= self.snapshot_interval:
            self._take_snapshot_multi(tick, alive_nxers)
            self.last_snapshot_tick = tick
    
    def _take_snapshot_multi(self, tick: int, alive_nxers: list):
        """Take detailed snapshots of ALL alive NxErs at intervals."""
        
        # Neuron snapshot - all neurons from all NxErs
        neuron_states = {}
        for a in alive_nxers:
            for n in a.net.all_neurons:
                neuron_states[f"{a.id}_{n.id}"] = {
                    'nxer_id': a.id,
                    'nxer_name': a.name,
                    'neuron_id': n.id,
                    'trinary_state': n.trinary_state,
                    'membrane_potential': n.membrane_potential,
                    'adaptation': n.adaptation,
                    'autoreceptor': n.autoreceptor,
                    'health': n.health,
                    'energy_level': n.energy_level,
                    'phase': n.phase,
                    'is_active': n.is_active,
                    'intrinsic_timescale': n.intrinsic_timescale,
                    'dendritic_branches': [{
                        'branch_id': b.branch_id,
                        'branch_potential': b.branch_potential,
                        'plateau_potential': b.plateau_potential,
                        'branch_threshold': b.branch_threshold,
                        'local_ca_influx': b.get_local_ca_influx()
                    } for b in n.dendritic_branches]
                }
        self.neuron_snapshots.append({'tick': tick, 'neuron_states': neuron_states})
        
        # Synapse snapshot - sample from all NxErs
        synapse_weights = {}
        for a in alive_nxers:
            sample_synapses = a.net.synapses[:50] if len(a.net.synapses) > 50 else a.net.synapses
            for s in sample_synapses:
                synapse_weights[f"{a.id}_{s.pre_id}_{s.post_id}"] = {
                    'nxer_id': a.id,
                    'nxer_name': a.name,
                    'w_fast': s.w_fast,
                    'w_slow': s.w_slow,
                    'w_meta': s.w_meta,
                    'integrity': s.integrity,
                    'pre_trace': s.pre_trace,
                    'post_trace': s.post_trace,
                    'is_silent': s.is_silent,
                    'is_modulatory': s.is_modulatory,
                    'tau_fast': s.tau_fast,
                    'tau_slow': s.tau_slow,
                    'tau_meta': s.tau_meta,
                    'learning_rate': s.learning_rate,
                    'plasticity_threshold': s.plasticity_threshold,
                    'potential_delta_w': s.potential_delta_w,
                    'neighbor_count': len(s.neighbor_synapses),
                }
        self.synapse_snapshots.append({'tick': tick, 'synapse_weights': synapse_weights})
        
        # ITU fitness history from all NxErs
        for a in alive_nxers:
            for circle in a.net.itu_circles:
                if circle.fitness_history:
                    self.itu_fitness_history.append({
                        'tick': tick,
                        'nxer_id': a.id,
                        'nxer_name': a.name,
                        'circle_id': circle.circle_id,
                        'fitness': circle.fitness_history[-1]
                    })
    
    
    def _take_snapshot(self, tick: int, network: 'NeuraxonNetwork', nxers: dict):
        """Take detailed snapshots at intervals."""
        
        # Existing neuron snapshot
        neuron_states = {}
        for n in network.all_neurons:
            neuron_states[n.id] = {
                'trinary_state': n.trinary_state,
                'membrane_potential': n.membrane_potential,
                'adaptation': n.adaptation,
                'autoreceptor': n.autoreceptor,  # NEW
                'health': n.health,
                'energy_level': n.energy_level,
                'phase': n.phase,
                'is_active': n.is_active,
                'intrinsic_timescale': n.intrinsic_timescale,
                # NEW: Dendritic branch details
                'dendritic_branches': [{
                    'branch_id': b.branch_id,
                    'branch_potential': b.branch_potential,
                    'plateau_potential': b.plateau_potential,
                    'branch_threshold': b.branch_threshold,
                    'local_ca_influx': b.get_local_ca_influx()
                } for b in n.dendritic_branches]
            }
        self.neuron_snapshots.append({'tick': tick, 'neuron_states': neuron_states})
        
        # Existing synapse snapshot (sample)
        synapse_weights = {}
        sample_synapses = network.synapses[:100] if len(network.synapses) > 100 else network.synapses
        for s in sample_synapses:
            synapse_weights[(s.pre_id, s.post_id)] = {
                'w_fast': s.w_fast,
                'w_slow': s.w_slow,
                'w_meta': s.w_meta,
                'integrity': s.integrity,
                'pre_trace': s.pre_trace,
                'post_trace': s.post_trace,
                'is_silent': s.is_silent,       # NEW
                'is_modulatory': s.is_modulatory, # NEW
                'tau_fast': s.tau_fast,          # NEW
                'tau_slow': s.tau_slow,          # NEW
                'tau_meta': s.tau_meta,          # NEW
                'learning_rate': s.learning_rate,  # NEW: Individual synapse learning rate
                'plasticity_threshold': s.plasticity_threshold,  # NEW
                'potential_delta_w': s.potential_delta_w,  # NEW: Current weight change
                'neighbor_count': len(s.neighbor_synapses),  # NEW: For associativity analysis
            }
        self.synapse_snapshots.append({'tick': tick, 'synapse_weights': synapse_weights})
        for circle in network.itu_circles:
            if circle.fitness_history:
                self.itu_fitness_history.append({
                    'tick': tick,
                    'circle_id': circle.circle_id,
                    'fitness': circle.fitness_history[-1]
                })
    
    def log_plasticity_event(self, tick: int, event_type: str, pre_id: int, post_id: int, 
                             delta_w: float, details: dict = None):
        self.summary['total_plasticity_events'] += 1
        if event_type == 'LTP':
            self.summary['total_ltp_events'] += 1
            # Update tick-level LTP rate
            if self.log_level >= 2 and self.time_series['ltp_rate']:
                self.time_series['ltp_rate'][-1] += 1
        elif event_type == 'LTD':
            self.summary['total_ltd_events'] += 1
            # Update tick-level LTD rate
            if self.log_level >= 2 and self.time_series['ltd_rate']:
                self.time_series['ltd_rate'][-1] += 1
        
        if self.log_level >= 2:
            self.plasticity_events.append({
                'tick': tick,
                'type': event_type,
                'pre_id': pre_id,
                'post_id': post_id,
                'delta_w': delta_w,
                'details': details or {}
            })
    
    # NEW: Event Logging Methods
    def log_silent_synapse_event(self, tick: int, pre_id: int, post_id: int, 
                                 became_active: bool, trigger: str = "unknown"):
        """Log when a silent synapse becomes active or vice versa."""
        if self.log_level >= 2:
            self.silent_synapse_events.append({
                'tick': tick,
                'pre_id': pre_id,
                'post_id': post_id,
                'became_active': became_active,
                'trigger': trigger
            })
            # Update transition counters
            if became_active:
                if self.time_series['silent_to_active_transitions']:
                    self.time_series['silent_to_active_transitions'][-1] += 1
            else:
                if self.time_series['active_to_silent_transitions']:
                    self.time_series['active_to_silent_transitions'][-1] += 1

    def log_spontaneous_event(self, tick: int, neuron_id: int, membrane_potential: float):
        """Log spontaneous firing events (not driven by synaptic input)."""
        if self.log_level >= 2:
            self.spontaneous_events.append({
                'tick': tick,
                'neuron_id': neuron_id,
                'membrane_potential': membrane_potential
            })
            if self.time_series['spontaneous_firing_count']:
                self.time_series['spontaneous_firing_count'][-1] += 1

    def log_driven_firing(self, tick: int):
        """Increment driven firing counter."""
        if self.log_level >= 2 and self.time_series['driven_firing_count']:
            self.time_series['driven_firing_count'][-1] += 1

    def log_homeostatic_event(self, tick: int, neuron_id: int, old_value: float, 
                              new_value: float, activity: float):
        """Log homeostatic plasticity threshold adjustments."""
        if self.log_level >= 2:
            self.summary['total_homeostatic_adjustments'] += 1
            self.homeostatic_events.append({
                'tick': tick,
                'neuron_id': neuron_id,
                'old_threshold': old_value,
                'new_threshold': new_value,
                'activity_level': activity,
                'direction': 'increased' if new_value > old_value else 'decreased'
            })

    def log_dendritic_spike_event(self, tick: int, neuron_id: int, branch_id: int,
                                   branch_potential: float, plateau_potential: float,
                                   ca_influx: float):
        """Log local dendritic spike events."""
        if self.log_level >= 2:
            self.summary['total_dendritic_spikes'] += 1
            self.dendritic_spike_events.append({
                'tick': tick,
                'neuron_id': neuron_id,
                'branch_id': branch_id,
                'branch_potential': branch_potential,
                'plateau_potential': plateau_potential,
                'ca_influx': ca_influx
            })

    def log_autoreceptor_event(self, tick: int, neuron_id: int, autoreceptor_value: float,
                               threshold_effect: float):
        """Log significant autoreceptor modulation events."""
        if self.log_level >= 2:
            self.autoreceptor_events.append({
                'tick': tick,
                'neuron_id': neuron_id,
                'autoreceptor_value': autoreceptor_value,
                'threshold_effect': threshold_effect
            })

    def log_neuromodulator_event(self, tick: int, modulator: str, level: float,
                                  crossed_threshold: str, effect: str):
        """Log neuromodulator threshold crossings (high/low affinity)."""
        if self.log_level >= 2:
            self.neuromodulator_events.append({
                'tick': tick,
                'modulator': modulator,
                'level': level,
                'crossed_threshold': crossed_threshold,
                'effect': effect
            })

    def log_phase_event(self, tick: int, event_type: str, phase_coherence: float,
                        details: dict = None):
        """Log phase synchronization events."""
        if self.log_level >= 2:
            self.phase_reset_events.append({
                'tick': tick,
                'event_type': event_type,
                'phase_coherence': phase_coherence,
                'details': details or {}
            })
            # Update peak coherence
            self.summary['peak_phase_coherence'] = max(
                self.summary['peak_phase_coherence'], phase_coherence)
    
    # ============================================================
    # NEW: Additional Event Logging Methods for Paper Validation
    # ============================================================
    
    def log_weight_evolution_event(self, tick: int, synapse_pre_id: int, synapse_post_id: int,
                                    w_fast_old: float, w_fast_new: float,
                                    w_slow_old: float, w_slow_new: float,
                                    w_meta_old: float, w_meta_new: float):
        """Log significant weight changes across all three timescales."""
        if self.log_level >= 2:
            self.weight_evolution_events.append({
                'tick': tick,
                'pre_id': synapse_pre_id,
                'post_id': synapse_post_id,
                'w_fast_delta': w_fast_new - w_fast_old,
                'w_slow_delta': w_slow_new - w_slow_old,
                'w_meta_delta': w_meta_new - w_meta_old
            })
    
    def log_threshold_modulation_event(self, tick: int, neuron_id: int,
                                        base_threshold: float, effective_threshold: float,
                                        ach_contribution: float, autoreceptor_contribution: float):
        """Log threshold modulation events (Paper Section 1)."""
        if self.log_level >= 2:
            self.summary['total_threshold_modulations'] += 1
            self.threshold_modulation_events.append({
                'tick': tick,
                'neuron_id': neuron_id,
                'base_threshold': base_threshold,
                'effective_threshold': effective_threshold,
                'ach_contribution': ach_contribution,
                'autoreceptor_contribution': autoreceptor_contribution,
                'total_modulation': effective_threshold - base_threshold
            })
    
    def log_associativity_event(self, tick: int, synapse_pre_id: int, synapse_post_id: int,
                                 own_delta_w: float, neighbor_contribution: float,
                                 final_delta_w: float):
        """Log associativity plasticity events (Paper Section 4 equation)."""
        if self.log_level >= 2:
            self.summary['total_associativity_events'] += 1
            self.associativity_events.append({
                'tick': tick,
                'pre_id': synapse_pre_id,
                'post_id': synapse_post_id,
                'own_delta_w': own_delta_w,
                'neighbor_contribution': neighbor_contribution,
                'final_delta_w': final_delta_w,
                'amplification_factor': final_delta_w / own_delta_w if own_delta_w != 0 else 0.0
            })
    
    def log_subthreshold_event(self, tick: int, neuron_id: int, membrane_potential: float,
                                threshold: float, distance_to_threshold: float):
        """Log subthreshold integration events (Paper Section 5)."""
        if self.log_level >= 2:
            self.summary['total_subthreshold_integrations'] += 1
            self.subthreshold_events.append({
                'tick': tick,
                'neuron_id': neuron_id,
                'membrane_potential': membrane_potential,
                'threshold': threshold,
                'distance_to_threshold': distance_to_threshold,
                'fraction_of_threshold': membrane_potential / threshold if threshold != 0 else 0.0
            })
    
    def log_itu_evolution_event(self, tick: int, circle_id: int, event_type: str,
                                 fitness_before: float, fitness_after: float,
                                 neurons_affected: int):
        """Log ITU/Aigarth evolution events (Paper Section 8)."""
        if self.log_level >= 2:
            if event_type == 'mutation':
                if self.time_series['itu_mutation_events']:
                    self.time_series['itu_mutation_events'][-1] += 1
            elif event_type == 'pruning':
                if self.time_series['itu_pruning_events']:
                    self.time_series['itu_pruning_events'][-1] += 1
    
    def get_event_lists(self) -> dict:
        """Helper to return references to all event lists."""
        return {
            'plasticity_events': self.plasticity_events,  # Missing
            'silent_synapse_events': self.silent_synapse_events,
            'spontaneous_events': self.spontaneous_events,
            'homeostatic_events': self.homeostatic_events,
            'dendritic_spike_events': self.dendritic_spike_events,
            'autoreceptor_events': self.autoreceptor_events,
            'neuromodulator_events': self.neuromodulator_events,
            'phase_reset_events': self.phase_reset_events,
            # NEW event lists
            'weight_evolution_events': self.weight_evolution_events,
            'threshold_modulation_events': self.threshold_modulation_events,
            'associativity_events': self.associativity_events,
            'subthreshold_events': self.subthreshold_events,
        }

    def clear_events(self):
        """Clears transient event lists (used in worker processes)."""
        for lst in self.get_event_lists().values():
            lst.clear()

    def merge_events(self, remote_events: dict):
        """Merges events from a worker process into the main logger."""
        local_lists = self.get_event_lists()
        for key, events in remote_events.items():
            if key in local_lists and events:
                local_lists[key].extend(events)
                # ADD: Count LTP/LTD from merged events
                if key == 'plasticity_events':
                    for evt in events:
                        if evt.get('type') == 'LTP':
                            self.summary['total_ltp_events'] += 1
                            if self.time_series['ltp_rate']:
                                self.time_series['ltp_rate'][-1] += 1
                        elif evt.get('type') == 'LTD':
                            self.summary['total_ltd_events'] += 1
                            if self.time_series['ltd_rate']:
                                self.time_series['ltd_rate'][-1] += 1

    def log_structural_event(self, tick: int, event_type: str, entity_id: int, details: dict = None):
        if event_type == 'synapse_created':
            self.summary['total_synapses_created'] += 1
        elif event_type == 'synapse_pruned':
            self.summary['total_synapses_pruned'] += 1
        elif event_type == 'neuron_created':
            self.summary['total_neurons_created'] += 1
        elif event_type == 'neuron_died':
            self.summary['total_neurons_died'] += 1
        if self.log_level >= 2:
            self.structural_events.append({
                'tick': tick,
                'type': event_type,
                'entity_id': entity_id,
                'details': details or {}
            })
    
    def log_nxer_event(self, tick: int, event_type: str, nxer_id: int, details: dict = None):
        if event_type == 'born':
            self.nxer_summary['total_born'] += 1
        elif event_type == 'died':
            self.nxer_summary['total_died'] += 1
        if self.log_level >= 2:
            self.nxer_events.append({
                'tick': tick,
                'type': event_type,
                'nxer_id': nxer_id,
                'details': details or {}
            })
    
    def log_io_pattern(self, tick: int, nxer_id: int, inputs: tuple, outputs: tuple):
        if self.log_level >= 2:
            if len(self.io_patterns) >= self.max_history_length:
                self.io_patterns = self.io_patterns[self.max_history_length // 10:]
            self.io_patterns.append({
                'tick': tick,
                'nxer_id': nxer_id,
                'inputs': list(inputs),
                'outputs': list(outputs)
            })
    
    def update_nxer_stats(self, nxer: 'NxEr'):
        self.nxer_summary['max_food_found'] = max(self.nxer_summary['max_food_found'], nxer.stats.food_found)
        self.nxer_summary['max_time_lived'] = max(self.nxer_summary['max_time_lived'], nxer.stats.time_lived_s)
        self.nxer_summary['max_mates'] = max(self.nxer_summary['max_mates'], nxer.stats.mates_performed)
        self.nxer_summary['max_explored'] = max(self.nxer_summary['max_explored'], nxer.stats.explored)
       
    def to_dict(self) -> dict:
        def sanitize(obj):
            if isinstance(obj, float):
                if math.isnan(obj) or math.isinf(obj):
                    return 0.0  # Replace NaN/Inf with 0.0
                return obj
            elif isinstance(obj, list):
                return [sanitize(x) for x in obj]
            elif isinstance(obj, dict):
                return {k: sanitize(v) for k, v in obj.items()}
            return obj
        """Serialize all logged data to a dictionary with compression."""
        self.game_metadata['end_timestamp'] = datetime.now().isoformat()
        self.game_metadata['duration_seconds'] = time.time() - self.start_time
        self.game_metadata['log_level'] = self.log_level
        
        data = {
            'metadata': self.game_metadata,
            'summary': self.summary,
            'nxer_summary': self.nxer_summary
        }
        
        if self.log_level >= 2:
            # Set limit_logs based on log level
            if self.log_level >= 3:
                limit_logs = 100000
            else:
                limit_logs = 5000
            
            serializable_synapse_snapshots = []
            for snapshot in self.synapse_snapshots:
                serializable_weights = {}
                for key, weights in snapshot.get('synapse_weights', {}).items():
                    k_str = f"{key[0]}_{key[1]}" if isinstance(key, tuple) else str(key)
                    serializable_weights[k_str] = weights
                serializable_synapse_snapshots.append({
                    'tick': snapshot['tick'],
                    'synapse_weights': serializable_weights
                })

            SPARSE_KEYS = {'alive', 'food_found', 'explored', 'mates_performed' }
            
            optimized_nxer_series = {}
            # Only include per_nxer_time_series at level 3
            if self.log_level >= 3:
                for nxer_id, series in self.per_nxer_time_series.items():
                    optimized_series = {}
                    for metric, values in series.items():
                        if metric in SPARSE_KEYS:
                            optimized_series[metric] = self._compress_series(values)
                        else:
                            optimized_series[metric] = values
                    optimized_nxer_series[nxer_id] = optimized_series

            data['level2'] = {                
                'time_series':sanitize(self.time_series),
                'per_nxer_time_series': sanitize(optimized_nxer_series),
                
                'plasticity_events': self.plasticity_events[-limit_logs:],
                'structural_events': self.structural_events[-limit_logs:],
                'neuron_snapshots': self.neuron_snapshots[-limit_logs:],
                'synapse_snapshots': serializable_synapse_snapshots[-limit_logs:],
                'nxer_events': self.nxer_events[-limit_logs:],
                'itu_fitness_history': self.itu_fitness_history[-limit_logs:],
                'io_patterns': self.io_patterns[-limit_logs:],
                'silent_synapse_events': self.silent_synapse_events[-limit_logs:],
                'spontaneous_events': self.spontaneous_events[-limit_logs:],
                'homeostatic_events': self.homeostatic_events[-limit_logs:],
                'dendritic_spike_events': self.dendritic_spike_events[-limit_logs:],
                'autoreceptor_events': self.autoreceptor_events[-limit_logs:],
                'neuromodulator_events': self.neuromodulator_events[-limit_logs:],
                'phase_reset_events': self.phase_reset_events[-limit_logs:],
                'weight_evolution_events': self.weight_evolution_events[-limit_logs:],
                'threshold_modulation_events': self.threshold_modulation_events[-limit_logs:],
                'associativity_events': self.associativity_events[-limit_logs:],
                'subthreshold_events': self.subthreshold_events[-limit_logs:],
            }
        return data
    
    def save_to_file(self, filepath: str):
        data = self.to_dict()
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        print(f"[DATALOGGER] Saved to {filepath}")


# ============================================================
# NEW: Helper function to generate paper validation report
# ============================================================
def generate_paper_validation_report(logger: DataLogger) -> dict:
    """
    Generate a structured report mapping logged data to paper sections.
    Useful for validating the implementation against the Neuraxon paper.
    """
    report = {
        'paper_section_1_trinary_neuromodulation': {
            'trinary_state_distributions': {
                'excitatory_samples': len([x for x in logger.time_series.get('excitatory_fraction', []) if x > 0]),
                'inhibitory_samples': len([x for x in logger.time_series.get('inhibitory_fraction', []) if x > 0]),
                'neutral_samples': len([x for x in logger.time_series.get('neutral_fraction', []) if x > 0]),
            },
            'neuromodulator_dynamics': {
                mod: {
                    'peak': logger.summary['neuromodulator_peaks'].get(mod, 0),
                    'events_logged': len([e for e in logger.neuromodulator_events if e.get('modulator') == mod])
                } for mod in ['dopamine', 'serotonin', 'acetylcholine', 'norepinephrine']
            },
            'threshold_modulation_events': logger.summary.get('total_threshold_modulations', 0),
        },
        'paper_section_2_temporal_dynamics': {
            'total_ticks': logger.summary['total_ticks'],
            'timestamps_logged': len(logger.time_series.get('timestamps', [])),
            'oscillator_components_tracked': all(
                len(logger.time_series.get(k, [])) > 0 
                for k in ['oscillator_low', 'oscillator_mid', 'oscillator_high']
            ),
        },
        'paper_section_3_synaptic_computation': {
            'weight_timescales_tracked': {
                'w_fast': len(logger.time_series.get('mean_w_fast', [])),
                'w_slow': len(logger.time_series.get('mean_w_slow', [])),
                'w_meta': len(logger.time_series.get('mean_w_meta', [])),
            },
            'synaptic_trace_dynamics': {
                'pre_trace': len(logger.time_series.get('mean_pre_trace', [])),
                'post_trace': len(logger.time_series.get('mean_post_trace', [])),
            },
            'ionotropic_vs_metabotropic': {
                'ionotropic_samples': len(logger.time_series.get('ionotropic_contribution_mean', [])),
                'metabotropic_samples': len(logger.time_series.get('metabotropic_contribution_mean', [])),
            },
        },
        'paper_section_4_plasticity': {
            'total_plasticity_events': logger.summary['total_plasticity_events'],
            'ltp_events': logger.summary['total_ltp_events'],
            'ltd_events': logger.summary['total_ltd_events'],
            'associativity_events': logger.summary.get('total_associativity_events', 0),
            'homeostatic_adjustments': logger.summary.get('total_homeostatic_adjustments', 0),
        },
        'paper_section_5_complex_signaling': {
            'silent_synapse_activations': logger.summary.get('total_silent_synapse_activations', 0),
            'subthreshold_integrations': logger.summary.get('total_subthreshold_integrations', 0),
        },
        'paper_section_6_self_generated_activity': {
            'spontaneous_events': logger.summary.get('total_spontaneous_events', 0),
            'autocorrelation_window_tracked': len(logger.time_series.get('mean_autocorrelation_window', [])) > 0,
            'peak_acw': logger.summary.get('peak_autocorrelation_window', 0),
        },
        'paper_section_7_synchronization': {
            'phase_coherence_tracked': len(logger.time_series.get('phase_coherence', [])),
            'peak_coherence': logger.summary.get('peak_phase_coherence', 0),
            'cfc_metrics_tracked': all(
                len(logger.time_series.get(k, [])) > 0 
                for k in ['cfc_low_mid', 'cfc_mid_high', 'pac_theta_gamma']
            ),
        },
        'paper_section_8_aigarth_hybrid': {
            'itu_fitness_tracked': len(logger.time_series.get('itu_mean_fitness', [])),
            'itu_fitness_history': len(logger.itu_fitness_history),
        },
    }
    return report


# Global data logger instance
_data_logger: Optional[DataLogger] = None

def get_data_logger() -> DataLogger:
    global _data_logger
    if _data_logger is None:
        _data_logger = DataLogger(log_level=1)
    return _data_logger

def set_data_logger_level(level: int):
    get_data_logger().set_level(level)

# New Version 2.2: Enhanced Full Feldged Inheritance
def Inheritance(father: 'NxEr', mother: 'NxEr') -> 'NeuraxonNetwork':
    """
    Creates a child NeuraxonNetwork by inheriting 50% of ALL parameters from each parent.
    
    HANDLES DIFFERENT-SIZED NETWORKS:
    - Uses proportional mapping for neurons (not modulo)
    - Intelligently matches synapses by relative position
    - Weighted sampling when structures don't align
    
    Args:
        father: The male NxEr parent
        mother: The female NxEr parent
    
    Returns:
        A new NeuraxonNetwork with 50% inheritance from each parent
    """
    
    father_net = father.net
    mother_net = mother.net
    father_params = father_net.params
    mother_params = mother_net.params
    
    # ==========================================================================
    # DETERMINE FITTER PARENT (NEW in v2.34)
    # ==========================================================================
    father_fitness = father.stats.food_found + father.stats.time_lived_s * 0.1
    mother_fitness = mother.stats.food_found + mother.stats.time_lived_s * 0.1
    father_is_fitter = father_fitness >= mother_fitness
    
    # ==========================================================================
    # HELPER FUNCTIONS
    # ==========================================================================
    
    def pick(father_val, mother_val):
        """50% chance to pick from father or mother."""
        return father_val if random.random() < 0.5 else mother_val
    
    def pick_biased(father_val, mother_val, bias: float = 0.7):
        """Pick from fitter parent with bias probability."""
        if father_is_fitter:
            return father_val if random.random() < bias else mother_val
        else:
            return mother_val if random.random() < bias else father_val
    
    def blend(father_val, mother_val, variation: float = 0.05):
        """Blend two numerical values with small random variation."""
        avg = (father_val + mother_val) / 2.0
        return avg * random.uniform(1.0 - variation, 1.0 + variation)
    
    def blend_int(father_val, mother_val, variation: float = 0.1):
        """Blend two integer values, returning an integer result."""
        result = blend(father_val, mother_val, variation)
        return max(1, int(round(result)))
    
    def blend_bounded(father_val, mother_val, low: float, high: float, variation: float = 0.05):
        """Blend two values and clamp to bounds."""
        result = blend(father_val, mother_val, variation)
        return max(low, min(high, result))
    
    def pick_or_blend(father_val, mother_val, blend_prob: float = 0.7):
        """With blend_prob probability, blend values; otherwise pick one."""
        if random.random() < blend_prob:
            return blend(father_val, mother_val)
        return pick(father_val, mother_val)
    
    def proportional_index(child_idx: int, child_count: int, parent_count: int) -> int:
        """
        Map a child index to a parent index using proportional mapping.
        
        Example: If child has 15 neurons and parent has 10:
        - child[0] -> parent[0]
        - child[7] -> parent[4 or 5]
        - child[14] -> parent[9]
        
        This preserves the relative position in the network.
        """
        if parent_count == 0:
            return 0
        if child_count <= 1:
            return 0
        # Map child position [0, child_count-1] to parent position [0, parent_count-1]
        ratio = child_idx / (child_count - 1) if child_count > 1 else 0
        parent_idx = int(round(ratio * (parent_count - 1)))
        return min(parent_idx, parent_count - 1)
    
    def get_parent_neuron_pair(child_idx: int, child_count: int, 
                                father_neurons: list, mother_neurons: list) -> Tuple[Any, Any]:
        """
        Get the corresponding parent neurons for a child neuron index.
        Uses proportional mapping to handle different sizes.
        
        Returns (father_neuron, mother_neuron) - either can be None if parent list is empty.
        """
        f_neuron = None
        m_neuron = None
        
        if father_neurons:
            f_idx = proportional_index(child_idx, child_count, len(father_neurons))
            f_neuron = father_neurons[f_idx]
        
        if mother_neurons:
            m_idx = proportional_index(child_idx, child_count, len(mother_neurons))
            m_neuron = mother_neurons[m_idx]
        
        return f_neuron, m_neuron
    
    def weighted_random_choice(father_list: list, mother_list: list) -> Any:
        """
        Pick a random element from combined parent lists (50/50 parent selection).
        """
        # First decide which parent to sample from
        use_father = random.random() < 0.5
        
        if use_father and father_list:
            return random.choice(father_list)
        elif mother_list:
            return random.choice(mother_list)
        elif father_list:
            return random.choice(father_list)
        return None
    
    def find_similar_synapse(child_pre_id: int, child_post_id: int,
                             child_neuron_count: int,
                             parent_synapses: list,
                             parent_neuron_count: int) -> Optional[Any]:
        """
        Find a synapse in parent that has similar relative pre/post positions.
        
        This handles the case where child and parent have different neuron counts
        by matching based on relative position rather than absolute IDs.
        """
        if not parent_synapses or parent_neuron_count == 0:
            return None
        
        # Calculate relative positions for child synapse
        child_pre_rel = child_pre_id / max(1, child_neuron_count - 1)
        child_post_rel = child_post_id / max(1, child_neuron_count - 1)
        
        # Find the parent synapse with closest relative positions
        best_synapse = None
        best_distance = float('inf')
        
        for syn in parent_synapses:
            parent_pre_rel = syn.pre_id / max(1, parent_neuron_count - 1)
            parent_post_rel = syn.post_id / max(1, parent_neuron_count - 1)
            
            # Euclidean distance in relative position space
            distance = math.sqrt(
                (child_pre_rel - parent_pre_rel) ** 2 + 
                (child_post_rel - parent_post_rel) ** 2
            )
            
            if distance < best_distance:
                best_distance = distance
                best_synapse = syn
        
        # Only use if reasonably close (threshold: 0.3 in relative space)
        if best_distance < 0.3:
            return best_synapse
        
        # Fallback to random selection
        return random.choice(parent_synapses)
    
    # ==========================================================================
    # LEVEL 1: INHERIT NETWORK PARAMETERS
    # ==========================================================================
    
    child_params = NetworkParameters()
    
    # --- General Network Architecture ---
    child_params.network_name = pick(father_params.network_name, mother_params.network_name)
    child_params.num_input_neurons = pick(father_params.num_input_neurons, mother_params.num_input_neurons)
    child_params.num_hidden_neurons = blend_int(father_params.num_hidden_neurons, mother_params.num_hidden_neurons)
    child_params.num_output_neurons = pick(father_params.num_output_neurons, mother_params.num_output_neurons)
    
    # --- Temporal Dynamics & Simulation ---
    child_params.dt = pick_or_blend(father_params.dt, mother_params.dt)
    child_params.min_dt = pick_or_blend(father_params.min_dt, mother_params.min_dt)
    child_params.max_dt = pick_or_blend(father_params.max_dt, mother_params.max_dt)
    child_params.activity_threshold = blend_bounded(father_params.activity_threshold, mother_params.activity_threshold, 0.1, 0.9)
    child_params.simulation_steps = blend_int(father_params.simulation_steps, mother_params.simulation_steps)
    
    # --- Network Topology ---
    child_params.connection_probability = blend_bounded(father_params.connection_probability, mother_params.connection_probability, 0.05, 0.5)
    child_params.small_world_k = blend_int(father_params.small_world_k, mother_params.small_world_k)
    child_params.small_world_rewire_prob = blend_bounded(father_params.small_world_rewire_prob, mother_params.small_world_rewire_prob, 0.0, 0.5)
    child_params.preferential_attachment = pick(father_params.preferential_attachment, mother_params.preferential_attachment)
    
    # --- Core Neuron Properties ---
    child_params.membrane_time_constant = pick_or_blend(father_params.membrane_time_constant, mother_params.membrane_time_constant)
    child_params.firing_threshold_excitatory = blend_bounded(father_params.firing_threshold_excitatory, mother_params.firing_threshold_excitatory, 0.3, 2.0)
    child_params.firing_threshold_inhibitory = blend_bounded(father_params.firing_threshold_inhibitory, mother_params.firing_threshold_inhibitory, -2.5, -0.3)
    child_params.adaptation_rate = blend_bounded(father_params.adaptation_rate, mother_params.adaptation_rate, 0.0, 0.3)
    child_params.spontaneous_firing_rate = blend_bounded(father_params.spontaneous_firing_rate, mother_params.spontaneous_firing_rate, 0.0, 0.15)
    child_params.neuron_health_decay = blend_bounded(father_params.neuron_health_decay, mother_params.neuron_health_decay, 0.0001, 0.01)
    
    # --- Dendritic Branch Properties ---
    child_params.num_dendritic_branches = blend_int(father_params.num_dendritic_branches, mother_params.num_dendritic_branches)
    child_params.branch_threshold = blend_bounded(father_params.branch_threshold, mother_params.branch_threshold, 0.3, 1.0)
    child_params.plateau_decay = pick_or_blend(father_params.plateau_decay, mother_params.plateau_decay)
    
    # --- Synaptic Properties & Plasticity ---
    child_params.tau_fast = pick_or_blend(father_params.tau_fast, mother_params.tau_fast)
    child_params.tau_slow = pick_or_blend(father_params.tau_slow, mother_params.tau_slow)
    child_params.tau_meta = pick_or_blend(father_params.tau_meta, mother_params.tau_meta)
    child_params.tau_ltp = pick_or_blend(father_params.tau_ltp, mother_params.tau_ltp)
    child_params.tau_ltd = pick_or_blend(father_params.tau_ltd, mother_params.tau_ltd)
    
    # --- Synaptic Weight Initialization Ranges ---
    child_params.w_fast_init_min = pick_or_blend(father_params.w_fast_init_min, mother_params.w_fast_init_min)
    child_params.w_fast_init_max = pick_or_blend(father_params.w_fast_init_max, mother_params.w_fast_init_max)
    child_params.w_slow_init_min = pick_or_blend(father_params.w_slow_init_min, mother_params.w_slow_init_min)
    child_params.w_slow_init_max = pick_or_blend(father_params.w_slow_init_max, mother_params.w_slow_init_max)
    child_params.w_meta_init_min = pick_or_blend(father_params.w_meta_init_min, mother_params.w_meta_init_min)
    child_params.w_meta_init_max = pick_or_blend(father_params.w_meta_init_max, mother_params.w_meta_init_max)
    
    # --- Learning and Plasticity Rules ---
    child_params.learning_rate = blend_bounded(father_params.learning_rate, mother_params.learning_rate, 0.001, 0.1)
    child_params.stdp_window = pick_or_blend(father_params.stdp_window, mother_params.stdp_window)
    child_params.learning_rate_mod = pick_or_blend(father_params.learning_rate_mod, mother_params.learning_rate_mod)
    child_params.plasticity_threshold = blend_bounded(father_params.plasticity_threshold, mother_params.plasticity_threshold, 0.2, 0.9)
    child_params.associativity_strength = blend_bounded(father_params.associativity_strength, mother_params.associativity_strength, 0.01, 0.3)
    
    # --- Structural Plasticity ---
    child_params.synapse_integrity_threshold = blend_bounded(father_params.synapse_integrity_threshold, mother_params.synapse_integrity_threshold, 0.02, 0.3)
    child_params.synapse_formation_prob = blend_bounded(father_params.synapse_formation_prob, mother_params.synapse_formation_prob, 0.005, 0.1)
    child_params.synapse_death_prob = blend_bounded(father_params.synapse_death_prob, mother_params.synapse_death_prob, 0.005, 0.05)
    child_params.neuron_death_threshold = blend_bounded(father_params.neuron_death_threshold, mother_params.neuron_death_threshold, 0.02, 0.3)
    
    # --- Neuromodulation ---
    child_params.dopamine_baseline = blend_bounded(father_params.dopamine_baseline, mother_params.dopamine_baseline, 0.05, 0.4)
    child_params.dopamine_high_affinity_threshold = pick_or_blend(father_params.dopamine_high_affinity_threshold, mother_params.dopamine_high_affinity_threshold)
    child_params.dopamine_low_affinity_threshold = pick_or_blend(father_params.dopamine_low_affinity_threshold, mother_params.dopamine_low_affinity_threshold)
    child_params.serotonin_baseline = blend_bounded(father_params.serotonin_baseline, mother_params.serotonin_baseline, 0.05, 0.4)
    child_params.serotonin_high_affinity_threshold = pick_or_blend(father_params.serotonin_high_affinity_threshold, mother_params.serotonin_high_affinity_threshold)
    child_params.serotonin_low_affinity_threshold = pick_or_blend(father_params.serotonin_low_affinity_threshold, mother_params.serotonin_low_affinity_threshold)
    child_params.acetylcholine_baseline = blend_bounded(father_params.acetylcholine_baseline, mother_params.acetylcholine_baseline, 0.05, 0.4)
    child_params.acetylcholine_high_affinity_threshold = pick_or_blend(father_params.acetylcholine_high_affinity_threshold, mother_params.acetylcholine_high_affinity_threshold)
    child_params.acetylcholine_low_affinity_threshold = pick_or_blend(father_params.acetylcholine_low_affinity_threshold, mother_params.acetylcholine_low_affinity_threshold)
    child_params.norepinephrine_baseline = blend_bounded(father_params.norepinephrine_baseline, mother_params.norepinephrine_baseline, 0.05, 0.4)
    child_params.norepinephrine_high_affinity_threshold = pick_or_blend(father_params.norepinephrine_high_affinity_threshold, mother_params.norepinephrine_high_affinity_threshold)
    child_params.norepinephrine_low_affinity_threshold = pick_or_blend(father_params.norepinephrine_low_affinity_threshold, mother_params.norepinephrine_low_affinity_threshold)
    child_params.neuromod_decay_rate = blend_bounded(father_params.neuromod_decay_rate, mother_params.neuromod_decay_rate, 0.001, 0.2)
    child_params.diffusion_rate = blend_bounded(father_params.diffusion_rate, mother_params.diffusion_rate, 0.005, 0.1)
    
    # --- Oscillators & Synchronization ---
    child_params.oscillator_low_freq = pick_or_blend(father_params.oscillator_low_freq, mother_params.oscillator_low_freq)
    child_params.oscillator_mid_freq = pick_or_blend(father_params.oscillator_mid_freq, mother_params.oscillator_mid_freq)
    child_params.oscillator_high_freq = pick_or_blend(father_params.oscillator_high_freq, mother_params.oscillator_high_freq)
    child_params.oscillator_strength = blend_bounded(father_params.oscillator_strength, mother_params.oscillator_strength, 0.05, 0.4)
    
    # --- Energy Metabolism ---
    child_params.energy_baseline = pick_or_blend(father_params.energy_baseline, mother_params.energy_baseline)
    child_params.firing_energy_cost = pick_or_blend(father_params.firing_energy_cost, mother_params.firing_energy_cost)
    child_params.plasticity_energy_cost = pick_or_blend(father_params.plasticity_energy_cost, mother_params.plasticity_energy_cost)
    child_params.metabolic_rate = blend_bounded(father_params.metabolic_rate, mother_params.metabolic_rate, 0.4, 1.8)
    child_params.recovery_rate = pick_or_blend(father_params.recovery_rate, mother_params.recovery_rate)
    
    # --- Homeostasis ---
    child_params.target_firing_rate = blend_bounded(father_params.target_firing_rate, mother_params.target_firing_rate, 0.02, 0.3)
    child_params.homeostatic_plasticity_rate = blend_bounded(father_params.homeostatic_plasticity_rate, mother_params.homeostatic_plasticity_rate, 0.0001, 0.005)
    
    # --- Aigarth Hybridization ---
    child_params.itu_circle_radius = blend_int(father_params.itu_circle_radius, mother_params.itu_circle_radius)
    child_params.evolution_interval = blend_int(father_params.evolution_interval, mother_params.evolution_interval)
    child_params.fitness_temporal_weight = blend_bounded(father_params.fitness_temporal_weight, mother_params.fitness_temporal_weight, 0.1, 0.6)
    child_params.fitness_energy_weight = blend_bounded(father_params.fitness_energy_weight, mother_params.fitness_energy_weight, 0.1, 0.5)
    child_params.fitness_pattern_weight = blend_bounded(father_params.fitness_pattern_weight, mother_params.fitness_pattern_weight, 0.1, 0.5)
    
    # --- Miscellaneous ---
    child_params.phase_coupling_strength = blend_bounded(father_params.phase_coupling_strength, mother_params.phase_coupling_strength, 0.05, 0.3)
    child_params.max_axonal_delay = pick_or_blend(father_params.max_axonal_delay, mother_params.max_axonal_delay)
    
    # ==========================================================================
    # LEVEL 2: CREATE BASE CHILD NETWORK
    # ==========================================================================
    
    child_net = NeuraxonNetwork(child_params)
    
    # Get counts for proportional mapping
    child_total_neurons = len(child_net.all_neurons)
    father_total_neurons = len(father_net.all_neurons)
    mother_total_neurons = len(mother_net.all_neurons)
    
    # ==========================================================================
    # LEVEL 3: INHERIT NEURON-LEVEL PARAMETERS (with proportional mapping)
    # ==========================================================================
    
    def inherit_neuron_properties(child_neuron, f_neuron, m_neuron):
        """
        Inherit individual neuron properties from parent neurons.
        Handles None parents gracefully.
        """
        # If both parents are None, keep defaults
        if f_neuron is None and m_neuron is None:
            return
        
        # If only one parent available, use that one with variation
        if f_neuron is None:
            f_neuron = m_neuron
        if m_neuron is None:
            m_neuron = f_neuron
        
        # --- Individualized Membrane Properties ---
        child_neuron.membrane_time_constant = pick_or_blend(f_neuron.membrane_time_constant, m_neuron.membrane_time_constant)
        child_neuron.firing_threshold_excitatory = pick_or_blend(f_neuron.firing_threshold_excitatory, m_neuron.firing_threshold_excitatory)
        child_neuron.firing_threshold_inhibitory = pick_or_blend(f_neuron.firing_threshold_inhibitory, m_neuron.firing_threshold_inhibitory)
        child_neuron.adaptation_rate = pick_or_blend(f_neuron.adaptation_rate, m_neuron.adaptation_rate)
        child_neuron.spontaneous_firing_rate = pick_or_blend(f_neuron.spontaneous_firing_rate, m_neuron.spontaneous_firing_rate)
        child_neuron.neuron_health_decay = pick_or_blend(f_neuron.neuron_health_decay, m_neuron.neuron_health_decay)
        
        # --- Individualized Energy Metabolism ---
        child_neuron.energy_baseline = pick_or_blend(f_neuron.energy_baseline, m_neuron.energy_baseline)
        child_neuron.firing_energy_cost = pick_or_blend(f_neuron.firing_energy_cost, m_neuron.firing_energy_cost)
        child_neuron.plasticity_energy_cost = pick_or_blend(f_neuron.plasticity_energy_cost, m_neuron.plasticity_energy_cost)
        child_neuron.metabolic_rate = pick_or_blend(f_neuron.metabolic_rate, m_neuron.metabolic_rate)
        child_neuron.recovery_rate = pick_or_blend(f_neuron.recovery_rate, m_neuron.recovery_rate)
        
        # --- Phase and Frequency Properties ---
        child_neuron.natural_frequency = pick_or_blend(f_neuron.natural_frequency, m_neuron.natural_frequency)
        child_neuron.intrinsic_timescale = pick_or_blend(f_neuron.intrinsic_timescale, m_neuron.intrinsic_timescale)
        child_neuron.fitness_score = blend(f_neuron.fitness_score, m_neuron.fitness_score, variation=0.2)
        
        # --- Inherit Dendritic Branch Properties ---
        inherit_dendritic_branches(child_neuron, f_neuron, m_neuron)
    
    def inherit_dendritic_branches(child_neuron, f_neuron, m_neuron):
        """
        Inherit dendritic branch properties using proportional mapping.
        Handles different numbers of branches between parents.
        """
        f_branches = f_neuron.dendritic_branches if f_neuron else []
        m_branches = m_neuron.dendritic_branches if m_neuron else []
        
        if not f_branches and not m_branches:
            return
        
        child_branch_count = len(child_neuron.dendritic_branches)
        f_branch_count = len(f_branches)
        m_branch_count = len(m_branches)
        
        for i, branch in enumerate(child_neuron.dendritic_branches):
            # Use proportional mapping for branches too
            f_b = None
            m_b = None
            
            if f_branches:
                f_idx = proportional_index(i, child_branch_count, f_branch_count)
                f_b = f_branches[f_idx]
            
            if m_branches:
                m_idx = proportional_index(i, child_branch_count, m_branch_count)
                m_b = m_branches[m_idx]
            
            # Handle None cases
            if f_b is None and m_b is None:
                continue
            if f_b is None:
                f_b = m_b
            if m_b is None:
                m_b = f_b
            
            branch.branch_threshold = pick_or_blend(f_b.branch_threshold, m_b.branch_threshold)
            branch.plateau_decay = pick_or_blend(f_b.plateau_decay, m_b.plateau_decay)
    
    # Apply neuron inheritance using proportional mapping
    # Input neurons
    for i, neuron in enumerate(child_net.input_neurons):
        f_n, m_n = get_parent_neuron_pair(
            i, len(child_net.input_neurons),
            father_net.input_neurons, mother_net.input_neurons
        )
        inherit_neuron_properties(neuron, f_n, m_n)
    
    # Hidden neurons (most likely to have different counts)
    for i, neuron in enumerate(child_net.hidden_neurons):
        f_n, m_n = get_parent_neuron_pair(
            i, len(child_net.hidden_neurons),
            father_net.hidden_neurons, mother_net.hidden_neurons
        )
        inherit_neuron_properties(neuron, f_n, m_n)
    
    # Output neurons
    for i, neuron in enumerate(child_net.output_neurons):
        f_n, m_n = get_parent_neuron_pair(
            i, len(child_net.output_neurons),
            father_net.output_neurons, mother_net.output_neurons
        )
        inherit_neuron_properties(neuron, f_n, m_n)
    
    # ==========================================================================
    # LEVEL 4: INHERIT SYNAPSE-LEVEL PARAMETERS (with relative position matching)
    # ==========================================================================
    
    f_synapses = list(father_net.synapses) if father_net.synapses else []
    m_synapses = list(mother_net.synapses) if mother_net.synapses else []
    
    def inherit_synapse_properties(child_synapse):
        """
        Inherit synapse properties using relative position matching.
        This handles different-sized networks by finding synapses with
        similar relative pre/post positions.
        """
        # Try to find similar synapses in each parent
        f_s = find_similar_synapse(
            child_synapse.pre_id, child_synapse.post_id,
            child_total_neurons, f_synapses, father_total_neurons
        )
        m_s = find_similar_synapse(
            child_synapse.pre_id, child_synapse.post_id,
            child_total_neurons, m_synapses, mother_total_neurons
        )
        
        # Handle None cases
        if f_s is None and m_s is None:
            return  # Keep default initialization
        if f_s is None:
            f_s = m_s
        if m_s is None:
            m_s = f_s
        
        # --- Inherit Synaptic Weights (BIASED toward fitter parent v2.34) ---
        child_synapse.w_fast = pick_biased(f_s.w_fast, m_s.w_fast, 0.7)
        child_synapse.w_slow = pick_biased(f_s.w_slow, m_s.w_slow, 0.7)
        child_synapse.w_meta = pick_biased(f_s.w_meta, m_s.w_meta, 0.7)
        
        # --- Inherit Individualized Time Constants ---
        child_synapse.tau_fast = pick_or_blend(f_s.tau_fast, m_s.tau_fast)
        child_synapse.tau_slow = pick_or_blend(f_s.tau_slow, m_s.tau_slow)
        child_synapse.tau_meta = pick_or_blend(f_s.tau_meta, m_s.tau_meta)
        child_synapse.tau_ltp = pick_or_blend(f_s.tau_ltp, m_s.tau_ltp)
        child_synapse.tau_ltd = pick_or_blend(f_s.tau_ltd, m_s.tau_ltd)
        
        # --- Inherit Learning Parameters ---
        child_synapse.learning_rate = pick_or_blend(f_s.learning_rate, m_s.learning_rate)
        child_synapse.plasticity_threshold = pick_or_blend(f_s.plasticity_threshold, m_s.plasticity_threshold)
        
        # --- Inherit Synapse Type Properties ---
        child_synapse.is_silent = pick(f_s.is_silent, m_s.is_silent)
        child_synapse.is_modulatory = pick(f_s.is_modulatory, m_s.is_modulatory)
        child_synapse.axonal_delay = pick_or_blend(f_s.axonal_delay, m_s.axonal_delay)
        child_synapse.integrity = blend_bounded(f_s.integrity, m_s.integrity, 0.0, 1.0, variation=0.02)
        
        # Update synapse type based on inherited properties
        child_synapse.synapse_type = child_synapse._determine_type()
    
    # Apply synapse inheritance
    for synapse in child_net.synapses:
        inherit_synapse_properties(synapse)
    
    # ==========================================================================
    # LEVEL 5: INHERIT NEUROMODULATOR STATES
    # ==========================================================================
    
    for mod in ['dopamine', 'serotonin', 'acetylcholine', 'norepinephrine']:
        f_level = father_net.neuromodulators.get(mod, 0.12)
        m_level = mother_net.neuromodulators.get(mod, 0.12)
        baseline = getattr(child_params, f'{mod}_baseline')
        inherited = blend(f_level, m_level, variation=0.1)
        child_net.neuromodulators[mod] = inherited * 0.7 + baseline * 0.3
    
    # Inherit modulator grid (with handling for different sizes)
    try:
        f_grid = np.array(father_net.modulator_grid)
        m_grid = np.array(mother_net.modulator_grid)
        child_shape = child_net.modulator_grid.shape
        
        if f_grid.shape == m_grid.shape == child_shape:
            # Same size - direct blend
            avg = (f_grid + m_grid) / 2.0
            noise = np.random.uniform(0.9, 1.1, avg.shape)
            child_net.modulator_grid = avg * noise
        else:
            # Different sizes - interpolate to child size
            from scipy.ndimage import zoom as scipy_zoom
            
            def resize_grid(grid, target_shape):
                if grid.shape == target_shape:
                    return grid
                zoom_factors = [t / s for t, s in zip(target_shape, grid.shape)]
                return scipy_zoom(grid, zoom_factors, order=1)
            
            try:
                f_resized = resize_grid(f_grid, child_shape)
                m_resized = resize_grid(m_grid, child_shape)
                avg = (f_resized + m_resized) / 2.0
                noise = np.random.uniform(0.9, 1.1, avg.shape)
                child_net.modulator_grid = avg * noise
            except ImportError:
                # scipy not available - use simple average and add noise
                child_net.modulator_grid = child_net.modulator_grid * random.uniform(0.9, 1.1)
    except Exception:
        pass  # Keep default grid on any error
    
    # ==========================================================================
    # LEVEL 6: INHERIT OSCILLATOR CONFIGURATIONS
    # ==========================================================================
    
    f_phases = father_net.oscillator_phase_offsets
    m_phases = mother_net.oscillator_phase_offsets
    
    child_phases = []
    for i in range(3):
        f_p = f_phases[i] if i < len(f_phases) else random.random() * 2 * math.pi
        m_p = m_phases[i] if i < len(m_phases) else random.random() * 2 * math.pi
        
        if random.random() < 0.5:
            child_phases.append(pick(f_p, m_p))
        else:
            # Circular average for phases
            avg_phase = math.atan2(
                (math.sin(f_p) + math.sin(m_p)) / 2,
                (math.cos(f_p) + math.cos(m_p)) / 2
            )
            child_phases.append((avg_phase + random.uniform(-0.2, 0.2)) % (2 * math.pi))
    
    child_net.oscillator_phase_offsets = tuple(child_phases)
    
    # ==========================================================================
    # LEVEL 7: INHERIT ITU CIRCLE PARAMETERS (with different counts)
    # ==========================================================================
    
    f_circles = father_net.itu_circles if father_net.itu_circles else []
    m_circles = mother_net.itu_circles if mother_net.itu_circles else []
    
    if child_net.itu_circles and (f_circles or m_circles):
        child_circle_count = len(child_net.itu_circles)
        f_circle_count = len(f_circles)
        m_circle_count = len(m_circles)
        
        for i, circle in enumerate(child_net.itu_circles):
            # Use proportional mapping for ITU circles
            f_c = None
            m_c = None
            
            if f_circles:
                f_idx = proportional_index(i, child_circle_count, f_circle_count)
                f_c = f_circles[f_idx]
            
            if m_circles:
                m_idx = proportional_index(i, child_circle_count, m_circle_count)
                m_c = m_circles[m_idx]
            
            # Handle None cases
            if f_c is None and m_c is None:
                continue
            if f_c is None:
                f_c = m_c
            if m_c is None:
                m_c = f_c
            
            # Inherit mutation rate
            circle.mutation_rate = blend_bounded(f_c.mutation_rate, m_c.mutation_rate, 0.001, 0.1)
            
            # Initialize fitness history with inherited baseline
            f_fitness = f_c.fitness_history[-1] if f_c.fitness_history else 0.5
            m_fitness = m_c.fitness_history[-1] if m_c.fitness_history else 0.5
            avg_fitness = (f_fitness + m_fitness) / 2
            circle.fitness_history = [avg_fitness * random.uniform(0.9, 1.1)]
    
    # ==========================================================================
    # LEVEL 8: INHERIT ADDITIONAL NETWORK STATE
    # ==========================================================================
    
    # Inherit branching ratio tendency
    child_net.branching_ratio = blend(
        father_net.branching_ratio,
        mother_net.branching_ratio,
        variation=0.15
    )
    
    # Reset time-based counters for new child
    child_net.time = 0.0
    child_net.step_count = 0
    child_net.total_energy_consumed = 0.0
    
    return child_net


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
    # v2.37b: ASYMMETRIC thresholds - inhibitory is MUCH easier to reach
    # BIOINSPIRED: GABAergic interneurons have lower activation thresholds
    firing_threshold_excitatory: float = 0.60  # Slightly lower than v2.36
    firing_threshold_inhibitory: float = -0.25  # v2.37b: DRAMATICALLY lowered from -0.70
    adaptation_rate: float = 0.08  # v2.36: Raised from 0.02 - stronger spike-frequency adaptation
    # v2.38: REDUCED spontaneous rate for biologically plausible ratio
    # BIOINSPIRED: Cortical neurons have ~1-5Hz baseline (0.001-0.005 probability per ms)
    # Target: ~15-25% spontaneous, ~75-85% driven during active behavior
    spontaneous_firing_rate: float = 0.004  # v2.38: Reduced from 0.012 for bio-plausible ratios
    neuron_health_decay: float = 0.001 
    
    # --- Membrane Potential Dynamics (NEW v2.36) ---
    resting_potential_decay: float = 0.06  # v2.37b: HALVED - allow negative states to persist longer
    
    # --- Negative Bias for E/I Balance (NEW v2.37c) ---
    membrane_negative_bias: float = -0.25  # was -0.15, need 1.5x more
    
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
    
    # --- Miscellaneous ---
    phase_coupling_strength: float = 0.1 
    max_axonal_delay: float = 10.0
    
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

# Defines the core types within the model, aligning with the paper's terminology.
class NeuronType(Enum): INPUT = "input"; HIDDEN = "hidden"; OUTPUT = "output"
class SynapseType(Enum): IONOTROPIC_FAST = "ionotropic_fast"; IONOTROPIC_SLOW = "ionotropic_slow"; METABOTROPIC = "metabotropic"; SILENT = "silent"
class TrinaryState(Enum): INHIBITORY = -1; NEUTRAL = 0; EXCITATORY = 1

def _variate(val: float, variance: float = 0.2) -> float:
    """Helper to apply biological heterogeneity to parameters."""
    return val * random.uniform(1.0 - variance, 1.0 + variance)

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
        
        if pre_state == 1 and post_state == 1:
            # LTP now only occurs during Dopamine Surges (Reward)
            delta = self.learning_rate * self.learning_rate_mod * da_high * self.pre_trace
            self._pending_delta_w = delta
            # FIX v2.2505: Log LTP event when delta is significant
            if delta > 0.0001 and logger.log_level >= 2:
                logger.log_plasticity_event(tick=0, event_type='LTP', 
                                            pre_id=self.pre_id, post_id=self.post_id,
                                            delta_w=delta)
            return delta
        elif pre_state == 1 and post_state <= 0:
            # FIX v2.2505: LTD occurs when pre fires but post does NOT respond (neutral or inhibitory)
            # Previously required post_state == -1 (inhibitory only ~0.2%), now includes neutral (~95%)
            # Scale LTD strength: full strength for inhibitory, reduced for neutral
            # ACh Modulation: If high ACh and no reward (LTP), favors easier forgetting (Paper Claim)
            ach_forgetting_mult = 1.5 if ach > 0.6 else 1.0
            
            ltd_scale = (1.0 if post_state == -1 else 0.3) * ach_forgetting_mult
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
        #self.membrane_potential = 0.0
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
        self.phase = random.random() * 2 * math.pi
        self.natural_frequency = random.uniform(0.5, 2.0)
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
    
    def _update_phase_oscillator(self, dt: float, global_osc: float):
        self.phase += 2 * math.pi * self.natural_frequency * dt + self.params.phase_coupling_strength * math.sin(global_osc - self.phase) * dt
        self.phase %= 2 * math.pi
    
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
    
    def update(self, synaptic_inputs: List[float], modulatory_inputs: List[float], external_input: float, neuromodulators: Dict[str, float], dt: float, global_osc: float):
        if not self.is_active or self.energy_level <= 0: return

        phase_coupling_strength = self.params.phase_coupling_strength
        
        self._update_intrinsic_timescale(dt)
        
        # CRITICAL FIX: Cap intrinsic timescale AFTER update, not before
        # This ensures the cap is always enforced regardless of ACW calculation
        self.intrinsic_timescale = min(self.intrinsic_timescale, self.params.max_intrinsic_timescale)
        
        self.phase += dt * self.natural_frequency * 2 * math.pi + phase_coupling_strength * math.sin(global_osc - self.phase)
        
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
                # Inject current (allows competition)
                # 90% inhibitory instead of 70%
                spontaneous = random.choice([-1.0]*9 + [1.0]) * self.params.spontaneous_current_magnitude
            else:
                # Legacy: force threshold
                if random.random() < 0.5:
                    self.membrane_potential = self.firing_threshold_excitatory + 0.01
                else:
                    spontaneous = random.choice([-1.0, 1.0]) * 2.0
                
        threshold_mod = (acetylcholine - 0.5) * 0.5 + sum(modulatory_inputs) * 0.3
        gain = 1.0 + (norepi - 0.5) * 0.4
        
        # v2.37b: Add global negative bias to promote inhibitory states
        negative_bias = getattr(self.params, 'membrane_negative_bias', -0.03)
        
        drive = (total_synaptic + external_input + spontaneous + negative_bias * 5.0) * gain
        
        tau_eff = max(1.0, self.intrinsic_timescale)
        prev_state = self.trinary_state
        
        # v2.37b: MODIFIED - Asymmetric membrane decay
        # Decay POSITIVE potentials faster than negative ones
        # This helps maintain E/I balance by allowing inhibitory states to persist
        if hasattr(self.params, 'resting_potential_decay'):
            resting_decay = self.params.resting_potential_decay * dt
            if self.membrane_potential > 0:
                # Positive potentials decay normally toward zero
                self.membrane_potential *= (1.0 - resting_decay)
            else:
                # Negative potentials decay MORE SLOWLY (half rate)
                # BIOINSPIRED: Inhibitory postsynaptic potentials often have longer time constants
                self.membrane_potential *= (1.0 - resting_decay * 0.5)
        
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
        # v2.37b: Inhibitory threshold has REDUCED autoreceptor effect (easier to fire inhibitory)
        theta_inh = self.firing_threshold_inhibitory - threshold_mod - autoreceptor_effect * 0.3 - threshold_energy_mod * 0.3
        
        # v2.37b: ASYMMETRIC hysteresis - easier to enter/stay in inhibitory
        # Excitatory has MORE hysteresis (harder to reach/stay)
        # Inhibitory has LESS hysteresis (easier to reach/stay)
        hysteresis_exc = 0.04 if self.trinary_state == 0 else 0.0
        hysteresis_inh = 0.01 if self.trinary_state == 0 else 0.0
        
        if self.membrane_potential > (theta_exc + hysteresis_exc): 
            self.trinary_state = TrinaryState.EXCITATORY.value
        elif self.membrane_potential < (theta_inh - hysteresis_inh): 
            self.trinary_state = TrinaryState.INHIBITORY.value
        else: 
            self.trinary_state = TrinaryState.NEUTRAL.value
        
        self.state_history.append(self.trinary_state)
        self._update_autocorrelation()
        activity_level = abs(self.trinary_state)
        
        # === SPIKE CLASSIFICATION AND LOGGING ===
        # Determine if spike was driven (by input) or spontaneous
        # BIOINSPIRED: Biological neurons show ~70-90% driven, ~10-30% spontaneous activity
        # Paper Section 6: Spontaneous activity provides substrate for plasticity but 
        # most spikes during active behavior are stimulus-driven
        logger = get_data_logger()
        if abs(self.trinary_state) > 0 and self.params.spike_classification_enabled:
            # Calculate relative contributions
            input_contribution = abs(total_synaptic) + abs(external_input)
            spont_contribution = abs(spontaneous)
            
            # FIXED v2.38: Improved spike classification for biological plausibility
            # A spike is "driven" if:
            # 1. Input contribution is above noise floor (driven_input_threshold), OR
            # 2. No spontaneous event triggered this spike
            # A spike is "spontaneous" only if spontaneous event occurred AND dominates
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
            # If we're in neutral state but close to threshold
            if self.trinary_state == 0:
                distance_to_exc = theta_exc - self.membrane_potential
                distance_to_inh = self.membrane_potential - theta_inh
                
                # Log if within 30% of either threshold
                if distance_to_exc < abs(theta_exc) * 0.3:
                    logger.log_subthreshold_event(
                        0, self.id, self.membrane_potential, 
                        theta_exc, distance_to_exc
                    )
                elif distance_to_inh < abs(theta_inh) * 0.3:
                    logger.log_subthreshold_event(
                        0, self.id, self.membrane_potential,
                        theta_inh, distance_to_inh
                    )
        
        # NEW: Log significant autoreceptor effects Updated Save states in v 2.1
        if abs(self.autoreceptor) > 0.1:
            logger = get_data_logger()
            if logger.log_level >= 2:
                threshold_effect = -0.1 * self.autoreceptor
                logger.log_autoreceptor_event(0, self.id, self.autoreceptor, threshold_effect)
        
        # NEW: Log threshold modulation events (when crossing state boundaries) Updated Save states in v 2.1
        if prev_state != self.trinary_state:
            logger = get_data_logger()
            if logger.log_level >= 2:
                ach_contrib = (neuromodulators.get('acetylcholine', 0.5) - 0.5) * 0.5
                autoreceptor_contrib = -0.1 * self.autoreceptor
                logger.log_threshold_modulation_event(
                    0, self.id, self.firing_threshold_excitatory,
                    theta_exc, ach_contrib, autoreceptor_contrib
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


class ITUCircle:
    """
    Implements an Intelligent Tissue Unit (ITU) circle, a concept from the Aigarth hybridization (Section 8 of the Neuraxon paper).
    This class manages a group of neurons that are subject to evolutionary pressures. It calculates
    a collective fitness score and applies mutation and selection (pruning) to its member neurons.
    """
    def __init__(self, circle_id: int, neurons: List[Neuraxon], params: NetworkParameters):
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
        
        # Initialize random phase offsets for the three global oscillators.
        self.oscillator_phase_offsets = (random.random() * 2 * math.pi, random.random() * 2 * math.pi, random.random() * 2 * math.pi)
        self.activation_history = deque(maxlen=1000)
        self.branching_ratio = 1.0 # A measure of network criticality. A value near 1.0 is often optimal.
        
        # NEW v2.2503: Track excitatory fraction history for adaptive threshold homeostasis
        self.excitatory_fraction_history = deque(maxlen=200)
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
            
            self.neuromodulators[mod] += (base - self.neuromodulators[mod]) * self.params.neuromod_decay_rate * decay_factor * dt / 100.0
    
    def _apply_homeostatic_plasticity(self):
        """A slow-acting plasticity rule that adjusts neuron excitability."""
        if self.step_count % 100 != 0: return 
        
        # NEW v2.2503: Apply network-wide adaptive threshold homeostasis
        self._apply_adaptive_threshold_homeostasis()
        
        
        logger = get_data_logger()
        
        for neuron in self.all_neurons:
            if neuron.type == NeuronType.HIDDEN and len(neuron.state_history) > 0:
                recent_activity = sum(abs(s) for s in neuron.state_history) / len(neuron.state_history)
                old_threshold = neuron.params.firing_threshold_excitatory
                
                if recent_activity > self.params.target_firing_rate * 1.2:
                    neuron.params.firing_threshold_excitatory += self.params.homeostatic_plasticity_rate
                elif recent_activity < self.params.target_firing_rate * 0.8:
                    neuron.params.firing_threshold_excitatory -= self.params.homeostatic_plasticity_rate
                
                # NEW: Log if threshold changed
                new_threshold = neuron.params.firing_threshold_excitatory
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
        
        # === PRIMARY TARGET: Branching Ratio (Criticality) ===
        sigma = self.branching_ratio
        
        # v2.36: Also check excitatory fraction to ensure neutral dominance
        excitatory_count = sum(1 for n in active_neurons if n.trinary_state == 1)
        excitatory_fraction = excitatory_count / len(active_neurons)
        
        # v2.37b: Track inhibitory for E/I balance homeostasis
        inhibitory_count = sum(1 for n in active_neurons if n.trinary_state == -1)
        inhibitory_fraction = inhibitory_count / len(active_neurons)
        
        # Critical regime for branching ratio: σ ∈ [0.85, 1.15]
        sigma_ok = 0.85 <= sigma <= 1.15
        
        # v2.36: NEW - Also target appropriate excitatory fraction for neutral dominance
        target_exc = getattr(self.params, 'target_excitatory_fraction', 0.22)
        exc_ok = abs(excitatory_fraction - target_exc) < 0.08
        
        # Only skip adjustment if BOTH criticality AND excitatory fraction are good
        # v2.37b: Also check inhibitory fraction
        min_inh = getattr(self.params, 'min_inhibitory_fraction', 0.10)
        inh_ok = inhibitory_fraction >= min_inh
        
        if sigma_ok and exc_ok and inh_ok:
            return
        
        # v2.37b: PRIORITY 1 - Fix inhibitory deficit (most critical for E/I balance)
        if not inh_ok and inhibitory_fraction < min_inh:
            # Need more inhibitory - lower inhibitory threshold for ALL neurons
            deficit = min_inh - inhibitory_fraction
            adjustment_strength = min(0.05, deficit * 0.5)  # Proportional to deficit
            
            for neuron in active_neurons:
                # Move inhibitory threshold toward zero (make it easier to reach)
                new_inh = neuron.firing_threshold_inhibitory + adjustment_strength
                neuron.firing_threshold_inhibitory = max(-0.50, min(-0.10, new_inh))
            
            # Log the adjustment
            logger = get_data_logger()
            if logger.log_level >= 2:
                logger.log_homeostatic_event(
                    tick=self.step_count,
                    neuron_id=-2,  # -2 = inhibitory homeostasis
                    old_value=inhibitory_fraction,
                    new_value=min_inh,
                    activity=excitatory_fraction
                )
            return  # Don't compound adjustments
        
        # v2.37b: PRIORITY 2 - Excitatory fraction correction
        # This ensures neutral state dominance even at criticality
        adjustment = 0.0
        reason = None
        
        if sigma_ok and not exc_ok:
            # Sigma is good but excitatory fraction needs correction
            if excitatory_fraction > self.params.max_excitatory_fraction:
                # Too much excitatory - raise thresholds even though sigma is OK
                adjustment = self.params.adaptive_threshold_adjustment * 1.5
                reason = f"excess_excitatory_{excitatory_fraction:.3f}_target_{target_exc:.3f}"
            elif excitatory_fraction < self.params.min_excitatory_fraction:
                # Too little excitatory - lower thresholds
                adjustment = -self.params.adaptive_threshold_adjustment
                reason = f"deficit_excitatory_{excitatory_fraction:.3f}_target_{target_exc:.3f}"
            else:
                return
        else:
            # Original criticality-based adjustment continues below...
            # Proportional control: adjustment scales with distance from criticality
            # This mimics biological homeostasis where larger deviations cause stronger responses
            sigma_error = 1.0 - sigma
            
            # Base adjustment magnitude, scaled by error (max 2x base)
            base_adjustment = self.params.adaptive_threshold_adjustment
            proportional_gain = min(2.0, 1.0 + abs(sigma_error))
            adjustment_magnitude = base_adjustment * proportional_gain
            
            # === ALSO CHECK: Excitatory Fraction as Secondary Signal ===
            self.excitatory_fraction_history.append(excitatory_fraction)
            
            # Determine adjustment direction based on sigma
            if sigma < 0.85:  # Subcritical - network too quiet
                # Lower thresholds to increase excitability (biological: upregulate Na+ channels)
                adjustment = -adjustment_magnitude
                reason = f"subcritical_sigma_{sigma:.3f}_exc_{excitatory_fraction:.3f}"
                
                # Secondary boost: increase oscillator drive if very subcritical
                if sigma < 0.7:
                    self.params.oscillator_strength = min(0.40, 
                        self.params.oscillator_strength + 0.005)
            
            elif sigma > 1.15:  # Supercritical - network too active
                # Raise thresholds to decrease excitability (biological: upregulate K+ channels)
                adjustment = adjustment_magnitude
                reason = f"supercritical_sigma_{sigma:.3f}_exc_{excitatory_fraction:.3f}"
                
                # Secondary damping: reduce oscillator drive if very supercritical
                if sigma > 1.3:
                    self.params.oscillator_strength = max(0.10,
                        self.params.oscillator_strength - 0.005)
        
        # === APPLY GLOBAL THRESHOLD ADJUSTMENT ===
        if adjustment != 0.0:
            neurons_adjusted = 0
            for neuron in active_neurons:
                # Excitatory threshold: biological range [0.25, 1.2]
                new_exc_threshold = neuron.firing_threshold_excitatory + adjustment
                neuron.firing_threshold_excitatory = max(0.25, min(1.2, new_exc_threshold))
                
                # Inhibitory threshold: adjust symmetrically, range [-1.2, -0.25]
                new_inh_threshold = neuron.firing_threshold_inhibitory - adjustment
                neuron.firing_threshold_inhibitory = max(-1.2, min(-0.25, new_inh_threshold))
                
                neurons_adjusted += 1
            
            # === LOG THE HOMEOSTATIC EVENT ===
            logger = get_data_logger()
            if logger.log_level >= 2:
                logger.log_homeostatic_event(
                    tick=self.step_count,
                    neuron_id=-1,  # -1 indicates network-wide adjustment
                    old_value=sigma,  # Using sigma as reference
                    new_value=sigma + adjustment,  # Direction indicator
                    activity=excitatory_fraction
                )
                
                # Additional detail logging for analysis
                if hasattr(logger, 'time_series') and 'adaptive_threshold_adjustments' not in logger.time_series:
                    logger.time_series['adaptive_threshold_adjustments'] = []
                if hasattr(logger, 'time_series'):
                    logger.time_series.setdefault('adaptive_threshold_adjustments', []).append({
                        'tick': self.step_count,
                        'sigma': sigma,
                        'excitatory_fraction': excitatory_fraction,
                        'adjustment': adjustment,
                        'reason': reason,
                        'neurons_affected': neurons_adjusted,
                        'new_oscillator_strength': self.params.oscillator_strength
                    })
    
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
            if inp_neuron.is_active and inp_neuron.trinary_state != 0:
                input_signal = inp_neuron.trinary_state * self.params.sensory_input_gain
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
            immediate, delayed = s.compute_input(pre.trinary_state, self.time)
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
            n.update(syn_inputs[n.id], mod_inputs[n.id], ext, self.neuromodulators, dt, osc_drive)
            
            # Aggregate activity for this specific tick
            step_activity_sum += abs(n.trinary_state)
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
                s.potential_delta_w = s.calculate_delta_w(pre.trinary_state, post.trinary_state, self.neuromodulators, dt)
                
        for s in self.synapses:
            if s.integrity <= 0: continue
            pre = self.all_neurons[s.pre_id]
            post = self.all_neurons[s.post_id]
            if pre.is_active and post.is_active:
                neighbor_deltas = [ns.potential_delta_w for ns in s.neighbor_synapses]
                s.apply_update(dt, self.neuromodulators, neighbor_deltas)        
        for n in self.all_neurons:
            if n.is_active:
                activity = abs(n.trinary_state)
                self.total_energy_consumed += n.firing_energy_cost * activity * dt
                        
        self._update_neuromodulator_diffusion(dt)
        for k in ('dopamine', 'serotonin', 'acetylcholine', 'norepinephrine'):
            self.neuromodulators[k] = max(0.0, min(2.0, self.neuromodulators[k] + osc_drive * (0.02 if k == 'dopamine' else 0.01 if k in ('serotonin', 'acetylcholine') else 0.015)))
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

        # pattern/activity term (same spirit as logger)
        activity = sum(abs(n.trinary_state) for n in active) / len(active)

        # phase order parameter (this matches what you log in get_energy_status)
        phases = [n.phase for n in active]
        if len(phases) >= 2:
            sync = abs(sum(cmath.exp(1j * p) for p in phases) / len(phases))
        else:
            sync = 0.0

        # efficiency should NOT be "avg energy level" (leaks energy into fitness)
        # approximate per-tick energy spent by this circle
        spent = sum(n.firing_energy_cost * abs(n.trinary_state) for n in active) + 1e-9
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
            #if pruned_ids: 
             #   print(f"[EVOLUTION] Circle {circle.circle_id} pruned {len(pruned_ids)} neurons")
    
    def set_input_states(self, states: List[int]):
        """Clamps the input neurons to the given trinary states."""
        for i, s in enumerate(states[:len(self.input_neurons)]):
            self.input_neurons[i].set_state(s)
    
    def get_output_states(self) -> List[int]:
        """Returns the current trinary states of all active output neurons."""
        return [n.trinary_state for n in self.output_neurons if n.is_active]
    
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
                n.trinary_state = nd['trinary_state']
                n.health = nd['health']
                n.is_active = nd['is_active']
                n.energy_level = nd.get('energy_level', params.energy_baseline)
                n.phase = nd.get('phase', random.random() * 2 * math.pi)
                n.fitness_score = nd.get('fitness_score', 0.0)
                
                # Individualized neuron parameters
                n.membrane_time_constant = nd.get('membrane_time_constant', params.membrane_time_constant)
                n.firing_threshold_excitatory = nd.get('firing_threshold_excitatory', params.firing_threshold_excitatory)
                n.firing_threshold_inhibitory = nd.get('firing_threshold_inhibitory', params.firing_threshold_inhibitory)
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
    

    # Re-link neighbor synapses, which is necessary for the associativity rule.
    #for s in net.synapses:
#        s.neighbor_synapses = [ns for ns in net.synapses if ns.pre_id == s.pre_id and ns.post_id != s.post_id]
        
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
                # else: it's just an int (old format), skip
    return net
    

# --- General Utility and Helper Functions ---
def _clamp(v, a, b): return max(a, min(b, v))
def _now_str(): 
    from datetime import timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")

def _safe_path(name: str) -> str: return str((pathlib.Path(os.getcwd()) / name).resolve())
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
def _strip_leading_digits(name: str) -> str:
    """Removes leading digits from a string, used for generating names for offspring."""
    i = 0
    while i < len(name) and name[i].isdigit(): i += 1
    return name[i:] if i < len(name) else ""
def _rand_color(exclude: List[Tuple[int, int, int]]) -> Tuple[int, int, int]:
    """Generates a random color that is visually distinct from a list of excluded colors."""
    while True:
        c = (random.randint(30, 235), random.randint(30, 235), random.randint(30, 235))
        if any(sum((c[i] - e[i]) ** 2 for i in range(3)) < 1200 for e in exclude): continue
        if c in [(20, 120, 255), (40, 180, 60), (130, 130, 130), (220, 40, 40)]: continue
        return c
def _rot(x, y, a):
    """Rotates a 2D point (x, y) around the origin by angle 'a'."""
    ca, sa = math.cos(a), math.sin(a)
    return (x * ca - y * sa, x * sa + y * ca)
def _chunked(seq, n):
    """Yields successive n-sized chunks from a sequence."""
    n = max(1, int(n))
    for i in range(0, len(seq), n):
        yield seq[i:i + n]
def _pick_save_file(default_name: str) -> Optional[str]:
    """Opens a native OS file dialog to choose a save location."""
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        path = filedialog.asksaveasfilename(defaultextension=".json", initialfile=default_name, filetypes=[("JSON files", "*.json")])
        root.destroy()
        return path if path else None
    except Exception:
        return _safe_path(default_name)
def _pick_open_file() -> Optional[str]:
    """Opens a native OS file dialog to choose a file to open."""
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        root.destroy()
        return path if path else None
    except Exception:
        # A simple fallback for environments without a GUI.
        cand = sorted([p for p in os.listdir(os.getcwd()) if p.endswith(".json") and p.startswith("nxer_")])
        return cand[-1] if cand else None

class Slider:
    """A simple UI slider widget implemented with Pygame for the configuration screen."""
    def __init__(self, rect: pygame.Rect, min_val: float, max_val: float, default_val: float, label: str, is_int: bool = True):
        self.rect = rect
        self.min_val = min_val
        self.max_val = max_val
        self.is_int = is_int
        self.label = label
        self.handle_radius = 10
        self.dragging = False
        range_size = max_val - min_val
        self.normalized_pos = (default_val - min_val) / range_size if range_size != 0 else 0.5
        self.normalized_pos = _clamp(self.normalized_pos, 0.0, 1.0)
        track_y = rect.centery
        self.track_left = rect.x + self.handle_radius
        self.track_right = rect.x + rect.width - self.handle_radius
        self.track_top = track_y
        self.track_bottom = track_y
        self.handle_x = self.track_left + self.normalized_pos * (self.track_right - self.track_left)
        self.handle_y = track_y
    
    def handle_event(self, event: pygame.event.Event):
        """Handles mouse input for dragging the slider."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos
            if math.hypot(mouse_x - self.handle_x, mouse_y - self.handle_y) <= self.handle_radius:
                self.dragging = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            mouse_x, _ = event.pos
            self.handle_x = _clamp(mouse_x, self.track_left, self.track_right)
            self.normalized_pos = (self.handle_x - self.track_left) / (self.track_right - self.track_left)
            return True
        return False
    
    def get_value(self) -> float:
        """Returns the current numerical value of the slider."""
        value = self.min_val + self.normalized_pos * (self.max_val - self.min_val)
        return int(round(value)) if self.is_int else float(value)
    
    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        """Renders the slider onto a Pygame surface."""
        track_y = self.rect.centery
        pygame.draw.line(surface, (100, 100, 100), (self.track_left, track_y), (self.track_right, track_y), 3)
        pygame.draw.circle(surface, (200, 200, 200), (int(self.handle_x), int(self.handle_y)), self.handle_radius)
        pygame.draw.circle(surface, (150, 150, 150), (int(self.handle_x), int(self.handle_y)), self.handle_radius, 2)
        label_surf = font.render(self.label, True, (220, 220, 220))
        label_x = self.rect.x + self.rect.width // 2 - label_surf.get_width() // 2
        surface.blit(label_surf, (label_x, self.rect.y - 20))
        value = self.get_value()
        value_str = str(int(value)) if self.is_int else f"{value:.2f}"
        value_surf = font.render(value_str, True, (255, 255, 0))
        surface.blit(value_surf, (self.rect.x + self.rect.width + 10, self.rect.y))

# --- Game of Life Simulation: World, Agent, and Object Definitions ---

# Constants for terrain types.
T_SEA, T_LAND, T_ROCK = 0, 1, 2
# A list of colors reserved for UI or special objects to ensure agent colors are distinct.
RESERVED_COLORS = [(20, 120, 255), (40, 180, 60), (130, 130, 130), (220, 40, 40)]

@dataclass
class NxErStats:
    """A dataclass to store performance statistics for a single NxEr agent."""
    food_found: float = 0.0
    food_taken: float = 0.0
    explored: int = 0
    time_lived_s: float = 0.0
    mates_performed: int = 0
    energy_efficiency: float = 0.0
    temporal_sync_score: float = 0.0
    fitness_score: float = 0.0

@dataclass
class NxEr:
    """
    Represents a single agent (a "Neuraxon-enabled life form" or NxEr) in the simulation.
    """
    id: int
    name: str
    color: Tuple[int, int, int]
    pos: Tuple[int, int]
    can_land: bool
    can_sea: bool
    net: NeuraxonNetwork
    food: float
    is_male: bool
    alive: bool = True
    born_ts: float = time.time()
    died_ts: Optional[float] = None
    # UPDATED: 6 inputs now
    last_inputs: Tuple[float, ...] = (0, 0, 0, 0, 0, 0) 
    last_outputs: Tuple[int, int, int, int, int] = (0, 0, 0, 0, 0)
    ticks_per_action: int = 1
    tick_accum: int = 0
    harvesting: Optional[int] = None
    mating_with: Optional[int] = None
    mating_end_tick: Optional[int] = None
    stats: NxErStats = None
    visited: set = None
    dopamine_boost_ticks: int = 0
    _last_O4: int = 0
    mating_intent_until_tick: int = 0
    parents: Tuple[Optional[str], Optional[str]] = (None, None)  # Parent names
    ancestors: List[str] = field(default_factory=list)  # Full lineage (ancestor names)
    rounds_survived: int = 0  # How many rounds this NxEr has survived
    clan_id: Optional[int] = None  # Clan Heritage ID
    mate_cooldown_until_tick: int = 0
    last_move_tick: int = 0
    last_pos: Tuple[int, int] = (0, 0)
    
    # --- NEW PARAMETERS in V2.0---
    vision_range: int = 5     # Random 2 to 15
    smell_radius: int = 3     # Random 2 to 5
    heading: int = 0          # 0=NW, 1=N, 2=NE, 3=E, 4=SE, 5=S, 6=SW, 7=W
    clan_id: Optional[int] = None # Clan Heritage ID

@dataclass
class Food:
    """Represents a source of food in the world."""
    id: int
    anchor: Tuple[int, int] # The original spawn location, used for respawning nearby.
    pos: Tuple[int, int] # The current location.
    alive: bool = True
    respawn_at_tick: Optional[int] = None # The simulation tick at which this food will respawn.
    remaining: int = 25 # How much food is left at this source.
    progress: Dict[int, int] = field(default_factory=dict) # Tracks harvesting progress by different NxErs.

class World:
    """Generates and holds the state of the 2D grid-based environment."""
    def __init__(self, N: int, sea_pct: float, rock_pct: float, rnd_seed=None):
        self.N = N
        if rnd_seed is not None: random.seed(rnd_seed)
        # Use multiple layers of a simple noise function to generate natural-looking terrain.
        self.noise_offsets = [(random.random() * 100, random.random() * 100) for _ in range(3)]
        self.grid = [[T_LAND for _ in range(N)] for _ in range(N)]
        self._gen(sea_pct, rock_pct)
    
    def _noise(self, x, y, s, offset_idx):
        """A simple noise function based on sine and cosine waves."""
        ox, oy = self.noise_offsets[offset_idx]
        x_off, y_off = x + ox, y + oy
        return (math.sin(x_off * 0.15 * s) + math.cos(y_off * 0.13 * s) + math.sin((x_off + y_off) * 0.07 * s)) * 0.333
    
    def _gen(self, sea_pct, rock_pct):
        """Procedurally generates the world map with land, sea, and rocks."""
        N = self.N
        values = [[0.0] * N for _ in range(N)]
        # Generate a heightmap using layered noise, with a radial gradient to form an island.
        for y in range(N):
            for x in range(N):
                r = math.hypot(x - N / 2, y - N / 2) / (N * 0.7)
                v = (self._noise(x, y, 0.5, 0) + self._noise(x, y, 1.0, 1) + self._noise(x, y, 1.8, 2)) / 3.0 - r * 0.9
                values[y][x] = v
        
        # Determine the sea level threshold based on the desired percentage of sea.
        flat = sorted(v for row in values for v in row)
        k = int(len(flat) * sea_pct)
        sea_thresh = flat[k] if 0 <= k < len(flat) else min(flat)
        
        # Assign terrain types based on height relative to the sea level.
        for y in range(N):
            for x in range(N):
                self.grid[y][x] = T_SEA if values[y][x] <= sea_thresh else T_LAND
                
        # Randomly place rocks on a percentage of the land tiles.
        land = [(x, y) for y in range(N) for x in range(N) if self.grid[y][x] == T_LAND]
        num_rocks = int(len(land) * rock_pct)
        if num_rocks > 0:
            for (x, y) in random.sample(land, k=min(num_rocks, len(land))):
                self.grid[y][x] = T_ROCK
    
    def in_bounds(self, p):
        """Checks if a coordinate is within the world boundaries."""
        x, y = p
        return 0 <= x < self.N and 0 <= y < self.N
    
    def terrain(self, p):
        """Returns the terrain type at a given coordinate, with toroidal (wrapping) boundaries."""
        x, y = p
        return self.grid[y % self.N][x % self.N]

class Renderer:
    """Handles all Pygame-based rendering and user input for the main simulation window."""
    def __init__(self, world: World, textures: Dict[str, Optional[str]], textures_alpha: float):
        pygame.init()
        pygame.display.set_caption("Neuraxon Game of Life v 2.0 (Research Version) - By David Vivancos & Dr Jose Sanchez for Qubic Science")
        self.screen = pygame.display.set_mode((1920, 1080), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.world = world
        # Camera state variables.
        self.zoom = max(2.0, 800.0 / world.N)
        self.pan = [world.N * 0.5, world.N * 0.5]
        self.rot = 0.0
        self.dt = 1 / 60.0
        self.dragging = False
        self.drag_start = (0, 0)
        self.textures_alpha = _clamp(int(textures_alpha * 255) if textures_alpha <= 1 else int(textures_alpha), 0, 255)
        self.font = pygame.font.SysFont("consolas", 16)
        self.small = pygame.font.SysFont("consolas", 14)
        self.big = pygame.font.SysFont("consolas", 20, bold=True)
        self._load_textures(textures)
        # Rectangles for clickable UI elements.
        self.button_rects = {}
        self.overlay_buttons = {}
        self.selected_nxer_id: Optional[int] = None # The ID of the currently selected NxEr for the detail view.
        self.detail_buttons: Dict[str, pygame.Rect] = {}
        self.ranking_click_areas: List[Tuple[pygame.Rect, int]] = []
        self.visual_mode = False  # NEW: Visual mode flag, set to off for speed with V Key
        
    def _load_textures(self, tex):
        """Loads optional image files to be used as textures for world elements."""
        def load_one(path):
            if not path or str(path).lower() == "none": return None
            try:
                s = pygame.image.load(path).convert_alpha()
                s.set_alpha(self.textures_alpha)
                return s
            except: return None
        self.tex_land = load_one(tex.get("TextureLand"))
        self.tex_sea = load_one(tex.get("TextureSea"))
        self.tex_rock = load_one(tex.get("TextureRock"))
        self.tex_food = load_one(tex.get("TextureFood"))
        self.tex_nxer = load_one(tex.get("TextureNxEr"))
    
    def world_to_screen(self, x, y):
        """Converts world coordinates to screen coordinates, applying camera pan, zoom, and rotation."""
        cx, cy = self.pan
        dx, dy = (x - cx), (y - cy)
        rx, ry = _rot(dx, dy, self.rot)
        return (int(self.screen.get_width() / 2 + rx * self.zoom), int(self.screen.get_height() / 2 + ry * self.zoom))
    
    def screen_to_world(self, sx, sy) -> Tuple[float, float]:
        """Converts screen coordinates back to world coordinates, reversing the camera transform."""
        cx, cy = self.pan
        rx = (sx - self.screen.get_width() / 2) / self.zoom
        ry = (sy - self.screen.get_height() / 2) / self.zoom
        wx, wy = _rot(rx, ry, -self.rot)
        return (cx + wx, cy + wy)
    
    def _draw_effects(self, effects: List[dict], step_tick: int, GlobalTimeSteps: int):
        """Renders temporary visual effects like hearts for mating or skulls for death."""
        for ef in effects:
            age = step_tick - ef['start']
            if age < 0 or age >= GlobalTimeSteps: continue
            rise_px = int(-40 * (age / max(1, GlobalTimeSteps)))
            sx, sy = self.world_to_screen(ef['pos'][0], ef['pos'][1])
            sy += rise_px
            if ef['kind'] == 'heart':
                r = max(6, int(self.zoom * 0.5))
                pygame.draw.circle(self.screen, (220, 40, 60), (sx - r // 2, sy - r // 4), r // 2)
                pygame.draw.circle(self.screen, (220, 40, 60), (sx + r // 2, sy - r // 4), r // 2)
                pygame.draw.polygon(self.screen, (220, 40, 60), [(sx - r, sy), (sx + r, sy), (sx, sy + r)])
            elif ef['kind'] == 'skull':
                r = max(6, int(self.zoom * 0.45))
                pygame.draw.circle(self.screen, (0, 0, 0), (sx, sy), r)
                pygame.draw.rect(self.screen, (0, 0, 0), pygame.Rect(sx - r // 2, sy, r, r // 2), border_radius=3)
                eye_r = max(2, r // 5)
                pygame.draw.circle(self.screen, (200, 200, 200), (sx - r // 3, sy - r // 4), eye_r)
                pygame.draw.circle(self.screen, (200, 200, 200), (sx + r // 3, sy - r // 4), eye_r)
    
    def _draw_restart_modal(self):
        """Renders the "Game Over" modal dialog with options to restart or quit."""
        self.overlay_buttons = {}
        W, H = self.screen.get_size()
        bw, bh = 200, 48
        rect = pygame.Rect(W // 2 - 260, H // 2 - 140, 520, 280)
        srf = pygame.Surface((W, H), pygame.SRCALPHA)
        srf.fill((0, 0, 0, 160))
        self.screen.blit(srf, (0, 0))
        pygame.draw.rect(self.screen, (15, 15, 18), rect, border_radius=12)
        pygame.draw.rect(self.screen, (90, 90, 100), rect, 2, border_radius=12)
        title = self.big.render("All NxErs have perished.", True, (235, 235, 240))
        subtitle = self.small.render("Restart? (Will do in 10 seconds if no response)", True, (220, 220, 220))
        self.screen.blit(title, (rect.x + (rect.w - title.get_width()) // 2, rect.y + 28))
        self.screen.blit(subtitle, (rect.x + (rect.w - subtitle.get_width()) // 2, rect.y + 60))
        y = rect.y + 130
        yes_rect = pygame.Rect(rect.x + 40, y, bw - 30, bh)
        no_rect = pygame.Rect(rect.x + rect.w - 60 - bw, y, bw - 30, bh)
        for r, lab, key in [(yes_rect, "Yes", "restart_yes"), (no_rect, "No", "restart_no")]:
            pygame.draw.rect(self.screen, (35, 35, 45), r, border_radius=10)
            pygame.draw.rect(self.screen, (110, 110, 130), r, 2, border_radius=10)
            tx = self.big.render(lab, True, (235, 235, 240))
            self.screen.blit(tx, (r.x + (bw - tx.get_width()) // 2, r.y + (bh - tx.get_height()) // 2))
            self.overlay_buttons[key] = r
    
    def draw_world(self, foods: Dict[int, Food], nxers: Dict[int, NxEr], hud: Dict[str, List[Tuple[str, str]]], alive_count: int, dead_count: int, born_count: int, paused: bool, effects: List[dict], step_tick: int, GlobalTimeSteps: int, game_over: bool, game_index: int, best_scores: Optional[Dict[str, float]] = None):
        """The main rendering function, called once per frame to draw the entire scene."""
        self.screen.fill((0, 0, 0))
        w, h = self.screen.get_size()
        cx, cy = self.pan
        
        # --- Draw World Terrain (ONLY IF VISUAL MODE IS ON) ---
        if self.visual_mode:
            # Calculate the visible portion of the world to avoid drawing off-screen tiles.
            radius = max(w, h) / self.zoom * 1.5
            x0 = int(max(0, cx - radius)); x1 = int(min(self.world.N, cx + radius))
            y0 = int(max(0, cy - radius)); y1 = int(min(self.world.N, cy + radius))
            
            # Use Level of Detail (LOD) to speed up rendering when zoomed out.
            lod = 1
            tile = max(2, int(self.zoom))
            if tile < 4: lod = 3
            elif tile < 2: lod = 6
            
            for y in range(y0, y1, lod):
                for x in range(x0, x1, lod):
                    t = self.world.grid[y][x]
                    base = (40, 180, 60) if t == T_LAND else ((25, 100, 200) if t == T_SEA else (110, 110, 110))
                    height = 0 if t == T_SEA else (2 if t == T_ROCK else 1)
                    c = tuple(_clamp(int(b * (0.85 + 0.08 * height)), 0, 255) for b in base)
                    sx, sy = self.world_to_screen(x, y)
                    if sx < -tile or sx > w + tile or sy < -tile or sy > h + tile: continue
                    pygame.draw.rect(self.screen, c, pygame.Rect(sx, sy, int(self.zoom * lod) + 1, int(self.zoom * lod) + 1))
            
            # --- Draw Objects (Food and NxErs) ---
            for f in foods.values():
                if not f.alive: continue
                sx, sy = self.world_to_screen(f.pos[0], f.pos[1])
                if sx < -50 or sx > w + 50 or sy < -50 or sy > h + 50: continue
                s = max(6, int(self.zoom * 0.8))
                pygame.draw.polygon(self.screen, (220, 40, 40), [(sx, sy - s), (sx - s // 2, sy), (sx + s // 2, sy)])
            for a in nxers.values():
                if not a.alive: continue
                sx, sy = self.world_to_screen(a.pos[0], a.pos[1])
                if sx < -50 or sx > w + 50 or sy < -50 or sy > h + 50: continue
                rad = max(4, int(self.zoom * 0.45))
                pygame.draw.circle(self.screen, a.color, (sx, sy), rad)
                pygame.draw.circle(self.screen, (20, 20, 20), (sx, sy), rad, 1)
                # Draw an inner yellow circle representing the agent's energy level.
                if hasattr(a.net, 'get_energy_status'):
                    energy = a.net.get_energy_status().get('average_energy', 0.0)
                    energy_rad = max(2, int(rad * energy / 100.0))
                    pygame.draw.circle(self.screen, (255, 255, 0), (sx, sy), energy_rad, 1)
            
            self._draw_effects(effects, step_tick, GlobalTimeSteps)
        
        # --- Draw Heads-Up Display (HUD) Side Panel (ALWAYS VISIBLE) ---
        panel_w = 300
        x = self.screen.get_width() - panel_w - 16; y = 12
        rows = 1
        for _, lst in hud.items(): rows += 1 + min(3, len(lst))
        rows += 11
        panel_h = 26 + rows * 18 + 24
        base_rect = pygame.Rect(x - 10, y - 8, panel_w + 20, panel_h-50)
        pygame.draw.rect(self.screen, (0, 0, 0, 200), base_rect, border_radius=8)
        pygame.draw.rect(self.screen, (60, 60, 60), base_rect, 1, border_radius=8)
        round_text = self.big.render(f"Game Metrics: Round #{game_index}", True, (230, 230, 230))
        self.screen.blit(round_text, (x, y)); y += 28
        
        # Draw Rankings.
        name2color = {a.name: a.color for a in nxers.values()}
        self.ranking_click_areas = []
        for title, rows in hud.items():
            display_title = title
            score = best_scores.get(title) if best_scores else None
            if score is not None: display_title = f"{title} ({score:.2f})" if isinstance(score, float) else f"{title} ({int(score)})"
            self.screen.blit(self.small.render(display_title, True, (180, 180, 180)), (x, y)); y += 18
            for name, val in rows[:3]:
                base_name = name.replace(" [Die]", "")
                base_name = base_name.split(" [", 1)[0].strip()   #now the round is emmbedd in the name in hud
                dot_c = name2color.get(base_name, (200, 200, 200))
                pygame.draw.circle(self.screen, dot_c, (x + 8, y + 8), 6)
                name_text = self.small.render(f"{name}", True, (230, 230, 230))
                val_text = self.small.render(f"{val}", True, (220, 220, 220))
                name_rect = name_text.get_rect(topleft=(x + 20, y))
                val_rect = val_text.get_rect(topleft=(x + 180, y))
                clicked_nxer_name = None
                for nxer_obj in nxers.values():
                    if nxer_obj.name == base_name: clicked_nxer_name = nxer_obj.name; break
                if clicked_nxer_name: # Store the clickable area for this ranking entry.
                    combined_rect = name_rect.union(val_rect)
                    self.ranking_click_areas.append((combined_rect, clicked_nxer_name))
                self.screen.blit(name_text, (x + 20, y))
                self.screen.blit(val_text, (x + 180, y))
                y += 16
        y += 6
        
        # Draw general statistics.
        self.screen.blit(self.small.render(f"Alive: {alive_count}", True, (220, 220, 220)), (x, y)); y += 18
        self.screen.blit(self.small.render(f"Dead : {dead_count}", True, (220, 220, 220)), (x, y)); y += 18
        self.screen.blit(self.small.render(f"Born : {born_count}", True, (220, 220, 220)), (x, y)); y += 24
        
        # Draw aggregate network statistics.
        if nxers:
            alive_nxers = [a for a in nxers.values() if a.alive]            
            if alive_nxers:
                avg_energy = np.mean([a.net.get_energy_status().get('average_energy', 0.0) for a in alive_nxers])
                avg_branching = np.mean([a.net.branching_ratio for a in alive_nxers])
                self.screen.blit(self.small.render(f"Avg Energy: {avg_energy:.1f}", True, (200, 200, 0)), (x, y)); y += 18
                self.screen.blit(self.small.render(f"Branching: {avg_branching:.2f}", True, (180, 180, 180)), (x, y)); y += 24
        
        # Draw control buttons.
        self.button_rects = {}
        button_rows = [[("playpause", "Pause" if not paused else "Play"), ("exit", "Exit Game")], [("save", "Save Game"), ("load", "Load Game")], [("save_best", "Save Bests")]]
        bx, by, bw, bh, pad = x, y, 120, 28, 8
        for row in button_rows:
            row_x = bx
            for key, lab in row:
                r = pygame.Rect(row_x, by, bw, bh)
                pygame.draw.rect(self.screen, (35, 35, 40), r, border_radius=6)
                pygame.draw.rect(self.screen, (90, 90, 100), r, 1, border_radius=6)
                tx = self.small.render(lab, True, (230, 230, 230))
                self.screen.blit(tx, (r.x + (bw - tx.get_width()) // 2, r.y + (bh - tx.get_height()) // 2))
                self.button_rects[key] = r
                row_x += bw + pad
            by += bh + pad
        
        # --- Draw Detail Panel for Selected NxEr (ALWAYS AVAILABLE WHEN PAUSED) ---
        self.detail_buttons = {}
        if paused and self.selected_nxer_id is not None and self.selected_nxer_id in nxers:
            a = nxers[self.selected_nxer_id]
            px, py, pw, ph = x, by + 12, panel_w, 340
            rect = pygame.Rect(px - 10, py - 8, pw + 20, ph+50)
            pygame.draw.rect(self.screen, (0, 0, 0, 200), rect, border_radius=8)
            pygame.draw.rect(self.screen, (80, 80, 80), rect, 1, border_radius=8)
            
            gender_str = "Male" if a.is_male else "Female"
            title = f"{a.name} (id {a.id}) - {gender_str}"
            self.screen.blit(self.big.render(title, True, (230, 230, 230)), (px, py)); py += 28
            
            # Display detailed stats for the selected agent.
            terrain_type = "Land" if a.can_land and not a.can_sea else ("Sea" if a.can_sea and not a.can_land else "Both")
            energy_status = a.net.get_energy_status() if hasattr(a.net, 'get_energy_status') else {}
            facts = [f"Color : {a.color}", f"Pos : {a.pos} Food : {a.food:.1f}", f"Alive : {a.alive} Terr: {terrain_type} Lived : {a.stats.time_lived_s:.1f}s", f"Found : {a.stats.food_found:.1f} Taken: {a.stats.food_taken:.1f}", f"Mates : {a.stats.mates_performed} Explr : {a.stats.explored}", f"Energy: {energy_status.get('average_energy', 0):.1f} Fitness: {a.stats.fitness_score:.3f}", f"Branching: {energy_status.get('branching_ratio', 0):.2f}"]
            for line in facts:
                self.screen.blit(self.small.render(line, True, (220, 220, 220)), (px, py)); py += 18
            py += 6
            
            # Display key parameters of the agent's neural network.
            self.screen.blit(self.small.render("Network params:", True, (200, 200, 200)), (px, py)); py += 18
            P = a.net.params
            main_params = [f"inputs={P.num_input_neurons} hidden={P.num_hidden_neurons} outputs={P.num_output_neurons}", f"conn_prob={P.connection_probability:.2f} steps={P.simulation_steps}", f"tau_fast={P.tau_fast:.2f} slow={P.tau_slow:.2f} meta={P.tau_meta:.2f}", f"thr_exc={P.firing_threshold_excitatory:.3f} thr_inh={P.firing_threshold_inhibitory:.3f}", f"learn={P.learning_rate:.3f} stdp_win={P.stdp_window:.3f}", f"dopamine={P.dopamine_baseline:.3f} serotonin={P.serotonin_baseline:.3f}", f"energy_cost={P.firing_energy_cost:.1f} meta_rate={P.metabolic_rate:.2f}", f"circles={len(a.net.itu_circles)} evolve_int={P.evolution_interval}"]
            for line in main_params:
                self.screen.blit(self.small.render(line, True, (210, 210, 210)), (px, py)); py += 16
            py += 10
            
            # Draw buttons specific to the detail panel (e.g., save this specific NxEr).
            bw2, bh2, pad2 = 120, 26, 8
            detail_button_rows = [[("save_nxer", "Save NxEr"), ("load_nxer", "Load NxEr")], [("save_nxvizer", "Save NxVizer"), ("load_nxvizer", "Load NxVizer")]]
            for row in detail_button_rows:
                row_x = px
                for key, lab in row:
                    r = pygame.Rect(row_x, py, bw2, bh2)
                    pygame.draw.rect(self.screen, (35, 35, 40), r, border_radius=6)
                    pygame.draw.rect(self.screen, (90, 90, 100), r, 1, border_radius=6)
                    tx = self.small.render(lab, True, (230, 230, 230))
                    self.screen.blit(tx, (r.x + (bw2 - tx.get_width()) // 2, r.y + (bh2 - tx.get_height()) // 2))
                    self.detail_buttons[key] = r
                    row_x += bw2 + pad2
                py += bh2 + pad2
        
        # --- Draw Visual Mode Indicator ---
        if not self.visual_mode:
            indicator = self.big.render("(V to view)", True, (255, 0, 0))
            self.screen.blit(indicator, (20, 20))
                
        if game_over: self._draw_restart_modal()
        pygame.display.flip()
    
    def handle_input(self, dt):
        """Handles continuous keyboard input for camera panning."""
        if not self.visual_mode: return  # NEW: Skip input handling when visual mode is off
        keys = pygame.key.get_pressed()
        pstep = (50.0 / self.zoom) * dt
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: self.pan[0] -= pstep
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: self.pan[0] += pstep
        if keys[pygame.K_w] or keys[pygame.K_UP]: self.pan[1] -= pstep
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: self.pan[1] += pstep
    
    def event_zoom_rotate_pan(self, ev):
        """Handles discrete user input events for camera control (zoom, rotation, drag-pan)."""
        if not self.visual_mode: return  # NEW: Skip event handling when visual mode is off
        if ev.type == pygame.MOUSEWHEEL:
            self.zoom *= 1.1 if ev.y > 0 else 0.9
            self.zoom = _clamp(self.zoom, 0.5, 64.0)
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_q: self.rot -= 0.04
            elif ev.key == pygame.K_e: self.rot += 0.04
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 3: # Right mouse button for drag-pan.
            self.dragging = True
            self.drag_start = ev.pos
        elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 3:
            self.dragging = False
        elif ev.type == pygame.MOUSEMOTION and self.dragging:
            dx = ev.pos[0] - self.drag_start[0]
            dy = ev.pos[1] - self.drag_start[1]
            self.drag_start = ev.pos
            wx, wy = _rot(dx / self.zoom, dy / self.zoom, -self.rot)
            self.pan[0] -= wx
            self.pan[1] -= wy
    
    def button_clicked(self, pos) -> Optional[str]:
        """Checks if a click position collides with any of the main UI buttons."""
        for k, r in self.button_rects.items():
            if r.collidepoint(pos): return k
        for k, r in self.overlay_buttons.items():
            if r.collidepoint(pos): return k
        return None
    
    def detail_button_clicked(self, pos) -> Optional[str]:
        """Checks if a click position collides with any buttons in the detail panel."""
        for k, r in self.detail_buttons.items():
            if r.collidepoint(pos): return k
        return None
    
    def ranking_clicked(self, pos) -> Optional[int]:
        """Checks if a click position collides with any of the names in the ranking list."""
        for rect, name in self.ranking_click_areas:
            if rect.collidepoint(pos): return name
        return None
    
    def clear_detail(self):
        """Deselects the current NxEr and clears the detail panel."""
        self.selected_nxer_id = None
        self.detail_buttons = {}
    
    def tick(self, fps_cap=60):
        """Advances the Pygame clock, enforces an FPS cap, and returns the frame's delta time."""
        self.dt = self.clock.tick(fps_cap) / 1000.0
        return self.dt

def GameOfLife(NxWorldSize: int = 100, NxWorldSea: float = 0.60, NxWorldRocks: float = 0.05, StartingNxErs: int = 30, MaxNxErs: int = 400, MaxFood: int = 300, FoodRespan: int = 600, StartFood: float = 40.0, MaxNeurons: int = 12, GlobalTimeSteps: int = 60, TextureLand: Optional[str] = None, TextureSea: Optional[str] = None, TextureRock: Optional[str] = None, TextureFood: Optional[str] = None, TextureNxEr: Optional[str] = None, TexturesAlpha: float = 0.7, MateCooldownSeconds: int = 10, random_seed: Optional[int] = None, limit_minutes: Optional[int] = None, auto_save: bool = False, auto_save_prefix: str = "", auto_start: bool = False, save_on_round_end: bool = True):
    """
    The main function that initializes and runs the entire Game of Life simulation.
    """
    # Clamp parameters
    NxWorldSize = _clamp(int(NxWorldSize), 30, 1000)
    NxWorldSea = _clamp(float(NxWorldSea), 0.0, 0.95)
    NxWorldRocks = _clamp(float(NxWorldRocks), 0.0, 0.9)
    StartingNxErs = _clamp(int(StartingNxErs), 1, 150)
    MaxNxErs = _clamp(int(MaxNxErs), 100, 180) #Clamped atm to 180 to prevent the exponential in compute
    MaxFood = _clamp(int(MaxFood), 10, 1000)
    FoodRespan = _clamp(int(FoodRespan), 10, 3000)
    StartFood = _clamp(float(StartFood), 10.0, 250.0)
    MaxNeurons = _clamp(int(MaxNeurons), 1, 50)
    GlobalTimeSteps = _clamp(int(GlobalTimeSteps), 30, 300)
    MateCooldownSeconds = _clamp(int(MateCooldownSeconds), 0, 300)
    if random_seed is not None: random.seed(int(random_seed))
    # Initialize session globals
    
    mate_cooldown_ticks = MateCooldownSeconds * GlobalTimeSteps
    textures = {"TextureLand": TextureLand, "TextureSea": TextureSea, "TextureRock": TextureRock, "TextureFood": TextureFood, "TextureNxEr": TextureNxEr}
    
    # Initialize Core Components
    world = World(NxWorldSize, NxWorldSea, NxWorldRocks, rnd_seed=random_seed)
    renderer = Renderer(world, textures, TexturesAlpha)
    nxers: Dict[int, NxEr] = {}
    foods: Dict[int, Food] = {}
    occupied = set()
    births_count = 0
    deaths_count = 0
    effects: List[dict] = []
    champion_counts: Dict[str, int] = {}
    game_index = 1
    # Initialize session globals
    global _session_id, _current_round, _game_id, _next_nxer_id
    if _session_id is None:
        _reset_session_globals()
    _current_round = game_index
    _game_id = "".join([str(random.randint(0, 9)) for _ in range(9)])

    all_time_best: Dict[str, List[NxEr]] = {'food_found': [], 'food_taken': [], 'explored': [], 'time_lived_s': [], 'mates_performed': [], 'fitness_score': []}
    
    # --- CLAN & DIRECTION GLOBALS ---
    next_clan_id = 1
    # 0=NW, 1=N, 2=NE, 3=E, 4=SE, 5=S, 6=SW, 7=W
    DIR_OFFSETS = {
        0: (-1, -1), 1: (0, -1), 2: (1, -1),
        3: (1, 0),               7: (-1, 0),
        4: (1, 1),   5: (0, 1),  6: (-1, 1)
    }

    def wrap_pos(p: Tuple[int, int]) -> Tuple[int, int]: return (p[0] % world.N, p[1] % world.N)
    
    def find_free(allow_sea=True, allow_land=True, forbid=None, near=None, search_radius=5):
        """Finds a valid, unoccupied coordinate in the world, optionally near a specific point."""
        forbid = forbid or set()
        if near is not None:
            nx, ny = near
            for r in range(0, max(2, search_radius)):
                cand = []
                for dy in range(-r, r + 1):
                    for dx in range(-r, r + 1):
                        x, y = wrap_pos((nx + dx, ny + dy))
                        if (x, y) in forbid or (x, y) in occupied: continue
                        t = world.terrain((x, y))
                        if t == T_ROCK or (t == T_LAND and not allow_land) or (t == T_SEA and not allow_sea): continue
                        cand.append((x, y))
                random.shuffle(cand)
                for c in cand: return c
            return None
        else:
            for _ in range(4000): # Try a number of random positions.
                x = random.randrange(world.N)
                y = random.randrange(world.N)
                if (x, y) in forbid or (x, y) in occupied: continue
                t = world.terrain((x, y))
                if t == T_ROCK or (t == T_LAND and not allow_land) or (t == T_SEA and not allow_sea): continue
                return (x, y)
            return None
            
    def place_initial_food(count):
        """Populates the world with the initial set of food sources."""
        foods.clear()
        for i in range(count):
            p = find_free(allow_sea=True, allow_land=True)
            if not p: break
            foods[i] = Food(id=i, anchor=p, pos=p, alive=True, respawn_at_tick=None, remaining=25, progress={})
    place_initial_food(min(MaxFood, max(30, MaxFood // 2)))
    used_colors = set(RESERVED_COLORS)
    
    def _random_params(hidden_max: int) -> NetworkParameters:
        """Creates a randomized set of network parameters WITH BIOLOGICAL CORRELATIONS."""
        p = NetworkParameters(network_name="Neuraxon NxEr", num_input_neurons=6, num_hidden_neurons=random.randint(3, hidden_max), num_output_neurons=5)
        
        # --- Network Topology ---
        p.connection_probability = random.uniform(0.06, 0.19) 
        p.small_world_k = random.randint(4, 10)
        p.small_world_rewire_prob = random.uniform(0.08, 0.25)
        p.preferential_attachment = random.choice([True, False])
        
        # --- Core Neuron Properties ---
        p.membrane_time_constant = random.uniform(9.0, 48.0) 
        #p.firing_threshold_excitatory = random.uniform(0.35, 1.7) 
        p.firing_threshold_excitatory =random.uniform(0.1, 0.25) #FIX v2.23 to improve biological parameters previously set to 0.35, 1.7
        p.firing_threshold_inhibitory = random.uniform(-2.0, -0.5)
        p.adaptation_rate = random.uniform(0.0, 0.2)        
        p.spontaneous_firing_rate = random.uniform(0.02, 0.08) #FIX v2.23 to improve biological parameters previously set to 0.0, 0.1
        p.neuron_health_decay = random.uniform(0.0001, 0.005)  
        
        # --- Dendritic Branch Properties ---
        p.num_dendritic_branches = random.randint(2, 6)
        p.branch_threshold = random.uniform(0.4, 0.8)
        p.plateau_decay = random.uniform(200.0, 800.0)
        
        # --- SYNAPTIC TIME CONSTANTS ---        
        p.tau_fast = random.uniform(2.0, 8.0)
        p.tau_slow = p.tau_fast * random.uniform(5, 12) 
        p.tau_meta = random.uniform(270, 2900) 
        p.tau_ltp = random.uniform(10.0, 25.0)
        p.tau_ltd = p.tau_ltp * random.uniform(1.5, 3.0)  
        
        # --- Synaptic Weight Initialization ---
        #p.w_fast_init_min = random.uniform(-1.5, -0.5)
        #p.w_fast_init_max = random.uniform(0.5, 1.5)
        p.w_fast_init_min = random.uniform(0.1, 0.3)   #FIX v2.23 to improve biological parameters previously set to -1.5, -0.5 Weak connections
        p.w_fast_init_max = random.uniform(0.8, 1.2)   #FIX v2.23 to improve biological parameters previously set to 0.5, 1.5 Strong "Driver" connections

        p.w_slow_init_min = random.uniform(-0.8, -0.3)
        p.w_slow_init_max = random.uniform(0.3, 0.8)
        p.w_meta_init_min = random.uniform(-0.5, -0.1)
        p.w_meta_init_max = random.uniform(0.1, 0.5)
        
        # --- Learning and Plasticity ---
        p.learning_rate = random.uniform(0.005, 0.038) 
        p.stdp_window = random.uniform(15.0, 40.0)
        p.plasticity_threshold = random.uniform(0.3, 0.7)
        p.associativity_strength = random.uniform(0.05, 0.2)
        
        # --- Structural Plasticity ---
        p.synapse_integrity_threshold = random.uniform(0.05, 0.2)
        p.synapse_formation_prob = random.uniform(0.02, 0.06)
        #p.synapse_death_prob = random.uniform(0.01, 0.03)  
        p.synapse_death_prob = random.uniform(0.0001, 0.0005) #FIX v2.23 to improve biological parameters previously set to 0.01, 0.03 
        p.neuron_death_threshold = random.uniform(0.05, 0.2)
        
        # neuromodulators baseline levels
        base_neuromod = random.uniform(0.10, 0.22)  
        p.dopamine_baseline = base_neuromod * random.uniform(0.85, 1.15)
        p.serotonin_baseline = base_neuromod * random.uniform(0.85, 1.15)
        p.acetylcholine_baseline = base_neuromod * random.uniform(0.85, 1.15)
        p.norepinephrine_baseline = base_neuromod * random.uniform(0.85, 1.15)
        
        # --- Neuromodulator Affinity Thresholds ---
        p.dopamine_high_affinity_threshold = random.uniform(0.005, 0.05)
        p.dopamine_low_affinity_threshold = random.uniform(0.5, 1.5)
        p.serotonin_high_affinity_threshold = random.uniform(0.005, 0.05)
        p.serotonin_low_affinity_threshold = random.uniform(0.5, 1.5)
        p.acetylcholine_high_affinity_threshold = random.uniform(0.005, 0.05)
        p.acetylcholine_low_affinity_threshold = random.uniform(0.5, 1.5)
        p.norepinephrine_high_affinity_threshold = random.uniform(0.005, 0.05)
        p.norepinephrine_low_affinity_threshold = random.uniform(0.5, 1.5)
        
        p.neuromod_decay_rate = random.uniform(0.005, 0.05)  
        p.diffusion_rate = random.uniform(0.01, 0.05) 
        
        # --- Oscillators & Synchronization ---
        p.oscillator_low_freq = random.uniform(0.04, 0.12)
        p.oscillator_mid_freq = random.uniform(0.5, 1.2)
        p.oscillator_high_freq = random.uniform(2.5, 5.0)
        p.oscillator_strength = random.uniform(0.12, 0.30)  
        p.phase_coupling_strength = random.uniform(0.10, 0.25)  
                
        # Higher metabolism needs more energy baseline and faster recovery
        p.metabolic_rate = random.uniform(0.6, 1.2)  
        p.energy_baseline = 80 + 35 * p.metabolic_rate 
        p.recovery_rate = 0.35 + 0.35 * p.metabolic_rate  
        p.firing_energy_cost = random.uniform(2.0, 6.0)  
        p.plasticity_energy_cost = random.uniform(5.0, 12.0)
        
        # --- Homeostasis ---
        p.target_firing_rate = random.uniform(0.05, 0.2)
        p.homeostatic_plasticity_rate = random.uniform(0.0005, 0.003)
        
        # --- Aigarth/ITU Evolution ---
        p.itu_circle_radius = random.randint(7, 14)  
        p.evolution_interval = random.randint(510, 1700) 
        
        # Normalize fitness weights to sum to ~1.0
        ft = random.uniform(0.2, 0.5)
        fe = random.uniform(0.2, 0.4)
        fp = 1.0 - ft - fe
        p.fitness_temporal_weight = ft
        p.fitness_energy_weight = fe
        p.fitness_pattern_weight = max(0.1, fp)
        
        # --- Miscellaneous ---
        p.max_axonal_delay = random.uniform(5.0, 15.0)
        p.activity_threshold = random.uniform(0.3, 0.7)
        
        # --- Temporal/Simulation ---
        p.dt = 1.0
        p.simulation_steps = random.randint(10, max(20, 2 * GlobalTimeSteps))
        return p

    
    def make_nxer() -> NxEr:
        """Factory function to create a single new NxEr."""
        global _next_clan_id, _clan_history, _next_nxer_id
        
        idx = _next_nxer_id
        _next_nxer_id += 1
        
        p = _random_params(MaxNeurons)
        net = NeuraxonNetwork(p)
        pos = find_free(allow_sea=True, allow_land=True) or (random.randrange(world.N), random.randrange(world.N))
        terrain = world.terrain(pos)
        if terrain == T_LAND: can_land, can_sea = True, False
        elif terrain == T_SEA: can_land, can_sea = False, True
        else: can_land, can_sea = True, False
        is_male = random.random() < 0.5
        
        # Use global name counter for unique name
        name = _get_next_global_name()
        
        vision = random.randint(2, 15)
        smell = random.randint(2, 5)
        heading = random.randint(0, 7)
        
        # Create individual clan for this NxEr
        clan_id = _next_clan_id
        _next_clan_id += 1
        _clan_history[clan_id] = {
            'members': {name},
            'merged_from': [],
            'created_at_round': _current_round,
            'active': True
        }
        
        nx = NxEr(
            id=_next_nxer_id, 
            name=name, 
            color=_rand_color(list(used_colors)), 
            pos=pos, 
            can_land=can_land, 
            can_sea=can_sea, 
            net=net, 
            food=float(StartFood), 
            is_male=is_male, 
            ticks_per_action=max(1, int(GlobalTimeSteps / max(1, p.simulation_steps))), 
            stats=NxErStats(), 
            visited=set([pos]), 
            parents=(None, None),
            ancestors=[],  # No ancestors for original NxErs
            rounds_survived=0,
            mate_cooldown_until_tick=0, 
            last_move_tick=0, 
            last_pos=pos,
            vision_range=vision, 
            smell_radius=smell, 
            heading=heading, 
            clan_id=clan_id
        )
        used_colors.add(nx.color)
        nx.last_inputs = (0, 0, 0, 0, 0, 0)
        return nx
    
    def spawn_child(A: NxEr, B: NxEr, near_pos: Tuple[int, int]) -> Optional[NxEr]:
        """Creates a new NxEr from two parents."""
        nonlocal births_count
        global _next_clan_id, _clan_history, _next_nxer_id
        
        if len(nxers) >= MaxNxErs: return None
        child_id = _next_nxer_id
        _next_nxer_id += 1
        child_net = Inheritance(A, B)
        
        # Terrain inheritance logic (unchanged)
        A_land_specialist = A.can_land and not A.can_sea
        A_sea_specialist = A.can_sea and not A.can_land
        B_land_specialist = B.can_land and not B.can_sea
        B_sea_specialist = B.can_sea and not B.can_land
        terrain_A = world.terrain(A.pos)
        terrain_B = world.terrain(B.pos)
        is_seashore_mating = (A_land_specialist and B_sea_specialist and terrain_A == T_LAND and terrain_B == T_SEA) or \
                            (A_sea_specialist and B_land_specialist and terrain_A == T_SEA and terrain_B == T_LAND)
        if is_seashore_mating: 
            can_land, can_sea = True, True
        else:
            if A_land_specialist and B_land_specialist: can_land, can_sea = True, False
            elif A_sea_specialist and B_sea_specialist: can_land, can_sea = False, True
            else:
                can_land = A.can_land or B.can_land
                can_sea = A.can_sea or B.can_sea
        if not (can_land or can_sea): can_land = True
        
        is_male_child = random.random() < 0.5
        
        # Build full ancestor list from both parents
        child_ancestors = []
        child_ancestors.append(A.name)
        child_ancestors.append(B.name)
        child_ancestors.extend(A.ancestors)
        child_ancestors.extend(B.ancestors)
        child_ancestors = list(dict.fromkeys(child_ancestors))  # Remove duplicates, preserve order (parents first)
        
        # Clan merging: Create new clan from both parent clans
        new_clan_id = _next_clan_id
        _next_clan_id += 1
        
        old_clan_a = A.clan_id
        old_clan_b = B.clan_id
        
        # Collect all members from both clans
        all_members = set()
        merged_from = []
        
        if old_clan_a is not None and old_clan_a in _clan_history:
            all_members.update(_clan_history[old_clan_a]['members'])
            merged_from.append(old_clan_a)
            _clan_history[old_clan_a]['active'] = False
            
        if old_clan_b is not None and old_clan_b in _clan_history and old_clan_b != old_clan_a:
            all_members.update(_clan_history[old_clan_b]['members'])
            merged_from.append(old_clan_b)
            _clan_history[old_clan_b]['active'] = False
        
        child_name = _get_next_global_name()  # Get name early so we can use it
        all_members.add(child_name)  # Use name instead of ID
        
        # Create new clan
        _clan_history[new_clan_id] = {
            'members': all_members,
            'merged_from': merged_from,
            'created_at_round': _current_round,
            'active': True
        }
        
        # Update all members of both old clans to new clan
        for member_id in all_members:
            if member_id in nxers and nxers[member_id].alive:
                nxers[member_id].clan_id = new_clan_id
        
        # child_name already generated above for clan tracking
        
        vision = A.vision_range if random.random() < 0.5 else B.vision_range
        smell = A.smell_radius if random.random() < 0.5 else B.smell_radius
        heading = random.randint(0, 7)
        
        child = NxEr(
            id=child_id,
            name=child_name,
            color=_rand_color(list(RESERVED_COLORS) + [a.color for a in nxers.values()]),
            pos=near_pos,
            can_land=can_land,
            can_sea=can_sea,
            net=child_net,
            food=0.0,
            is_male=is_male_child,
            ticks_per_action=max(1, int(GlobalTimeSteps / max(1, child_net.params.simulation_steps))),
            stats=NxErStats(),
            visited=set(),
            parents=(A.name, B.name),
            ancestors=child_ancestors,
            rounds_survived=0,
            mate_cooldown_until_tick=0,
            last_move_tick=step_tick,
            last_pos=near_pos,
            vision_range=vision,
            smell_radius=smell,
            heading=heading,
            clan_id=new_clan_id
        )
        
        transfer = min(5.0, min(A.food / 2, B.food / 2))
        A.food -= transfer
        B.food -= transfer
        child.food += transfer * 8
        max_limit = float(StartFood) * 1.5 
        child.food = min(transfer * 8, max_limit)#FIX v2.24 to improve biological parameters previously set to 15        
        child.pos = find_free(allow_sea=can_sea, allow_land=can_land, near=near_pos, search_radius=3) or near_pos
        nxers[child.id] = child
        occupied.add(child.pos)
        A.stats.mates_performed += 1
        B.stats.mates_performed += 1
        births_count += 1
        child.stats.fitness_score = (A.stats.fitness_score + B.stats.fitness_score) / 2
        
        # Paper Claim: Norepinephrine activated somewhat by the birth of offspring per se
        A.net.neuromodulators['norepinephrine'] = min(2.0, A.net.neuromodulators.get('norepinephrine', 0.12) + 0.15)
        B.net.neuromodulators['norepinephrine'] = min(2.0, B.net.neuromodulators.get('norepinephrine', 0.12) + 0.15)
        
        return child
        
    for i in range(StartingNxErs):
        a = make_nxer()
        nxers[a.id] = a
        occupied.add(a.pos)
        
    
    # CHANGE in V2.0: Start unpaused if auto_start is True
    running = True
    paused = not auto_start
    
    step_tick = 0
    boot_random_until = 5 * GlobalTimeSteps
    game_over = False
    game_over_start_time = None
    user_declined_restart = False
    
    # Time tracking for Limit Mode
    game_start_real_time = time.time()
    
    def push_effect(kind: str, pos: Tuple[int, int]): effects.append({'kind': kind, 'pos': pos, 'start': step_tick})
    
    # --- Save/Load Functions ---
    def save_nxer_to_file(a: NxEr, save_name: str = None):
        global _session_id
        if _session_id is None:
            _session_id = _generate_session_id()
        default = save_name or f"{_session_id}_nxer_{a.name}_{_now_str()}.json"
        path = _pick_save_file(default)
        if not path: return
        data = {"meta": {"created": _now_str(), "type": "NxEr", "session_id": _session_id, "game_id": _game_id}, "nxer": {"id": a.id, "name": a.name, "color": a.color, "pos": a.pos, "can_land": a.can_land, "can_sea": a.can_sea, 
        "food": a.food, "is_male": a.is_male, "alive": a.alive, "born_ts": a.born_ts, "died_ts": a.died_ts, "last_inputs": a.last_inputs, "last_outputs": a.last_outputs, "ticks_per_action": a.ticks_per_action, "tick_accum": a.tick_accum, "harvesting": a.harvesting, "mating_with": a.mating_with, "mating_end_tick": a.mating_end_tick, "visited": list(a.visited), "dopamine_boost_ticks": a.dopamine_boost_ticks, "_last_O4": a._last_O4, "mating_intent_until_tick": a.mating_intent_until_tick, "parents": list(a.parents) if a.parents else [None, None], "mate_cooldown_until_tick": a.mate_cooldown_until_tick, "last_move_tick": a.last_move_tick, "last_pos": a.last_pos, "stats": asdict(a.stats), "net": a.net.to_dict(),
        "vision_range": a.vision_range, "smell_radius": a.smell_radius, "heading": a.heading, "clan_id": a.clan_id, "ancestors": a.ancestors, "rounds_survived": a.rounds_survived}}
        if get_data_logger().log_level >= 2:
            data["nxer"]["network_detailed"] = _extract_detailed_network_state(a.net)
        with open(path, "w") as f: json.dump(data, f)
        print(f"[SAVE NxEr] {path}")
    
    def load_nxer_from_file(spawn_near: Tuple[int, int] = None):
        path = _pick_open_file()
        if not path: return
        with open(path, "r") as f: data = json.load(f)
        nd = data.get("nxer", data)
        net = _rebuild_net_from_dict(nd["net"])
        pos0 = tuple(nd.get("pos", (world.N // 2, world.N // 2)))
        if spawn_near is not None: pos0 = spawn_near
        pos = find_free(allow_sea=True, allow_land=True, near=pos0, search_radius=6) or wrap_pos(pos0)
        base_name = str(nd.get("name", f"N{len(nxers)}"))
        name = base_name; counter = 1
        alive_names = {a.name for a in nxers.values() if a.alive}
        while name in alive_names: name = f"{base_name}{counter}"; counter += 1
        a = NxEr(id=(max(nxers.keys()) + 1) if nxers else 0, name=name, color=tuple(nd.get("color", (200, 200, 200))), pos=pos, can_land=nd["can_land"], can_sea=nd["can_sea"], 
        net=net, food=float(StartFood), is_male=bool(nd.get("is_male", random.random() < 0.5)), alive=True, born_ts=time.time(), died_ts=None, last_inputs=tuple(nd.get("last_inputs", (0, 0, 0, 0, 0, 0))), last_outputs=tuple(nd.get("last_outputs", (0, 0, 0, 0, 0))), ticks_per_action=int(nd.get("ticks_per_action", 1)), tick_accum=int(nd.get("tick_accum", 0)), harvesting=nd["harvesting"], mating_with=nd["mating_with"], mating_end_tick=nd["mating_end_tick"], stats=NxErStats(**nd.get("stats", {})), visited=set(map(tuple, nd.get("visited", []))), dopamine_boost_ticks=int(nd.get("dopamine_boost_ticks", 0)), _last_O4=int(nd.get("_last_O4", 0)), mating_intent_until_tick=int(nd.get("mating_intent_until_tick", 0)), parents=tuple(nd.get("parents", [None, None])), mate_cooldown_until_tick=int(nd.get("mate_cooldown_until_tick", 0)), last_move_tick=int(nd.get("last_move_tick", step_tick)), last_pos=tuple(nd.get("last_pos", pos)),
                 vision_range=nd.get("vision_range", 5), smell_radius=nd.get("smell_radius", 3), heading=nd.get("heading", 0), clan_id=nd.get("clan_id", None))
        a.tick_accum = 0; a.harvesting = None; a.mating_with = None; a.mating_end_tick = None; a.mating_intent_until_tick = 0; a.mate_cooldown_until_tick = 0
        nxers[a.id] = a
        if get_data_logger().log_level >= 2 and "network_detailed" in nd:
            _apply_detailed_network_state(a.net, nd["network_detailed"])
        occupied.add(a.pos)
        print(f"[LOAD NxEr] spawned {a.name} at {a.pos}")
        get_data_logger().log_nxer_event(step_tick, 'loaded', a.id, {'name': a.name, 'from_file': path})
    
    def save_nxvizer_to_file(a: NxEr, save_name: str = None):
        default = save_name or f"nxvizer_{a.name}_{_now_str()}.json"
        path = _pick_save_file(default)
        if not path: return
        params = a.net.params
        data = {"network_name": params.network_name, "num_input_neurons": params.num_input_neurons, "num_hidden_neurons": params.num_hidden_neurons, "num_output_neurons": params.num_output_neurons, "connection_probability": params.connection_probability, "membrane_time_constant": params.membrane_time_constant, "firing_threshold_excitatory": params.firing_threshold_excitatory, "firing_threshold_inhibitory": params.firing_threshold_inhibitory, "adaptation_rate": params.adaptation_rate, "spontaneous_firing_rate": params.spontaneous_firing_rate, "neuron_health_decay": params.neuron_health_decay, "tau_fast": params.tau_fast, "w_fast_init_min": params.w_fast_init_min, "w_fast_init_max": params.w_fast_init_max, "tau_slow": params.tau_slow, "w_slow_init_min": params.w_slow_init_min, "w_slow_init_max": params.w_slow_init_max, "tau_meta": params.tau_meta, "w_meta_init_min": params.w_meta_init_min, "w_meta_init_max": params.w_meta_init_max, "learning_rate": params.learning_rate, "stdp_window": params.stdp_window, "synapse_integrity_threshold": params.synapse_integrity_threshold, "synapse_formation_prob": params.synapse_formation_prob, "synapse_death_prob": params.synapse_death_prob, "neuron_death_threshold": params.neuron_death_threshold, "dopamine_baseline": params.dopamine_baseline, "serotonin_baseline": params.serotonin_baseline, "acetylcholine_baseline": params.acetylcholine_baseline, "norepinephrine_baseline": params.norepinephrine_baseline, "neuromod_decay_rate": params.neuromod_decay_rate, "dt": params.dt, "simulation_steps": params.simulation_steps}
        with open(path, "w") as f: json.dump(data, f, indent=2)
        print(f"[SAVE NxVizer] {path}")
        
    def load_nxvizer_from_file(spawn_near: Tuple[int, int] = None):
        path = _pick_open_file()
        if not path: return
        with open(path, "r") as f: data = json.load(f)
        params = NetworkParameters(network_name=data.get("network_name", "Neuraxon NxEr"), num_input_neurons=data.get("num_input_neurons", 6), num_hidden_neurons=data.get("num_hidden_neurons", 10), num_output_neurons=data.get("num_output_neurons", 5), connection_probability=data.get("connection_probability", 0.15), membrane_time_constant=data.get("membrane_time_constant", 20.0), firing_threshold_excitatory=data.get("firing_threshold_excitatory", 0.9), firing_threshold_inhibitory=data.get("firing_threshold_inhibitory", -0.9), adaptation_rate=data.get("adaptation_rate", 0.05), spontaneous_firing_rate=data.get("spontaneous_firing_rate", 0.02), neuron_health_decay=data.get("neuron_health_decay", 0.001), tau_fast=data.get("tau_fast", 5.0), w_fast_init_min=data.get("w_fast_init_min", -1.0), w_fast_init_max=data.get("w_fast_init_max", 1.0), tau_slow=data.get("tau_slow", 50.0), w_slow_init_min=data.get("w_slow_init_min", -0.5), w_slow_init_max=data.get("w_slow_init_max", 0.5), tau_meta=data.get("tau_meta", 1000.0), w_meta_init_min=data.get("w_meta_init_min", -0.3), w_meta_init_max=data.get("w_meta_init_max", 0.3), learning_rate=data.get("learning_rate", 0.01), stdp_window=data.get("stdp_window", 20.0), synapse_integrity_threshold=data.get("synapse_integrity_threshold", 0.1), synapse_formation_prob=data.get("synapse_formation_prob", 0.02), synapse_death_prob=data.get("synapse_death_prob", 0.01), neuron_death_threshold=data.get("neuron_death_threshold", 0.1), dopamine_baseline=data.get("dopamine_baseline", 0.12), serotonin_baseline=data.get("serotonin_baseline", 0.12), acetylcholine_baseline=data.get("acetylcholine_baseline", 0.12), norepinephrine_baseline=data.get("norepinephrine_baseline", 0.12), neuromod_decay_rate=data.get("neuromod_decay_rate", 0.1), dt=data.get("dt", 1.0), simulation_steps=data.get("simulation_steps", 30))
        net = NeuraxonNetwork(params)
        pos0 = spawn_near or (world.N // 2, world.N // 2)
        pos = find_free(allow_sea=True, allow_land=True, near=pos0, search_radius=6) or wrap_pos(pos0)
        terrain_choice = random.random()
        if terrain_choice < 0.33: can_land, can_sea = True, False
        elif terrain_choice < 0.66: can_land, can_sea = False, True
        else: can_land, can_sea = True, True
        base_name = "NxVizer"; name = base_name; counter = 1
        alive_names = {a.name for a in nxers.values() if a.alive}
        while name in alive_names: name = f"{base_name}{counter}"; counter += 1
        
        vision = random.randint(2, 15); smell = random.randint(2, 5); heading = random.randint(0, 7)
        
        a = NxEr(id=(max(nxers.keys()) + 1) if nxers else 0, name=name, color=_rand_color(list(used_colors)), pos=pos, can_land=can_land, can_sea=can_sea, net=net, food=float(StartFood), is_male=random.random() < 0.5, alive=True, born_ts=time.time(), died_ts=None, last_inputs=(0, 0, 0, 0, 0, 0), ticks_per_action=max(1, int(GlobalTimeSteps / max(1, params.simulation_steps))), tick_accum=0, harvesting=None, mating_with=None, mating_end_tick=None, stats=NxErStats(), visited=set([pos]), dopamine_boost_ticks=0, _last_O4=0, mating_intent_until_tick=0, parents=(None, None), mate_cooldown_until_tick=0, last_move_tick=step_tick, last_pos=pos,
                 vision_range=vision, smell_radius=smell, heading=heading, clan_id=None)
        used_colors.add(a.color); nxers[a.id] = a; occupied.add(a.pos)
        print(f"[LOAD NxVizer] spawned {a.name} at {a.pos}")
    
    def _extract_detailed_network_state(net: NeuraxonNetwork) -> dict:
        """Extract detailed network state for Level 2 logging."""
        return {
            'all_neuron_states': [{
                'id': n.id,
                'membrane_potential': n.membrane_potential,
                'trinary_state': n.trinary_state,
                'adaptation': n.adaptation,
                'autoreceptor': n.autoreceptor,
                'health': n.health,
                'energy_level': n.energy_level,
                'phase': n.phase,
                'natural_frequency': n.natural_frequency,
                'intrinsic_timescale': n.intrinsic_timescale,
                'fitness_score': n.fitness_score,
                'state_history': list(n.state_history),
                'dendritic_branches': [{
                    'branch_potential': b.branch_potential,
                    'plateau_potential': b.plateau_potential,
                    'local_spike_history': list(b.local_spike_history)
                } for b in n.dendritic_branches]
            } for n in net.all_neurons],
            'all_synapse_states': [{
                'pre_id': s.pre_id,
                'post_id': s.post_id,
                'w_fast': s.w_fast,
                'w_slow': s.w_slow,
                'w_meta': s.w_meta,
                'integrity': s.integrity,
                'pre_trace': s.pre_trace,
                'post_trace': s.post_trace,
                'pre_trace_ltd': s.pre_trace_ltd,
                'learning_rate_mod': s.learning_rate_mod,
                'associative_strength': s.associative_strength
            } for s in net.synapses],
            'neuromodulators': dict(net.neuromodulators),
            'modulator_grid': net.modulator_grid.tolist(),
            'oscillator_phase_offsets': list(net.oscillator_phase_offsets),
            'activation_history': list(net.activation_history),
            'branching_ratio': net.branching_ratio,
            'time': net.time,
            'step_count': net.step_count,
            'total_energy_consumed': net.total_energy_consumed
        }
    
    def _apply_detailed_network_state(net: NeuraxonNetwork, detailed: dict):
        """Apply detailed network state from Level 2 save."""
        if 'all_neuron_states' in detailed:
            for ns in detailed['all_neuron_states']:
                if ns['id'] < len(net.all_neurons):
                    n = net.all_neurons[ns['id']]
                    n.state_history = deque(ns.get('state_history', []), maxlen=50)
                    n.autoreceptor = ns.get('autoreceptor', 0.0)
        
        if 'modulator_grid' in detailed:
            net.modulator_grid = np.array(detailed['modulator_grid'])
        
        if 'activation_history' in detailed:
            net.activation_history = deque(detailed['activation_history'], maxlen=1000)
        
        net.branching_ratio = detailed.get('branching_ratio', 1.0)
        
    def save_state(name=None):
        global _session_id
        if _session_id is None:
            _session_id = _generate_session_id()
        
        # Include session ID in filename
        name = name or f"{_session_id}_nx_world_save_{_now_str()}.json"
        
        data = {
            "meta": {
                "created": _now_str(), 
                "step_tick": step_tick, 
                "GlobalTimeSteps": GlobalTimeSteps, 
                "births_count": births_count, 
                "deaths_count": deaths_count, 
                "game_index": game_index,
                "session_id": _session_id,
                "game_id": _game_id,
                "global_name_counter": _global_name_counter,
                "used_names": list(_used_names),
                "next_clan_id": _next_clan_id,
                "current_round": _current_round,
                "next_nxer_id": _next_nxer_id
            },
            "clan_history": {str(k): {
                'members': list(v['members']),
                'merged_from': v['merged_from'],
                'created_at_round': v['created_at_round'],
                'active': v['active']
            } for k, v in _clan_history.items()},
            "world": {"N": world.N, "grid": world.grid},
            "nxers": [{
                "id": a.id, 
                "name": a.name, 
                "color": a.color, 
                "pos": a.pos, 
                "can_land": a.can_land, 
                "can_sea": a.can_sea, 
                "food": a.food, 
                "is_male": a.is_male, 
                "alive": a.alive, 
                "born_ts": a.born_ts, 
                "died_ts": a.died_ts,
                "last_inputs": a.last_inputs, 
                "last_outputs": a.last_outputs, 
                "ticks_per_action": a.ticks_per_action, 
                "tick_accum": a.tick_accum, 
                "harvesting": a.harvesting, 
                "mating_with": a.mating_with, 
                "mating_end_tick": a.mating_end_tick, 
                "visited": list(a.visited), 
                "dopamine_boost_ticks": a.dopamine_boost_ticks, 
                "_last_O4": a._last_O4, 
                "mating_intent_until_tick": a.mating_intent_until_tick, 
                "parents": list(a.parents) if a.parents else [None, None],
                "ancestors": a.ancestors,
                "rounds_survived": a.rounds_survived,
                "mate_cooldown_until_tick": a.mate_cooldown_until_tick, 
                "last_move_tick": a.last_move_tick, 
                "last_pos": a.last_pos, 
                "stats": asdict(a.stats), 
                "net": a.net.to_dict(),
                "vision_range": a.vision_range, 
                "smell_radius": a.smell_radius, 
                "heading": a.heading, 
                "clan_id": a.clan_id
            } for a in nxers.values()],
            "foods": [{"id": f.id, "anchor": f.anchor, "pos": f.pos, "alive": f.alive, "respawn_at_tick": f.respawn_at_tick, "remaining": f.remaining, "progress": f.progress} for f in foods.values()],
            "all_time_best": {k: [{"name": a.name, "is_male": a.is_male, "stats": asdict(a.stats), "net": a.net.to_dict(), "can_land": a.can_land, "can_sea": a.can_sea, "ancestors": getattr(a, 'ancestors', []), "rounds_survived": getattr(a, 'rounds_survived', 0)} for a in v] for k, v in all_time_best.items()}
        }
        logger = get_data_logger()
        data["data_logger"] = logger.to_dict()
        path = _safe_path(name)
        with open(path, "w") as f: json.dump(data, f)
        print(f"[SAVE] {path}")
    
    def load_state(path):
        nonlocal step_tick, nxers, foods, occupied, births_count, deaths_count, world, game_index, all_time_best
        global _session_id, _global_name_counter, _used_names, _clan_history, _next_clan_id, _current_round, _game_id, _next_nxer_id
        
        with open(path, "r") as f: data = json.load(f)
        
        step_tick = data["meta"]["step_tick"]
        births_count = int(data["meta"].get("births_count", 0))
        deaths_count = int(data["meta"].get("deaths_count", 0))
        game_index = int(data["meta"].get("game_index", 1))
        
        # Restore global tracking variables
        _session_id = data["meta"].get("session_id", _generate_session_id())
        _game_id = data["meta"].get("game_id", "".join([str(random.randint(0, 9)) for _ in range(9)]))
        _global_name_counter = data["meta"].get("global_name_counter", 0)
        _used_names = set(data["meta"].get("used_names", []))
        _next_clan_id = data["meta"].get("next_clan_id", 1)
        _current_round = data["meta"].get("current_round", 1)
        _next_nxer_id = data["meta"].get("next_nxer_id", max((n["id"] for n in data["nxers"]), default=0) + 1)
        
        # Restore clan history
        if "clan_history" in data:
            _clan_history = {}
            for k, v in data["clan_history"].items():
                _clan_history[int(k)] = {
                    'members': set(v['members']),
                    'merged_from': v['merged_from'],
                    'created_at_round': v['created_at_round'],
                    'active': v['active']
                }
        
        world.grid = data["world"]["grid"]
        world.N = len(world.grid)
        renderer.pan = [world.N * 0.5, world.N * 0.5]
        renderer.zoom = max(2.0, 800.0 / world.N)
        
        # Restore all_time_best with new fields
        if "all_time_best" in data:
            all_time_best = {k: [] for k in data["all_time_best"]}
            for category, champs in data["all_time_best"].items():
                for champ_data in champs:
                    net = _rebuild_net_from_dict(champ_data["net"])
                    champ_nxer = NxEr(
                        id=-1, 
                        name=champ_data["name"], 
                        color=(200, 200, 200), 
                        pos=(0, 0), 
                        can_land=champ_data.get("can_land", True), 
                        can_sea=champ_data.get("can_sea", False), 
                        net=net, 
                        food=0, 
                        is_male=champ_data.get("is_male", random.random() < 0.5), 
                        stats=NxErStats(**champ_data["stats"]),
                        ancestors=champ_data.get("ancestors", []),
                        rounds_survived=champ_data.get("rounds_survived", 0)
                    )
                    all_time_best[category].append(champ_nxer)
        
        nxers = {}
        occupied = set()
        for nd in data["nxers"]:
            net = _rebuild_net_from_dict(nd["net"])
            pos_wrapped = wrap_pos(tuple(nd["pos"]))
            a = NxEr(
                id=nd["id"], 
                name=nd["name"], 
                color=tuple(nd["color"]), 
                pos=pos_wrapped, 
                can_land=nd["can_land"], 
                can_sea=nd["can_sea"], 
                net=net, 
                food=float(nd["food"]),
                is_male=nd.get("is_male", random.random() < 0.5), 
                alive=nd["alive"], 
                born_ts=nd["born_ts"], 
                died_ts=nd["died_ts"],
                last_inputs=tuple(nd["last_inputs"]), 
                last_outputs=tuple(nd["last_outputs"]), 
                ticks_per_action=int(nd["ticks_per_action"]), 
                tick_accum=int(nd["tick_accum"]), 
                harvesting=nd["harvesting"], 
                mating_with=nd["mating_with"], 
                mating_end_tick=nd["mating_end_tick"], 
                stats=NxErStats(**nd["stats"]), 
                visited=set(map(tuple, nd.get("visited", []))), 
                dopamine_boost_ticks=int(nd.get("dopamine_boost_ticks", 0)), 
                _last_O4=int(nd.get("_last_O4", 0)), 
                mating_intent_until_tick=int(nd.get("mating_intent_until_tick", 0)), 
                parents=tuple(nd.get("parents", [None, None])),
                ancestors=nd.get("ancestors", []),
                rounds_survived=nd.get("rounds_survived", 0),
                mate_cooldown_until_tick=int(nd.get("mate_cooldown_until_tick", 0)), 
                last_move_tick=int(nd.get("last_move_tick", step_tick)), 
                last_pos=tuple(nd.get("last_pos", pos_wrapped)),
                vision_range=nd.get("vision_range", 5), 
                smell_radius=nd.get("smell_radius", 3), 
                heading=nd.get("heading", 0), 
                clan_id=nd.get("clan_id", None)
            )
            nxers[a.id] = a
            if a.alive: occupied.add(a.pos)
        
        foods = {}
        for fd in data["foods"]:
            f = Food(id=fd["id"], anchor=wrap_pos(tuple(fd["anchor"])), pos=wrap_pos(tuple(fd["pos"])), alive=fd["alive"], respawn_at_tick=fd["respawn_at_tick"], remaining=int(fd.get("remaining", 25)), progress={int(k): int(v) for k, v in fd.get("progress", {}).items()})
            foods[f.id] = f
        
        if "data_logger" in data and get_data_logger().log_level >= 2:
            logger = get_data_logger()
            saved_level = data["data_logger"].get("metadata", {}).get("log_level", 1)
            logger.set_level(saved_level)
            logger.reset()
            logger.game_metadata['loaded_from'] = path
            
    def schedule_respawn(food: Food, cur_tick: int):
        food.alive = False
        food.respawn_at_tick = cur_tick + FoodRespan * GlobalTimeSteps
        food.progress.clear()
        
    def try_respawns(cur_tick: int):
        if sum(1 for f in foods.values() if f.alive) >= MaxFood: return
        for f in foods.values():
            if not f.alive and f.respawn_at_tick and cur_tick >= f.respawn_at_tick:
                p = find_free(allow_sea=True, allow_land=True, near=f.anchor, search_radius=6)
                if p:
                    f.pos = p; f.alive = True; f.respawn_at_tick = None; f.remaining = 25; f.progress.clear()
                if sum(1 for ff in foods.values() if ff.alive) >= MaxFood: break
                
    def update_all_time_best():
        nonlocal all_time_best
        current_agents = list(nxers.values())
        if not current_agents: return

        for a in current_agents:
            energy_status = a.net.get_energy_status()
            energy_efficiency = energy_status.get('efficiency', 0.0)
            branching_ratio = energy_status.get('branching_ratio', 1.0)
            normalized_food = min(a.stats.food_found / 100.0, 1.0)
            normalized_explored = min(a.stats.explored / 1000.0, 1.0)
            normalized_time = min(a.stats.time_lived_s / 1000.0, 1.0)
            normalized_energy = min(a.stats.energy_efficiency / 10.0, 1.0) if a.stats.energy_efficiency else 0.0
            normalized_sync = min(a.stats.temporal_sync_score / 2.0, 1.0)
            normalized_mates = min(a.stats.mates_performed / 5.0, 1.0)  # NEW in 2.0
            
            a.stats.fitness_score = (
                normalized_food * 0.25 + 
                normalized_explored * 0.15 + 
                normalized_time * 0.20 + 
                normalized_energy * 0.10 + 
                normalized_sync * 0.10 +
                normalized_mates * 0.20  
            )

        categories = {
            'food_found': sorted(current_agents, key=lambda a: a.stats.food_found, reverse=True)[:3],
            'food_taken': sorted(current_agents, key=lambda a: a.stats.food_taken, reverse=True)[:3],
            'explored': sorted(current_agents, key=lambda a: a.stats.explored, reverse=True)[:3],
            'time_lived_s': sorted(current_agents, key=lambda a: a.stats.time_lived_s, reverse=True)[:3],
            'mates_performed': sorted(current_agents, key=lambda a: a.stats.mates_performed, reverse=True)[:3],
            'fitness_score': sorted(current_agents, key=lambda a: a.stats.fitness_score, reverse=True)[:3]
        }

        for stat_name, top_champs in categories.items():
            combined_champs = all_time_best.get(stat_name, []) + top_champs
            combined_champs.sort(key=lambda a: getattr(a.stats, stat_name), reverse=True)
            seen_names = set()
            unique_champs = []
            for champ in combined_champs:
                base_name = _strip_leading_digits(champ.name).lstrip('-') or champ.name
                if base_name not in seen_names:
                    seen_names.add(base_name)
                    unique_champs.append(champ)
            all_time_best[stat_name] = unique_champs[:5]
            
    def rankings():
        all_nxers = list(nxers.values())
        if not all_nxers: return {}
        food_found = sorted(all_nxers, key=lambda a: a.stats.food_found, reverse=True)
        explored = sorted(all_nxers, key=lambda a: a.stats.explored, reverse=True)
        lived = sorted(all_nxers, key=lambda a: a.stats.time_lived_s, reverse=True)
        mated = sorted(all_nxers, key=lambda a: a.stats.mates_performed, reverse=True)
        food_taken = sorted(all_nxers, key=lambda a: a.stats.food_taken, reverse=True)
        fitness = sorted(all_nxers, key=lambda a: a.stats.fitness_score, reverse=True)
        fmt = lambda v: f"{v:.1f}" if isinstance(v, float) else str(v)
        #def format_entry(agent, value): return (f"{agent.name} [Die]" if not agent.alive else agent.name, fmt(value))
        def format_entry(agent, value):
            has_parents = (
                hasattr(agent, "parents")
                and agent.parents is not None
                and any(p is not None for p in agent.parents)
            )

            star = "*" if has_parents else ""
            name = f"{agent.name} [{agent.rounds_survived}{star}]"

            return (
                f"{name} [Die]" if not agent.alive else name,
                fmt(value)
            )

        return {"Food found": [format_entry(a, a.stats.food_found) for a in food_found], "Food taken": [format_entry(a, a.stats.food_taken) for a in food_taken], "World explored": [format_entry(a, a.stats.explored) for a in explored], "Time lived (s)": [format_entry(a, a.stats.time_lived_s) for a in lived], "Mates": [format_entry(a, a.stats.mates_performed) for a in mated], "Fitness": [format_entry(a, a.stats.fitness_score) for a in fitness]}
    
    def _is_parent_child(A: NxEr, B: NxEr) -> bool:
        """Check if A and B share any ancestry (prevents inbreeding)."""
        # Direct parent check (using names)
        if A.name in (B.parents or (None, None)) or B.name in (A.parents or (None, None)):
            return True
        # Full ancestry check - no mating with ANY ancestor (using names)
        if A.name in B.ancestors or B.name in A.ancestors:
            return True
        # Check if they share common ancestors (siblings/cousins)
        if A.ancestors and B.ancestors:
            if set(A.ancestors) & set(B.ancestors):
                return True
        return False

    def can_mate(A: NxEr, B: NxEr, now_tick: int) -> bool:
        if A.id == B.id or not A.alive or not B.alive or A.is_male == B.is_male or A.mating_with is not None or B.mating_with is not None or A.food < 5 or B.food < 5 or _is_parent_child(A, B) or now_tick < A.mate_cooldown_until_tick or now_tick < B.mate_cooldown_until_tick: return False
        return True
        
    def champions_from_last_game() -> List[NxEr]:
        all_agents = list(nxers.values())
        if not all_agents: return []
        by_food = sorted(all_agents, key=lambda a: a.stats.food_found, reverse=True)[:3]
        by_expl = sorted(all_agents, key=lambda a: a.stats.explored, reverse=True)[:3]
        by_lived = sorted(all_agents, key=lambda a: a.stats.time_lived_s, reverse=True)[:3]
        by_fitness = sorted(all_agents, key=lambda a: a.stats.fitness_score, reverse=True)[:3]
        potential_champs = []
        for category_champs in all_time_best.values(): potential_champs.extend(category_champs)
        potential_champs.extend(by_food); potential_champs.extend(by_expl); potential_champs.extend(by_lived); potential_champs.extend(by_fitness)
        seen_names = set()
        unique_champs = []
        for a in potential_champs:
            base_name_with_hyphen = _strip_leading_digits(a.name)
            base_name = base_name_with_hyphen.lstrip('-') or a.name
            if base_name not in seen_names:
                seen_names.add(base_name)
                unique_champs.append(a)
        return unique_champs[:9]
    
    def restart_game_with_champions():
        nonlocal world, nxers, foods, occupied, births_count, deaths_count, effects, game_index, used_colors
        global _current_round, _next_clan_id, _clan_history, _game_id, _next_nxer_id
        
        update_all_time_best()
        champs = champions_from_last_game()
        
        get_data_logger().reset()
        
        game_index += 1
        _current_round = game_index
        _game_id = "".join([str(random.randint(0, 9)) for _ in range(9)])
        effects.clear()
        births_count = 0
        deaths_count = 0
        used_colors = set(RESERVED_COLORS)
        
        world = World(NxWorldSize, NxWorldSea, NxWorldRocks, rnd_seed=None)
        renderer.world = world
        renderer.pan = [world.N * 0.5, world.N * 0.5]
        renderer.zoom = max(2.0, 800.0 / world.N)
        nxers = {}
        occupied = set()
        place_initial_food(min(MaxFood, max(30, MaxFood // 2)))
        next_id = 0
        
        for a in champs:
            # Keep the same name - NO round prefix
            new_name = a.name  # Name stays the same across rounds
            
            net_copy = _rebuild_net_from_dict(a.net.to_dict())
            allow_land, allow_sea = a.can_land, a.can_sea
            pos = find_free(allow_sea=allow_sea, allow_land=allow_land) or (random.randrange(world.N), random.randrange(world.N))
            
            vision = a.vision_range
            smell = a.smell_radius
            heading = random.randint(0, 7)
            
            # Create new clan for champion
            clan_id = _next_clan_id
            _next_clan_id += 1
            _clan_history[clan_id] = {
                'members': {new_name},
                'merged_from': [],
                'created_at_round': _current_round,
                'active': True
            }
            
            nx = NxEr(
                id=_next_nxer_id, 
                name=new_name, 
                color=_rand_color(list(used_colors)), 
                pos=pos, 
                can_land=allow_land, 
                can_sea=allow_sea, 
                net=net_copy, 
                food=float(StartFood * 1.1), 
                is_male=a.is_male, 
                ticks_per_action=max(1, int(GlobalTimeSteps / max(1, net_copy.params.simulation_steps))), 
                stats=NxErStats(), 
                visited=set([pos]), 
                parents=a.parents if hasattr(a, 'parents') else (None, None),
                ancestors=a.ancestors.copy() if hasattr(a, 'ancestors') else [],
                rounds_survived=a.rounds_survived + 1 if hasattr(a, 'rounds_survived') else 1,
                mate_cooldown_until_tick=0, 
                last_move_tick=0, 
                last_pos=pos,
                vision_range=vision, 
                smell_radius=smell, 
                heading=heading, 
                clan_id=clan_id
            )
            used_colors.add(nx.color)
            _next_nxer_id += 1
            nxers[nx.id] = nx
            occupied.add(nx.pos)
        
        # Fill remaining slots with new NxErs
        while len(nxers) < StartingNxErs:
            a = make_nxer()
            nxers[a.id] = a
            occupied.add(a.pos)
        
        print(f"[RESTART] Game #{game_index} started with {len(champs)} champions and {len(nxers) - len(champs)} new NxErs.")

    def get_heading_from_move(dx: int, dy: int, current: int) -> int:
        if dx == 0 and dy == 0: return current
        if dx == -1 and dy == -1: return 0 # NW
        if dx == 0 and dy == -1: return 1  # N
        if dx == 1 and dy == -1: return 2  # NE
        if dx == 1 and dy == 0: return 3   # E
        if dx == 1 and dy == 1: return 4   # SE
        if dx == 0 and dy == 1: return 5   # S
        if dx == -1 and dy == 1: return 6  # SW
        if dx == -1 and dy == 0: return 7  # W
        return current

    FIXED_DT = 1.0 / GlobalTimeSteps
    METABOLIC_RAMP_PER_SEC = 10  # Metabolic Ramp: +1000%/sec idle (atrophy) for the new v2.23 metrics
    accumulator = 0.0
    data_logger = get_data_logger()
    
    try:
        while running:
            frame_dt = renderer.tick(60)
            accumulator += frame_dt
            
            # --- TEST MODE CHECK ---
            if limit_minutes is not None:
                elapsed_minutes = (time.time() - game_start_real_time) / 60.0
                if elapsed_minutes >= limit_minutes:
                    print(f"[TEST MODE] Time limit reached ({limit_minutes} mins). Saving and stopping.")
                    if auto_save and auto_save_prefix: save_state(f"{auto_save_prefix}.json")
                    running = False
                    continue

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: running = False
                elif ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE: running = False
                    elif ev.key == pygame.K_SPACE:
                        if not game_over: paused = not paused; renderer.clear_detail() if not paused else None
                    elif ev.key == pygame.K_s:
                        was_paused = paused; paused = True; save_state(); paused = was_paused
                    elif ev.key == pygame.K_l:
                        candidates = sorted([p for p in os.listdir(os.getcwd()) if p.startswith("nx_world_save_") and p.endswith(".json") and not p.endswith("_log.json")])
                        if candidates: paused = True; load_state(candidates[-1]); paused = False; renderer.clear_detail()
                    elif ev.key == pygame.K_v:
                        renderer.visual_mode = not renderer.visual_mode
                        print(f"[VISUAL MODE] {'ON' if renderer.visual_mode else 'OFF'}")
                elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    btn = renderer.button_clicked(ev.pos)
                    if btn == "playpause":
                        if not game_over: paused = not paused; renderer.clear_detail() if not paused else None
                    elif btn == "save":
                        update_all_time_best()
                        was_paused = paused; paused = True; save_state(); paused = was_paused
                    elif btn == "load":
                        candidates = sorted([p for p in os.listdir(os.getcwd()) if p.startswith("nx_world_save_") and p.endswith(".json") and not p.endswith("_log.json")])
                        if candidates: paused = True; load_state(candidates[-1]); paused = False; renderer.clear_detail()
                    elif btn == "save_best":
                        file_mapping = {'food_found': 'BestFoodFound.json', 'food_taken': 'BestFoodTaken.json', 'explored': 'BestWorldExplorer.json', 'time_lived_s': 'BestTimeLived.json', 'mates_performed': 'BestMates.json', 'fitness_score': 'BestFitness.json'}
                        update_all_time_best()
                        for category, champs in all_time_best.items():
                            if category not in file_mapping: continue
                            filename = file_mapping[category]
                            for champ in champs[:1]: save_nxer_to_file(champ, save_name=filename)
                        print(f"[SAVE BEST] Saved champions to JSON files")
                    elif btn == "exit":
                        if limit_minutes is not None:
                            pygame.quit()
                            sys.exit(0)
                        running = False
                    elif btn == "restart_yes" and game_over:
                        game_over = False; paused = False; restart_game_with_champions(); step_tick = 0; accumulator = 0.0
                        renderer.clear_detail(); game_over_start_time = None; user_declined_restart = False
                    elif btn == "restart_no" and game_over:
                        user_declined_restart = True; running = False
                    else:
                        dbtn = renderer.detail_button_clicked(ev.pos)
                        if dbtn and renderer.selected_nxer_id is not None and renderer.selected_nxer_id in nxers:
                            a = nxers[renderer.selected_nxer_id]
                            if dbtn == "save_nxer": save_nxer_to_file(a, save_name=a.name)
                            elif dbtn == "load_nxer": load_nxer_from_file(spawn_near=a.pos)
                            elif dbtn == "save_nxvizer": save_nxvizer_to_file(a)
                            elif dbtn == "load_nxvizer": load_nxvizer_from_file(spawn_near=a.pos)
                        elif paused and not game_over:
                            clicked_name = renderer.ranking_clicked(ev.pos)
                            if clicked_name:
                                for a in nxers.values():
                                    if a.name == clicked_name: renderer.selected_nxer_id = a.id; break
                            else:
                                if renderer.visual_mode:
                                    mx, my = ev.pos
                                    best_id, best_d = None, 1e9
                                    for a in nxers.values():
                                        if not a.alive: continue
                                        sx, sy = renderer.world_to_screen(a.pos[0], a.pos[1])
                                        d2 = (sx - mx) ** 2 + (sy - my) ** 2
                                        if d2 < best_d: best_d = d2; best_id = a.id
                                    if best_id is not None and best_d <= (14 * 14): renderer.selected_nxer_id = best_id
                                    else: renderer.clear_detail()
                renderer.event_zoom_rotate_pan(ev)
            
            if game_over and game_over_start_time is not None and not user_declined_restart:                
                if time.time() - game_over_start_time > 10: # Auto-restart after 10 sec                 
                    # FIX: Update Hall of Fame statistics BEFORE saving so the file includes this round's champions
                    update_all_time_best()
                    
                    if save_on_round_end:
                    # 1. Autosave the round
                        timestamp = _now_str().replace(":", "-")
                        #game_id = "".join([str(random.randint(0, 9)) for _ in range(10)])
                        filename = f"{_session_id}_{_game_id}_{game_index}_Completed_{timestamp}.json"
                        save_state(filename)
                        print(f"[SAVING ROUND] {game_index} saved as {filename}")
                                        
                    game_over = False; paused = False; restart_game_with_champions(); step_tick = 0; accumulator = 0.0
                    renderer.clear_detail(); game_over_start_time = None; user_declined_restart = False
                    
            renderer.handle_input(frame_dt)
            
            steps_to_process = 0
            if not paused and not game_over:
                while accumulator >= FIXED_DT:
                    steps_to_process += 1
                    accumulator -= FIXED_DT
                    if steps_to_process >= 10:
                        accumulator = 0.0
                        break
            
            for _ in range(steps_to_process):
                step_tick += 1                
                #current_network = next((a.net for a in nxers.values() if a.alive), None) #FIX v2.22
                #data_logger.log_tick(step_tick, current_network, nxers)
                data_logger.log_tick(step_tick, nxers)  #FIX v2.22
                # --- A. Update Game World State & Agent Vitals ---
                effects[:] = [ef for ef in effects if (step_tick - ef['start']) < GlobalTimeSteps]
                for a in nxers.values():
                    if not a.alive: continue
                    a.stats.time_lived_s += FIXED_DT
                    
                    # UPDATED: Metabolic Calculation
                    # 1. Calculate idle seconds
                    idle_seconds = max(0.0, (step_tick - a.last_move_tick) / GlobalTimeSteps)
                    # 2. Calculate Atrophy Factor (1.0 = Base, +1.2 per second idle)                    
                    atrophy_factor = 1.0 + METABOLIC_RAMP_PER_SEC * idle_seconds                    
                    # 3. Apply consumption                    
                    a.food -= 0.01 * FIXED_DT * atrophy_factor
                    
                    # NEW v2.28: Behavioral Modulation Scenarios (Consolidation)
                    # "This made me feel good" (Stability/Satiety) -> serotonin increases
                    current_serotonin = a.net.neuromodulators.get('serotonin', 0.12)
                    current_ach = a.net.neuromodulators.get('acetylcholine', 0.12)
                    
                    if a.food > StartFood * 0.6:
                        # Consolidation scenario: 5-HT and ACh increase.
                        a.net.neuromodulators['serotonin'] = min(2.0, current_serotonin + 0.002)
                        a.net.neuromodulators['acetylcholine'] = min(2.0, current_ach + 0.001)
                    # "This was very risky, difficult, or bad for us" (Starvation risk) -> serotonin decreases
                    elif a.food < StartFood * 0.25:
                        a.net.neuromodulators['serotonin'] = max(0.0, current_serotonin * 0.99)
                        
                    
                    if a.food <= 0 and a.alive:
                        a.alive = False; a.died_ts = time.time(); deaths_count += 1
                        data_logger.log_nxer_event(step_tick, 'died', a.id, {'cause': 'starvation', 'name': a.name})
                        data_logger.update_nxer_stats(a)
                        if a.pos in occupied: occupied.discard(a.pos)
                        push_effect('skull', a.pos)
                for a in nxers.values():
                    if not a.alive: continue
                    if a.mating_with is not None and step_tick >= (a.mating_end_tick or 0):
                        a.mating_with = None; a.mating_end_tick = None
                        a.mate_cooldown_until_tick = max(a.mate_cooldown_until_tick, step_tick + mate_cooldown_ticks)

                # --- B. Gather and Execute Network Updates (Sequential Optimization) ---
                occupant_at = {a.pos: a.id for a in nxers.values() if a.alive}
                food_at = {f.pos: 1 for f in foods.values() if f.alive}

                for a in nxers.values():
                    if not a.alive or a.mating_with is not None: continue
                    
                    # Paper Claim: If Norepinephrine is high, it could increase movement speed
                    # We modulate ticks_per_action (lower = faster) based on NE level
                    ne_level = a.net.neuromodulators.get('norepinephrine', 0.12)
                    base_speed = max(1, int(GlobalTimeSteps / max(1, a.net.params.simulation_steps)))
                    # Apply speed boost if NE is elevated (> 0.25)
                    speed_modifier = max(0.4, 1.0 - (ne_level * 0.5)) if ne_level > 0.25 else 1.0
                    a.ticks_per_action = max(1, int(base_speed * speed_modifier))
                    
                    a.tick_accum += 1
                    if a.tick_accum >= a.ticks_per_action:
                        a.tick_accum = 0
                                                
                        if step_tick < boot_random_until:
                            inputs = [random.choice([-1, 0, 1]) for _ in range(6)]
                        else:
                            # [DOPAMINE UPDATE] Disappointment Dynamics
                            # Paper Claim: "It has to decrease when expectations fail (I look for food but don't find it)"
                            # Check previous inputs: Index 4 (Sight) or 5 (Smell) == 1 means Food was expected.
                            was_expecting_food = (a.last_inputs[4] == 1 or a.last_inputs[5] == 1)
                            # We approximate "didn't find" by checking if food level didn't increase significantly 
                            # (accounting for metabolic decay). Storing _prev_food allows this delta check.
                            if was_expecting_food and getattr(a, '_prev_food', 0) >= a.food:
                                a.net.neuromodulators['dopamine'] = max(0.0, a.net.neuromodulators.get('dopamine', 0.12) - 0.05)
                            
                            # [BEHAVIORAL SCENARIOS] Risk, Hyperactivity, Danger
                            da_level = a.net.neuromodulators.get('dopamine', 0.12)
                            ser_level = a.net.neuromodulators.get('serotonin', 0.12)
                            ach_level = a.net.neuromodulators.get('acetylcholine', 0.12)
                            ne_level = a.net.neuromodulators.get('norepinephrine', 0.12)

                            # Hyperactivity scenario*: High DA but low ACh.
                            is_hyperactive = (da_level > 0.6 and ach_level < 0.3)
                            
                            # Risk-taking: High DA, low serotonin -> increased risk-taking
                            if (da_level > 0.6 and ser_level < 0.4) or is_hyperactive:
                                # Hyperactivity triggers randomness more often
                                chance = 0.25 if is_hyperactive else 0.10
                                if random.random() < chance:
                                    a.heading = random.randint(0, 7)
                            
                            # Danger scenario*: All low (implied by bad health/food) or NA high.
                            # Survival mode: NA increases, ACh increases for focus.
                            if (a.food < StartFood * 0.2 or a.net.all_neurons[0].health < 0.3) or ne_level > 0.7:
                                a.net.neuromodulators['norepinephrine'] = min(2.0, ne_level + 0.05)
                                a.net.neuromodulators['acetylcholine'] = min(2.0, ach_level + 0.02)
                            
                            # 4. Hunger
                            hunger_val = 0
                            if a.food < (StartFood * 0.2): hunger_val = -1
                            
                            # 5. Sight (Line of sight in heading)
                            sight_val = -1
                            seen_neighbors_count = 0
                            seen_different_clan = False
                            vx, vy = DIR_OFFSETS[a.heading]
                            found_obj = False
                            for dist in range(1, a.vision_range + 1):
                                tx, ty = wrap_pos((a.pos[0] + (vx * dist), a.pos[1] + (vy * dist)))
                                t_type = world.terrain((tx, ty))
                                if t_type == T_ROCK: break
                                if (tx, ty) in food_at:
                                    sight_val = 1; found_obj = True; 
                                    # [DOPAMINE UPDATE] Anticipation (Visual Food Cue)
                                    # Paper Claim: "Dopamine – triggered by... visual food cues"
                                    a.net.neuromodulators['dopamine'] = min(2.0, a.net.neuromodulators.get('dopamine', 0.12) + 0.02)
                                    break
                                if (tx, ty) in occupant_at:
                                    other_id = occupant_at[(tx, ty)]
                                    other_a = nxers[other_id]
                                    seen_neighbors_count += 1
                                    if a.clan_id is not None and other_a.clan_id is not None and a.clan_id != other_a.clan_id:
                                        seen_different_clan = True
                                    sight_val = 0 if (other_a.clan_id is not None and other_a.clan_id == a.clan_id) else -1
                                    found_obj = True;
                                    # [DOPAMINE UPDATE] Anticipation (Possible Mating)
                                    if a.is_male != other_a.is_male and can_mate(a, other_a, step_tick):
                                        a.net.neuromodulators['dopamine'] = min(2.0, a.net.neuromodulators.get('dopamine', 0.12) + 0.05)
                                    break
                            if not found_obj: sight_val = -1
                            
                            # Paper Claim: NE activated by high population density and proximity to members of different clans
                            ne_boost = 0.0
                            if seen_neighbors_count >= 3: ne_boost += 0.05
                            if seen_different_clan: ne_boost += 0.10 # "Surprise/Threat"
                            if ne_boost > 0:
                                a.net.neuromodulators['norepinephrine'] = min(2.0, a.net.neuromodulators.get('norepinephrine', 0.12) + ne_boost)
                            
                            # 6. Smell (Square Radius)
                            smell_val = -1
                            found_food_smell = False; found_nxer_smell = False
                            for dy in range(-a.smell_radius, a.smell_radius + 1):
                                for dx in range(-a.smell_radius, a.smell_radius + 1):
                                    if dx == 0 and dy == 0: continue
                                    sx, sy = wrap_pos((a.pos[0] + dx, a.pos[1] + dy))
                                    if (sx, sy) in food_at: found_food_smell = True
                                    if (sx, sy) in occupant_at: found_nxer_smell = True
                            if found_food_smell: 
                                smell_val = 1
                                # [DOPAMINE UPDATE] Anticipation (Olfactory Food Cue)
                                # Paper Claim: "Dopamine – triggered by olfactory... food cues"
                                a.net.neuromodulators['dopamine'] = min(2.0, a.net.neuromodulators.get('dopamine', 0.12) + 0.02)
                            elif found_nxer_smell: smell_val = 0
                            else: smell_val = -1

                            # Combine with physical inputs from previous step
                            inputs = list(a.last_inputs)
                            if len(inputs) < 6: inputs = list(inputs) + [0]*(6-len(inputs))
                            inputs[3] = hunger_val
                            inputs[4] = sight_val
                            inputs[5] = smell_val
                        
                        a.last_inputs = tuple(inputs)
                        # [DOPAMINE UPDATE] Store current food for next tick's disappointment check
                        a._prev_food = a.food
                        
                        # Apply Metabolic Ramp directly to the live object
                        idle_seconds = max(0.0, (step_tick - a.last_move_tick) / GlobalTimeSteps)
                        a.net.params.metabolic_rate *= (1.0 + METABOLIC_RAMP_PER_SEC * idle_seconds)
                        
                        if a.dopamine_boost_ticks > 0:
                            nd = a.net.neuromodulators
                            nd['dopamine'] = max(nd.get('dopamine', 0.12), 0.9); nd['serotonin'] = max(nd.get('serotonin', 0.12), 0.6)
                            a.dopamine_boost_ticks -= 1
                        
                        # --- SIMULATION EXECUTION (Directly on object) ---
                        steps_to_sim = max(1, a.net.params.simulation_steps // GlobalTimeSteps)
                        for _ in range(steps_to_sim):
                            a.net.set_input_states(list(a.last_inputs))
                            a.net.simulate_step()
                        
                        # Capture results directly
                        outs = a.net.get_output_states()
                        energy_status = a.net.get_energy_status()

                        # --- C. Apply Network Outputs ---
                        if energy_status:
                            a.stats.energy_efficiency = energy_status.get('efficiency', a.stats.energy_efficiency)                        
                            a.stats.temporal_sync_score = energy_status.get('temporal_sync', a.stats.temporal_sync_score)
                            normalized_food = min(a.stats.food_found / 100.0, 1.0)
                            normalized_explored = min(a.stats.explored / 1000.0, 1.0)
                            normalized_time = min(a.stats.time_lived_s / 1000.0, 1.0)
                            normalized_energy = min(a.stats.energy_efficiency / 10.0, 1.0) if a.stats.energy_efficiency else 0.0
                            normalized_sync = min(a.stats.temporal_sync_score / 2.0, 1.0)
                            a.stats.fitness_score = normalized_food * 0.3 + normalized_explored * 0.2 + normalized_time * 0.2 + normalized_energy * 0.15 + normalized_sync * 0.15
                            if energy_status.get('efficiency', 0) > 0.5:
                                data_logger.log_plasticity_event(step_tick, 'activity', -1, a.id, energy_status.get('efficiency', 0))
                        
                        o = (outs + [0, 0, 0, 0, 0])[:5]
                        a.last_outputs = tuple(o)
                        data_logger.log_io_pattern(step_tick, a.id, a.last_inputs, tuple(a.last_outputs))
                        O1, O2, O3, O4, O5 = o
                        #GOD MODE DISABLED for moving to avoid zombies v2.23
                        #if O1 == 0 and O2 == 0 and random.random() < 0.4:
                         #   if random.random() < 0.5: O1 = random.choice([-1, 1])
                            #else: O2 = random.choice([-1, 1])
                        #GOD MODE DISABLED for mating v2.23
                        #if O4 == 0 and random.random() < 0.08: O4 = random.choice([-1, 1])
                        
                        dx = -O1; dy = -O2
                        a.heading = get_heading_from_move(dx, dy, a.heading)
                        a._pending_move = (dx, dy, O3, O4, O5)

                # --- D. Resolve Agent Interactions ---
                intents = []; move_target = {}
                for a in nxers.values():
                    if not a.alive: continue
                    pm = getattr(a, "_pending_move", None)
                    std_input = (-1, 0, (1 if world.terrain(a.pos) == T_LAND else (0 if world.terrain(a.pos) == T_SEA else -1)), 0, -1, -1)
                    if pm is None: a.last_inputs = std_input; continue
                    
                    dx, dy, O3, O4, O5 = pm; delattr(a, "_pending_move")
                    
                    # Output 5: Give Food
                    if O5 >= 0 and a.food > StartFood:
                        for ndx in range(-1, 2):
                            for ndy in range(-1, 2):
                                if ndx==0 and ndy==0: continue
                                tx, ty = wrap_pos((a.pos[0]+ndx, a.pos[1]+ndy))
                                if (tx, ty) in occupant_at:
                                    rec = nxers[occupant_at[(tx, ty)]]
                                    if a.clan_id is not None and rec.clan_id == a.clan_id:
                                        if rec.food < StartFood:
                                            amt = 5.0 if O5 == 1 else 2.0
                                            if a.food > amt:
                                                a.food -= amt
                                                rec.food += amt
                    
                    if dx == 0 and dy == 0: a.last_inputs = std_input; continue
                    tx, ty = wrap_pos((a.pos[0] + dx, a.pos[1] + dy))
                    intents.append((a.id, (tx, ty), O3, O4)); move_target[a.id] = (tx, ty)

                by_pos: Dict[Tuple[int, int], List[Tuple[int, int, int]]] = {}
                for aid, tgt, O3, O4 in intents: by_pos.setdefault(tgt, []).append((aid, O3, O4))
                
                valid_intents = []
                for tgt, lst in by_pos.items():
                    tt = world.terrain(tgt)
                    if tt == T_ROCK:
                        for (aid, _, _) in lst: 
                            prev = list(nxers[aid].last_inputs)
                            prev[0], prev[1], prev[2] = -1, 0, -1
                            nxers[aid].last_inputs = tuple(prev)
                        continue
                    for (aid, O3, O4) in lst:
                        a = nxers[aid]
                        origin_terrain = world.terrain(a.pos)
                        is_seashore_crossing = (origin_terrain == T_LAND and tt == T_SEA) or (origin_terrain == T_SEA and tt == T_LAND)
                        if not is_seashore_crossing:
                            if tt == T_LAND and not a.can_land: 
                                prev = list(a.last_inputs); prev[0:3] = [-1, 0, 1]; a.last_inputs = tuple(prev)
                                continue
                            if tt == T_SEA and not a.can_sea: 
                                prev = list(a.last_inputs); prev[0:3] = [-1, 0, 0]; a.last_inputs = tuple(prev)
                                continue
                        valid_intents.append((tgt, aid, O3, O4, tt))

                # Handle Head-on Swaps
                handled_swap = set()
                for aid, tgt, O3, O4 in intents:
                    if aid in handled_swap: continue
                    occ = occupant_at.get(tgt)
                    if occ is None: continue
                    A = nxers[aid]; B = nxers[occ]
                    if A.id == B.id: continue
                    
                    prevA = list(A.last_inputs); prevA[0:3] = [-1, 1, (1 if world.terrain(tgt)==T_LAND else 0)]; A.last_inputs = tuple(prevA)
                    prevB = list(B.last_inputs); prevB[0:3] = [-1, 1, (1 if world.terrain(A.pos)==T_LAND else 0)]; B.last_inputs = tuple(prevB)
                    
                    # NEW v2.27: Serotonin Behavioral Modulation
                    ser_A = A.net.neuromodulators.get('serotonin', 0.12)
                    ser_B = B.net.neuromodulators.get('serotonin', 0.12)
                    
                    # High Serotonin increases mating probability (Maintenance/Stability)
                    mating_boost_A = 0.05 if ser_A > 0.6 else 0.0
                    mating_boost_B = 0.05 if ser_B > 0.6 else 0.0

                    if O4 == 1 or random.random() < (0.03 + mating_boost_A): 
                        A.mating_intent_until_tick = step_tick + 6 * GlobalTimeSteps
                    if getattr(B, "_last_O4", 0) == 1 or random.random() < (0.03 + mating_boost_B): 
                        B.mating_intent_until_tick = step_tick + 3 * GlobalTimeSteps
                    if (A.mating_intent_until_tick > step_tick and B.mating_intent_until_tick > step_tick and can_mate(A, B, step_tick)):
                        A.mating_with = B.id; B.mating_with = A.id; dur = max(A.net.params.simulation_steps, B.net.params.simulation_steps)
                        A.mating_end_tick = step_tick + dur; B.mating_end_tick = step_tick + dur; A.food -= 1; B.food -= 1
                        push_effect('heart', A.pos); spawn_child(A, B, A.pos)
                        data_logger.log_nxer_event(step_tick, 'mating', A.id, {'partner': B.id})
                    
                    # Stealing Logic (Family Check)
                    same_clan = (A.clan_id is not None and B.clan_id is not None and A.clan_id == B.clan_id)
                    
                    # [DOPAMINE UPDATE] Novelty / Interaction with other clans
                    # Paper Claim: "Higher levels favor... interaction with other clans."
                    # If Dopamine is high (Novelty Seeking), suppress the hostile stealing logic for different clans
                    is_novelty_seeking = (A.net.neuromodulators.get('dopamine', 0.12) > 0.7)
                    
                    if not same_clan and not is_novelty_seeking:
                        # NEW v2.27: Impulse vs Serenity
                        # "With low serotonin... increases probability of stealing"
                        # "With high serotonin, I don't steal"
                        impulse_to_steal = 0.4 if ser_A < 0.3 else 0.0
                        is_serene = (ser_A > 0.6 and A.food > 5.0)
                        
                        if not is_serene:
                            if (O4 == -1 or O3 == -1 or (A.food < 2 and B.food > 3 and random.random() < (0.3 + impulse_to_steal))) and B.food > 0:
                                data_logger.log_nxer_event(step_tick, 'stealing_attempt', A.id, {'target': B.id, 'serotonin': ser_A})
                                B.food -= 1; A.food += 1; A.stats.food_taken += 1
                                # Stealing is risky/conflict -> serotonin drop
                                A.net.neuromodulators['serotonin'] = max(0.0, ser_A * 0.98)
                                
                                # Stress scenario*: High DA (Reward), very high NA (Stress).
                                A.net.neuromodulators['dopamine'] = min(2.0, A.net.neuromodulators.get('dopamine', 0.12) + 0.1)
                                A.net.neuromodulators['norepinephrine'] = min(2.0, A.net.neuromodulators.get('norepinephrine', 0.12) + 0.2)
                            
                    A._last_O4 = O4; handled_swap.add(aid); handled_swap.add(occ)

                # Move Resolutions
                winners = []; tgt_map: Dict[Tuple[int, int], List[Tuple[int, int, int, int]]] = {}
                for tgt, aid, O3, O4, tt in valid_intents: tgt_map.setdefault(tgt, []).append((aid, O3, O4, tt))
                
                for tgt, lst in tgt_map.items():
                    fid = -1
                    for f in foods.values():
                        if f.alive and f.pos == tgt: fid = f.id; break
                    
                    if fid != -1:
                        f = foods[fid]
                        for (aid, O3, O4, tt) in lst:
                            a = nxers[aid]
                            prev = list(a.last_inputs); prev[0:3] = [1, 0, (1 if tt == T_LAND else 0)]; a.last_inputs = tuple(prev)
                            if f.remaining > 0:
                                f.progress[aid] = f.progress.get(aid, 0) + 1
                                f.remaining -= 1; a.food += 1.0; a.stats.food_found += 1.0
                                a.food -= 0.1
                                                                
                                # [DOPAMINE UPDATE] Surprise vs Expectation
                                # Paper Claim: "strongly by unexpected positive surprise"
                                # Check if we saw (4) or smelled (5) food in last inputs
                                expected = (a.last_inputs[4] == 1 or a.last_inputs[5] == 1)
                                surprise_multiplier = 2.0 if not expected else 1.0
                                base_reward = a.net.params.dopamine_reward_magnitude
                                
                                a.net.neuromodulators['dopamine'] = min(
                                    2.0,
                                    a.net.neuromodulators['dopamine'] + (base_reward * surprise_multiplier)
                                )
                                
                                # Exploration scenario: If something works, DA increases and ACh increases.
                                a.net.neuromodulators['acetylcholine'] = min(
                                    2.0,
                                    a.net.neuromodulators.get('acetylcholine', 0.12) + 0.05
                                )
                                
                                # Paper Claim: NE activated by proximity to food after a rise in dopamine
                                if a.net.neuromodulators['dopamine'] > 0.3:
                                    a.net.neuromodulators['norepinephrine'] = min(2.0, a.net.neuromodulators.get('norepinephrine', 0.12) + 0.1)
                                
                                if a.food <= 0 and a.alive:
                                    a.alive = False; a.died_ts = time.time(); deaths_count += 1
                                    data_logger.log_nxer_event(step_tick, 'died', a.id, {'cause': 'harvesting_exhaustion', 'name': a.name})
                                    data_logger.update_nxer_stats(a)
                                    if a.pos in occupied: occupied.discard(a.pos)
                                    push_effect('skull', a.pos)
                        if f.remaining <= 0:
                            winner_id = None
                            if f.progress:
                                max_prog = max(f.progress.values())
                                candidates = [k for k, v in f.progress.items() if v == max_prog]
                                winner_id = random.choice(candidates)
                            wnx = nxers.get(winner_id) if winner_id is not None else None
                            if wnx and wnx.alive:
                                if wnx.pos in occupied: occupied.discard(wnx.pos)
                                wnx.pos = f.pos
                                occupied.add(wnx.pos); wnx.visited.add(wnx.pos); wnx.stats.explored = len(wnx.visited)
                            schedule_respawn(f, step_tick)
                        continue

                    occ = occupant_at.get(tgt)
                    if occ is not None:
                        for (aid, O3, O4, tt) in lst:
                            if aid in handled_swap: continue 
                            a = nxers[aid]; b = nxers.get(occ)
                            if not b: continue
                            prev = list(a.last_inputs); prev[0:3] = [-1, 1, (1 if tt == T_LAND else 0)]; a.last_inputs = tuple(prev)
                            if not b.alive or a.id == b.id: continue
                            if (a.mating_intent_until_tick > step_tick and b.mating_intent_until_tick > step_tick and can_mate(a, b, step_tick)):
                                a.mating_with = b.id; b.mating_with = a.id
                                dur = max(a.net.params.simulation_steps, b.net.params.simulation_steps)
                                a.mating_end_tick = step_tick + dur; b.mating_end_tick = step_tick + dur
                                a.food -= 1; b.food -= 1; push_effect('heart', tgt); spawn_child(a, b, tgt)
                                data_logger.log_nxer_event(step_tick, 'mating', a.id, {'partner': b.id})
                            same_clan = (a.clan_id is not None and b.clan_id is not None and a.clan_id == b.clan_id)
                            if not same_clan:
                                ser_a = a.net.neuromodulators.get('serotonin', 0.12)
                                impulse_to_steal = 0.4 if ser_a < 0.3 else 0.0
                                is_serene = (ser_a > 0.6 and a.food > 5.0)
                                
                                if not is_serene:
                                    if (O4 == -1 or O3 == -1 or (a.food < 2 and b.food > 3 and random.random() < (0.3 + impulse_to_steal))) and b.food > 0:
                                        data_logger.log_nxer_event(step_tick, 'stealing_attempt', a.id, {'target': b.id, 'serotonin': ser_a})
                                        b.food -= 1; a.food += 1; a.stats.food_taken += 1
                                        a.net.neuromodulators['serotonin'] = max(0.0, ser_a * 0.98)
                                        
                            a._last_O4 = O4
                        continue
                    
                    contenders = lst[:]
                    want = contenders
                    if len(want) > 1:
                        # Paper Claim: NE activated by competition with others for food or offspring
                        # Multiple agents wanting the same tile implies direct competition
                        for (aid_comp, _, _, _) in want:
                             nxers[aid_comp].net.neuromodulators['norepinephrine'] = min(2.0, nxers[aid_comp].net.neuromodulators.get('norepinephrine', 0.12) + 0.2)
                        
                        for (aid, O3, O4, tt) in want:
                            giver = nxers[aid]
                            if O3 == 1 and giver.food > 1.0:
                                slowest = max(want, key=lambda it: nxers[it[0]].ticks_per_action)[0]
                                if slowest != aid:
                                    giver.food -= 1.0; nxers[slowest].food += 1.0
                        want.sort(key=lambda it: nxers[it[0]].ticks_per_action)
                        top = [w for w in want if nxers[w[0]].ticks_per_action == nxers[want[0][0]].ticks_per_action]
                        winner = random.choice(top)
                        winners.append((winner[0], tgt, winner[3]))
                        for (aid, O3, O4, tt) in want:
                            if aid == winner[0]: continue
                            a = nxers[aid]
                            prev = list(a.last_inputs); prev[0:3] = [-1, 1, (1 if tt == T_LAND else 0)]; a.last_inputs = tuple(prev)
                            a._last_O4 = O4
                    elif want:
                        (aid, O3, O4, tt) = want[0]
                        winners.append((aid, tgt, tt))
                        nxers[aid]._last_O4 = O4

                for (aid, tgt, tt) in winners:
                    a = nxers.get(aid)
                    if not a or not a.alive: continue
                    if tgt in occupied:
                        prev = list(a.last_inputs); prev[0:3] = [-1, 1, (1 if tt == T_LAND else 0)]; a.last_inputs = tuple(prev)
                    else:
                        if a.pos in occupied: occupied.discard(a.pos)
                        if a.pos != tgt:
                            a.last_move_tick = step_tick; a.last_pos = a.pos
                        a.pos = tgt
                        occupied.add(a.pos); a.visited.add(a.pos); a.stats.explored = len(a.visited)
                        prev = list(a.last_inputs); prev[0:3] = [-1, 0, (1 if tt == T_LAND else 0)]; a.last_inputs = tuple(prev)
                        a.food -= 0.1
                        if a.food <= 0 and a.alive:
                            a.alive = False; a.died_ts = time.time(); deaths_count += 1
                            data_logger.log_nxer_event(step_tick, 'died', a.id, {'cause': 'movement_exhaustion', 'name': a.name})
                            data_logger.update_nxer_stats(a)
                            if a.pos in occupied: occupied.discard(a.pos)
                            push_effect('skull', a.pos)
                
                try_respawns(step_tick)

            alive_count = sum(1 for a in nxers.values() if a.alive)
            
            # --- TEST MODE AUTO-SAVE on DEATH ---
            if alive_count == 0 and auto_save and auto_save_prefix and limit_minutes is not None:
                print("[TEST MODE] All NxErs died. Saving and stopping.")
                save_state(f"{auto_save_prefix}.json")
                running = False
                continue

            if alive_count == 0 and not game_over:
                paused = True; game_over = True; game_over_start_time = time.time(); user_declined_restart = False
            best_scores = {}
            title_to_stat = {"Food found": "food_found", "Food taken": "food_taken", "World explored": "explored", "Time lived (s)": "time_lived_s", "Mates": "mates_performed", "Fitness": "fitness_score"}
            for title, stat_name in title_to_stat.items():
                all_candidates = list(nxers.values())
                if stat_name in all_time_best: all_candidates.extend(all_time_best[stat_name])
                if not all_candidates: best_scores[title] = 0
                else: best_scores[title] = max(getattr(a.stats, stat_name) for a in all_candidates)
            renderer.draw_world(foods, nxers, rankings(), alive_count, deaths_count, births_count, paused, effects, step_tick, GlobalTimeSteps, game_over, game_index, best_scores)
            # Update NxEr stats in logger
            for a in nxers.values():
                data_logger.update_nxer_stats(a)
        
        # --- FORCE FULL SAVE AT END OF GAME ---        
        if auto_save_prefix:
            final_save_name = f"{auto_save_prefix}_Final.json"
            save_state(final_save_name)
        
        # --- GENERATE FINAL STATS ---        
        update_all_time_best()
        active_agents = [a for a in nxers.values() if a.alive]
        
        game_stats = {
            "total_ticks": step_tick,
            "total_time_simulated_seconds": step_tick * (1.0 / GlobalTimeSteps) * GlobalTimeSteps, # Approximation
            "births": births_count,
            "deaths": deaths_count,
            "survivors": len(active_agents),
            "reason_end": "timeout" if limit_minutes and (time.time() - game_start_real_time) / 60.0 >= limit_minutes else "extinction/manual",
            "hall_of_fame": {}
        }

        # Extract serializable data from the internal all_time_best dictionary
        # We only save the name and score to keep the JSON readable
        for category, champs in all_time_best.items():
            game_stats["hall_of_fame"][category] = [
                {
                    "name": c.name,
                    "score": getattr(c.stats, category, 0.0),
                    "is_male": c.is_male
                } 
                for c in champs
            ]
            
        return game_stats

    except Exception as ex:
        print("Fatal error:", ex)
        import traceback; traceback.print_exc()
        return {"error": str(ex), "status": "crashed"}
    finally:
        pygame.quit()

def run_config_screen() -> Optional[Dict[str, any]]:
    """
    Displays a pre-simulation configuration screen using Pygame, allowing the user
    to adjust key parameters with sliders before starting the game.
    """
    pygame.init()
    screen = pygame.display.set_mode((1920, 1080), pygame.RESIZABLE)
    pygame.display.set_caption("Neuraxon Game Of Life v 2.2 (Research Version) By David Vivancos & Dr Jose Sanchez for Qubic Science - Configuration")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 16); title_font = pygame.font.SysFont("consolas", 32, bold=True)
    # Define the parameters that will be configurable via sliders.
    param_specs = [("World Size", 30, 150, 40, True, lambda x: x), ("Sea Percentage", 20, 80, 55, True, lambda x: x / 100.0), ("Rock Percentage", 1, 10, 2, True, lambda x: x / 100.0),
     ("Starting NxErs", 1, 100, 30, True, lambda x: x), ("Food Sources", 25, 300, 50, True, lambda x: x), ("Food Respawn", 200, 600, 400, True, lambda x: x),
     ("Start Food", 25, 200, 25, True, lambda x: float(x)), ("Max Neurons", 5, 50, 50, True, lambda x: x), ("Global Time Steps", 30, 90, 60, True, lambda x: x),
      ("Mate Cooldown (sec)", 6, 20, 12, True, lambda x: x), ("Log Level (1-3)", 1, 3, 3, True, lambda x: x)]
    screen_width, screen_height = screen.get_size()
    slider_container_width = 700; slider_width = 600
    slider_start_x = (screen_width - slider_container_width) // 2 + (slider_container_width - slider_width) // 2
    start_y = 130; slider_height = 50
    sliders = []
    for i, (label, min_val, max_val, default_val, is_int, _) in enumerate(param_specs):
        rect = pygame.Rect(slider_start_x, start_y + i * slider_height, slider_width, 20)
        sliders.append(Slider(rect, min_val, max_val, default_val, label, is_int))
    
    play_button_width = 250; play_button_height = 50
    play_button_x = (screen_width - play_button_width) // 2
    
    # Test Mode Sliders
    test_slider_y_start = 800
    
    # Start Game Button (above test sliders)
    play_button_y = 700
    play_button_rect = pygame.Rect(play_button_x, play_button_y, play_button_width, play_button_height)
    
    # Test Mode Button (below test sliders)
    test_button_rect = pygame.Rect(play_button_x, test_slider_y_start + slider_height + 70, play_button_width, play_button_height)
    test_games_slider_rect = pygame.Rect(slider_start_x, test_slider_y_start, slider_width, 20)
    test_time_slider_rect = pygame.Rect(slider_start_x, test_slider_y_start + slider_height, slider_width, 20)
    test_games_slider = Slider(test_games_slider_rect, 1, 50, 10, "Test Mode: Number of Games", True)
    test_time_slider = Slider(test_time_slider_rect, 1, 60, 20, "Test Mode: Max Minutes per Game", True)
    test_sliders = [test_games_slider, test_time_slider]
    
    running = True
    while running:
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return None
            for slider in sliders: slider.handle_event(event)
            for slider in test_sliders: slider.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if play_button_rect.collidepoint(event.pos):
                    params = {}
                    for i, slider in enumerate(sliders): # Collect values from all sliders.
                        raw_value = slider.get_value()
                        conversion_func = param_specs[i][5]
                        param_name = ["NxWorldSize", "NxWorldSea", "NxWorldRocks", "StartingNxErs", "MaxFood", "FoodRespan", "StartFood", "MaxNeurons", "GlobalTimeSteps", "MateCooldownSeconds", "LogLevel"][i]
                        params[param_name] = conversion_func(raw_value)
                    log_level = params.pop("LogLevel", 2)
                    set_data_logger_level(log_level)
                    return params # Return the dictionary of parameters to the main function.
                elif test_button_rect.collidepoint(event.pos):
                    # Trigger Test Mode with slider values
                    games_count = int(test_games_slider.get_value())
                    max_minutes = int(test_time_slider.get_value())
                    TestMode(games_count=games_count, max_minutes=max_minutes)
                    return None # Exit config screen after test mode finishes

        screen.fill((15, 15, 18))
        title_surf = title_font.render("Neuraxon Game Of Life 2.0 (Research Version) - World Configuration", True, (235, 235, 240))
        screen.blit(title_surf, (screen.get_width() // 2 - title_surf.get_width() // 2, 50))
        for slider in sliders: slider.draw(screen, font)
        #instr_text = font.render("Adjust parameters with sliders, then click 'Start Game'", True, (180, 180, 180))
        #screen.blit(instr_text, (screen.get_width() // 2 - instr_text.get_width() // 2, 720))
        
        # Draw Play Button (above test sliders)
        pygame.draw.rect(screen, (35, 180, 60), play_button_rect, border_radius=8)
        pygame.draw.rect(screen, (60, 220, 90), play_button_rect, 2, border_radius=8)
        play_text = font.render("Start Game", True, (255, 255, 255))
        screen.blit(play_text, (play_button_rect.x + (play_button_rect.width - play_text.get_width()) // 2, play_button_rect.y + (play_button_rect.height - play_text.get_height()) // 2))
        
        # Draw Test Mode Sliders
        for slider in test_sliders: slider.draw(screen, font)
        
        # Draw Test Mode Button
        pygame.draw.rect(screen, (180, 60, 35), test_button_rect, border_radius=8)
        pygame.draw.rect(screen, (220, 90, 60), test_button_rect, 2, border_radius=8)
        games_count = int(test_games_slider.get_value())
        max_minutes = int(test_time_slider.get_value())
        #test_text = font.render(f"Run Test Mode ({games_count} Games, {max_minutes} min/game)", True, (255, 255, 255))
        test_text = font.render(f"Run Test Mode", True, (255, 255, 255))
        screen.blit(test_text, (test_button_rect.x + (test_button_rect.width - test_text.get_width()) // 2, test_button_rect.y + (test_button_rect.height - test_text.get_height()) // 2))
        
        pygame.display.flip()

def TestMode(games_count: int = 2, max_minutes: int = 1):
    """
    Generates random configurations and runs sequential simulations (Test Mode).
    Saves config + results AFTER the game finishes.
    """
    print(f"--- STARTING TEST MODE: {games_count} Games, Max {max_minutes} mins each ---")
    
    history_configs = []
    
    def generate_unique_config():
        for _ in range(1000):           
            params = {

                 "NxWorldSize": random.randint(20, 150),
                 "NxWorldSea": random.uniform(0.25, 0.75),   
                 "NxWorldRocks": random.uniform(0.01, 0.25), 
                 "StartingNxErs": random.randint(2, 100),
                 "MaxNxErs": 175,
                 "MaxFood": random.randint(50, 400),
                 "FoodRespan": random.randint(100, 500), 
                 "StartFood": random.randint(50, 400),
                 "MaxNeurons": random.randint(3, 50), 
                 "GlobalTimeSteps": random.randint(20, 120), 
                 "MateCooldownSeconds": random.randint(5, 25), 
                "limit_minutes": 20,
                "auto_save": True,
                "auto_start": True
                 
            }

            sig = tuple(sorted(params.items()))
            if sig not in history_configs:
                history_configs.append(sig)
                return params
        return None

    for i in range(1, games_count + 1):
        config = generate_unique_config()
        if not config:
            print("Could not generate unique configuration. Stopping Test Mode.")
            break
            
        rnd_id = "".join([str(random.randint(0, 9)) for _ in range(10)])
        ts = _now_str().replace(":", "-")
        base_name = f"TestGame_{i}_{rnd_id}_{ts}"
        
        print(f"\n[TEST MODE] Starting Game {i}/{games_count} -> ID: {rnd_id}")
        
        # Pass the filename prefix so GameOfLife knows what to name the full save file
        config["auto_save_prefix"] = base_name
        
        game_stats = {}
        try:
            # Run the Game and capture the return value (Final Stats)
            game_stats = GameOfLife(**config)
        except Exception as e:
            print(f"[TEST MODE] Game {i} crashed: {e}")
            game_stats = {"error": str(e), "status": "crashed"}
            import traceback; traceback.print_exc()
            
        # --- SAVE CONFIG + STATS ---
        config_filename = f"{base_name}_config.json"
        
        # Prepare the data object
        final_report = {
            "game_id": rnd_id,
            "timestamp": ts,
            "configuration": config.copy(),
            "results": game_stats
        }
        
        # Clean up internal control flags from the saved config for clarity
        for k in ["limit_minutes", "auto_save", "auto_start", "auto_save_prefix"]:
            if k in final_report["configuration"]: 
                del final_report["configuration"][k]
        
        with open(_safe_path(config_filename), "w") as f:
            json.dump(final_report, f, indent=4)
            
        print(f"[TEST MODE] Game {i} finished. Config & Stats saved: {config_filename}")
        
        # Small delay to allow cleanup before next round
        time.sleep(1.0)

    print("--- TEST MODE COMPLETE ---")

if __name__ == "__main__":
    # First, show the configuration screen to the user.
    config_params = run_config_screen()
    # If the user confirmed the settings start the main simulation.
    if config_params is not None:
        GameOfLife(**config_params)
    else:
        # If the user closed the configuration window, exit gracefully.
        print("Game cancelled by user.")
        pygame.quit()
        sys.exit(0)

# Neuraxon Game of Life Game Loop
# Based on the Paper "Neuraxon: A New Neural Growth & Computation Blueprint" by David Vivancos https://vivancos.com/  & Dr. Jose Sanchez  https://josesanchezgarcia.com/ for Qubic Science https://qubic.org/
# https://www.researchgate.net/publication/397331336_Neuraxon
# Play the Lite Version of the Game of Life at https://huggingface.co/spaces/DavidVivancos/NeuraxonLife
import os
import sys
import time
import json
import math
import random
from collections import deque
from dataclasses import asdict
from typing import Dict, List, Tuple, Optional, Set

import pygame
import numpy as np

# Import Configuration and Globals
import config
from config import (
    NetworkParameters, RESERVED_COLORS,
    T_SEA, T_LAND, T_ROCK,
    _generate_session_id, _get_next_global_name, _reset_session_globals
)

# Import Utilities
from utils import (
    _clamp, _rand_color, _now_str, _safe_path, 
    _pick_save_file, _pick_open_file, _strip_leading_digits,
    safe_json_save  
)

# Import Logging
from logger import get_data_logger

# Import Neural Core
from neuraxon.network import NeuraxonNetwork, _rebuild_net_from_dict
from neuraxon.genetics import Inheritance

# Import Simulation Entities & World
from simulation.world import World
from simulation.entities import NxEr, NxErStats, Food

# Import UI
from ui.renderer import Renderer


def GameOfLife(NxWorldSize: int = 100, NxWorldSea: float = 0.60, NxWorldRocks: float = 0.05, 
               StartingNxErs: int = 30, MaxNxErs: int = 400, MaxFood: int = 300, 
               FoodRespan: int = 600, StartFood: float = 40.0, MaxNeurons: int = 12, 
               GlobalTimeSteps: int = 60, TextureLand: Optional[str] = None, 
               TextureSea: Optional[str] = None, TextureRock: Optional[str] = None, 
               TextureFood: Optional[str] = None, TextureNxEr: Optional[str] = None, 
               TexturesAlpha: float = 0.7, MateCooldownSeconds: int = 10, 
               random_seed: Optional[int] = None, limit_minutes: Optional[int] = None, 
               auto_save: bool = False, auto_save_prefix: str = "", 
               auto_start: bool = False, save_on_round_end: bool = True):
    """
    The main function that initializes and runs the entire Game of Life simulation.
    """
    # Clamp parameters
    NxWorldSize = _clamp(int(NxWorldSize), 30, 1000)
    NxWorldSea = _clamp(float(NxWorldSea), 0.0, 0.95)
    NxWorldRocks = _clamp(float(NxWorldRocks), 0.0, 0.9)
    StartingNxErs = _clamp(int(StartingNxErs), 1, 150)
    MaxNxErs = _clamp(int(MaxNxErs), 100, 180) # Clamped atm to 180 to prevent the exponential in compute
    MaxFood = _clamp(int(MaxFood), 10, 1000)
    FoodRespan = _clamp(int(FoodRespan), 10, 3000)
    StartFood = _clamp(float(StartFood), 10.0, 250.0)
    MaxNeurons = _clamp(int(MaxNeurons), 1, 50)
    GlobalTimeSteps = _clamp(int(GlobalTimeSteps), 30, 300)
    MateCooldownSeconds = _clamp(int(MateCooldownSeconds), 0, 300)
    
    if random_seed is not None: random.seed(int(random_seed))
    
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
    if config._session_id is None:
        _reset_session_globals()
    config._current_round = game_index
    config._game_id = "".join([str(random.randint(0, 9)) for _ in range(9)])

    all_time_best: Dict[str, List[NxEr]] = {'food_found': [], 'food_taken': [], 'explored': [], 'time_lived_s': [], 'mates_performed': [], 'fitness_score': []}
    
    # --- CLAN & DIRECTION GLOBALS ---
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
        p.firing_threshold_excitatory = random.uniform(0.1, 0.25)
        p.firing_threshold_inhibitory = random.uniform(-2.0, -0.5)
        p.adaptation_rate = random.uniform(0.0, 0.2)        
        p.spontaneous_firing_rate = random.uniform(0.02, 0.08)
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
        p.w_fast_init_min = random.uniform(0.1, 0.3)
        p.w_fast_init_max = random.uniform(0.8, 1.2)
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
        p.synapse_death_prob = random.uniform(0.0001, 0.0005)
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
        
        idx = config._next_nxer_id
        config._next_nxer_id += 1
        
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
        clan_id = config._next_clan_id
        config._next_clan_id += 1
        config._clan_history[clan_id] = {
            'members': {name},
            'merged_from': [],
            'created_at_round': config._current_round,
            'active': True
        }
        
        nx = NxEr(
            id=idx, 
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
        
        if len(nxers) >= MaxNxErs: return None
        child_id = config._next_nxer_id
        config._next_nxer_id += 1
        child_net = Inheritance(A, B)
        
        # Terrain inheritance logic
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
        new_clan_id = config._next_clan_id
        config._next_clan_id += 1
        
        old_clan_a = A.clan_id
        old_clan_b = B.clan_id
        
        # Collect all members from both clans
        all_members = set()
        merged_from = []
        
        if old_clan_a is not None and old_clan_a in config._clan_history:
            all_members.update(config._clan_history[old_clan_a]['members'])
            merged_from.append(old_clan_a)
            config._clan_history[old_clan_a]['active'] = False
            
        if old_clan_b is not None and old_clan_b in config._clan_history and old_clan_b != old_clan_a:
            all_members.update(config._clan_history[old_clan_b]['members'])
            merged_from.append(old_clan_b)
            config._clan_history[old_clan_b]['active'] = False
        
        child_name = _get_next_global_name()  # Get name early so we can use it
        all_members.add(child_name)  # Use name instead of ID
        
        # Create new clan
        config._clan_history[new_clan_id] = {
            'members': all_members,
            'merged_from': merged_from,
            'created_at_round': config._current_round,
            'active': True
        }
        
        # Update all members of both old clans to new clan
        for member_id in all_members:
            if member_id in nxers and nxers[member_id].alive:
                nxers[member_id].clan_id = new_clan_id
        
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
        child.food = min(transfer * 8, max_limit)     
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
        if config._session_id is None:
            config._session_id = _generate_session_id()
        default = save_name or f"{config._session_id}_nxer_{a.name}_{_now_str()}.json"
        path = _pick_save_file(default)
        if not path: return
        data = {"meta": {"created": _now_str(), "type": "NxEr", "session_id": config._session_id, "game_id": config._game_id}, "nxer": {"id": a.id, "name": a.name, "color": a.color, "pos": a.pos, "can_land": a.can_land, "can_sea": a.can_sea, 
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
        if config._session_id is None:
            config._session_id = _generate_session_id()
        
        # Include session ID in filename
        name = name or f"{config._session_id}_nx_world_save_{_now_str()}.json"
        
        data = {
            "meta": {
                "created": _now_str(), 
                "step_tick": step_tick, 
                "GlobalTimeSteps": GlobalTimeSteps, 
                "births_count": births_count, 
                "deaths_count": deaths_count, 
                "game_index": game_index,
                "session_id": config._session_id,
                "game_id": config._game_id,
                "global_name_counter": config._global_name_counter,
                "used_names": list(config._used_names),
                "next_clan_id": config._next_clan_id,
                "current_round": config._current_round,
                "next_nxer_id": config._next_nxer_id
            },
            "clan_history": {str(k): {
                'members': list(v['members']),
                'merged_from': v['merged_from'],
                'created_at_round': v['created_at_round'],
                'active': v['active']
            } for k, v in config._clan_history.items()},
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
        
        with open(path, "r") as f: data = json.load(f)
        
        step_tick = data["meta"]["step_tick"]
        births_count = int(data["meta"].get("births_count", 0))
        deaths_count = int(data["meta"].get("deaths_count", 0))
        game_index = int(data["meta"].get("game_index", 1))
        
        # Restore global tracking variables
        config._session_id = data["meta"].get("session_id", _generate_session_id())
        config._game_id = data["meta"].get("game_id", "".join([str(random.randint(0, 9)) for _ in range(9)]))
        config._global_name_counter = data["meta"].get("global_name_counter", 0)
        config._used_names = set(data["meta"].get("used_names", []))
        config._next_clan_id = data["meta"].get("next_clan_id", 1)
        config._current_round = data["meta"].get("current_round", 1)
        config._next_nxer_id = data["meta"].get("next_nxer_id", max((n["id"] for n in data["nxers"]), default=0) + 1)
        
        # Restore clan history
        if "clan_history" in data:
            config._clan_history = {}
            for k, v in data["clan_history"].items():
                config._clan_history[int(k)] = {
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
        
        update_all_time_best()
        champs = champions_from_last_game()
        
        get_data_logger().reset()
        
        game_index += 1
        config._current_round = game_index
        config._game_id = "".join([str(random.randint(0, 9)) for _ in range(9)])
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
            clan_id = config._next_clan_id
            config._next_clan_id += 1
            config._clan_history[clan_id] = {
                'members': {new_name},
                'merged_from': [],
                'created_at_round': config._current_round,
                'active': True
            }
            
            nx = NxEr(
                id=config._next_nxer_id, 
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
            config._next_nxer_id += 1
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
                        filename = f"{config._session_id}_{config._game_id}_{game_index}_Completed_{timestamp}.json"
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
                data_logger.log_tick(step_tick, nxers)
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
                        #a.net.neuromodulators['acetylcholine'] = min(2.0, current_ach + 0.001) +    # ACh should be novelty/attention-driven, not tonically increased by satiety (prevents ceiling saturation).
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
                            # Survival mode: NA increases, ACh increases for focus. , removed or ne_level > 0.7 
                            if (a.food < StartFood * 0.2 or a.net.all_neurons[0].health < 0.3): 
                                a.net.neuromodulators['norepinephrine'] = min(2.0, ne_level + 0.05)
                                #a.net.neuromodulators['acetylcholine'] = min(2.0, ach_level + 0.02) # ACh decoupled from threat-arousal for this test (should be novelty/attention-driven, not yoked to NE).
                            
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
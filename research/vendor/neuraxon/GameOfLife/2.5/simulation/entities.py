# Neuraxon Game of Life Simulation Entities
# Based on the Paper "Neuraxon: A New Neural Growth & Computation Blueprint" by David Vivancos https://vivancos.com/  & Dr. Jose Sanchez  https://josesanchezgarcia.com/ for Qubic Science https://qubic.org/
# https://www.researchgate.net/publication/397331336_Neuraxon
# Play the Lite Version of the Game of Life at https://huggingface.co/spaces/DavidVivancos/NeuraxonLife
import time
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict

# Type Checking import to avoid circular dependency
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from neuraxon.network import NeuraxonNetwork

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
    net: 'NeuraxonNetwork'
    food: float
    is_male: bool
    alive: bool = True
    born_ts: float = field(default_factory=time.time)
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
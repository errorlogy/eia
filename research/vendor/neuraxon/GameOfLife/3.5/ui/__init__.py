# Neuraxon Game of Life 3.5 UI Package (Neuraxon 2.0 Compliant) Internal version 104
# Based on the Papers:
#   "Neuraxon V2.0: A New Neural Growth & Computation Blueprint" by David Vivancos & Jose Sanchez
#   https://vivancos.com/ & https://josesanchezgarcia.com/ for Qubic Science https://qubic.org/
# https://www.researchgate.net/publication/400868863_Neuraxon_V20_A_New_Neural_Growth_Computation_Blueprint  (Neuraxon V2.0 )
# https://www.researchgate.net/publication/397331336_Neuraxon (V1) 
# Play the Lite Version of the Game of Life 3.5 at https://huggingface.co/spaces/DavidVivancos/NeuraxonLife
"""
User Interface Package
----------------------
Handles all graphical rendering via Pygame, including the main game loop visualization,
HUD overlays, interactive menus, and configuration screens.
"""

from .renderer import Renderer
from .widgets import Slider
from .menus import run_config_screen

__all__ = ['Renderer', 'Slider', 'run_config_screen']
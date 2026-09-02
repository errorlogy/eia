# Neuraxon Game of Life UI Package
# Based on the Paper "Neuraxon V2.0: A New Neural Growth & Computation Blueprint" by David Vivancos https://vivancos.com/  & Dr. Jose Sanchez  https://josesanchezgarcia.com/ for Qubic Science https://qubic.org/
# https://www.researchgate.net/publication/397331336_Neuraxon
# Play the Lite Version of the Game of Life at https://huggingface.co/spaces/DavidVivancos/NeuraxonLife
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
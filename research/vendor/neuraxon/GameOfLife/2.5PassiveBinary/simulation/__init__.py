# Neuraxon Game of Life Simulation Package
# Based on the Paper "Neuraxon: A New Neural Growth & Computation Blueprint" by David Vivancos https://vivancos.com/  & Dr. Jose Sanchez  https://josesanchezgarcia.com/ for Qubic Science https://qubic.org/
# https://www.researchgate.net/publication/397331336_Neuraxon
# Play the Lite Version of the Game of Life at https://huggingface.co/spaces/DavidVivancos/NeuraxonLife
"""
Simulation Logic Package
------------------------
This package contains the world generation, physics, and entities (agents, food)
that make up the environment for the Neuraxon networks.
"""

from .entities import NxEr, NxErStats, Food
from .world import World

__all__ = ['NxEr', 'NxErStats', 'Food', 'World']
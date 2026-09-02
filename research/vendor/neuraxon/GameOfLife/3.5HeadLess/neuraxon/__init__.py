# Neuraxon Game of Life Neuron Package (Nxon 2.0 compliant)
# Based on the Paper "Neuraxon: A New Neural Growth & Computation Blueprint" by David Vivancos https://vivancos.com/  & Dr. Jose Sanchez  https://josesanchezgarcia.com/ for Qubic Science https://qubic.org/
# https://www.researchgate.net/publication/397331336_Neuraxon
# Play the Lite Version of the Game of Life at https://huggingface.co/spaces/DavidVivancos/NeuraxonLife
"""
Neuraxon Neural Network Library
-------------------------------
Implements the core neural computation model based on the Neuraxon research paper.
Includes neurons, synapses, dendritic branches, and network-level plasticity rules.
"""

# Expose key classes for easier importing
from .neuron import Neuraxon
from .network import NeuraxonNetwork
from .components import Synapse, DendriticBranch, ITUCircle, MSTHState, ReceptorSubtype, OscillatorBank, NeuromodulatorSystem
from .enums import NeuronType, SynapseType, TrinaryState
from .genetics import Inheritance

__all__ = [
    'Neuraxon',
    'NeuraxonNetwork',
    'Synapse',
    'DendriticBranch',
    'ITUCircle',
    'NeuronType',
    'SynapseType',
    'TrinaryState',
    'Inheritance'
]
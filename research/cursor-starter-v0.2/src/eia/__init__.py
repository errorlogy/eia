"""Endogenous Initiative Architecture research substrate."""

from .causal import EndogeneityEstimate, EndogeneityEstimator
from .emergence import EmergenceConfig, EndogenousEmergenceSimulator
from .endogenous import EndogenousSpectrumLevel, EndogeneityVector
from .governors import ContactContext, ContactGovernor
from .runtime import EIAConfig, EIARuntime
from .woe_receipt import WoEReceipt, WoENodeType, apply_governor_isolation

__all__ = [
    "ContactContext",
    "ContactGovernor",
    "EIAConfig",
    "EIARuntime",
    "EmergenceConfig",
    "EndogenousEmergenceSimulator",
    "EndogenousSpectrumLevel",
    "EndogeneityEstimate",
    "EndogeneityEstimator",
    "EndogeneityVector",
    "WoENodeType",
    "WoEReceipt",
    "apply_governor_isolation",
]

__version__ = "0.2.0"

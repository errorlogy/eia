"""Endogenous Initiative Architecture research substrate."""

from .causal import EndogeneityEstimate, EndogeneityEstimator
from .governors import ContactContext, ContactGovernor
from .runtime import EIAConfig, EIARuntime

__all__ = [
    "ContactContext",
    "ContactGovernor",
    "EIAConfig",
    "EIARuntime",
    "EndogeneityEstimate",
    "EndogeneityEstimator",
]

__version__ = "0.1.0"


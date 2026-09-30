"""Tick 122: attribute the residual controllability loss in the balanced agent (tick 121 case B): budget loop only (no
per-motive cap) vs none / gated. 6 seeds x 3 motives."""
from tick121 import case
print(f"{'governor':<10}{'d self':>8}{'z':>7}")
for mode in ("none", "budget", "gated"):
    _, d, zz = case("B", mode); print(f"{mode:<10}{d:>8.1f}{zz:>7.2f}", flush=True)

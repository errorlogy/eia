"""Tick 123: slower budget integrator (ki 0.0005 vs 0.002) in the gated Governor. Case A (strong generator): share cap and
controllability; case B (balanced): controllability. Also overall rate in B. 6 seeds x 3 motives."""
import functools
import numpy as np
import tick121
from tick92 import T0, mods

orig = tick121.sim
print(f"{'ki':>7}{'case':<4}{'gen share':>11}{'d self':>8}{'z':>7}")
for ki in (0.002, 0.0005):
    tick121.sim = functools.partial(orig, ki=ki)
    for kind in ("A", "B"):
        sh, d, zz = tick121.case(kind, "gated")
        print(f"{ki:>7} {kind:<3}{sh:>11.2f}{d:>8.1f}{zz:>7.2f}", flush=True)

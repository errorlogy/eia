from __future__ import annotations

import unittest

from eia.amat_m0 import compute_m0_sketch


class AmatM0Tests(unittest.TestCase):
    def test_emit_m0_always_false(self) -> None:
        sketch = compute_m0_sketch(
            epistemic_pressure=0.9,
            peak_coherence=0.5,
            self_prior_mismatch=0.8,
        )
        self.assertFalse(sketch.emit_m0)
        self.assertFalse(sketch.as_audit_dict()["emit_m0"])

    def test_high_mismatch_hints_nd(self) -> None:
        sketch = compute_m0_sketch(
            epistemic_pressure=0.9,
            peak_coherence=0.5,
            self_prior_mismatch=0.9,
        )
        self.assertEqual(sketch.phase_hint, "K_AI_nd_hint")
        self.assertGreaterEqual(sketch.distance_to_typical, 1.2)


if __name__ == "__main__":
    unittest.main()

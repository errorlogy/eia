from __future__ import annotations

import unittest

from eia.math_model import (
    accumulated_prefix_risk,
    bayes_binary,
    binary_entropy,
    drive_transition,
    expected_binary_information_gain,
    wilson_interval,
)


class MathModelTests(unittest.TestCase):
    def test_bayes_update(self) -> None:
        posterior = bayes_binary(0.5, 0.9, 0.1)
        self.assertAlmostEqual(posterior, 0.9)

    def test_entropy_and_information_gain(self) -> None:
        self.assertAlmostEqual(binary_entropy(0.5), 1.0)
        self.assertGreater(expected_binary_information_gain(0.5, 0.9), 0.5)
        self.assertEqual(expected_binary_information_gain(0.5, 0.5), 0.0)

    def test_drive_is_bounded(self) -> None:
        value = drive_transition(
            0.95,
            decay=0.0,
            error=1.0,
            novelty=1.0,
            satisfaction=0.0,
            error_gain=1.0,
            novelty_gain=1.0,
            satisfaction_gain=0.0,
        )
        self.assertEqual(value, 1.0)

    def test_prefix_risk(self) -> None:
        self.assertAlmostEqual(accumulated_prefix_risk((0.1, 0.2)), 0.28)

    def test_wilson_interval_contains_rate(self) -> None:
        low, high = wilson_interval(75, 100)
        self.assertLess(low, 0.75)
        self.assertGreater(high, 0.75)


if __name__ == "__main__":
    unittest.main()


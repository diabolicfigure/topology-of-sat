"""Planted SAT and normalization checks."""

from __future__ import annotations

import math
import random
import unittest

from satlab.extractor import assignment_satisfies, enumerate_solutions
from satlab.generators import planted_ksat
from satlab.pipeline import analyze_formula, beta0_per_log_s


class PlantedTests(unittest.TestCase):
    def test_plant_is_always_a_solution(self) -> None:
        rng = random.Random(7)
        formula = planted_ksat(8, 3, 24, rng, seed=7)
        self.assertEqual(formula.family, "planted")
        self.assertIsNotNone(formula.planted_mask)
        self.assertTrue(assignment_satisfies(formula.planted_mask, formula.clauses))
        solutions = enumerate_solutions(formula)
        self.assertIn(formula.planted_mask, solutions)
        self.assertGreaterEqual(len(solutions), 1)

    def test_high_density_planted_stays_sat(self) -> None:
        rng = random.Random(11)
        formula = planted_ksat(10, 3, 80, rng, seed=11)
        result = analyze_formula(formula)
        self.assertGreaterEqual(result.n_solutions, 1)
        self.assertEqual(result.family, "planted")

    def test_beta0_per_log_s_undefined_for_tiny_s(self) -> None:
        self.assertIsNone(beta0_per_log_s(0, 0))
        self.assertIsNone(beta0_per_log_s(1, 1))
        self.assertAlmostEqual(beta0_per_log_s(2, 4), 2 / math.log(4))


if __name__ == "__main__":
    unittest.main()

"""Growing families, girth, and Path C scoring."""

from __future__ import annotations

import random
import unittest

from satlab.complex_builder import build_complex
from satlab.cycles import skeleton_girth
from satlab.extractor import enumerate_solutions
from satlab.generators import clause_stream, formula_from_clauses, prefix_formula
from satlab.lifecycle import score_family
from satlab.pipeline import analyze_formula


class LifecycleTests(unittest.TestCase):
    def test_prefixes_are_nested(self) -> None:
        rng = random.Random(3)
        clauses, plant = clause_stream(8, 3, 20, rng, family="uniform")
        small = prefix_formula(8, 3, clauses, 5, seed=3, family="uniform")
        big = prefix_formula(8, 3, clauses, 12, seed=3, family="uniform")
        self.assertEqual(small.clauses, big.clauses[:5])
        self.assertIsNone(plant)

    def test_planted_prefixes_stay_sat(self) -> None:
        rng = random.Random(5)
        clauses, plant = clause_stream(8, 3, 40, rng, family="planted")
        self.assertIsNotNone(plant)
        dense = prefix_formula(
            8, 3, clauses, 40, seed=5, family="planted", planted_mask=plant
        )
        solutions = enumerate_solutions(dense)
        self.assertIn(plant, solutions)

    def test_six_cycle_girth(self) -> None:
        solutions = [0b000, 0b001, 0b011, 0b111, 0b110, 0b100]
        complex_ = build_complex(3, solutions, max_dim=3)
        self.assertEqual(skeleton_girth(complex_), 6)
        result = analyze_formula(
            formula_from_clauses(3, 1, []),
            compute_girth=True,
        )
        # empty 3-SAT on n=3 is the full cube: filled, girth 4, cubical β₁ = 0
        self.assertEqual(result.girth, 4)
        self.assertEqual(result.cubical_beta1, 0)
        self.assertGreaterEqual(result.fill_gap, 1)

    def test_score_success_order(self) -> None:
        def row(alpha, s, b0, b1):
            return {
                "family": "uniform",
                "seed": 1,
                "alpha_target": alpha,
                "m": int(alpha * 14),
                "n_solutions": s,
                "beta0": b0,
                "cubical_beta1": b1,
                "beta2": 0,
                "truncated": False,
            }

        rows = [
            row(1.5, 200, 1, 0),
            row(2.0, 80, 1, 3),
            row(2.5, 40, 2, 1),
            row(3.0, 20, 4, 0),
            row(3.5, 8, 3, 0),
            row(4.0, 3, 2, 0),
            row(5.0, 0, 0, 0),
        ]
        # last row cubical_beta1 0 with n_solutions 0 is excluded from cubical
        rows[-1]["cubical_beta1"] = 0
        score = score_family(rows)
        self.assertEqual(score["verdict"], "success")
        self.assertEqual(score["onset_alpha"], 2.0)
        self.assertEqual(score["death_alpha"], 3.0)
        self.assertEqual(score["collapse_alpha"], 5.0)


if __name__ == "__main__":
    unittest.main()

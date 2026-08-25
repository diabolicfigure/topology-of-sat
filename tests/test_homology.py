"""Tight checks for the induced cubical complex and the 2-SAT counterexample."""

from __future__ import annotations

import unittest

from satlab.complex_builder import build_complex
from satlab.extractor import enumerate_solutions
from satlab.generators import formula_from_clauses
from satlab.homology import betti_1skeleton, betti_cubical
from satlab.pipeline import analyze_formula


class HomologyTests(unittest.TestCase):
    def test_two_sat_disconnected_counterexample(self) -> None:
        # (x ∨ y) ∧ (¬x ∨ ¬y) — solutions 01 and 10, Hamming distance 2.
        formula = formula_from_clauses(2, 2, [(1, 2), (-1, -2)])
        result = analyze_formula(formula)
        self.assertEqual(result.n_solutions, 2)
        self.assertGreaterEqual(result.beta0, 2)
        self.assertEqual(result.beta0, 2)
        self.assertEqual(result.beta1, 0)
        self.assertEqual(result.beta2, 0)

    def test_single_solution(self) -> None:
        # x ∧ ¬x is unsat; x alone: force x=1 via (x) as a 1-clause on n=1.
        formula = formula_from_clauses(1, 1, [(1,)])
        result = analyze_formula(formula)
        self.assertEqual(result.n_solutions, 1)
        self.assertEqual((result.beta0, result.beta1, result.beta2), (1, 0, 0))

    def test_empty_formula_cube_is_contractible(self) -> None:
        # All 8 vertices of Q3: induced cubical 3-cube is a ball.
        formula = formula_from_clauses(3, 1, [])
        result = analyze_formula(formula)
        self.assertEqual(result.n_solutions, 8)
        self.assertEqual((result.beta0, result.beta1, result.beta2), (1, 0, 0))

    def test_induced_6cycle_has_beta1(self) -> None:
        # 000-001-011-111-110-100-000, no 2-face filled.
        solutions = [0b000, 0b001, 0b011, 0b111, 0b110, 0b100]
        complex_ = build_complex(3, solutions, max_dim=3)
        self.assertEqual(complex_.n_vertices, 6)
        self.assertEqual(complex_.n_edges, 6)
        self.assertEqual(complex_.n_faces, 0)
        skeleton = betti_1skeleton(complex_)
        cubical = betti_cubical(complex_)
        self.assertEqual(skeleton.beta0, 1)
        self.assertEqual(skeleton.beta1, 1)
        self.assertEqual((cubical.beta0, cubical.beta1, cubical.beta2), (1, 1, 0))

    def test_two_adjacent_solutions(self) -> None:
        formula = formula_from_clauses(2, 1, [(-2,)])  # y = 0; solutions 00, 10
        sols = enumerate_solutions(formula)
        self.assertEqual(sorted(sols), [0b00, 0b01])  # bit0 = x, bit1 = y
        result = analyze_formula(formula)
        self.assertEqual((result.beta0, result.beta1, result.beta2), (1, 0, 0))


if __name__ == "__main__":
    unittest.main()

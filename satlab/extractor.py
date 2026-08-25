"""Full solution-space enumeration for small n."""

from __future__ import annotations

from satlab.generators import Formula


def assignment_satisfies(mask: int, clauses: tuple[tuple[int, ...], ...]) -> bool:
    for clause in clauses:
        sat = False
        for lit in clause:
            bit = (mask >> (abs(lit) - 1)) & 1
            if lit > 0:
                if bit:
                    sat = True
                    break
            elif bit == 0:
                sat = True
                break
        if not sat:
            return False
    return True


def enumerate_solutions(formula: Formula) -> list[int]:
    """Return satisfying assignments as bitmasks. Variable i is bit (i-1)."""
    if formula.n > 20:
        raise ValueError("full enumeration is only for n <= 20 in Phase 0")
    solutions: list[int] = []
    clauses = formula.clauses
    for mask in range(1 << formula.n):
        if assignment_satisfies(mask, clauses):
            solutions.append(mask)
    return solutions

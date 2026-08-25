"""Uniform random k-SAT generators."""

from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class Formula:
    n: int
    k: int
    clauses: tuple[tuple[int, ...], ...]
    seed: int | None = None
    family: str = "uniform"
    planted_mask: int | None = None

    @property
    def m(self) -> int:
        return len(self.clauses)

    @property
    def alpha(self) -> float:
        return (self.m / self.n) if self.n else 0.0


def random_ksat(
    n: int,
    k: int,
    m: int,
    rng: random.Random,
    *,
    seed: int | None = None,
) -> Formula:
    """Draw m non-tautological uniform random k-clauses on n variables.

    Literals are DIMACS-style: ±1 .. ±n. Duplicate clauses are allowed
    (standard G(n, m, k)). Tautologies (both x and ¬x in one clause) are rejected.
    """
    if n < 1:
        raise ValueError("n must be >= 1")
    if k < 1 or k > n:
        raise ValueError("need 1 <= k <= n")
    if m < 0:
        raise ValueError("m must be >= 0")

    variables = list(range(1, n + 1))
    clauses: list[tuple[int, ...]] = []
    while len(clauses) < m:
        chosen = rng.sample(variables, k)
        lits = []
        for v in chosen:
            lits.append(v if rng.randrange(2) else -v)
        clause = tuple(sorted(lits, key=lambda lit: (abs(lit), lit)))
        signs = {abs(lit): lit > 0 for lit in clause}
        if len(signs) < k:
            continue
        clauses.append(clause)
    return Formula(n=n, k=k, clauses=tuple(clauses), seed=seed, family="uniform")


def _random_clause(n: int, k: int, rng: random.Random) -> tuple[int, ...] | None:
    chosen = rng.sample(list(range(1, n + 1)), k)
    lits = [v if rng.randrange(2) else -v for v in chosen]
    clause = tuple(sorted(lits, key=lambda lit: (abs(lit), lit)))
    if len({abs(lit) for lit in clause}) < k:
        return None
    return clause


def clause_stream(
    n: int,
    k: int,
    m: int,
    rng: random.Random,
    *,
    family: str = "uniform",
    planted_mask: int | None = None,
) -> tuple[list[tuple[int, ...]], int | None]:
    """Draw a reusable clause list. Prefixes of this list are a growing family."""
    if family not in ("uniform", "planted"):
        raise ValueError(f"unknown family: {family}")
    plant = None
    if family == "planted":
        plant = planted_mask if planted_mask is not None else rng.randrange(1 << n)
    clauses: list[tuple[int, ...]] = []
    while len(clauses) < m:
        clause = _random_clause(n, k, rng)
        if clause is None:
            continue
        if plant is not None and not _clause_satisfied(plant, clause):
            continue
        clauses.append(clause)
    return clauses, plant


def prefix_formula(
    n: int,
    k: int,
    clauses: list[tuple[int, ...]],
    m: int,
    *,
    seed: int | None,
    family: str,
    planted_mask: int | None = None,
) -> Formula:
    if m < 0 or m > len(clauses):
        raise ValueError("m must be a prefix of the clause stream")
    return Formula(
        n=n,
        k=k,
        clauses=tuple(clauses[:m]),
        seed=seed,
        family=family,
        planted_mask=planted_mask,
    )


def _clause_satisfied(mask: int, clause: tuple[int, ...]) -> bool:
    for lit in clause:
        bit = (mask >> (abs(lit) - 1)) & 1
        if lit > 0 and bit:
            return True
        if lit < 0 and bit == 0:
            return True
    return False


def planted_ksat(
    n: int,
    k: int,
    m: int,
    rng: random.Random,
    *,
    seed: int | None = None,
    planted_mask: int | None = None,
) -> Formula:
    """Draw m k-clauses that are all satisfied by one planted assignment.

    The plant is included in the solution space by construction. Extra
    solutions may still exist. Tautologies are rejected.
    """
    if n < 1:
        raise ValueError("n must be >= 1")
    if k < 1 or k > n:
        raise ValueError("need 1 <= k <= n")
    if m < 0:
        raise ValueError("m must be >= 0")

    plant = planted_mask if planted_mask is not None else rng.randrange(1 << n)
    variables = list(range(1, n + 1))
    clauses: list[tuple[int, ...]] = []
    while len(clauses) < m:
        chosen = rng.sample(variables, k)
        lits = [v if rng.randrange(2) else -v for v in chosen]
        clause = tuple(sorted(lits, key=lambda lit: (abs(lit), lit)))
        if len({abs(lit) for lit in clause}) < k:
            continue
        if not _clause_satisfied(plant, clause):
            continue
        clauses.append(clause)
    return Formula(
        n=n,
        k=k,
        clauses=tuple(clauses),
        seed=seed,
        family="planted",
        planted_mask=plant,
    )


def formula_from_clauses(
    n: int,
    k: int,
    clauses: list[tuple[int, ...]],
    *,
    family: str = "hand",
) -> Formula:
    return Formula(n=n, k=k, clauses=tuple(clauses), seed=None, family=family)

"""End-to-end analysis of one formula."""

from __future__ import annotations

import math
import time
from dataclasses import asdict, dataclass

from satlab.complex_builder import CubicalComplex, build_complex
from satlab.cycles import skeleton_girth
from satlab.extractor import enumerate_solutions
from satlab.generators import Formula
from satlab.homology import BettiNumbers, betti_1skeleton, betti_cubical


# Higher cells get expensive on near-empty formulas. Stay under this.
DEFAULT_MAX_VERTICES_FOR_DIM3 = 8192


def beta0_per_log_s(beta0: int, n_solutions: int) -> float | None:
    """β₀ / ln(|S|). Defined only for |S| >= 2."""
    if n_solutions < 2:
        return None
    return beta0 / math.log(n_solutions)


def beta0_per_s(beta0: int, n_solutions: int) -> float | None:
    if n_solutions < 1:
        return None
    return beta0 / n_solutions


@dataclass
class Analysis:
    n: int
    k: int
    m: int
    alpha: float
    seed: int | None
    family: str
    planted_mask: int | None
    n_solutions: int
    n_vertices: int
    n_edges: int
    n_faces: int
    n_cubes: int
    built_dim: int
    beta0: int
    beta1: int
    beta2: int | None
    skeleton_beta1: int
    cubical_beta1: int | None
    fill_gap: int | None
    girth: int | None
    beta0_per_log_s: float | None
    beta0_per_s: float | None
    rank_d1: int
    rank_d2: int | None
    rank_d3: int | None
    truncated: bool
    enumerate_ms: float
    complex_ms: float
    homology_ms: float
    total_ms: float

    def as_log_row(self) -> dict:
        return asdict(self)


def _should_build_dim3(n_solutions: int, max_vertices: int) -> bool:
    return 0 < n_solutions <= max_vertices


def analyze_formula(
    formula: Formula,
    *,
    max_vertices_for_dim3: int = DEFAULT_MAX_VERTICES_FOR_DIM3,
    compute_girth: bool = False,
) -> Analysis:
    t0 = time.perf_counter()

    t = time.perf_counter()
    solutions = enumerate_solutions(formula)
    enumerate_ms = (time.perf_counter() - t) * 1000.0

    if len(solutions) == 0:
        truncated = False
        max_dim = 3
    elif _should_build_dim3(len(solutions), max_vertices_for_dim3):
        truncated = False
        max_dim = 3
    else:
        truncated = True
        max_dim = 1

    t = time.perf_counter()
    complex_ = build_complex(formula.n, solutions, max_dim=max_dim)
    complex_ms = (time.perf_counter() - t) * 1000.0

    t = time.perf_counter()
    betti = _compute_betti(complex_)
    skeleton = betti_1skeleton(complex_)
    girth = skeleton_girth(complex_) if compute_girth else None
    homology_ms = (time.perf_counter() - t) * 1000.0

    cubical_beta1 = betti.beta1 if complex_.built_dim >= 3 else None
    fill_gap = (
        skeleton.beta1 - cubical_beta1 if cubical_beta1 is not None else None
    )

    total_ms = (time.perf_counter() - t0) * 1000.0
    return Analysis(
        n=formula.n,
        k=formula.k,
        m=formula.m,
        alpha=formula.alpha,
        seed=formula.seed,
        family=formula.family,
        planted_mask=formula.planted_mask,
        n_solutions=len(solutions),
        n_vertices=complex_.n_vertices,
        n_edges=complex_.n_edges,
        n_faces=complex_.n_faces,
        n_cubes=complex_.n_cubes,
        built_dim=complex_.built_dim,
        beta0=betti.beta0,
        beta1=betti.beta1,
        beta2=betti.beta2,
        skeleton_beta1=skeleton.beta1,
        cubical_beta1=cubical_beta1,
        fill_gap=fill_gap,
        girth=girth,
        beta0_per_log_s=beta0_per_log_s(betti.beta0, len(solutions)),
        beta0_per_s=beta0_per_s(betti.beta0, len(solutions)),
        rank_d1=betti.rank_d1,
        rank_d2=betti.rank_d2,
        rank_d3=betti.rank_d3,
        truncated=truncated and len(solutions) > 0,
        enumerate_ms=enumerate_ms,
        complex_ms=complex_ms,
        homology_ms=homology_ms,
        total_ms=total_ms,
    )


def _compute_betti(complex_: CubicalComplex) -> BettiNumbers:
    if complex_.built_dim >= 3:
        return betti_cubical(complex_)
    return betti_1skeleton(complex_)

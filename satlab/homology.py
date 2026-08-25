"""Homology of the induced cubical complex over GF(2)."""

from __future__ import annotations

from dataclasses import dataclass

from satlab.complex_builder import CubicalComplex


@dataclass(frozen=True)
class BettiNumbers:
    beta0: int
    beta1: int
    beta2: int | None
    rank_d1: int
    rank_d2: int | None
    rank_d3: int | None


class UnionFind:
    def __init__(self, items: list[int]) -> None:
        self.parent = {x: x for x in items}
        self.rank = {x: 0 for x in items}
        self.components = len(items)

    def find(self, x: int) -> int:
        parent = self.parent
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(self, a: int, b: int) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        self.components -= 1


def gf2_column_rank(columns: list[list[int]]) -> int:
    """Rank of a GF(2) matrix given as a list of sparse columns (row indices)."""
    pivots: dict[int, set[int]] = {}
    for col in columns:
        remaining = set(col)
        while remaining:
            row = min(remaining)
            pivot = pivots.get(row)
            if pivot is None:
                pivots[row] = remaining
                break
            remaining ^= pivot
    return len(pivots)


def _edge_key(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u < v else (v, u)


def _face_boundary_rows(
    base: int,
    i: int,
    j: int,
    edge_index: dict[tuple[int, int], int],
) -> list[int]:
    a = base ^ (1 << i)
    b = base ^ (1 << j)
    c = a ^ (1 << j)
    edges = (
        _edge_key(base, a),
        _edge_key(base, b),
        _edge_key(a, c),
        _edge_key(b, c),
    )
    return [edge_index[e] for e in edges]


def _cube_boundary_rows(
    base: int,
    i: int,
    j: int,
    k: int,
    face_index: dict[tuple[int, int, int], int],
) -> list[int]:
    faces = (
        (base, i, j),
        (base, i, k),
        (base, j, k),
        (base ^ (1 << k), i, j),
        (base ^ (1 << j), i, k),
        (base ^ (1 << i), j, k),
    )
    return [face_index[f] for f in faces]


def betti_1skeleton(complex_: CubicalComplex) -> BettiNumbers:
    """Exact β₀ of K; β₁ of the 1-skeleton (upper bound on cubical β₁)."""
    if not complex_.vertices:
        return BettiNumbers(0, 0, None, 0, None, None)
    uf = UnionFind(complex_.vertices)
    for u, v in complex_.edges:
        uf.union(u, v)
    beta0 = uf.components
    v, e = complex_.n_vertices, complex_.n_edges
    beta1 = e - v + beta0
    rank_d1 = v - beta0
    return BettiNumbers(beta0, beta1, None, rank_d1, None, None)


def betti_cubical(complex_: CubicalComplex) -> BettiNumbers:
    """Exact cubical β₀, β₁, β₂ over GF(2) using the 3-skeleton.

    H₂ depends on ∂₂ and ∂₃ only, so 3-cubes are enough for exact β₂
    of the full induced cubical complex.
    """
    if complex_.built_dim < 3:
        raise ValueError("cubical β₂ needs the 3-skeleton (max_dim=3)")
    if not complex_.vertices:
        return BettiNumbers(0, 0, 0, 0, 0, 0)

    skeleton = betti_1skeleton(complex_)
    edge_index = {_edge_key(u, v): idx for idx, (u, v) in enumerate(complex_.edges)}
    face_index = {face: idx for idx, face in enumerate(complex_.faces)}

    d2_cols = [_face_boundary_rows(base, i, j, edge_index) for base, i, j in complex_.faces]
    d3_cols = [
        _cube_boundary_rows(base, i, j, k, face_index) for base, i, j, k in complex_.cubes
    ]
    rank_d2 = gf2_column_rank(d2_cols)
    rank_d3 = gf2_column_rank(d3_cols)

    v, e, f = complex_.n_vertices, complex_.n_edges, complex_.n_faces
    beta0 = skeleton.beta0
    beta1 = e - v + beta0 - rank_d2
    beta2 = f - rank_d2 - rank_d3
    if beta1 < 0 or beta2 < 0:
        raise RuntimeError(f"negative Betti numbers: β₁={beta1} β₂={beta2}")
    return BettiNumbers(beta0, beta1, beta2, skeleton.rank_d1, rank_d2, rank_d3)

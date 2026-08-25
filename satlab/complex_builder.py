"""Induced cubical complex of a subset of the hypercube."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CubicalComplex:
    """Induced cubical complex K(S) ⊆ Q_n.

    A d-face on bit set I is included iff all 2^|I| vertices obtained by
    flipping those bits from a base assignment lie in S.
    """

    n: int
    vertices: list[int]
    edges: list[tuple[int, int]] = field(default_factory=list)
    faces: list[tuple[int, int, int]] = field(default_factory=list)
    cubes: list[tuple[int, int, int, int]] = field(default_factory=list)
    built_dim: int = 0

    @property
    def n_vertices(self) -> int:
        return len(self.vertices)

    @property
    def n_edges(self) -> int:
        return len(self.edges)

    @property
    def n_faces(self) -> int:
        return len(self.faces)

    @property
    def n_cubes(self) -> int:
        return len(self.cubes)


def build_complex(
    n: int,
    solutions: list[int],
    *,
    max_dim: int = 1,
) -> CubicalComplex:
    """Build the induced cubical complex up to the requested dimension.

    max_dim=1: 1-skeleton (enough for β₀ and graph β₁).
    max_dim=3: 2-faces and 3-cubes (enough for exact cubical β₀, β₁, β₂).
    """
    if max_dim not in (1, 3):
        raise ValueError("max_dim must be 1 or 3")

    verts = list(solutions)
    sol = set(verts)
    complex_ = CubicalComplex(n=n, vertices=verts, built_dim=1)

    for x in verts:
        for i in range(n):
            y = x ^ (1 << i)
            if y in sol and x < y:
                complex_.edges.append((x, y))

    if max_dim < 3:
        return complex_

    for x in verts:
        for i in range(n):
            if (x >> i) & 1:
                continue
            yi = x ^ (1 << i)
            if yi not in sol:
                continue
            for j in range(i + 1, n):
                if (x >> j) & 1:
                    continue
                yj = x ^ (1 << j)
                yij = yi ^ (1 << j)
                if yj in sol and yij in sol:
                    complex_.faces.append((x, i, j))

    for x in verts:
        for i in range(n):
            if (x >> i) & 1:
                continue
            for j in range(i + 1, n):
                if (x >> j) & 1:
                    continue
                for k in range(j + 1, n):
                    if (x >> k) & 1:
                        continue
                    ok = True
                    for delta in range(1, 8):
                        y = x
                        if delta & 1:
                            y ^= 1 << i
                        if delta & 2:
                            y ^= 1 << j
                        if delta & 4:
                            y ^= 1 << k
                        if y not in sol:
                            ok = False
                            break
                    if ok:
                        complex_.cubes.append((x, i, j, k))

    complex_.built_dim = 3
    return complex_

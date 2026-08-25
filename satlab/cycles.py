"""1-skeleton cycle statistics. Not homology generators; just girth."""

from __future__ import annotations

from collections import defaultdict, deque

from satlab.complex_builder import CubicalComplex

GIRTH_VERTEX_CAP = 800


def skeleton_girth(complex_: CubicalComplex, *, max_vertices: int = GIRTH_VERTEX_CAP) -> int | None:
    """Length of the shortest cycle in the 1-skeleton, or None if acyclic / too large."""
    if complex_.n_vertices > max_vertices or complex_.n_edges == 0:
        return None

    adj: dict[int, list[int]] = defaultdict(list)
    for u, v in complex_.edges:
        adj[u].append(v)
        adj[v].append(u)

    best: int | None = None
    for start in complex_.vertices:
        dist = {start: 0}
        parent: dict[int, int | None] = {start: None}
        queue = deque([start])
        while queue:
            u = queue.popleft()
            du = dist[u]
            if best is not None and 2 * du >= best:
                continue
            for v in adj[u]:
                if v == parent[u]:
                    continue
                if v not in dist:
                    dist[v] = du + 1
                    parent[v] = u
                    queue.append(v)
                    continue
                cycle = du + dist[v] + 1
                if best is None or cycle < best:
                    best = cycle
                    if best == 4:
                        return 4
    return best

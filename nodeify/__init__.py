"""Library providing a lazily re-evaluating computation graph, built from instance methods."""

from ._graph import Graph, GraphMeta, node

__all__ = (
    "Graph",
    "GraphMeta",
    "node",
)

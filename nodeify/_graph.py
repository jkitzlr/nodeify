from __future__ import annotations

import ast
import functools
import inspect
import textwrap
from collections.abc import Callable
from typing import Any, Generic, Self, TypeVar

from nodeify._meta import AttributeAnalyzer
from nodeify._node import Node

G = TypeVar("G", bound="Graph")
T = TypeVar("T")


class NodeAttribute(Generic[G, T]):
    """Manages the getting and setting of values of nodes in the graph."""

    def __init__(self: Self, func: Callable[[G], T]) -> None:
        self.func = func

    def __set_name__(self: Self, owner: type[G], name: str) -> None:
        self.public_name = name
        self.private_name = f"_{name}"

    # TODO: handle missing Node attr
    def __get__(self: Self, obj: G, objtype: type[G] | None = None) -> T:
        node: Node[T] = getattr(obj, self.private_name)
        if node.dirty and not node.override:
            value = self.func(obj)
            node.set_value(value)

        if node.value is None:
            msg = f"No valid value set/computable for attribute {self.public_name}!"
            raise ValueError(msg)

        return node.value

    def __set__(self: Self, obj: G, value: T) -> None:
        node: Node[T] = getattr(obj, self.private_name)
        node.set_value(value=value, manual=True)


def node(func: Callable[[G], T]) -> NodeAttribute[G, T]:
    return NodeAttribute(func)


class GraphMeta(type):
    """Custom metaclass to manage creation of the dependency graph."""

    def __init__(cls, name: str, _: tuple[str], dct: dict[str, Any]) -> None:
        node_attrs = {name: attr for name, attr in dct.items() if isinstance(attr, NodeAttribute)}
        listeners: dict[str, list[str]] = {}
        for name, attr in node_attrs.items():
            analyzer = AttributeAnalyzer()
            func = attr.func
            code = func.__code__
            tree = ast.parse(textwrap.dedent(inspect.getsource(code)))
            analyzer.visit(tree)
            for p in analyzer.attributes:
                lstnrs = listeners.setdefault(p, [])
                lstnrs.append(name)

        # * deal with __init__ here
        init: Callable[..., None] | None = dct.get("__init__")

        def new_init(obj, *args, **kwargs):
            for node in list(node_attrs.keys()):
                # ! this is an abstraction leakage; ideally this class should have no
                # ! knowledge of the private name convention used by the descriptors; TBD
                private_name = f"_{node}"
                setattr(obj, private_name, Node())

            # * now, create the list of event listeners for each node in the graph
            for nm, lstnrs in listeners.items():
                private_name = f"_{nm}"
                node: Node[Any] = getattr(obj, private_name)  # type: ignore[annotation-unchecked]
                node.listeners = [getattr(obj, f"_{lstnr}") for lstnr in lstnrs]

            if init is not None:
                init(obj, *args, **kwargs)

        if init is not None:
            new_init = functools.update_wrapper(new_init, init)

        setattr(cls, "__init__", new_init)  # noqa: B010


class Graph(metaclass=GraphMeta):
    """A lazily re-evaluating graph framework."""

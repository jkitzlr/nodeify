from __future__ import annotations

import dataclasses
from typing import Any, Generic, Self, TypeVar

T = TypeVar("T")


@dataclasses.dataclass(
    init=True,
    slots=True,
    frozen=False,
)
class Node(Generic[T]):
    """A node in the compute graph."""

    value: T | None = dataclasses.field(default=None)
    dirty: bool = dataclasses.field(default=True)
    override: bool = dataclasses.field(default=False)
    listeners: list[Node[Any]] = dataclasses.field(default_factory=list)

    # TODO: is the order here correct? e.g. update the value, broadcast the change, then set manl fl
    def set_value(self: Self, value: T, manual: bool = False) -> None:
        """Set the value of this Node to value.

        The manual flag is used to indicate if the default pub/sub behavior should be disabled,
        i.e. the value should be static.

        Args:
            value: The value to which to set the node
            manual: Optional flag to indicate if the value is a manual override. Defaults to False.
        """
        self.value = value
        self.override = manual
        self.dirty = False
        self.notify()

    def update(self: Self) -> None:
        """Method for event publishers to broadcast changes.

        For this class, just sets the dirty flag.
        """
        if not self.override:
            self.dirty = True
            self.notify()

    def notify(self: Self) -> None:
        for listener in self.listeners:
            listener.update()

    def reset(self: Self) -> None:
        if self.override:
            self.override = False

        self.value = None

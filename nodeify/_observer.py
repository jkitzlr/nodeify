from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Self


class Observer(ABC):
    """Define the interface for an Observer class."""

    @abstractmethod
    def update(self: Self) -> None: ...

    def register_with(self: Self, observable: Observable) -> None:
        observable.register(self)


# TODO: should observers be a set? no duplicate registration, faster to unregister
class Observable(ABC):
    """Define the interface for an observable class."""

    listeners: list[Observer]

    def __new__(cls, *_: Any, **__: Any) -> Self:
        inst = super().__new__(cls)
        inst.listeners = []
        return inst

    @abstractmethod
    def notify(self: Self) -> None: ...

    def register(self: Self, observer: Observer) -> None:
        self.listeners.append(observer)

    def unregister(self: Self, observer: Observer) -> None:
        self.listeners.remove(observer)


class A(Observable):
    def __init__(self: Self, a: int, b: int) -> None:
        super().__init__()
        self.a = a
        self.b = b

from typing import Self

from nodeify import Graph, node


class Klass(Graph):
    def __init__(self: Self, x: int | None = None, y: int | None = None) -> None:
        if x is not None:
            self.x = x

        if y is not None:
            self.y = y

    @node
    def x(self: Self) -> int:
        return 10

    @node
    def y(self: Self) -> int:
        return 20

    @node
    def a(self: Self) -> int:
        print("calc'ing a")
        return self.x + self.y


inst = Klass()

print(inst.a)

inst.x = 60
inst.y = 9

print(inst.a)
print(inst.a)
print(inst.a)
print(inst.a)
print(inst.a)

import ast
from typing import Self


class AttributeAnalyzer(ast.NodeVisitor):
    """Compile a list of attribute accesses on the instance."""

    def __init__(self: Self) -> None:
        self.attributes: list[str] = []

    def visit_Attribute(self: Self, node: ast.Attribute) -> None:
        value = node.value
        if isinstance(value, ast.Name) and value.id == "self":
            self.attributes.append(node.attr)

        self.generic_visit(node)

#!/usr/bin/python
##-------------------------------##
## Ember Compiler: Middleware    ##
## Written By: Ryan Smith        ##
##-------------------------------##
## Node: Variables               ##
##-------------------------------##

## Imports
from pathlib import Path

from .base import NodeBase, NodeContextBase


## Classes
class NodeVarDeclaration(NodeContextBase):
    """
    Ember Language AST Node: Var Declaration
    - Node that represents a variable declaration and
    it's expression initializer if applicable
    """

    # -Constructor
    def __init__(
        self, file: Path, position: tuple[int, int, int],
        _id: str, initializer: NodeBase | None
    ) -> None:
        super().__init__(file, position)
        self.id: str = _id
        self.initializer: NodeBase | None = initializer

    # -Dunder Methods
    def __repr__(self) -> str:
        return (f"NodeVarDeclaration({super().__repr__()}, "
                f"id={self.id}, initializer={self.initializer!r}")

    def __str__(self) -> str:
        return (f"Symbol({self.id}) = " +
                (str(self.initializer) if self.initializer else "Uninitialized"))


class NodeVarAssignment(NodeBase):
    """
    Ember Language AST Node: Var Assignment
    - Node that represents a variable assignment with an
    associated lvalue and rvalue node
    """

    # -Constructor
    def __init__(self, lvalue: NodeBase, rvalue: NodeBase) -> None:
        self.lvalue: NodeBase = lvalue
        self.rvalue: NodeBase = rvalue

    # -Dunder Methods
    def __repr__(self) -> str:
        return f"NodeVarAssignment(lvalue={self.lvalue!r}, rvalue={self.rvalue!r})"

    def __str__(self) -> str:
        return f"{self.lvalue} = {self.rvalue}"

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
class NodeFunctionDeclaration(NodeContextBase):
    """
    Ember Language AST Node: Function Declaration
    - Node that represents a function declaration and it's id, parameters, and body
    """

    # -Constructor
    def __init__(
        self, file: Path, position: tuple[int, int, int],
        _id: str, parameters: tuple[str, ...] | None, body: NodeBase
    ) -> None:
        super().__init__(file, position)
        self.id: str = _id
        self.parameters: tuple[str, ...] | None = parameters
        self.body: NodeBase = body

    # -Dunder Methods
    def __repr__(self) -> str:
        return (f"NodeFunctionDeclaration({super().__repr__()}, "
                f"id={self.id}, paremters={self.parameters}, body={self.body!r})")

    def __str__(self) -> str:
        _str = f"{self.id}("
        if self.parameters:
            _str += ", ".join(str(param) for param in self.parameters)
        return _str + f") {{ {self.body} }}"

    # -Properties
    @property
    def arity(self) -> int:
        if not self.parameters:
            return 0
        return len(self.parameters)


class NodeFunctionCall(NodeBase):
    """
    Ember Language AST Node: Function Call
    - Node that represents a function call with it's callee and arguments
    """

    # -Constructor
    def __init__(
        self, callee: NodeBase, arguments: tuple[NodeBase, ...] | None
    ) -> None:
        self.callee: NodeBase = callee
        self.arguments: tuple[NodeBase, ...] | None = arguments

    # -Dunder Methods
    def __repr__(self) -> str:
        return f"NodeFunctionCall(callee={self.callee!r}, arguments={self.arguments})"

    def __str__(self) -> str:
        _str = f"{self.callee}("
        if self.arguments:
            _str += ','.join(str(arg) for arg in self.arguments)
        return _str + ')'

    # -Properties
    @property
    def argument_count(self) -> int:
        if not self.arguments:
            return 0
        return len(self.arguments)

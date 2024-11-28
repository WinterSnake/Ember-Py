#!/usr/bin/python
##-------------------------------##
## Ember Compiler: Middleware    ##
## Written By: Ryan Smith        ##
##-------------------------------##
## Node: Literal                 ##
##-------------------------------##

## Imports
from __future__ import annotations
from enum import IntEnum, auto
from pathlib import Path

from .base import NodeBase


## Classes
class NodeLiteral(NodeBase):
    """
    Ember Language AST Node: Literal
    - Node that represents a literal and it's associated value
    """

    # -Constructor
    def __init__(
        self, file: Path, position: tuple[int, int, int],
        _type: Type, value: int | str
    ) -> None:
        super().__init__(file, position)
        self.type: NodeLiteral.Type = _type
        self.value: int | str = value

    # -Dunder Methods
    def __repr__(self) -> str:
        return (f"NodeLiteral({super().__repr__()}, "
                f"type={self.type.name}, value={self.value})")

    def __str__(self) -> str:
        match self.type:
            case NodeLiteral.Type.Identifier:
                return f"Symbol({self.value})"
            case NodeLiteral.Type.Number:
                return str(self.value)

    # -Sub-Classes
    class Type(IntEnum):
        '''
        Ember Literal Type
        - Represents the node's literal value
        '''
        Identifier = auto()
        Number = auto()

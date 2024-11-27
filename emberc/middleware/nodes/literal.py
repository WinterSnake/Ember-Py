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
    """

    # -Constructor
    def __init__(self, _type: Type, value: int) -> None:
        self.type: NodeLiteral.Type = _type
        self.value: int = value

    # -Dunder Methods
    def __repr__(self) -> str:
        return f"NodeLiteral(type={self.type.name}, value={self.value})"

    def __str__(self) -> str:
        match self.type:
            case NodeLiteral.Type.Number:
                return str(self.value)

    # -Sub-Classes
    class Type(IntEnum):
        '''
        '''
        Number = auto()

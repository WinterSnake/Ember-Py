#!/usr/bin/python
##-------------------------------##
## Ember Compiler: Middleware    ##
## Written By: Ryan Smith        ##
##-------------------------------##
## Node: Binary Expression       ##
##-------------------------------##

## Imports
from __future__ import annotations
from enum import IntEnum, auto
from pathlib import Path

from .base import NodeBase


## Classes
class NodeBinaryExpression(NodeBase):
    """
    """

    # -Constructor
    def __init__(self, _type: Type, lhs: NodeBase, rhs: NodeBase) -> None:
        self.type: NodeBinaryExpression.Type = _type
        self.lhs: NodeBase = lhs
        self.rhs: NodeBase = rhs

    # -Dunder Methods
    def __repr__(self) -> str:
        return f"NodeBinaryExpression(type={self.type.name}, lhs={repr(self.lhs)}, rhs={repr(self.rhs)})"

    def __str__(self) -> str:
        symbol: str
        match self.type:
            case NodeBinaryExpression.Type.Add:
                symbol = '+'
            case NodeBinaryExpression.Type.Sub:
                symbol = '-'
            case NodeBinaryExpression.Type.Mul:
                symbol = '*'
            case NodeBinaryExpression.Type.Div:
                symbol = '/'
            case NodeBinaryExpression.Type.Mod:
                symbol = '%'
        return f"({self.lhs} {symbol} {self.rhs})"

    # -Sub-Classes
    class Type(IntEnum):
        '''
        '''
        Add = auto()
        Sub = auto()
        Mul = auto()
        Div = auto()
        Mod = auto()

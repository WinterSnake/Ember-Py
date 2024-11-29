#!/usr/bin/python
##-------------------------------##
## Ember Compiler: Middleware    ##
## Written By: Ryan Smith        ##
##-------------------------------##
## Node: Expression              ##
##-------------------------------##

## Imports
from __future__ import annotations
from enum import IntEnum, auto
from pathlib import Path

from .base import NodeBase, NodeContextBase


## Classes
class NodeExpressionBinary(NodeContextBase):
    """
    Ember Language AST Node: Expression Binary
    - Node that represents a binary expression and it's
    operator and lhs/rhs nodes
    """

    # -Constructor
    def __init__(
        self, file: Path, position: tuple[int, int, int],
        _type: Type, lhs: NodeBase, rhs: NodeBase
    ) -> None:
        super().__init__(file, position)
        self.type: NodeExpressionBinary.Type = _type
        self.lhs: NodeBase = lhs
        self.rhs: NodeBase = rhs

    # -Dunder Methods
    def __repr__(self) -> str:
        return (f"NodeExpressionBinary({super().__repr__()}, type="
                f"{self.type.name}, lhs={{{self.lhs!r}}}, rhs={{{self.rhs!r}}})")

    def __str__(self) -> str:
        symbol: str = ''
        match self.type:
            case NodeExpressionBinary.Type.Add:
                symbol = '+'
            case NodeExpressionBinary.Type.Sub:
                symbol = '-'
            case NodeExpressionBinary.Type.Mul:
                symbol = '*'
            case NodeExpressionBinary.Type.Div:
                symbol = '/'
            case NodeExpressionBinary.Type.Mod:
                symbol = '%'
            case NodeExpressionBinary.Type.Lt:
                symbol = '<'
            case NodeExpressionBinary.Type.Gt:
                symbol = '>'
            case NodeExpressionBinary.Type.LtEq:
                symbol = '<='
            case NodeExpressionBinary.Type.GtEq:
                symbol = '>='
            case NodeExpressionBinary.Type.EqEq:
                symbol = '=='
            case NodeExpressionBinary.Type.BangEq:
                symbol = '!='
            case _:
                raise NotImplementedError(f"Unhandled type '{self.type.name}'")
        return f"({self.lhs} {symbol} {self.rhs})"

    # -Sub-Classes
    class Type(IntEnum):
        '''
        Ember Binary Type
        - Represents the node's operator value
        '''
        Add = auto()
        Sub = auto()
        Mul = auto()
        Div = auto()
        Mod = auto()
        Lt = auto()
        Gt = auto()
        LtEq = auto()
        GtEq = auto()
        EqEq = auto()
        BangEq = auto()


class NodeExpressionUnary(NodeContextBase):
    """
    Ember Language AST Node: Expression Unary
    - Node that represents a unary expression and it's operator and node
    """

    # -Contructor
    def __init__(
        self, file: Path, position: tuple[int, int, int],
        _type: Type, node: NodeBase
    ) -> None:
        super().__init__(file, position)
        self.type: NodeExpressionUnary.Type = _type
        self.node: NodeBase = node

    # -Dunder Methods
    def __repr__(self) -> str:
        return (f"NodeExpressionUnary({super().__repr__()}, type="
                f"{self.type.name}, node={{{self.node!r}}})")

    def __str__(self) -> str:
        symbol: str = ''
        match self.type:
            case NodeExpressionUnary.Type.Not:
                symbol = '!'
            case NodeExpressionUnary.Type.Negate:
                symbol = '-'
            case _:
                raise NotImplementedError(f"Unhandled type '{self.type.name}'")
        return f"({symbol}({self.node}))"

    # -Sub-Classes
    class Type(IntEnum):
        '''
        Ember Unary Type
        - Represents the node's operator value
        '''
        Not = auto()
        Negate = auto()

#!/usr/bin/python
##-------------------------------##
## Ember Compiler: Middleware    ##
## Written By: Ryan Smith        ##
##-------------------------------##
## Node: Expression              ##
##-------------------------------##

## Imports
from __future__ import annotations

from .base import NodeBase


## Classes
class NodeStatementBlock(NodeBase):
    """
    Ember Language AST Node: Block Statement
    - Node that represents a block of nodes
    """

    # -Constructor
    def __init__(self, nodes: tuple[NodeBase, ...]) -> None:
        self.nodes: tuple[NodeBase, ...] = nodes

    # -Dunder Methods
    def __repr__(self) -> str:
        return f"NodeStatementBlock(nodes={self.nodes})"

    def __str__(self) -> str:
        return '{' + ','.join(str(node) for node in self.nodes) + '}'

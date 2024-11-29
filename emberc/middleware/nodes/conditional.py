#!/usr/bin/python
##-------------------------------##
## Ember Compiler: Middleware    ##
## Written By: Ryan Smith        ##
##-------------------------------##
## Node: Conditional             ##
##-------------------------------##

## Imports
from __future__ import annotations

from .base import NodeBase


## Classes
class NodeConditional(NodeBase):
    """
    Ember Language AST Node: Conditional
    - Node that represents a conditional statement and its true/false blocks
    """

    # -Constructor
    def __init__(
        self, condition: NodeBase,
        true_block: NodeBase, false_block: NodeBase | None
    ) -> None:
        self.condition: NodeBase = condition
        self.true_block: NodeBase = true_block
        self.false_block: NodeBase | None = false_block

    # -Dunder Methods
    def __repr__(self) -> str:
        return (f"NodeConditional(condition={self.condition!r}, true_block="
                f"{self.true_block}, false_block={self.false_block})")

    def __str__(self) -> str:
        _str = f"if({self.condition}) {{ {self.true_block} }}"
        if self.false_block:
            _str += f" else {{ {self.false_block} }}"
        return _str

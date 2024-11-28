#!/usr/bin/python
##-------------------------------##
## Ember Compiler: Middleware    ##
## Written By: Ryan Smith        ##
##-------------------------------##
## Node: Literal                 ##
##-------------------------------##

## Imports
from __future__ import annotations

from .base import NodeBase


## Classes
class NodeLoop(NodeBase):
    """
    Ember Language AST Node: Loop
    - Node that represents a while loop with it's condition and body
    Additionally carries context for running body
    initially before evaluation (do..while)
    """

    # -Constructor
    def __init__(
        self, condition: NodeBase, body: tuple[NodeBase, ...], run_before_eval: bool
    ) -> None:
        self.condition: NodeBase = condition
        self.body: tuple[NodeBase, ...] = body
        self.run_before_eval: bool = run_before_eval  # -true for do..while, false for while

    # -Dunder Methods
    def __repr__(self) -> str:
        return (f"NodeLoop(condition={self.condition!r}, body="
                f"{self.body}, run_before_eval={self.run_before_eval})")

    def __str__(self) -> str:
        body = ','.join(str(statement) for statement in self.body)
        if self.run_before_eval:
            return f"do({self.condition}) {{{body}}}"
        else:
            return f"while({self.condition}) {{{body}}}"

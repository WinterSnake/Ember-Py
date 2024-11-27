#!/usr/bin/python
##-------------------------------##
## Ember Compiler: Middleware    ##
## Written By: Ryan Smith        ##
##-------------------------------##
## Node: Function                ##
##-------------------------------##

## Imports
from __future__ import annotations
from enum import IntEnum, auto
from pathlib import Path

from .base import NodeBase


## Classes
class NodeFunctionDefinition(NodeBase):
    """
    """

    # -Constructor
    def __init__(self, name: str, return_type: str, body: list[NodeBase]) -> None:
        self.name: str = name
        self.return_type: str = return_type
        self.body: list[NodeBase] = body

    # -Dunder Methods
    def __repr__(self) -> str:
        return f"NodeFunctionDefinition()"

    def __str__(self) -> str:
        return f"NodeFunctionDefinition()"

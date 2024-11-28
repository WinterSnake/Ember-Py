#!/usr/bin/python
##-------------------------------##
## Ember Compiler: Middleware    ##
## Written By: Ryan Smith        ##
##-------------------------------##
## Node: Base                    ##
##-------------------------------##

## Imports
from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path


## Classes
class NodeBase(ABC):
    """
    Ember Language AST Node: Base
    - Abstract node that all other AST nodes derive
    """
    pass


class NodeContextBase(NodeBase):
    """
    Ember Language AST Node: Base with Context
    - Abstract node that other AST nodes derive that keep file/position context
    """

    # -Constructor
    def __init__(self, file: Path, position: tuple[int, int, int]) -> None:
        self.file: Path = file
        self.position: tuple[int, int, int] = position

    # -Dunder Methods
    def __repr__(self) -> str:
        return f"file={self.file}, position={self.position}"

    # -Properties
    @property
    def column(self) -> int:
        return self.position[1]

    @property
    def offset(self) -> int:
        return self.position[2]

    @property
    def row(self) -> int:
        return self.position[0]

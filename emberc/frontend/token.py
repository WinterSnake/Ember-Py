#!/usr/bin/python
##-------------------------------##
## Ember Compiler: Frontend      ##
## Written By: Ryan Smith        ##
##-------------------------------##
## Token                         ##
##-------------------------------##

## Imports
from __future__ import annotations
from enum import IntEnum, auto
from pathlib import Path

## Constants


## Functions


## Classes
class Token:
    """
    """

    # -Constructor
    def __init__(self, _type: Type, value: str | None) -> None:
        self.type: Type = _type
        self.value: str | None = value

    # -Dunder Methods
    def __repr__(self) -> str:
        return "Token()"

    def __str__(self) -> str:
        return f"{{type: {self.type.name}, value: {self.value}}}"

    # -Sub-Classes
    class Type(IntEnum):
        '''
        '''
        # -Keywords
        KeywordFunction = auto()
        # -Keyword: Types
        TypeVoid = auto()
        # -Symbols
        SymbolLParen = auto()
        SymbolRParen = auto()
        SymbolLBracket = auto()
        SymbolRBracket = auto()
        SymbolColon = auto()
        SymbolSemicolon = auto()
        # -Symbols: Math
        SymbolPlus = auto()
        SymbolMinus = auto()
        SymbolAsterisk = auto()
        SymbolFSlash = auto()
        SymbolPercent = auto()
        # -Literals
        NumberLiteral = auto()
        Identifier = auto()

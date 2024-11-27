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


## Classes
class Token:
    """
    """

    # -Constructor
    def __init__(
        self, file: Path, position: tuple[int, int, int],
        _type: Type, value: str | None
    ) -> None:
        self.file: Path = file
        self.position: tuple[int, int, int] = position
        self.type: Token.Type = _type
        self.value: str | None = value

    # -Dunder Methods
    def __repr__(self) -> str:
        return "Token()"

    def __str__(self) -> str:
        _str: str = f"Token[{self.file}:{self.row}:{self.column}]"
        _str += f"{{type: {self.type.name}"
        if self.value is not None:
            _str += f", value: {self.value}"
        return _str + '}'

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

    # -Sub-Classes
    class Type(IntEnum):
        '''
        '''
        # -Keywords
        KeywordFunction = auto()
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

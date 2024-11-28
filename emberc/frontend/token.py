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
SYMBOL_COUNT: int
OPERATOR_COUNT: int
WORD_COUNT: int

## Classes
class Token:
    """
    Ember Language Token
    - Represents a token element while lexing the Ember grammar
    Contains it's type in the grammar as well as it's value if applicable
    """

    # -Constructor
    def __init__(
        self, file: Path, position: tuple[int, int, int],
        _type: Type, value: str | None = None
    ) -> None:
        self.file: Path = file
        self.position: tuple[int, int, int] = position
        self.type: Token.Type = _type
        self.value: str | None = value

    # -Dunder Methods
    def __repr__(self) -> str:
        _repr = f"Token(file={self.file}, position={self.position}, type={self.type.name}"
        if self.value is not None:
            _repr += f", value={self.value}"
        return _repr + ')'

    def __str__(self) -> str:
        _str = f"[{self.file}:{self.row}:{self.column}]{self.type.name}"
        if self.value is not None:
            _str += f"::{self.value}"
        return _str

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
        Ember Token Type
        - Represents the symbol, keyword, or literal for the token
        '''

        # -Keywords
        KeywordIf = auto()
        KeywordElse = auto()
        KeywordFor = auto()
        KeywordWhile = auto()
        KeywordDo = auto()
        # -Keywords: Types
        TypeInt32 = auto()
        # -Symbols
        SymbolLParen = auto()
        SymbolRParen = auto()
        SymbolLBracket = auto()
        SymbolRBracket = auto()
        SymbolColon = auto()
        SymbolSemicolon = auto()
        # -Symbols: Operators
        SymbolEq = auto()
        SymbolPlus = auto()
        SymbolMinus = auto()
        SymbolAsterisk = auto()
        SymbolFSlash = auto()
        SymbolPercent = auto()
        SymbolEqEq = auto()
        SymbolLt = auto()
        SymbolGt = auto()
        SymbolLtEq = auto()
        SymbolGtEq = auto()
        # -Literals
        Identifier = auto()
        Number = auto()


## Body
SYMBOL_COUNT = Token.Type.Identifier - Token.Type.SymbolLParen
OPERATOR_COUNT = Token.Type.Identifier - Token.Type.SymbolPlus
WORD_COUNT = Token.Type.SymbolLParen - Token.Type.KeywordIf

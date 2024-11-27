#!/usr/bin/python
##-------------------------------##
## Ember Compiler: Frontend      ##
## Written By: Ryan Smith        ##
##-------------------------------##
## Lexer                         ##
##-------------------------------##

## Imports
from __future__ import annotations
from collections.abc import Generator
from enum import IntEnum, auto
from pathlib import Path
from typing import TextIO

from .token import Token

## Constants
SYMBOLS: tuple[str, ...] = (
    '(', ')', '{', '}', ':', ';',
    # -Math
    '+', '-', '*', '/', '%',
)
STATES: tuple[str, ...] = (
    "None",
    "Word",
    "Number",
)

## Functions
def _get_symbol_type(char: str) -> Token.Type | None:
    """
    """

    match char:
        case '(':
            return Token.Type.SymbolLParen
        case ')':
            return Token.Type.SymbolRParen
        case '{':
            return Token.Type.SymbolLBracket
        case '}':
            return Token.Type.SymbolRBracket
        case ':':
            return Token.Type.SymbolColon
        case ';':
            return Token.Type.SymbolSemicolon
        # -Math
        case '+':
            return Token.Type.SymbolPlus
        case '-':
            return Token.Type.SymbolMinus
        case '*':
            return Token.Type.SymbolAsterisk
        case '/':
            return Token.Type.SymbolFSlash
        case '%':
            return Token.Type.SymbolPercent
        case '_':
            return None


def _get_word_data(buffer: str) -> tuple[Token.Type, str | None]:
    """
    """

    _type = {
        'fn': Token.Type.KeywordFunction,
    }.get(buffer, Token.Type.Identifier)
    value = buffer if _type is Token.Type.Identifier else None
    return (_type, value)


## Classes
class Lexer:
    """
    """

    # -Constructor
    def __init__(self, file: Path | str) -> None:
        if isinstance(file, str):
            file = Path(file)
        self.file: Path = file
        self.row: int = 1
        self.column: int = 0
        self.offset: int = 0
        self._fp: TextIO | None = None

    # -Instance Methods
    # --Lex
    def lex(self) -> Generator[Token, None, None]:
        '''
        '''
        self._fp = self.file.open('r')
        buffer: str = ""
        token_position: tuple[int, int, int] | None = None
        state_current: Lexer.State = Lexer.State.Default
        state_new: Lexer.State = state_current
        while c := self._advance():
            match state_current:
                # -State[Default]
                case Lexer.State.Default:
                    # --Char[Whitespace]
                    if c.isspace():
                        pass
                    # --Char[Symbol]
                    elif c in SYMBOLS:
                        state_new = Lexer.State.Symbol
                        token_position = self.position
                        buffer = c
                    # --Char[Number]
                    elif c.isdigit():
                        state_new = Lexer.State.Number
                        token_position = self.position
                        buffer = c
                    # --Char[Word]
                    elif c.isalpha() or c == '_':
                        state_new = Lexer.State.Word
                        token_position = self.position
                        buffer = c
                # -State[Symbol]
                case Lexer.State.Symbol:
                    # --Char[Whitespace]
                    if c.isspace():
                        assert token_position is not None
                        state_new = Lexer.State.Default
                        token = Token(self.file, token_position, _get_symbol_type(buffer), None)
                        token_position = None
                        buffer = ""
                        yield token
                    # --Char[Symbol]
                    elif c in SYMBOLS:
                        if _get_symbol_type(buffer + c) is not None:
                            buffer += c
                        else:
                            assert token_position is not None
                            token = Token(self.file, token_position, _get_symbol_type(buffer), None)
                            token_position = self.position
                            buffer = c
                            yield token
                    # --Char[Number]
                    elif c.isdigit():
                        assert token_position is not None
                        state_new = Lexer.State.Number
                        token = Token(self.file, token_position, _get_symbol_type(buffer), None)
                        token_position = self.position
                        buffer = c
                        yield token
                    # --Char[Word]
                    elif c.isalpha():
                        assert token_position is not None
                        state_new = Lexer.State.Word
                        token = Token(self.file, token_position, _get_symbol_type(buffer), None)
                        token_position = self.position
                        buffer = c
                        yield token
                # -State[Number]
                case Lexer.State.Number:
                    # --Char[Whitespace]
                    if c.isspace():
                        assert token_position is not None
                        state_new = Lexer.State.Default
                        token = Token(self.file, token_position, Token.Type.NumberLiteral, buffer)
                        token_position = None
                        buffer = ""
                        yield token
                    # --Char[Symbol]
                    elif c in SYMBOLS:
                        assert token_position is not None
                        state_new = Lexer.State.Symbol
                        token = Token(self.file, token_position, Token.Type.NumberLiteral, buffer)
                        token_position = self.position
                        buffer = c
                        yield token
                    # --Char[Number]
                    elif c.isdigit():
                        buffer +=  c
                    # --Char[Word]
                    elif c.isalpha():
                        assert token_position is not None
                        state_new = Lexer.State.Word
                        token = Token(self.file, token_position, Token.Type.NumberLiteral, buffer)
                        token_position = self.position
                        buffer = c
                        yield token
                # -State[Word]
                case Lexer.State.Word:
                    # --Char[Whitespace]
                    if c.isspace():
                        assert token_position is not None
                        state_new = Lexer.State.Default
                        _type, value = _get_word_data(buffer)
                        token = Token(self.file, token_position, _type, value)
                        token_position = None
                        buffer = ""
                        yield token
                    # --Char[Symbol]
                    elif c in SYMBOLS:
                        assert token_position is not None
                        state_new = Lexer.State.Symbol
                        _type, value = _get_word_data(buffer)
                        token = Token(self.file, token_position, _type, value)
                        token_position = self.position
                        buffer = c
                        yield token
                    # --Char[Number | Word | '_']
                    elif c.isalnum() or c == '_':
                        buffer +=  c
            state_current = state_new
        self._fp.close()

    # --Control
    def _advance(self) -> str | None:
        '''
        '''
        assert self._fp is not None
        if self._fp.closed:
            return None
        char = self._fp.read(1)
        if char is None:
            return None
        if char == '\n':
            self.row += 1
            self.column = 0
        else:
            self.column += 1
        self.offset += 1
        return char

    # -Properties
    @property
    def position(self) -> tuple[int, int, int]:
        return (self.row, self.column, self.offset)

    # -Sub-Classes
    class State(IntEnum):
        '''
        '''
        Default = auto()
        Symbol = auto()
        Number = auto()
        Word = auto()

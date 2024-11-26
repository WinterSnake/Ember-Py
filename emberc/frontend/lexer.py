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
def _get_symbol_type(char: str) -> Token.Type:
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
    assert False, "Unreachable"

def _get_word_type(word: str) -> Token.Type:
    """
    """
    return {
        'fn': Token.Type.KeywordFunction,
        # -Types
        'void': Token.Type.TypeVoid,
    }.get(word, Token.Type.Identifier)


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
        self.state: Lexer.State = Lexer.State.Default

    # -Instance Methods
    def lex(self) -> Generator[Token, None, None]:
        self._fp = self.file.open('r')
        buffer: str = ""
        token_position: tuple[int, int, int] | None = None
        while c := self._advance():
            # -Whitespace
            if c.isspace():
                match self.state:
                    # --State[Word]
                    case Lexer.State.Word:
                        assert token_position is not None
                        _type = _get_word_type(buffer)
                        value: str | None = None
                        if _type is Token.Type.Identifier:
                            value = buffer
                        yield Token(self.file, token_position, _type, value)
                    # --State[Number]
                    case Lexer.State.Number:
                        assert token_position is not None
                        yield Token(self.file, token_position, Token.Type.NumberLiteral, buffer)
                self.state = Lexer.State.Default
                buffer = ""
                token_position = None
            # -Word
            elif c.isalpha() or c == '_':
                match self.state:
                    # --State[Default]
                    case Lexer.State.Default:
                        self.state = Lexer.State.Word
                        token_position = self.position
                        buffer = c
                    # --State[Word]
                    case Lexer.State.Word:
                        buffer += c
                    # --State[Number]
                    case Lexer.State.Number:
                        assert False, "Unreachable"
            # -Number
            elif c.isdigit():
                match self.state:
                    # --State[Default]
                    case Lexer.State.Default:
                        self.state = Lexer.State.Number
                        token_position = self.position
                        buffer = c
                    # --State[Word]
                    case Lexer.State.Word:
                        assert False, "Unreachable"
                    # --State[Number]
                    case Lexer.State.Number:
                        buffer += c
            # -Symbol
            elif c in SYMBOLS:
                match self.state:
                    # --State[Word]
                    case Lexer.State.Word:
                        assert token_position is not None
                        _type = _get_word_type(buffer)
                        value: str | None = None
                        if _type is Token.Type.Identifier:
                            value = buffer
                        yield Token(self.file, token_position, _type, value)
                        self.state = Lexer.State.Default
                        self.buffer = ""
                    # --State[Number]
                    case Lexer.State.Number:
                        assert token_position is not None
                        yield Token(self.file, token_position, Token.Type.NumberLiteral, buffer)
                        self.state = Lexer.State.Default
                        self.buffer = ""
                # --State[Default]
                _type = _get_symbol_type(c)
                yield Token(self.file, self.position, _type, None)
        self._fp.close()

    # -Instance Methods: Private
    def _advance(self) -> str | None:
        assert self._fp is not None
        if self._fp.closed:
            return None
        char: str = self._fp.read(1)
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
        Word = auto()
        Number = auto()

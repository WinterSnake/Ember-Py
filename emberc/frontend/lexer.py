#!/usr/bin/python
##-------------------------------##
## Ember Compiler: Frontend      ##
## Written By: Ryan Smith        ##
##-------------------------------##
## Lexer                         ##
##-------------------------------##

## Imports
from collections.abc import Generator
from pathlib import Path
from typing import TextIO

from .token import SYMBOL_COUNT, Token

## Constants
Type_TokenGenerator = Generator[Token, None, None]
SYMBOL_LUT: dict[str, Token.Type] = {
    # -Single-Char
    '(': Token.Type.SymbolLParen,
    ')': Token.Type.SymbolRParen,
    '{': Token.Type.SymbolLBracket,
    '}': Token.Type.SymbolRBracket,
    ':': Token.Type.SymbolColon,
    ';': Token.Type.SymbolSemicolon,
    '=': Token.Type.SymbolEq,
    '+': Token.Type.SymbolPlus,
    '-': Token.Type.SymbolMinus,
    '*': Token.Type.SymbolAsterisk,
    '/': Token.Type.SymbolFSlash,
    '%': Token.Type.SymbolPercent,
    '<': Token.Type.SymbolLt,
    '>': Token.Type.SymbolGt,
    # -Multi-Char
    '<=': Token.Type.SymbolLtEq,
    '>=': Token.Type.SymbolGtEq,
    '==': Token.Type.SymbolEqEq,
}
WORD_LUT: dict[str, Token.Type] = {
    # -Keywords
    # -Types
}


## Classes
class Lexer:
    """
    Ember Language FSM Lexer
    [Lookahead(1)]
    - Every internal lex function represents a state in the lexer
    Each state function controls its own flow and transitions as well
    as creating and returning a token from the given state
    """

    # -Constructor
    def __init__(self, file: Path | str) -> None:
        if isinstance(file, str):
            file = Path(file)
        # -Input data
        self.file: Path = file
        self.row: int = 1
        self.column: int = 0
        self.offset: int = 0
        self._fp: TextIO | None = None
        # -Token data
        self._type: Token.Type | None = None
        self._token_position: tuple[int, int, int] | None = None
        self._buffer: str = ""

    # -Dunder Methods
    def __repr__(self) -> str:
        return f"Lexer(file={self.file})"

    def __str__(self) -> str:
        return f"Lexer[{self.file}:{self.row}:{self.column}]"

    # -Instance Methods
    # --Lexing
    def lex(self) -> Type_TokenGenerator:
        '''
        Returns a generator to get each token from the input file
        Calls internal lexing functions to change states
        '''
        token: Token | None = None
        self._fp = self.file.open('r')
        # -State[Default]
        while c := self._advance():
            # -Char[Whitespace]
            if c.isspace():
                continue
            # -Char[Number]
            if c.isdigit():
                self._buffer = c
                token = self._lex_number()
            # -Char[Symbol]
            elif c in SYMBOL_LUT.keys():
                self._buffer = c
                token = self._lex_symbol()
            # -Char[Word]
            elif c.isalpha() or c == '_':
                self._buffer = c
                token = self._lex_word()
            if token is not None:
                yield token
                token = None
        self._fp.close()

    def _lex_number(self) -> Token:
        '''
        State[Number] lexs a valid number literal token
        '''
        self._type = Token.Type.Number
        if not self._token_position:
            self._token_position = self.position
        # -State[Number]
        while c := self._peek():
            # -Char[Whitespace]
            if c.isspace():
                break
            # -Char[Number]
            elif c.isdigit():
                self._buffer += self._next()
            # -Char[Symbol]
            elif c in SYMBOL_LUT.keys():
                break
            # -Char[Word]
            elif c.isalpha():
                break
        return self._build_token()

    def _lex_symbol(self) -> Token:
        '''
        State[Symbol] lexs a valid symbol token
        '''
        if not self._token_position:
            self._token_position = self.position
        # -State[Symbol]
        while c := self._peek():
            # -Char[Whitespace]
            if c.isspace():
                break
            # -Char[Number]
            elif c.isdigit():
                break
            # -Char[Symbol]
            elif c in SYMBOL_LUT.keys():
                if SYMBOL_LUT.get(self._buffer + c, None):
                    self._buffer += self._next()
                else:
                    break
            # -Char[Word]
            elif c.isalpha():
                break
        self._type = SYMBOL_LUT.get(self._buffer)
        self._buffer = ""
        return self._build_token()

    def _lex_word(self) -> Token:
        '''
        State[Word] lexs a valid word token
        - Handles keywords and identifiers
        '''
        if not self._token_position:
            self._token_position = self.position
        while c := self._peek():
            # -Char[Whitespace]
            if c.isspace():
                break
            # -Char[Symbol]
            elif c in SYMBOL_LUT.keys():
                break
            # -Char[Number|Word]
            elif c.isalnum() or c == '_':
                self._buffer += self._next()
        self._type = WORD_LUT.get(self._buffer, Token.Type.Identifier)
        if self._type is not Token.Type.Identifier:
            self._buffer = ""
        return self._build_token()

    # --Control
    def _build_token(self) -> Token:
        '''
        Builds and returns a Token from the lexer's
        internal state then resets internal token data
        '''
        assert self._type is not None and self._token_position is not None
        token = Token(
            self.file, self._token_position, self._type,
            self._buffer if self._buffer else None
        )
        self._type = None
        self._token_position = None
        self._buffer = ""
        return token

    def _advance(self) -> str | None:
        '''
        Increments file stream to next position and increments lexer's
        internal state; Returns read char or None if end of stream
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

    def _next(self) -> str:
        '''
        Gets next char in file stream and returns it
        or raises compiler error if end of stream
        '''
        # -TODO: Raise compiler error(lexical) if end of stream
        value = self._advance()
        assert value is not None
        return value

    def _peek(self) -> str | None:
        '''
        Gets next char in file stream without incrementing position
        Returns read char or None if end of stream
        '''
        assert self._fp is not None
        if self._fp.closed:
            return None
        position: int = self._fp.tell()
        char = self._fp.read(1)
        if char is None:
            return None
        self._fp.seek(position)
        return char

    # -Properties
    @property
    def position(self) -> tuple[int, int, int]:
        return (self.row, self.column, self.offset)


## Body
assert len(SYMBOL_LUT) == SYMBOL_COUNT, "Not all token symbols handled in Lexer.Symbol LUT"

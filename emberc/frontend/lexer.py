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

from .token import Token

## Constants
TOKEN_GENERATOR = Generator[Token, None, None]
SYMBOLS: tuple[str, ...] = (
    '(', ')', '{', '}', ':', ';',
    '+', '-', '*', '/', '%',
)


## Functions
def _get_symbol_type(buffer: str) -> Token.Type | None:
    """
    Matches the buffer string to a mapped symbol and returns
    the associated token type if applicable or returns None
    """
    match buffer:
        # -Single length symbols
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
    return None


def _get_word_type(buffer: str) -> Token.Type:
    """
    Matches the buffer string to a mapped keyword and returns
    the associated token type if applicable or returns Identifier type
    """
    raise NotImplementedError("_get_word_type() not supported")
    return {
        # -Keywords
        # -Builtin Types
    }.get(buffer, Token.Type.Identifier)


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
        self.file: Path = file
        self.row: int = 1
        self.column: int = 0
        self.offset: int = 0
        self._fp: TextIO | None = None
        self._buffer: str = ""
        self._token_position: tuple[int, int, int] | None = None

    # -Dunder Methods
    def __repr__(self) -> str:
        return f"Lexer(file={self.file})"

    def __str__(self) -> str:
        return f"Lexer[{self.file}:{self.row}:{self.column}]"

    # -Instance Methods
    # --Lexing
    def lex(self) -> TOKEN_GENERATOR:
        '''
        Returns a generator to get each token from the input file
        Calls internal lexing functions to change states
        '''
        token: Token | None = None
        self._fp = self.file.open('r')
        # -State[Default]
        while c := self._next():
            # -Char[Whitespace]
            if c.isspace():
                continue
            # -Char[Number]
            elif c.isdigit():
                self._buffer = c
                token = self._lex_number()
            # -Char[Symbol]
            elif c in SYMBOLS:
                token = self._lex_symbol(c)
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
        self._token_position = self.position
        # -State[Number]
        while c := self._peek():
            # -Char[Whitespace]
            if c.isspace():
                break
            # -Char[Number]
            elif c.isdigit():
                c = self._next()
                assert c is not None
                self._buffer += c
            # -Char[Symbol]
            elif c in SYMBOLS:
                break
            # -Char[Word]
            elif c.isalpha():
                break
        return self._create_token(Token.Type.Number)

    def _lex_symbol(self, buffer: str) -> Token:
        '''
        State[Symbol] lexs a valid symbol token
        '''
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
            elif c in SYMBOLS:
                if _get_symbol_type(buffer + c):
                    c = self._next()
                    assert c is not None
                    buffer += c
                else:
                    break
            # -Char[Word]
            elif c.isalpha():
                break
        symbol_type = _get_symbol_type(buffer)
        assert symbol_type is not None
        return self._create_token(symbol_type)

    def _lex_word(self) -> Token:
        '''
        State[Word] lexs a valid word token
        - Handles keywords and identifiers
        '''
        self._token_position = self.position
        while c := self._peek():
            # -Char[Whitespace]
            if c.isspace():
                break
            # -Char[Symbol]
            elif c in SYMBOLS:
                break
            # -Char[Number|Word]
            elif c.isalnum() or c == '_':
                c = self._next()
                assert c is not None
                self._buffer += c
        word_type = _get_word_type(self._buffer)
        if word_type is not Token.Type.Identifier:
            self._buffer = ""
        return self._create_token(word_type)

    # --Control
    def _create_token(self, _type: Token.Type) -> Token:
        '''
        Internal token creation to create a valid token
        and reset lexer token state
        '''
        assert self._token_position is not None
        value = None if self._buffer == "" else self._buffer
        token = Token(self.file, self._token_position, _type, value)
        self._buffer = ""
        self._token_position = None
        return token

    def _next(self) -> str | None:
        '''
        Returns next character in file and increments lexer position
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

    def _peek(self) -> str | None:
        '''
        Gets next character without advancing the file position
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

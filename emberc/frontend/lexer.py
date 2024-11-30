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

from .token import SYMBOL_COUNT, WORD_COUNT, Token

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
    ',': Token.Type.SymbolComma,
    '=': Token.Type.SymbolEq,
    '!': Token.Type.SymbolBang,
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
    '!=': Token.Type.SymbolBangEq,
}
WORD_LUT: dict[str, Token.Type] = {
    # -Keywords
    'if': Token.Type.KeywordIf,
    'else': Token.Type.KeywordElse,
    'for': Token.Type.KeywordFor,
    'while': Token.Type.KeywordWhile,
    'do': Token.Type.KeywordDo,
    'fn': Token.Type.KeywordFunction,
    'return': Token.Type.KeywordReturn,
    # -Types
    'void': Token.Type.TypeVoid,
    'int8': Token.Type.TypeInt8,
    'int16': Token.Type.TypeInt16,
    'int32': Token.Type.TypeInt32,
    'int64': Token.Type.TypeInt64,
    'uint8': Token.Type.TypeUInt8,
    'uint16': Token.Type.TypeUInt16,
    'uint32': Token.Type.TypeUInt32,
    'uint64': Token.Type.TypeUInt64,
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
            # -State[Default->Number]
            if c.isdigit():
                self._buffer = c
                token = self._lex_number()
            # -State[Default->Symbol]
            elif c in SYMBOL_LUT.keys():
                self._buffer = c
                token = self._lex_symbol()
            # -State[Default->Word]
            elif c.isalpha() or c == '_':
                self._buffer = c
                token = self._lex_word()
            # -State[Token->Default]
            if token is not None:
                yield token
                token = None
        self._fp.close()

    def _lex_number(self) -> Token:
        '''
        State[Number]
        Lexs a valid number literal token
        '''
        self._type = Token.Type.Number
        if not self._token_position:
            self._token_position = self.position
        # -State[Number]
        while c := self._peek():
            # -Char[Number]
            if c.isdigit():
                self._buffer += self._next()
            # -State[Number->Token]
            else:
                break
        return self._token_build()

    def _lex_symbol(self) -> Token | None:
        '''
        State[Symbol]
        Lexs a valid symbol token with greedy search or
        handles comment lexing and discarding
        '''
        if not self._token_position:
            self._token_position = self.position
        # -State[Symbol]
        while c := self._peek():
            # -Char[Symbol]
            if c in SYMBOL_LUT.keys():
                # -State[Symbol->Comment]
                if self._buffer == '/' and c in ('/', '*'):
                    self._advance()
                    self._token_reset()
                    # -State[Comment->Inline Comment]
                    if c == '/':
                        self._lex_comment_inline()
                        return None
                    # -State[Comment->Multiline Comment]
                    else:
                        self._lex_comment_multiline()
                        return None
                # -(Greedy symbol search)
                elif SYMBOL_LUT.get(self._buffer + c, None):
                    self._buffer += self._next()
                # -State[Symbol->Token]
                else:
                    break
            # -State[Symbol->Token]
            else:
                break
        self._type = SYMBOL_LUT.get(self._buffer)
        self._buffer = ""
        return self._token_build()

    def _lex_word(self) -> Token:
        '''
        State[Word]
        Lexs a valid word token with thrifty search for keywords
        '''
        if not self._token_position:
            self._token_position = self.position
        while c := self._peek():
            # -Char[Number|Word]
            if c.isalnum() or c == '_':
                self._buffer += self._next()
            # -State[Word->Token]
            else:
                break
        self._type = WORD_LUT.get(self._buffer, Token.Type.Identifier)
        if self._type is not Token.Type.Identifier:
            self._buffer = ""
        return self._token_build()

    def _lex_comment_inline(self) -> None:
        '''
        State[Inline Comment]
        Consumes chars until new line
        '''
        # -State[Inline Comment]
        while c := self._advance():
            # -State[Inline Comment->Default]
            if c == '\n':
                break

    def _lex_comment_multiline(self) -> None:
        '''
        State[Multiline Comment]
        Consumes chars until it reaches either a multi-line terminator or
        a new multi-line start and recursively nests multi-line lexing
        '''
        # -State[Multiline Comment]
        while c := self._advance():
            # -State[Multiline Comment->Default]
            if c == '*' and self._advance() == '/':
                break
            # -State[Multiline Comment->Multiline Comment]
            elif c == '/' and self._advance() == '*':
                self._lex_comment_multiline()

    # --Control
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

    # --Token Buffer
    def _token_build(self) -> Token:
        '''
        Builds and returns a Token from the lexer's
        internal buffer data then resets it
        '''
        assert self._type is not None and self._token_position is not None
        token = Token(
            self.file, self._token_position, self._type,
            self._buffer if self._buffer else None
        )
        self._token_reset()
        return token

    def _token_reset(self) -> None:
        '''
        Resets internal token buffer data
        '''
        self._type = None
        self._token_position = None
        self._buffer = ""


    # -Properties
    @property
    def position(self) -> tuple[int, int, int]:
        return (self.row, self.column, self.offset)


## Body
assert len(SYMBOL_LUT) == SYMBOL_COUNT, "Not all token symbols handled in Lexer.Symbol LUT"
assert len(WORD_LUT) == WORD_COUNT, "Not all token symbols handled in Lexer.Word LUT"

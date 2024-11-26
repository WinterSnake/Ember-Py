#!/usr/bin/python
##-------------------------------##
## Ember Compiler: Frontend      ##
## Written By: Ryan Smith        ##
##-------------------------------##
## Lexer                         ##
##-------------------------------##

## Imports
from pathlib import Path

from .token import Token

## Constants
KEYWORDS: dict[str, Token.Type] = {
    'fn': Token.Type.KeywordFunction,
    # -Types
    'void': Token.Type.TypeVoid,
}
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
def lex_file(file: str) -> list[Token]:
    """
    """
    tokens: list[Token] = []
    state: str = STATES[0]
    buffer: str = ""
    position = [0, 1]
    fp = open(file, 'r')
    while char := fp.read(1):
        position[1] += 1
        # -Whitespace
        if char.isspace():
            # --State[Word]
            if state == STATES[1]:
                state = STATES[0]
                token = create_word_token(buffer)
                tokens.append(token)
                buffer = ""
            # --State[Number]
            elif state == STATES[2]:
                state = STATES[0]
                token = create_number_token(buffer)
                tokens.append(token)
                buffer = ""
            # --Char[NEW LINE]
            if char == '\n':
                position = [position[0] + 1, 0]
            continue
        # -Character
        elif char.isalpha() or char == '_':
            # --State[None]
            if state == STATES[0]:
                state = STATES[1]
                buffer = char
            # --State[Word]
            elif state == STATES[1]:
                buffer += char
            continue
        # -Symbol
        elif char in SYMBOLS:
            # --State[Word]
            if state == STATES[1]:
                state = STATES[0]
                token = create_word_token(buffer)
                tokens.append(token)
                buffer = ""
            # --State[Number]
            elif state == STATES[2]:
                state = STATES[0]
                token = create_number_token(buffer)
                tokens.append(token)
                buffer = ""
            token = create_symbol_token(char)
            tokens.append(token)
            continue
        # -Numerical
        elif char.isdigit():
            # --State[None]
            if state == STATES[0]:
                state = STATES[2]
                buffer = char
            # --State[Word]
            elif state == STATES[1]:
                buffer += char
            # --State[Number]
            elif state == STATES[2]:
                buffer += char
            continue
    fp.close()
    return tokens


def create_word_token(buffer: str) -> Token:
    """
    """
    _type = KEYWORDS.get(buffer, Token.Type.Identifier)
    if _type is Token.Type.Identifier:
        return Token(_type, buffer)
    return Token(_type, None)


def create_number_token(buffer: str) -> Token:
    """
    """
    return Token(Token.Type.NumberLiteral, buffer)


def create_symbol_token(buffer: str) -> Token:
    """
    """
    match buffer:
        case '(':
            return Token(Token.Type.SymbolLParen, None)
        case ')':
            return Token(Token.Type.SymbolRParen, None)
        case '{':
            return Token(Token.Type.SymbolLBracket, None)
        case '}':
            return Token(Token.Type.SymbolRBracket, None)
        case ':':
            return Token(Token.Type.SymbolColon, None)
        case ';':
            return Token(Token.Type.SymbolSemicolon, None)
        # -Math
        case '+':
            return Token(Token.Type.SymbolPlus, None)
        case '-':
            return Token(Token.Type.SymbolMinus, None)
        case '*':
            return Token(Token.Type.SymbolAsterisk, None)
        case '/':
            return Token(Token.Type.SymbolFSlash, None)
        case '%':
            return Token(Token.Type.SymbolPercent, None)

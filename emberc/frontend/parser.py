#!/usr/bin/python
##-------------------------------##
## Ember Compiler: Frontend      ##
## Written By: Ryan Smith        ##
##-------------------------------##
## Parser                        ##
##-------------------------------##

## Imports
from __future__ import annotations
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .token import OPERATOR_COUNT, Token
from ..middleware.nodes import (
    NodeBase, NodeExpressionBinary, NodeLiteral,
)

if TYPE_CHECKING:
    from .lexer import Type_TokenGenerator

## Constants
Type_OperatorStack = list[tuple[
    Path,
    tuple[int, int, int],
    NodeExpressionBinary.Type,
    int
]]
LITERALS: tuple[Token.Type, ...] = (
    Token.Type.Identifier, Token.Type.Number,
)
OPERATOR_LUT: dict[Token.Type, tuple[NodeExpressionBinary.Type, int]] = {
    Token.Type.SymbolPlus: (NodeExpressionBinary.Type.Add, 1),
    Token.Type.SymbolMinus: (NodeExpressionBinary.Type.Sub, 1),
    Token.Type.SymbolAsterisk: (NodeExpressionBinary.Type.Mul, 2),
    Token.Type.SymbolFSlash: (NodeExpressionBinary.Type.Div, 2),
    Token.Type.SymbolPercent: (NodeExpressionBinary.Type.Mod, 2),
}


## Function
def _build_node_expression_binary(
    nodes: list[NodeBase], operators: Type_OperatorStack
) -> NodeExpressionBinary:
    """
    Builds and returns a NodeExpressionBinary from a node stack and an operator stack
    """
    rhs = nodes.pop()
    lhs = nodes.pop()
    operator = operators.pop()
    return NodeExpressionBinary(operator[0], operator[1], operator[2], lhs, rhs)


## Classes
class Parser:
    """
    Ember Language Recursive-Descent Parser
    [Lookahead(1)]
    - Every internal parse function represents a grammar rule
    in the language and handles returning a node from the given rule
    Hybrid recursive-descent + shunting yard algorithim for parsing expressions
    """

    # -Constructor
    def __init__(self, token_generator: Type_TokenGenerator) -> None:
        self._token_generator: Type_TokenGenerator = token_generator
        self._buffer: Token | None = None

    # -Instance Methods
    # --Parsing
    def parse(self) -> list[NodeBase]:
        '''
        Returns an AST of the given input tokens
        Calls internal parsing functions based on grammar rules
        '''
        statements: list[NodeBase] = []
        while self._peek():
            statements.append(self._parse_statement())
        return statements

    def _parse_statement(self) -> NodeBase:
        '''
        Grammar[Statement]
        expression ';';
        '''
        node = self._parse_expression()
        self._expect(Token.Type.SymbolSemicolon)
        return node

    def _parse_expression(self) -> NodeBase:
        '''
        Grammar[Expression]
        expression_binary;
        '''
        return self._parse_expression_binary()

    def _parse_expression_binary(self) -> NodeBase:
        '''
        Grammar[Expression::Binary]
        primary ( ('+' | '-' | '*' | '/' | '%') primary)*;
        '''
        node_stack: list[NodeBase] = [self._parse_primary()]
        operator_stack: Type_OperatorStack = []
        # -Rule: <operator> primary
        while self._matches(*OPERATOR_LUT.keys()):
            operator_token = self._next()
            operator = OPERATOR_LUT[operator_token.type]
            # -Handle precedence
            while operator_stack and operator[1] <= operator_stack[-1][3]:
                node = _build_node_expression_binary(node_stack, operator_stack)
                node_stack.append(node)
            node_stack.append(self._parse_primary())
            operator_stack.append((
                operator_token.file, operator_token.position, *operator
            ))
        # -Flush operator stack
        while operator_stack:
            node = _build_node_expression_binary(node_stack, operator_stack)
            node_stack.append(node)
        assert len(node_stack) == 1
        return node_stack.pop()


    def _parse_primary(self) -> NodeBase:
        '''
        Grammar[Primary]
        IDENTIFIER | NUMBER | '(' expression ')';
        '''
        node: NodeBase
        # -Rule: ( expression )
        if self._consume(Token.Type.SymbolLParen):
            node = self._parse_expression()
            self._expect(Token.Type.SymbolRParen)
        # -Rule: Literal
        else:
            literal = self._next()
            assert (literal.type in LITERALS and
                    literal.value is not None)
            _type: NodeLiteral.Type
            value: Any
            match literal.type:
                case Token.Type.Identifier:
                    _type = NodeLiteral.Type.Identifier
                    value = literal.value
                case Token.Type.Number:
                    _type = NodeLiteral.Type.Number
                    value = int(literal.value)
                case _:
                    # -TODO: Raise compiler error(syntactical) invalid primary parse
                    pass
            node = NodeLiteral(literal.file, literal.position, _type, value)
        return node

    # --Control
    def _advance(self) -> Token | None:
        '''
        Increment token stream to next position or pops the buffered
        tokens if applicable; Returns found token or None if end of stream
        '''
        if self._buffer is None:
            return next(self._token_generator, None)
        token = self._buffer
        self._buffer = None
        return token

    def _consume(self, _type: Token.Type) -> bool:
        '''
        Checks if next token matches predicate and advances token stream
        position if success; Returns success or raises compiler error if end of stream
        '''
        # -TODO: Raise compiler error(Syntactical) if End of Stream
        token = self._peek()
        assert token is not None
        if token.type is not _type:
            return False
        self._advance()
        return True

    def _expect(self, _type: Token.Type) -> None:
        '''
        Advances token stream and matches token to predicate
        Raises compiler error if type mismatch or end of stream
        '''
        # -TODO: Raise compiler error(Syntactical) if type mismatch or End of Stream
        token = self._advance()
        assert token is not None and token.type is _type

    def _matches(self, *types: Token.Type) -> bool:
        '''
        Checks if next token matches predicate
        without advancing; Returns success
        '''
        token = self._peek()
        if token is None or token.type not in types:
            return False
        return True

    def _next(self) -> Token:
        '''
        Gets next token in token stream and returns it
        or raises compiler error if end of stream
        '''
        # -TODO: Raise compiler error(Syntactical) if end of stream
        token = self._advance()
        assert token is not None
        return token

    def _peek(self) -> Token | None:
        '''
        Gets next token in stream and buffers it
        Returns found token or None if end of stream
        '''
        if not self._buffer:
            self._buffer = next(self._token_generator, None)
        return self._buffer


## Body
assert len(OPERATOR_LUT) == OPERATOR_COUNT, "Not all token symbols handled in Parser.Operator LUT"

#!/usr/bin/python
##-------------------------------##
## Ember Compiler: Frontend      ##
## Written By: Ryan Smith        ##
##-------------------------------##
## Parser                        ##
##-------------------------------##

## Import
from __future__ import annotations
from typing import TYPE_CHECKING

from .token import Token
from ..middleware.nodes import (
    NodeBase, NodeExpressionBinary, NodeLiteral
)

if TYPE_CHECKING:
    from .lexer import TOKEN_GENERATOR


## Functions
def _get_operator_type(_type: Token.Type) -> NodeExpressionBinary.Type:
    """
    Matches the token type to a mapped expression operator
    """
    match _type:
        case Token.Type.SymbolPlus:
            return NodeExpressionBinary.Type.Add
        case Token.Type.SymbolMinus:
            return NodeExpressionBinary.Type.Sub
        case Token.Type.SymbolAsterisk:
            return NodeExpressionBinary.Type.Mul
        case Token.Type.SymbolFSlash:
            return NodeExpressionBinary.Type.Div
        case Token.Type.SymbolPercent:
            return NodeExpressionBinary.Type.Mod
    raise TypeError(f"Unhandled get_operator type '{_type.name}'")


def _get_operator_precedence(_type: NodeExpressionBinary.Type) -> int:
    """
    Matches the expression operator to it's precedence value.
    """
    match _type:
        case NodeExpressionBinary.Type.Add:
            return 1
        case NodeExpressionBinary.Type.Sub:
            return 1
        case NodeExpressionBinary.Type.Mul:
            return 2
        case NodeExpressionBinary.Type.Div:
            return 2
        case NodeExpressionBinary.Type.Mod:
            return 2
    raise TypeError(f"Unhandled get_precedence type '{_type.name}'")


def _build_expression_node(
    nodes: list[NodeBase], operators: list[Token]
) -> NodeExpressionBinary:
    """
    Builds an ExpressionBinary node by popping elements off the nodes stack
    and the operator from the operator stack and returns the constructed node
    """
    rhs = nodes.pop()
    lhs = nodes.pop()
    op_token = operators.pop()
    op = _get_operator_type(op_token.type)
    return NodeExpressionBinary(
        op_token.file, op_token.position, op, lhs, rhs
    )


## Classes
class Parser:
    """
    Ember Language Recursive-Descent Parser
    [Lookahead(1)]
    - Every internal parse function represents a grammar rule
    in the language and handles returning a node from the given rule
    Hybrid recursive-descent + shunting yard algorithim for parsing
    expressions
    """

    # -Constructor
    def __init__(self, tokens: TOKEN_GENERATOR) -> None:
        self._tokens_generator: TOKEN_GENERATOR = tokens
        self._buffer: Token | None = None

    # -Dunder Methods
    def __repr__(self) -> str:
        return f"Parser(tokens={repr(self._tokens_generator)})"

    def __str__(self) -> str:
        return "Parser()"

    # -Instance Methods
    # --Parsing
    def parse(self) -> list[NodeBase]:
        '''
        Returns an AST of the given input tokens
        Calls internal parsing functions based on grammar rules
        '''
        statements: list[NodeBase] = []
        while self._peek():
            statement = self._parse_statement()
            statements.append(statement)
        return statements

    def _parse_statement(self) -> NodeBase:
        '''
        Grammar[Statement]
        expression ';';
        '''
        expression = self._parse_expression()
        self._consume(Token.Type.SymbolSemicolon)
        return expression

    def _parse_expression(self) -> NodeBase:
        '''
        Grammar[Expression]
        primary | primary ('+' | '-' | '*' | '/' | '%') primary;
        '''
        # -Rule: primary
        lhs: NodeBase = self._parse_primary()
        node_stack: list[NodeBase] = [lhs]
        operator_stack: list[Token] = []
        # -Rule: primary operator primary
        # --Add operators to stack
        while self._match(
            Token.Type.SymbolPlus, Token.Type.SymbolMinus,
            Token.Type.SymbolAsterisk, Token.Type.SymbolFSlash,
            Token.Type.SymbolPercent
        ):
            operator_token = self._next()
            assert operator_token is not None
            operator = _get_operator_type(operator_token.type)
            precedence = _get_operator_precedence(operator)
            # --Clear higher precedence operators
            while (
                operator_stack and
                precedence <= _get_operator_precedence(
                    _get_operator_type(operator_stack[-1].type)
                )
            ):
                node = _build_expression_node(node_stack, operator_stack)
                node_stack.append(node)
            rhs = self._parse_primary()
            node_stack.append(rhs)
            operator_stack.append(operator_token)
        # --Clear operator stack
        while operator_stack:
            node = _build_expression_node(node_stack, operator_stack)
            node_stack.append(node)
        assert len(node_stack) == 1 and len(operator_stack) == 0
        return node_stack.pop()

    def _parse_primary(self) -> NodeBase:
        '''
        Grammar[Primary]
        LITERAL | '(' expression ')';
        '''
        node: NodeBase
        primary = self._next()
        assert primary is not None
        # -Rule: ( expression )
        if primary.type is Token.Type.SymbolLParen:
            node = self._parse_expression()
            self._consume(Token.Type.SymbolRParen)
        # -Terminal: LITERAL
        elif primary.type is Token.Type.Number:
            assert primary.value is not None
            node = NodeLiteral(
                primary.file, primary.position,
                NodeLiteral.Type.Number, int(primary.value)
            )
        assert node is not None
        return node

    # --Control
    def _consume(self, _type: Token.Type) -> None:
        '''
        Consumes the token based on the expected token type given
        and returns a parsing error if unable (TODO)
        '''
        token = self._next()
        if token is None:
            print("Invalid consume")
        elif token.type is not _type:
            print("Invalid consume")

    def _match(self, *types: Token.Type) -> bool:
        '''
        Returns if the next token in the input matches the given types
        '''
        token = self._peek()
        if token is not None and token.type in types:
            return True
        return False

    def _next(self) -> Token | None:
        '''
        Returns next token from the token stream
        '''
        if self._buffer is None:
            return next(self._tokens_generator, None)
        token = self._buffer
        self._buffer = None
        return token

    def _peek(self) -> Token | None:
        '''
        Returns next token from token stream and stores in internal buffer
        '''
        if self._buffer is None:
            self._buffer = next(self._tokens_generator, None)
        return self._buffer

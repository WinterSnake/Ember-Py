#!/usr/bin/python
##-------------------------------##
## Ember Compiler: Frontend      ##
## Written By: Ryan Smith        ##
##-------------------------------##
## Parser                        ##
##-------------------------------##

## Imports
from collections.abc import Generator

from .token import Token
from ..middleware.nodes import (
    NodeBase, NodeBinaryExpression, NodeLiteral
)


## Functions
def _get_binary_operator(_type: Token.Type) -> NodeBinaryExpression.Type:
    """
    """
    match _type:
        case Token.Type.SymbolPlus:
            return NodeBinaryExpression.Type.Add
        case Token.Type.SymbolMinus:
            return NodeBinaryExpression.Type.Sub
        case Token.Type.SymbolAsterisk:
            return NodeBinaryExpression.Type.Mul
        case Token.Type.SymbolFSlash:
            return NodeBinaryExpression.Type.Div
        case Token.Type.SymbolPercent:
            return NodeBinaryExpression.Type.Mod
    assert False, f"get binary operator '{_type.name}' not handled"


def _get_operator_precedence(_type: NodeBinaryExpression.Type) -> int:
    """
    """
    match _type:
        case NodeBinaryExpression.Type.Sub:
            return 1
        case NodeBinaryExpression.Type.Add:
            return 1
        case NodeBinaryExpression.Type.Mul:
            return 2
        case NodeBinaryExpression.Type.Div:
            return 2
        case NodeBinaryExpression.Type.Mod:
            return 2
    assert False, f"get binary precedence '{_type.name}' not handled"


## Classes
class Parser:
    """
    """

    # -Constructor
    def __init__(self, generator: Generator[Token, None, None]) -> None:
        self._token_generator: Generator[Token, None, None] = generator
        self._buffer: Token | None = None

    # -Instance Methods
    # -TODO: Error handling + reporting
    # --Parsing
    def parse(self) -> NodeBase:
        '''
        '''
        statements: list[NodeBase] = []
        while self._peek() is not None:
            statement = self._parse_statement()
            statements.append(statement)
        return statements

    def _parse_statement(self) -> NodeBase:
        '''
        '''
        expr = self._parse_expression()
        self._consume(Token.Type.SymbolSemicolon)
        return expr

    def _parse_expression(self) -> NodeBase:
        '''
        '''
        lhs: BaseNode = self._parse_primary()
        node_stack: list[NodeBase] = [lhs]
        operator_stack: list[NodeBinaryExpression.Type] = []
        # -Iterate through operator tokens
        while self._match(
            Token.Type.SymbolPlus, Token.Type.SymbolMinus,
            Token.Type.SymbolAsterisk, Token.Type.SymbolFSlash,
            Token.Type.SymbolPercent
        ):
            binary_operator = _get_binary_operator(self._advance().type)
            precedence: int = _get_operator_precedence(binary_operator)
            # -Operator stack precedence
            while operator_stack and _get_operator_precedence(operator_stack[-1]) >= precedence:
                rhs = node_stack.pop()
                lhs = node_stack.pop()
                operator = operator_stack.pop()
                node_stack.append(NodeBinaryExpression(operator, lhs, rhs))
            # -Add next leaf
            operator_stack.append(binary_operator)
            rhs: BaseNode = self._parse_primary()
            node_stack.append(rhs)
        # -Iterate over operator stack
        while len(operator_stack) > 0:
            rhs = node_stack.pop()
            lhs = node_stack.pop()
            operator = operator_stack.pop()
            node_stack.append(NodeBinaryExpression(operator, lhs, rhs))
        assert len(node_stack) == 1, "Node stack larger than 1"
        return node_stack.pop()

    def _parse_primary(self) -> NodeBase:
        '''
        '''
        if self._peek().type is Token.Type.SymbolLParen:
            self._consume()
            expr = self._parse_expression()
            self._consume(Token.Type.SymbolRParen)
            return expr
        return self._parse_literal()

    def _parse_literal(self) -> NodeBase:
        '''
        '''
        token = self._advance()
        if token.type is Token.Type.NumberLiteral:
            return NodeLiteral(NodeLiteral.Type.Number, int(token.value))

    # --Control
    def _advance(self) -> Token | None:
        '''
        '''
        if self._buffer is None:
            return next(self._token_generator, None)
        token = self._buffer
        self._buffer = None
        return token

    def _consume(self, _type: Token.Type | None = None) -> None:
        '''
        '''
        token = self._advance()
        if token is None:
            print("Invalid consume")
        elif _type is not None and token.type is not _type:
            print("Invalid consume")

    def _peek(self) -> Token | None:
        '''
        '''
        if self._buffer is None:
            self._buffer = next(self._token_generator, None)
        return self._buffer

    def _match(self, *types: Token.Type) -> bool:
        '''
        '''
        token = self._peek()
        if token is not None and token.type in types:
            return True
        return False

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
    NodeBase, NodeFunctionDefinition,
    NodeBinaryExpression, NodeLiteral
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
        return self._parse_function()

    def _parse_function(self) -> NodeBase:
        '''
        '''
        self._consume(Token.Type.KeywordFunction)
        id_token = self._advance()
        assert id_token is not None and id_token.type is Token.Type.Identifier and id_token.value is not None
        self._consume(Token.Type.SymbolLParen)
        self._consume(Token.Type.SymbolRParen)
        self._consume(Token.Type.SymbolColon)
        return_token = self._advance()
        assert return_token is not None and return_token.type is Token.Type.Identifier and return_token.value is not None
        self._consume(Token.Type.SymbolLBracket)
        body: list[NodeBase] = []
        n_token = self._peek()
        while n_token is not None and n_token.type is not Token.Type.SymbolRBracket:
            statement = self._parse_statement()
            body.append(statement)
            n_token = self._peek()
        self._consume(Token.Type.SymbolRBracket)
        return NodeFunctionDefinition(id_token.value, return_token.value, body)

    def _parse_statement(self) -> NodeBase:
        '''
        '''
        expr = self._parse_expression()
        self._consume(Token.Type.SymbolSemicolon)
        return expr

    def _parse_expression(self) -> NodeBase:
        '''
        '''
        lhs: NodeBase = self._parse_primary()
        node_stack: list[NodeBase] = [lhs]
        operator_stack: list[NodeBinaryExpression.Type] = []
        # -Iterate through operator tokens
        while self._match(
            Token.Type.SymbolPlus, Token.Type.SymbolMinus,
            Token.Type.SymbolAsterisk, Token.Type.SymbolFSlash,
            Token.Type.SymbolPercent
        ):
            op_token = self._advance()
            assert op_token is not None
            binary_operator = _get_binary_operator(op_token.type)
            assert binary_operator is not None
            precedence: int = _get_operator_precedence(binary_operator)
            # -Operator stack precedence
            rhs: NodeBase
            while operator_stack and _get_operator_precedence(operator_stack[-1]) >= precedence:
                rhs = node_stack.pop()
                lhs = node_stack.pop()
                operator = operator_stack.pop()
                node_stack.append(NodeBinaryExpression(operator, lhs, rhs))
            # -Add next leaf
            operator_stack.append(binary_operator)
            rhs = self._parse_primary()
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
        n_token = self._peek()
        assert n_token is not None
        if n_token.type is Token.Type.SymbolLParen:
            self._consume()
            expr = self._parse_expression()
            self._consume(Token.Type.SymbolRParen)
            return expr
        return self._parse_literal()

    def _parse_literal(self) -> NodeBase:
        '''
        '''
        token = self._advance()
        assert token is not None
        if token.type is Token.Type.NumberLiteral:
            assert token.value is not None
            return NodeLiteral(NodeLiteral.Type.Number, int(token.value))
        assert False, "Unreachable"

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

    def _match(self, *types: Token.Type) -> bool:
        '''
        '''
        token = self._peek()
        if token is not None and token.type in types:
            return True
        return False

    def _peek(self) -> Token | None:
        '''
        '''
        if self._buffer is None:
            self._buffer = next(self._token_generator, None)
        return self._buffer

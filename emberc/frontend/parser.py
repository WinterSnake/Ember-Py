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
    NodeBase, NodeStatementBlock, NodeConditional, NodeLoop,
    NodeFunctionDeclaration, NodeFunctionCall,
    NodeVarDeclaration, NodeVarAssignment,
    NodeExpressionBinary, NodeExpressionUnary, NodeLiteral,
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
OPERATOR_UNARY_LUT: dict[Token.Type, NodeExpressionUnary.Type] = {
    Token.Type.SymbolBang: NodeExpressionUnary.Type.Not,
    Token.Type.SymbolMinus: NodeExpressionUnary.Type.Negate,
}
OPERATOR_BINARY_LUT: dict[Token.Type, tuple[NodeExpressionBinary.Type, int]] = {
    Token.Type.SymbolEqEq: (NodeExpressionBinary.Type.EqEq, 1),
    Token.Type.SymbolBangEq: (NodeExpressionBinary.Type.BangEq, 1),
    Token.Type.SymbolLt: (NodeExpressionBinary.Type.Lt, 2),
    Token.Type.SymbolGt: (NodeExpressionBinary.Type.Gt, 2),
    Token.Type.SymbolLtEq: (NodeExpressionBinary.Type.LtEq, 2),
    Token.Type.SymbolGtEq: (NodeExpressionBinary.Type.GtEq, 2),
    Token.Type.SymbolPlus: (NodeExpressionBinary.Type.Add, 3),
    Token.Type.SymbolMinus: (NodeExpressionBinary.Type.Sub, 3),
    Token.Type.SymbolAsterisk: (NodeExpressionBinary.Type.Mul, 4),
    Token.Type.SymbolFSlash: (NodeExpressionBinary.Type.Div, 4),
    Token.Type.SymbolPercent: (NodeExpressionBinary.Type.Mod, 4),
}
TYPES: tuple[Token.Type, ...] = (
    Token.Type.TypeVoid,
    Token.Type.TypeInt8, Token.Type.TypeInt16,
    Token.Type.TypeInt32, Token.Type.TypeInt64,
    Token.Type.TypeUInt8, Token.Type.TypeUInt16,
    Token.Type.TypeUInt32, Token.Type.TypeUInt64,
)


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
        conditional | loop | `{` statement* `}` | declaration | `return`? expression `;`;
        '''
        # -Rule: conditional
        if self._consume(Token.Type.KeywordIf):
            return self._parse_conditional()
        # -Rule: loop-for
        elif self._consume(Token.Type.KeywordFor):
            return self._parse_loop_for()
        # -Rule: loop-while
        elif self._consume(Token.Type.KeywordWhile):
            return self._parse_loop_while()
        # -Rule: loop-do
        elif self._consume(Token.Type.KeywordDo):
            return self._parse_loop_do()
        # -Rule: block
        elif self._consume(Token.Type.SymbolLBracket):
            return self._parse_statement_block()
        # -Rule: declaration
        elif node := self._parse_declaration():
            return node
        return_token: Token | None = None
        # -Rule: return
        if self._matches(Token.Type.KeywordReturn):
            return_token = self._next()
        # -Rule: expression
        node = self._parse_expression()
        self._expect(Token.Type.SymbolSemicolon)
        # -Rule: return(finialize)
        if return_token:
            node = NodeExpressionUnary(
                return_token.file, return_token.position,
                NodeExpressionUnary.Type.Return, node
            )
        return node

    def _parse_conditional(self) -> NodeBase:
        '''
        Grammar[Conditional]
        `if` `(` expression `)` statement (`else` statement)?;
        '''
        self._expect(Token.Type.SymbolLParen)
        condition = self._parse_expression()
        self._expect(Token.Type.SymbolRParen)
        true_block: NodeBase = self._parse_statement()
        false_block: NodeBase | None = None
        if self._consume(Token.Type.KeywordElse, False):
            false_block = self._parse_statement()
        return NodeConditional(condition, true_block, false_block)

    def _parse_loop_for(self) -> NodeBase:
        '''
        Grammar[Loop::For]
        `for` `(` (declaration | expression)? `;` expression? `;` expression? `)` statement;
        '''
        self._expect(Token.Type.SymbolLParen)
        # -Initializer
        initializer: NodeBase | None = None
        if not self._consume(Token.Type.SymbolSemicolon):
            if not (initializer := self._parse_declaration()):
                initializer = self._parse_expression()
                self._expect(Token.Type.SymbolSemicolon)
        # -Condition
        condition: NodeBase
        cond_token = self._peek()
        if not self._consume(Token.Type.SymbolSemicolon):
            condition = self._parse_expression()
            self._expect(Token.Type.SymbolSemicolon)
        else:
            assert cond_token is not None
            condition = NodeLiteral(
                cond_token.file, cond_token.position,
                NodeLiteral.Type.Boolean, True
            )
        # -Increment
        increment: NodeBase | None = None
        if not self._consume(Token.Type.SymbolRParen):
            increment = self._parse_expression()
            self._expect(Token.Type.SymbolRParen)
        # -Body
        body: NodeBase = self._parse_statement()
        # -De-sugared nodes
        if increment:
            body = NodeStatementBlock((body, increment))
        loop = NodeLoop(condition, body, False)
        return NodeStatementBlock(
            (initializer, loop) if initializer else (loop,)
        )

    def _parse_loop_while(self) -> NodeBase:
        '''
        Grammar[Loop::While]
        `while` `(` expression `)` statement;
        '''
        self._expect(Token.Type.SymbolLParen)
        condition = self._parse_expression()
        self._expect(Token.Type.SymbolRParen)
        body: NodeBase = self._parse_statement()
        return NodeLoop(condition, body, False)

    def _parse_loop_do(self) -> NodeBase:
        '''
        Grammar[Loop::Do..While]
        `do` statement `while` `(` expression `)` `;`;
        '''
        body = self._parse_statement()
        self._expect(Token.Type.KeywordWhile)
        self._expect(Token.Type.SymbolLParen)
        condition = self._parse_expression()
        self._expect(Token.Type.SymbolRParen)
        self._expect(Token.Type.SymbolSemicolon)
        return NodeLoop(condition, body, True)

    def _parse_declaration(self) -> NodeBase | None:
        '''
        Grammar[Declaration]
        decl_function | decl_variable;
        '''
        if self._consume(Token.Type.KeywordFunction):
            return self._parse_declaration_function()
        return self._parse_declaration_variable()

    def _parse_declaration_function(self) -> NodeBase:
        '''
        Grammar[Declaration::Function]
        `fn` IDENTIFIER `(` param? `)` `:` TYPES `{` statement* `}`;

        param: TYPES IDENTIFIER (`,` param)*;
        TYPES: IDENTIFIER | `void` | `int32`;
        '''
        # -Id
        id_token = self._next()
        assert (id_token.type is Token.Type.Identifier and
                id_token.value is not None)
        # -Parameters
        self._expect(Token.Type.SymbolLParen)
        params: list[str] = []
        while token := self._peek():
            if token.type is Token.Type.SymbolRParen:
                break
            if len(params) > 0:
                self._consume(Token.Type.SymbolComma)
            param_type_token = self._next()
            param_id_token = self._next()
            assert (param_id_token.type is Token.Type.Identifier and
                    param_id_token.value is not None)
            params.append(param_id_token.value)
        self._expect(Token.Type.SymbolRParen)
        # -Return
        self._expect(Token.Type.SymbolColon)
        return_type = self._next()
        # -Body
        self._expect(Token.Type.SymbolLBracket)
        body = self._parse_statement_block()
        parameters = tuple(params) if params else None
        return NodeFunctionDeclaration(
            id_token.file, id_token.position,
            id_token.value, parameters, body
        )

    def _parse_declaration_variable(self) -> NodeBase | None:
        '''
        Grammar[Declaration::Variable]
        TYPES IDENTIFIER (`=` expression)?;

        TYPES: `void` | `int32`;
        '''
        if not self._matches(*TYPES):
            return None
        _type = self._next()
        _id = self._next()
        assert _id.type is Token.Type.Identifier and _id.value is not None
        initializer: NodeBase | None = None
        if self._consume(Token.Type.SymbolEq):
            initializer = self._parse_expression()
        node = NodeVarDeclaration(_id.file, _id.position, _id.value, initializer)
        self._expect(Token.Type.SymbolSemicolon)
        return node

    def _parse_statement_block(self) -> NodeBase:
        '''
        Grammar[Statement::Block]
        `{` statement* `}`
        '''
        body: list[NodeBase] = []
        while token := self._peek():
            if token.type is Token.Type.SymbolRBracket:
                break
            body.append(self._parse_statement())
        self._consume(Token.Type.SymbolRBracket)
        return NodeStatementBlock(tuple(body))

    def _parse_expression(self) -> NodeBase:
        '''
        Grammar[Expression]
        (IDENTIFIER `=`)? expression_binary;
        '''
        # -Rule: expression_binary
        node = self._parse_expression_binary()
        # -Rule: assignment
        if self._consume(Token.Type.SymbolEq):
            value = self._parse_expression()
            node = NodeVarAssignment(node, value)
        return node

    def _parse_expression_binary(self) -> NodeBase:
        '''
        Grammar[Expression::Binary]
        primary (OPERATOR_BINARY primary)*;

        OPERATOR_BINARY: `+` | `-` | `*` | `/` | `%` | `<` | `>` | `<=` | `>=` | `==` | `!=`;
        '''
        node_stack: list[NodeBase] = [self._parse_expression_unary()]
        operator_stack: Type_OperatorStack = []
        # -Rule: <operator> primary
        while self._matches(*OPERATOR_BINARY_LUT.keys()):
            operator_token = self._next()
            operator = OPERATOR_BINARY_LUT[operator_token.type]
            # -Handle precedence
            while operator_stack and operator[1] <= operator_stack[-1][3]:
                node = _build_node_expression_binary(node_stack, operator_stack)
                node_stack.append(node)
            node_stack.append(self._parse_expression_unary())
            operator_stack.append((
                operator_token.file, operator_token.position, *operator
            ))
        # -Flush operator stack
        while operator_stack:
            node = _build_node_expression_binary(node_stack, operator_stack)
            node_stack.append(node)
        assert len(node_stack) == 1
        return node_stack.pop()

    def _parse_expression_unary(self) -> NodeBase:
        '''
        Grammar[Expression::Unary]
        primary | OPERATOR_UNARY expression_unary;

        OPERATOR_UNARY: `!` | `-`;
        '''
        node: NodeBase
        if self._matches(*OPERATOR_UNARY_LUT.keys()):
            operator_token = self._next()
            operator = OPERATOR_UNARY_LUT[operator_token.type]
            node = NodeExpressionUnary(
                operator_token.file, operator_token.position,
                operator, self._parse_expression_unary()
            )
        else:
            node = self._parse_expression_postfix()
        return node

    def _parse_expression_postfix(self) -> NodeBase:
        '''
        Grammar[Expression::Postfix]
        primary (`(` argument? `)`)*;

        argument: expression (`,` argument)*;
        '''
        node = self._parse_primary()
        # -Rule: function call
        if self._consume(Token.Type.SymbolLParen):
            args: list[NodeBase] = []
            # -Arguments
            while token := self._peek():
                if token.type is Token.Type.SymbolRParen:
                    break
                if len(args) > 0:
                    self._consume(Token.Type.SymbolComma)
                args.append(self._parse_expression())
            self._expect(Token.Type.SymbolRParen)
            arguments = tuple(args) if args else None
            node = NodeFunctionCall(node, arguments)
        return node

    def _parse_primary(self) -> NodeBase:
        '''
        Grammar[Primary]
        IDENTIFIER | NUMBER | `(` expression `)`;
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

    def _consume(self, _type: Token.Type, error_on_fail: bool = True) -> bool:
        '''
        Checks if next token matches predicate and advances token stream
        position if success; Returns success or raises compiler error if end of stream
        '''
        # -TODO: Raise compiler error(Syntactical) if End of Stream
        token = self._peek()
        if error_on_fail:
            assert token is not None
        if token is None or token.type is not _type:
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
assert len(OPERATOR_BINARY_LUT) == OPERATOR_COUNT, "Not all token symbols handled in Parser.Operator LUT"

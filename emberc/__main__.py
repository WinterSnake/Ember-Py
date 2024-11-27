#!/usr/bin/python
##-------------------------------##
## Ember Compiler                ##
## Written By: Ryan Smith        ##
##-------------------------------##

## Imports
import sys
from pathlib import Path

from .frontend import Lexer, Parser
from .middleware.nodes import NodeFunctionDefinition, NodeBinaryExpression

## Constants


## Functions
def visit_node(node) -> int | None:
    if isinstance(node, NodeFunctionDefinition):
        print(f"Function[name:{node.name}, return:{node.return_type}]")
        for i, statement in enumerate(node.body):
            print(f"[{i}] = {visit_node(statement)}")
    elif isinstance(node, NodeBinaryExpression):
        lhs = visit_node(node.lhs)
        rhs = visit_node(node.rhs)
        assert lhs is not None and rhs is not None
        match node.type:
            case NodeBinaryExpression.Type.Add:
                return lhs + rhs
            case NodeBinaryExpression.Type.Sub:
                return lhs - rhs
            case NodeBinaryExpression.Type.Mul:
                return lhs * rhs
            case NodeBinaryExpression.Type.Div:
                return lhs // rhs
            case NodeBinaryExpression.Type.Mod:
                return lhs % rhs
    else:
        return node.value
    return None


## Body
lexer = Lexer("./tests/test-00.ember")
parser = Parser(lexer.lex())
ast = parser.parse()
visit_node(ast)

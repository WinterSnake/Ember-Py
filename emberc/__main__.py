#!/usr/bin/python
##-------------------------------##
## Ember Compiler                ##
## Written By: Ryan Smith        ##
##-------------------------------##

## Imports
import sys
from pathlib import Path

from .frontend import Lexer, Parser
from .middleware.nodes import NodeBinaryExpression

## Constants


## Functions
def visit_node(node) -> None:
    if isinstance(node, NodeBinaryExpression):
        lhs = visit_node(node.lhs)
        rhs = visit_node(node.rhs)
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


## Body
lexer = Lexer("./tests/test-00.ember")
parser = Parser(lexer.lex())
ast = parser.parse()
for statement in ast:
    value = visit_node(statement)
    print(value)

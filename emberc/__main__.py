#!/usr/bin/python
##-------------------------------##
## Ember Compiler                ##
## Written By: Ryan Smith        ##
##-------------------------------##

## Imports
import sys
from pathlib import Path

from .frontend import Lexer

## Constants


## Body
lexer = Lexer("./tests/test-00.ember")
for token in lexer.lex():
    print(token)

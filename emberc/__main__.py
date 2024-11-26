#!/usr/bin/python
##-------------------------------##
## Ember Compiler                ##
## Written By: Ryan Smith        ##
##-------------------------------##

## Imports
import sys
from pathlib import Path

from .frontend import lex_file

## Constants


## Body
tokens = lex_file("./tests/test-00.ember")
for token in tokens:
    print(token)

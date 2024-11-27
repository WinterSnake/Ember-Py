#!/usr/bin/python
##-------------------------------##
## Ember Compiler                ##
## Written By: Ryan Smith        ##
##-------------------------------##

## Imports
import sys
from pathlib import Path

from .frontend import Lexer, Parser


## Constants
SRC: Path = None  #type: ignore


## Functions


## Body
if len(sys.argv) < 2:
    print(f"No input file found. Usage: {sys.argv[0]} <file.ember>", file=sys.stderr)
    sys.exit(1)
SRC = Path(sys.argv[1])
if not SRC.exists():
    print(f"'{SRC}' is not a valid file. Usage: {sys.argv[0]} <file.ember>", file=sys.stderr)
    sys.exit(1)
lexer = Lexer(SRC)
parser = Parser(lexer.lex())
ast = parser.parse()
for node in ast:
    print(node)

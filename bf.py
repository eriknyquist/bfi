# This sample shows how to read Brainfuck source code from a text file
# and evaluate it using Brainfuck.interpret()

import sys
import Brainfuck

if len(sys.argv) != 2:
    print 'Usage: %s <brainfuck source file>'
    sys.exit(1)

with open(sys.argv[1], 'r') as fh:
    prog = fh.read()

# Default behaviour is to read/write directly from stdin/stdout
# when , or . is encountered
Brainfuck.interpret(prog)

# Alternatively, setting 'buffer_stdout to True causes all output characters
# to be combined into a string which the 'interpret' method will return after
# the BF program has finished
#
# output = Brainfuck.interpret(prog, buffer_stdout=True)

# Input data can also be passed as a string to the 'interpret' method, and
# the interpreter will use this data instead of reading from stdin
#
# Brainfuck.interpret(prog, stdin="Some input string")


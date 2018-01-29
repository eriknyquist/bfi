import os
import sys
import time
from collections import defaultdict

OPCODE_MOVE   = 0
OPCODE_LEFT   = 1
OPCODE_RIGHT  = 2
OPCODE_ADD    = 3
OPCODE_SUB    = 4
OPCODE_OPEN   = 5
OPCODE_CLOSE  = 6
OPCODE_INPUT  = 7
OPCODE_OUTPUT = 8
OPCODE_CLEAR  = 9
OPCODE_COPY   = 10
OPCODE_SCANL  = 11
OPCODE_SCANR  = 12

opcode_map = {
    "<": OPCODE_LEFT,
    ">": OPCODE_RIGHT,
    "+": OPCODE_ADD,
    "-": OPCODE_SUB,
    "[": OPCODE_OPEN,
    "]": OPCODE_CLOSE,
    ",": OPCODE_INPUT,
    ".": OPCODE_OUTPUT,
}

class BrainfuckSyntaxError(Exception):
    pass

class Opcode(object):
    name_map = {
        OPCODE_MOVE: "move",
        OPCODE_ADD: "add",
        OPCODE_SUB: "sub",
        OPCODE_OPEN: "open",
        OPCODE_CLOSE: "close",
        OPCODE_INPUT: "input",
        OPCODE_OUTPUT: "output",
        OPCODE_CLEAR: "clear",
        OPCODE_COPY: "copy",
        OPCODE_SCANL: "scanl",
        OPCODE_SCANR: "scanr"
    }

    def __init__(self, code, move=0, value=None):
        self.code = code
        self.value = value
        self.move = move

    def __str__(self):
        ret = '%s %d' % (self.name_map[self.code], self.move)
        if self.value is not None:
            ret += ' %s' % self.value

        return ret

def raise_unmatched(brace):
    raise BrainfuckSyntaxError("Error: unmatched '" + brace + "' symbol")

def count_dupes_ahead(string, index):
    """
    Counts the number of repeated characters in 'string', starting at 'index'
    """

    ret = 0
    i = index
    end = len(string) - 1

    while (i < end) and (string[i + 1] == string[i]):
        i += 1
        ret += 1

    return ret

def is_copyloop(program, size, index, ii):
    """
    Detects a copy loop, or a multiply loop and returns equivalent opcodes
    """

    # Copy/multiply loop must start with a decrement
    if (index > (size - 6)) or (program[index + 1] != "-"):
        return [], 0

    mult = 0
    depth = 0
    mults = {}
    i = index + 2

    # Consume the loop contents until the cell pointer movement changes
    # direction. Keep track of pointer movement, and the number of increments
    # at each cell, so we can create Opcodes to recreate the copy / multiply
    # operations performed by the loop
    while i < size:
        if program[i] in "><":
            if mult > 0:
                mults[depth] = mult
                mult = 0

            if program[i] == "<":
                break

            depth += 1

        elif program[i] == "+":
            mult += 1

        else:
            return [], 0

        i += 1

    # If no cell or pointer increments by now, this isn't a copy/multiply loop
    if (len(mults) == 0) or (depth == 0) or (i == (size - 1)):
        return [], 0

    ret = [Opcode(OPCODE_COPY, ii, mults)]

    # Consume all the pointer decrements until the end of the loop.
    # If we encounter any non-"<" characters in the loop at this stage,
    # this isn't a copy/multiply loop (at least, not one I want to mess with!)
    while (i < size) and (program[i] != "]"):
        if program[i] != "<":
            return [], 0

        depth -= 1
        i += 1

    if (depth != 0) or (i == (size - 1)):
        return [], 0

    return ret, (i - index) + 1

def is_scanloop(program, size, index, ii):
    """
    Detects a scan loop and returns equivalent opcodes
    """

    if index < (size - 3):
        clr = program[index : index + 3]

        if clr == "[>]":
            return [Opcode(OPCODE_SCANR, ii)], 3

        elif clr == "[<]":
            return [Opcode(OPCODE_SCANL, ii)], 3

    return [], 0

def is_clearloop(program, size, index, ii):
    """
    Detects a clear loop and returns equivalent opcodes
    """

    if index < (size - 3):
        clr = program[index : index + 3]
        if clr == "[+]" or clr == "[-]":
            return [Opcode(OPCODE_CLEAR, ii)], 3

    return [], 0

def run_optimizers(program, size, index, ii):
    """
    Runs all the loop optimizers on the current token, and returns
    the resulting opcodes of the first one that succeeds
    """

    loop_opts = [
        is_clearloop, is_copyloop, is_scanloop
    ]

    for opt in loop_opts:
        codes, chars = opt(program, size, index, ii)
        if chars > 0:
            return codes, chars

    return [], 0

def parse(program):
    """
    Convert the BF source into some more efficient opcodes. Specifically;
        - Strip out whitespace and any other non-BF characters
        - Replace copy loops, multiply loops, clear loops and scan loops with
          a single opcode that acheives the same effect
        - Collapse sequences of repeated "+", "-", ">" and "<" characters into
          a single opcode
    """

    left_positions = []
    opcodes = []

    program = ''.join(program.split())
    size = len(program)

    pi = 0
    ii = 0

    while pi < size:
        if program[pi] not in opcode_map:
            pi += 1
            continue

        opcode = opcode_map[program[pi]]

        if opcode == OPCODE_OPEN:
            # Optimize common loop constructs
            codes, chars = run_optimizers(program, size, pi, ii)
            if chars > 0:
                opcodes.extend(codes)
                pi += chars
                ii = 0
                continue

            if ii != 0:
                opcodes.append(Opcode(OPCODE_MOVE, 0, ii))
                ii = 0

            # No optimization possible, treat as normal BF loop
            left_positions.append(len(opcodes))
            opcodes.append(Opcode(OPCODE_OPEN))

        elif opcode == OPCODE_CLOSE:
            if len(left_positions) == 0:
                raise_unmatched("]")

            left = left_positions.pop()
            right = len(opcodes)
            opcodes[left].value = right
            opcodes.append(Opcode(OPCODE_CLOSE, ii, left))
            ii = 0

        elif opcode in [OPCODE_INPUT, OPCODE_OUTPUT]:
            opcodes.append(Opcode(opcode_map[program[pi]], ii))
            ii = 0
        else:
            num = count_dupes_ahead(program, pi)
            if opcode == OPCODE_LEFT:
                ii -= (num + 1)
            elif opcode == OPCODE_RIGHT:
                ii += (num + 1)
            else:
                opcodes.append(Opcode(opcode_map[program[pi]], ii, num + 1))
                ii = 0

            pi += num

        pi += 1

    if len(left_positions) != 0:
        raise_unmatched('[')

    return opcodes

class Control:
    def __init__(self, tape_size):
        self.tape = bytearray(tape_size)
        self.size = tape_size
        self.i = 0
        self._i = 0

    def movePointer(self, i, num):
        self._i += num

    def incrementData(self, i, num):
        self._i += i
        self.tape[self._i] = (self.tape[self._i] + num) % 256

    def decrementData(self, i, num):
        self._i += i
        self.tape[self._i] = (self.tape[self._i] - num) % 256

    def clearData(self, i, op_value):
        self._i += i
        self.tape[self._i] = 0

    def copyMultiply(self, i, mults):
        self._i += i

        if self.tape[self._i] == 0:
            return

        for off in mults:
            index = self._i + off
            self.tape[index] = (self.tape[index]
                + (self.tape[self._i] * mults[off])) % 256

        self.tape[self._i] = 0

    def scanLeft(self, i, op_value):
        self._i += i

        while self._i > 0 and self.tape[self._i] != 0:
            self._i -= 1

    def scanRight(self, i, op_value):
        self._i += i

        while self._i < (self.size - 1) and self.tape[self._i] != 0:
            self._i += 1

    def get(self):
        return self.tape[self._i]

    def put(self, intVal):
        self.tape[self._i] = intVal

def execute(opcodes, stdin=None, time_limit=None, tape_size=30000,
              buffer_stdout=False):
    """
    Execute compiled opcodes
    """

    ctrl = Control(tape_size)
    if stdin != None:
        stdin = list(reversed(stdin))

    size = len(opcodes)
    ret = []
    ctrl.i = 0

    def write_stdout(c):
        os.write(1, c)

    def write_buf(c):
        ret.append(c)

    def read_stdin():
        return os.read(0, 1)

    def read_buf():
        try:
            ret = stdin.pop()
        except:
            return ''

        return ret

    do_write = write_buf if buffer_stdout else write_stdout
    do_read = read_stdin if stdin == None else read_buf

    def do_open(i, val):
        if ctrl.get() == 0:
           ctrl.i = val

    def do_close(i, val):
        ctrl.movePointer(0, i)
        if ctrl.get() != 0:
            ctrl.i = val - 1

    def do_output(i, val):
        ctrl.movePointer(0, i)
        do_write(chr(ctrl.get()))

    def do_input(i, val):
        ctrl.movePointer(0, i)
        ch = do_read()
        if len(ch) > 0 and ord(ch) > 0:
            ctrl.put(ord(ch))

    def do_copy(i, val):
        ctrl.copyMultiply(i, val)

    cmd_map = defaultdict(
        lambda: None,
        {
            OPCODE_MOVE: ctrl.movePointer,
            OPCODE_ADD: ctrl.incrementData,
            OPCODE_SUB: ctrl.decrementData,
            OPCODE_CLEAR: ctrl.clearData,
            OPCODE_COPY: do_copy,
            OPCODE_SCANL: ctrl.scanLeft,
            OPCODE_SCANR: ctrl.scanRight,
            OPCODE_OPEN: do_open,
            OPCODE_CLOSE: do_close,
            OPCODE_OUTPUT: do_output,
            OPCODE_INPUT: do_input
        }
    )

    def do_loop():
        op = opcodes[ctrl.i]
        cmd_map[op.code](op.move, op.value)
        ctrl.i += 1

    if time_limit:
        start = time.time()
        while ctrl.i < size:
            do_loop()

            if (time.time() - start) >= time_limit:
                return None
    else:
        while ctrl.i < size:
            do_loop()

    return "".join(ret) if buffer_stdout == True else None

def interpret(program, **kwargs):
    """
    Interpret & execute a brainfuck program
    """

    if not isinstance(program, basestring):
        raise ValueError("expecting a string containing Brainfuck code. "
            "Got %s instead" % type(program))

    opcodes = parse(program)
    return execute(opcodes, **kwargs)

def main():
    if len(sys.argv) != 2:
        print 'Usage: %s <brainfuck source file>'
        sys.exit(1)

    with open(sys.argv[1], 'r') as fh:
        prog = fh.read()

    interpret(prog)

if __name__ == "__main__":
    main()

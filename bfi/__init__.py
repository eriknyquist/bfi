import os
import sys
import time

OPCODE_LEFT   = 0
OPCODE_RIGHT  = 1
OPCODE_ADD    = 2
OPCODE_SUB    = 3
OPCODE_OPEN   = 4
OPCODE_CLOSE  = 5
OPCODE_INPUT  = 6
OPCODE_OUTPUT = 7
OPCODE_CLEAR  = 8
OPCODE_COPY   = 9
OPCODE_SCANL  = 10
OPCODE_SCANR  = 11

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

class BrainfuckMemoryError(Exception):
    pass

class Opcode(object):
    name_map = {
        OPCODE_LEFT: "left",
        OPCODE_RIGHT: "right",
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

    def __init__(self, code, value=None):
        self.code = code
        self.value = value

    def __str__(self):
        ret = '%s' % self.name_map[self.code]
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

def is_copyloop(program, size, index):
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

    ret = [Opcode(OPCODE_COPY, mults)]

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

def is_scanloop(program, size, index):
    """
    Detects a scan loop and returns equivalent opcodes
    """

    if index < (size - 3):
        clr = program[index : index + 3]

        if clr == "[>]":
            return [Opcode(OPCODE_SCANR)], 3

        elif clr == "[<]":
            return [Opcode(OPCODE_SCANL)], 3

    return [], 0

def is_clearloop(program, size, index):
    """
    Detects a clear loop and returns equivalent opcodes
    """

    if index < (size - 3):
        clr = program[index : index + 3]
        if clr == "[+]" or clr == "[-]":
            return [Opcode(OPCODE_CLEAR)], 3

    return [], 0

def run_optimizers(program, size, i):
    """
    Runs all the loop optimizers on the current token, and returns
    the resulting opcodes of the first one that succeeds
    """

    loop_opts = [
        is_clearloop, is_copyloop, is_scanloop
    ]

    for opt in loop_opts:
        codes, chars = opt(program, size, i)
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

    i = 0
    while i < size:
        if program[i] not in opcode_map:
            i += 1
            continue

        opcode = opcode_map[program[i]]

        if opcode == OPCODE_OPEN:
            # Optimize common loop constructs
            codes, chars = run_optimizers(program, size, i)
            if chars > 0:
                opcodes.extend(codes)
                i += chars
                continue

            # No optimization possible, treat as normal BF loop
            left_positions.append(len(opcodes))
            opcodes.append(Opcode(OPCODE_OPEN))

        elif opcode == OPCODE_CLOSE:
            if len(left_positions) == 0:
                raise_unmatched("]")

            left = left_positions.pop()
            right = len(opcodes)
            opcodes[left].value = right
            opcodes.append(Opcode(OPCODE_CLOSE, value=left))

        elif opcode in [OPCODE_INPUT, OPCODE_OUTPUT]:
            opcodes.append(Opcode(opcode_map[program[i]]))

        else:
            num = count_dupes_ahead(program, i)
            opcodes.append(Opcode(opcode_map[program[i]], value=num + 1))
            i += num

        i += 1

    if len(left_positions) != 0:
        raise_unmatched('[')

    return opcodes

class Control:
    def __init__(self, tape_size):
        self.tape = bytearray(tape_size)
        self.size = tape_size
        self.i = 0

    def __checkIndex(self, i):
        if i < 0 or i >= self.size:
            raise BrainfuckMemoryError("Can't access memory at cell %d, must "
                "be within range 0-%d" % (i, self.size - 1))

    def incrementPointer(self, num=1):
        self.i += num

    def decrementPointer(self, num=1):
        self.i -= num

    def incrementData(self, num=1):
        self.__checkIndex(self.i)
        self.tape[self.i] = (self.tape[self.i] + num) % 256

    def decrementData(self, num=1):
        self.__checkIndex(self.i)
        self.tape[self.i] = (self.tape[self.i] - num) % 256

    def clearData(self):
        self.__checkIndex(self.i)
        self.tape[self.i] = 0

    def copyMultiply(self, mults):
        self.__checkIndex(self.i)

        for off in mults:
            index = self.i + off
            self.__checkIndex(index)
            self.tape[index] = (self.tape[index]
                + (self.tape[self.i] * mults[off])) % 256

        self.tape[self.i] = 0

    def scanLeft(self):
        self.__checkIndex(self.i)
        while self.tape[self.i] != 0:
            self.i -= 1

    def scanRight(self):
        self.__checkIndex(self.i)
        while self.tape[self.i] != 0:
            self.i += 1

    def get(self):
        self.__checkIndex(self.i)
        return self.tape[self.i]

    def put(self, intVal):
        self.__checkIndex(self.i)
        self.tape[self.i] = intVal

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
    i = 0

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

    if time_limit != None:
        start = time.time()

    while i < size:
        op = opcodes[i]

        if op.code == OPCODE_RIGHT:
            ctrl.incrementPointer(op.value)

        elif op.code == OPCODE_LEFT:
            ctrl.decrementPointer(op.value)

        elif op.code == OPCODE_ADD:
            ctrl.incrementData(op.value)

        elif op.code == OPCODE_SUB:
            ctrl.decrementData(op.value)

        elif op.code == OPCODE_CLEAR:
            ctrl.clearData()

        elif op.code == OPCODE_COPY:
            if ctrl.get() != 0:
                ctrl.copyMultiply(op.value)

        elif op.code == OPCODE_SCANL:
            ctrl.scanLeft()

        elif op.code == OPCODE_SCANR:
            ctrl.scanRight()

        elif op.code == OPCODE_OPEN:
            if ctrl.get() == 0:
                i = op.value - 1

        elif op.code == OPCODE_CLOSE:
            if ctrl.get() != 0:
                i = op.value - 1

        elif op.code == OPCODE_OUTPUT:
            do_write(chr(ctrl.get()))

        elif op.code == OPCODE_INPUT:
            ch = do_read()
            if len(ch) > 0 and ord(ch) > 0:
                ctrl.put(ord(ch))

        i += 1

        if time_limit != None and (time.time() - start) > time_limit:
            return None

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

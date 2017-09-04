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
    def __init__(self, code, value=None):
        self.code = code
        self.value = value

def raise_unmatched(brace):
    raise BrainfuckSyntaxError("Error: unmatched '" + brace + "' symbol")

def count_dupes_ahead(string, index):
    ret = 0
    i = index
    end = len(string) - 1

    while (i < end) and (string[i + 1] == string[i]):
        i += 1
        ret += 1

    return ret

def is_copyloop(program, size, index):
    if (size - index - 1) < 20:
        MAX_COPYLOOP_LEN = size - index - 1
    else:
        MAX_COPYLOOP_LEN = 20

    if MAX_COPYLOOP_LEN < 2 or program[index + 1] != "-":
        return 0, 0

    i = 0
    depth = 0
    index += 2

    while (i < MAX_COPYLOOP_LEN) and (program[i:i + 2] == ">+"):
        depth += 1
        i += 2

    if depth == 0:
        return 0, 0

    maxdepth = depth

    while i < MAX_COPYLOOP_LEN:
        if program[i] == "]" and depth == 0:
            return maxdepth, i

        elif program[i] != "<":
            return 0, 0

        depth -= 1
        i += 1

    return 0, 0

def parse(program):
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
            # Optimise for 'clear cell value to 0' construct
            if i <= (size - 2):
                clr = program[i : i + 3]
                if clr == "[-]" or clr == "[+]":
                    opcodes.append(Opcode(OPCODE_CLEAR))
                    i += 3
                    continue

            # Optimise for copy-loop construct
            copies, chars = is_copyloop(program, size, i)
            if copies > 0:
                opcodes.append(Opcode(OPCODE_COPY, range(1, copies + 1)))
                opcodes.append(Opcode(OPCODE_CLEAR))
                i += chars + 1
                continue

            left_positions.append(len(opcodes))
            opcodes.append(Opcode(OPCODE_OPEN))

        elif opcode == OPCODE_CLOSE:
            if len(left_positions) == 0:
                raise_unmatched("]")

            left = left_positions.pop()
            right = len(opcodes)
            opcodes[left].value = right
            opcodes.append(Opcode(OPCODE_CLOSE, value=left))

        elif opcode == OPCODE_INPUT or opcode == OPCODE_OUTPUT:
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

    def copyData(self, *offs):
        self.__checkIndex(self.i)
        for off in offs:
            index = self.i + off
            self.__checkIndex(index)
            self.tape[index] = self.tape[self.i]

    def get(self):
        self.__checkIndex(self.i)
        return self.tape[self.i]

    def put(self, intVal):
        self.__checkIndex(self.i)
        self.tape[self.i] = intVal

def print_opcodes(opcodes):
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
        OPCODE_COPY: "copy"
    }

    for op in opcodes:
        print "%s %s" % (name_map[op.code], op.value)

def interpret(program, stdin=None, time_limit=None, tape_size=30000,
              buffer_stdout=False):
    if not isinstance(program, basestring):
        raise ValueError("expecting a string containing Brainfuck code. "
            "Got %s instead" % type(program))

    ctrl = Control(tape_size)
    if stdin != None:
        stdin = list(reversed(stdin))

    opcodes = parse(program)   # IR opcodes
    size = len(opcodes)        # number of opcodes in IR
    ret = []                   # program output
    i = 0                      # index of current character in program

    #print_opcodes(opcodes)

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
            ctrl.copyData(*op.value)
        elif op.code == OPCODE_OPEN and ctrl.get() == 0:
            i = op.value - 1

        elif op.code == OPCODE_CLOSE and ctrl.get() != 0:
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


def main():
    if len(sys.argv) != 2:
        print 'Usage: %s <brainfuck source file>'
        sys.exit(1)

    with open(sys.argv[1], 'r') as fh:
        prog = fh.read()

    interpret(prog)

if __name__ == "__main__":
    main()

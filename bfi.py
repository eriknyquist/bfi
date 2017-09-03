import os
import sys
import time

class BrainfuckSyntaxError(Exception):
    pass

class BrainfuckMemoryError(Exception):
    pass

def raise_unmatched(brace):
    raise BrainfuckSyntaxError("Error: unmatched '" + brace + "' symbol")

def create_jump_table(chars):
    table = {}
    left_positions = []

    for i in range(len(chars)):
        if chars[i] == '[':
            left_positions.append(i)

        elif chars[i] == ']':
            if len(left_positions) == 0:
                raise_unmatched(']')

            left = left_positions.pop()
            table[left] = i
            table[i] = left

    if len(left_positions) != 0:
        raise_unmatched('[')

    return table

class Control:
    def __init__(self, tape_size):
        self.tape = bytearray(tape_size)
        self.size = tape_size
        self.i = 0

    def __checkIndex(self):
        if self.i < 0 or self.i >= self.size:
            raise BrainfuckMemoryError("Can't access memory at cell %d, must "
                "be within 0-%d" % (self.i, self.size))

    def incrementPointer(self, num=1):
        self.i += num

    def decrementPointer(self, num=1):
        self.i -= num

    def incrementData(self, num=1):
        self.__checkIndex()
        self.tape[self.i] = (self.tape[self.i] + num) % 256

    def decrementData(self, num=1):
        self.__checkIndex()
        self.tape[self.i] = (self.tape[self.i] - num) % 256

    def get(self):
        self.__checkIndex()
        return self.tape[self.i]

    def put(self, intVal):
        self.__checkIndex()
        self.tape[self.i] = intVal

def count_dupes_ahead(string, index):
    ret = 0
    i = index
    end = len(string) - 1

    while (i < end) and (string[i + 1] == string[i]):
        i += 1
        ret += 1

    return ret

def interpret(program, stdin=None, time_limit=None, tape_size=30000,
              buffer_stdout=False):
    ctrl = Control(tape_size)
    if stdin != None:
        stdin = list(reversed(stdin))

    size = len(program) # number of characters in the program
    ret = []            # program output
    i = 0               # index of current character in program

    def write_stdout(c):
        os.write(1, c)

    def write_buf(c):
        ret.append(c)

    def read_stdin():
        return os.read(0, 1)

    def read_buf():
        return stdin.pop()

    do_write = write_buf if buffer_stdout else write_stdout
    do_read = read_stdin if stdin == None else read_buf

    jump_table = create_jump_table(program)

    if time_limit != None:
        start = time.time()

    while i < size:
        c = program[i]

        if c == '>':
            num = count_dupes_ahead(program, i)
            ctrl.incrementPointer(num + 1)
            i += num

        elif c == '<':
            num = count_dupes_ahead(program, i)
            ctrl.decrementPointer(num + 1)
            i += num

        elif c == '+':
            num = count_dupes_ahead(program, i)
            ctrl.incrementData(num + 1)
            i += num

        elif c == '-':
            num = count_dupes_ahead(program, i)
            ctrl.decrementData(num + 1)
            i += num

        elif c == '[' and ctrl.get() == 0:
            i = jump_table[i]

        elif c == ']' and ctrl.get() != 0:
            i = jump_table[i]

        elif c == '.':
            do_write(chr(ctrl.get()))

        elif c == ',':
            ch = do_read()
            if len(ch) > 0 and ord(ch) > 0:
                ctrl.put(ord(ch))

        i += 1

        if time_limit != None and (time.time() - start) > time_limit:
            return None

    return ''.join(ret)


def main():
    if len(sys.argv) != 2:
        print 'Usage: %s <brainfuck source file>'
        sys.exit(1)

    with open(sys.argv[1], 'r') as fh:
        prog = fh.read()

    interpret(prog)

if __name__ == "__main__":
    main()

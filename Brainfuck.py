import sys
import time

class Control:
    def __init__(self, tape_size):
        self.tape = bytearray(tape_size)
        self.size = tape_size
        self.i = 0

    def __checkIndex(self):
        if self.i < 0 or self.i >= self.size:
            raise IndexError('Memory access outside cells 0-%d' % self.size)

    def incrementPointer(self, num=1):
        self.i += num

    def decrementPointer(self, num=1):
        self.i -= num

    def incrementData(self, num=1):
        self.__checkIndex()
        if (self.tape[self.i] + num) > 255:
            self.tape[self.i] = (self.tape[self.i] + num) - 255 - 1
        else:
            self.tape[self.i] += num

    def decrementData(self, num=1):
        self.__checkIndex()
        if (self.tape[self.i] - num) < 0:
            self.tape[self.i] = 255 + 1 + (self.tape[self.i] - num)
        else:
            self.tape[self.i] -= num

    def get(self):
        self.__checkIndex()
        return self.tape[self.i]

    def put(self, intVal):
        self.__checkIndex()
        self.tape[self.i] = intVal


def findMatchingBrace(curr, string):
    depth = 1

    for i in range(curr, len(string)):
        if string[i] == '[':
            depth += 1
        elif string[i] == ']':
            if depth == 1:
                return i
            else:
                depth -= 1

    return None

def unmatched(brace):
    print "Error: unmatched '" + brace + "' symbol"
    return None

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
    loops = []          # stack to track loop nesting
    ret = ""            # program output
    i = 0               # index of current character in program

    if time_limit != None:
        start = time.time()

    while i < size:
        c = program[i]

        if c == '>':
            num = count_dupes_ahead(program, i) + 1
            ctrl.incrementPointer(num)
            i += num

        elif c == '<':
            num = count_dupes_ahead(program, i) + 1
            ctrl.decrementPointer(num)
            i += num

        elif c == '+':
            num = count_dupes_ahead(program, i) + 1
            ctrl.incrementData(num)
            i += num

        elif c == '-':
            num = count_dupes_ahead(program, i) + 1
            ctrl.decrementData(num)
            i += num

        elif c == '[':
            # Add this loop to the stack, if not already added
            if i not in [x[0] for x in loops]:
                loops.append([i, None])

            if ctrl.get() == 0:
                # Skip to the end of the loop
                if loops[-1][1] == None:
                    # If this is the first run through the loop,
                    # we don't know the ending index, so we must find it
                    end = findMatchingBrace(i + 1, program)
                    if end == None:
                        raise ValueError("Unmatched '['")

                    loops[-1][1] = end

                i = loops[-1][1] + 1
                loops.pop()
            else:
                i += 1

        elif c == ']':
            if len(loops) == 0:
                raise ValueError("Unmatched ']'")

            # Save loop end index, if not already saved
            if loops[-1][1] == None:
                loops[-1][1] = i

            # Reset to loop start
            i = loops[-1][0]

        elif c == '.':
            char = chr(ctrl.get())
            if buffer_stdout:
                ret += char
            else:
                sys.stdout.write(char)

            i += 1

        elif c == ',':
            if stdin == None:
                ch = sys.stdin.read(1)
            else:
                ch = stdin.pop()

            if len(ch) > 0 and ord(ch) > 0:
                ctrl.put(ord(ch))

            i += 1
        else:
            i += 1

        if time_limit != None and (time.time() - start) > time_limit:
            return None

    if len(loops) != 0:
        raise ValueError("Unmatched '['")

    return ret

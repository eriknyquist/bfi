import os
import time
import glob

from bfi import (interpret, BrainfuckMemoryError)

SAMPLES_DIR = os.path.join("test", "samples")

class SampleCode(object):
    def __init__(self, name):
        self.filename = self._find_filename(name)
        self.fp = None

    def _find_filename(self, name):
        base = os.path.splitext(name)[0]
        pattern = os.path.join(SAMPLES_DIR, base)
        found = glob.glob(pattern + "*")

        if len(found) == 0:
            raise IOError("Can't file any files matching %s" % pattern)
        elif len(found) > 1:
            raise IOError("Multiple files found matching %s: %s"
                % (pattern, found))

        return found[0]

    def __enter__(self):
        self.fp = open(self.filename, "r")
        return self.fp.read()

    def __exit__(self, exc_type, exc_value, traceback):
        self.fp.close()

def verify_tape_size(size):
    increment = ""

    count = size
    while count > 1:
        increment += ">"
        count -= 1

    edge = increment + "."
    over = increment + ">" + "."

    try:
        interpret(edge, tape_size=size, buffer_stdout=True)
    except:
        print "Error: effective tape size is not %s as expected" % size
        raise

    try:
        interpret(over, tape_size=size, buffer_stdout=True)
    except BrainfuckMemoryError:
        pass
    else:
        print "Error: effective tape size is not %s as expected" % size

def verify_exec_time(limit, func, *args, **kwargs):
    start = time.time()
    func(*args, **kwargs)
    end = time.time()

    delta = end - start
    if abs(delta - limit) >= 0.01:
        raise Exception("execution took %.2f secs. Expecting %.2f or less"
            % (delta, limit))


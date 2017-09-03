import unittest

from test.utils import SampleCode, verify_exec_time, verify_tape_size
from bfi import (interpret, BrainfuckMemoryError, BrainfuckSyntaxError)

class TestInterpretArguments(unittest.TestCase):
    def test_stdout_kwarg(self):
        with SampleCode("hello_world") as program:
            self.assertEqual(interpret(program), None)

            ret = interpret(program, buffer_stdout=True)
            self.assertEqual(ret.strip(), "Hello World!")

    def test_time_limit_kwarg(self):
        limits = [0.3, 0.5, 1.2, 1.8]

        for limit in limits:
            verify_exec_time(limit, interpret, "+[><]", time_limit=limit)

    def test_tape_size_kwarg(self):
        sizes = [1, 3, 5, 7, 10, 15, 20, 100, 200, 30000, 300000]
        for size in sizes:
            verify_tape_size(size)

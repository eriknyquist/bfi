import unittest

from bfi.test.utils import SampleCode
from bfi import interpret

class TestSamplePrograms(unittest.TestCase):
    def verify_program(self, name, stdin, stdout):
        with SampleCode(name) as program:
            out = interpret(program, stdin=stdin, buffer_stdout=True)
            self.assertEqual(out, stdout,
                "Brainfuck program %s gave unexpected output: %s" % (name, out))

    def test_hello_world(self):
        self.verify_program("hello_world", None, "Hello World!\n")

    def test_bitwidth(self):
        self.verify_program("bitwidth", None, "Hello World! 255\n")

    def test_eof_behaviour(self):
        self.verify_program("eoftest", "\n\x00", "LK\nLK\n")

    def test_collatz(self):
        self.verify_program("collatz", "fsef\n\x00", "42\n")
        self.verify_program("collatz", "blah\n\x00", "34\n")
        self.verify_program("collatz", "6\n\x00", "8\n")
        self.verify_program("collatz", "66\n\x00", "27\n")

    def test_rot13(self):
        self.verify_program("rot13", "erik\n\x04", "revx\n\x04")
        self.verify_program("rot13", "brainfuck\n\x04", "oenvashpx\n\x04")
        self.verify_program("rot13", "d3adb33f\n\x04", "q3nqo33s\n\x04")

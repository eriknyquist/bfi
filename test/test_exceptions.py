import unittest
from bfi import (interpret, BrainfuckMemoryError, BrainfuckSyntaxError)

class TestBFIExceptions(unittest.TestCase):
    def test_syntax_unmatched_open(self):
        self.assertRaises(BrainfuckSyntaxError, interpret, "[")
        self.assertRaises(BrainfuckSyntaxError, interpret, "[[")
        self.assertRaises(BrainfuckSyntaxError, interpret, "[][")
        self.assertRaises(BrainfuckSyntaxError, interpret, "[[]")
        self.assertRaises(BrainfuckSyntaxError, interpret, "[[[[[]]]]")
        self.assertRaises(BrainfuckSyntaxError, interpret, "++++++>><<[")
        self.assertRaises(BrainfuckSyntaxError, interpret, "[++++++>><<")
        self.assertRaises(BrainfuckSyntaxError, interpret, "[++[+[++>>]<<]")

    def test_syntax_unmatched_close(self):
        self.assertRaises(BrainfuckSyntaxError, interpret, "]")
        self.assertRaises(BrainfuckSyntaxError, interpret, "[]]")
        self.assertRaises(BrainfuckSyntaxError, interpret, "[[]]]")
        self.assertRaises(BrainfuckSyntaxError, interpret, "[[[]]]]")
        self.assertRaises(BrainfuckSyntaxError, interpret, "++++++>><<]")
        self.assertRaises(BrainfuckSyntaxError, interpret, "]++++++>><<")
        self.assertRaises(BrainfuckSyntaxError, interpret, "[[++[+[++>>]]<<]")

    def test_memory_error_low(self):
        self.assertRaises(BrainfuckMemoryError, interpret, "<.")
        self.assertRaises(BrainfuckMemoryError, interpret, "<<.")
        self.assertRaises(BrainfuckMemoryError, interpret, "><<.")
        self.assertRaises(BrainfuckMemoryError, interpret, ">>>>><<<<<<.")

    def test_memory_error_high(self):
        self.assertRaises(BrainfuckMemoryError, interpret, ">>>>>>.",
            tape_size=5)
        self.assertRaises(BrainfuckMemoryError, interpret, "<<>>>>>>>>.",
            tape_size=5)
        self.assertRaises(BrainfuckMemoryError, interpret, ">>>>>>>><<>>.",
            tape_size=5)

    def test_invalid_program(self):
        self.assertRaises(ValueError, interpret, None)
        self.assertRaises(ValueError, interpret, {})
        self.assertRaises(ValueError, interpret, [])
        self.assertRaises(ValueError, interpret, 56)

import unittest
from bfi import (interpret, BrainfuckSyntaxError)

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

    def test_memory_error_high(self):
        self.assertRaises(IndexError, interpret, ">>>>>>.", tape_size=5)
        self.assertRaises(IndexError, interpret, "<<>>>>>>>>.", tape_size=5)
        self.assertRaises(IndexError, interpret, ">>>>>>>><<>>.", tape_size=5)

    def test_invalid_program(self):
        self.assertRaises(BrainfuckSyntaxError, interpret, None)
        self.assertRaises(BrainfuckSyntaxError, interpret, {})
        self.assertRaises(BrainfuckSyntaxError, interpret, [])
        self.assertRaises(BrainfuckSyntaxError, interpret, 56)

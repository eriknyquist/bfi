import unittest

from bfi.test.utils import SampleCode, verify_exec_time, verify_tape_size
from bfi import interpret

class TestInterpretArguments(unittest.TestCase):
    def test_stdout_kwarg(self):
        with SampleCode("hello_world") as program:
            self.assertEqual(interpret(program), None)

            ret = interpret(program, buffer_output=True)
            self.assertEqual(ret.strip(), "Hello World!")

    def test_stdin_stdout_kwargs(self):
        ret = interpret(',>,>,>,<<<.>.>.>.', buffer_output=True, input_data='dddd')
        self.assertEqual('dddd', ret)

        ret = interpret(',>,>,>,<<<.>.>.>.', buffer_output=True, input_data='abcd')
        self.assertEqual('abcd', ret)

        ret = interpret(',>,>,>,>,<<<<.>.>.>.>.', buffer_output=True, input_data='pphhu')
        self.assertEqual('pphhu', ret)

    def test_write_byte_func(self):
        read_data = []

        def write_byte_func(i):
            read_data.append(chr(i))

        ret = interpret(',>,>,>,>,<<<<.>.>.>.>.', write_byte=write_byte_func, input_data='zxcvb')
        self.assertEqual(None, ret)
        self.assertEqual(''.join(read_data), 'zxcvb')

        # Repeat the same test with some different data
        read_data = []
        ret = interpret(',>,>,>,>,<<<<.>.>.>.>.', write_byte=write_byte_func, input_data='howdy')
        self.assertEqual(None, ret)
        self.assertEqual(''.join(read_data), 'howdy')

    def test_read_byte_func(self):
        def read_byte_func1():
            return ord('x')

        ret = interpret(',>,>,>,>,<<<<.>.>.>.>.', read_byte=read_byte_func1, buffer_output=True)
        self.assertEqual(ret, 'xxxxx')

        def read_byte_func2():
            return ord('y')

        ret = interpret(',>,>,>,>,<<<<.>.>.>.>.', read_byte=read_byte_func2, buffer_output=True)
        self.assertEqual(ret, 'yyyyy')

    def test_read_write_byte_funcs(self):
        write_data = []

        def write_byte_func(i):
            write_data.append(chr(i))

        def read_byte_func():
            return ord('q')

        ret = interpret(',>,>,>,>,<<<<.>.>.>.>.', read_byte=read_byte_func, write_byte=write_byte_func)
        self.assertEqual(ret, None)
        self.assertEqual(''.join(write_data), 'qqqqq')

    def test_time_limit_kwarg(self):
        limits = [0.3, 0.5, 1.2, 1.8]

        for limit in limits:
            verify_exec_time(limit, interpret, "+[><]", time_limit=limit)

    def test_tape_size_kwarg(self):
        sizes = [1, 3, 5, 7, 10, 15, 20, 100, 200, 30000, 300000]
        for size in sizes:
            verify_tape_size(size)

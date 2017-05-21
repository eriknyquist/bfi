Brainfuck interpreter
=====================

This is a python-based interpreter for the
`Brainfuck <https://en.wikipedia.org/wiki/Brainfuck>`_ esoteric programming
language. It has several features which make it easier to use in a
genetic programming algorithm that evolves Brainfuck code.

* Allows a maximum run-time to be set, preventing infinite loops
* stdin data can optionally be passed to the Brainfuck program as a string
  parameter when invoking the interpreter method, and stdout data from the
  Brainfuck program can optionally be buffered and returned as a string


Implementation details
----------------------

* No change on EOF
* Tape size is configurable, default is 300,000 cells
* Cells are one byte, valid values between 0-255. Overflow/underflow wraps
  around

Reference
---------

The Brainfuck module only has one method of interest, the ``interpret`` method:

.. code:: python

   Brainfuck.interpret(program, stdin=None, time_limit=None, tape_size=300000, buffer_stdout=False):

* **Parameter** ``program``: String. Brainfuck code to be interpreted
* **Parameter** ``stdin``: String. stdin data for Brainfuck program. If not set,
  input will be read directly from stdin as normal
* **Parameter** ``time_limit``: Float. If the interpreter runs for longer than
  ``time_limit`` seconds, return without finishing the program (NOTE: this won't
  work if your program is blocking on a read from stdin)
* **Parameter** ``tape_size``: String. Number of cells in the tape-- the array
  of memory cells-- used by the Brainfuck program
* **Parameter** ``buffer_stdout``: Boolean. If true, any output printed by the
  Brainfuck program will be buffered and returned as a string, rather than
  printed directly to stdout

**Return value:** If ``buffer_stdout`` is set, a string containing the output
data is returned. Otherise, an empty string is returned. If ``time_limit`` is
reached before the interpreter completes, ``None`` is returned.

**Exceptions:** Throws ``ValueError`` for unmatched ``[`` or ``]`` characters.
Throws ``IndexError`` for a bad cell access (cell pointer outside the tape).

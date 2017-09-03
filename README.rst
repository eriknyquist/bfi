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

Check out `BrainfuckIntern <https://github.com/eriknyquist/BrainfuckIntern>`_,
a Python program that writes Brainfuck programs, using this very Brainfuck
interpreter to provide information for a useful fitness evaluation on generated
Brainfuck programs

Implementation details
----------------------

* No change on EOF
* Tape size is configurable, default is 30,000 cells
* Cells are one byte, valid values between 0-255. Overflow/underflow wraps
  around

Using the interpreter from the command-line
--------------------------------------------

The brainfuck interpreter can be invoked from the command line using the
``bf.py`` script. Several sample Brainfuck programs are provided in the
``examples`` directory. Just run ``bf.py`` and pass your brainfuck source
file. For examle, to play "Lost Kingdom", a text-based adventure game written
in Brainfuck, you can run this command:

::

    $> python bfi.py examples/LostKingdom.b


Using the interpreter in your own code
--------------------------------------

You can also import the Brainfuck module to call its ``interpret()`` method
in your own code. This allows you to access some extra features, like
passing program input data directly to the interpreter as a string, obtaining
program output data as a string returned by the interpreter, and imposing
a maximum time limit for program execution to help prevent infinite loops.

Here is how you use the bfi module to execute some Brainfuck code
normally (reading data directly from stdin and writing directly to stdout):

::

    >>> import bfi
    >>> with open('samples/hello_world.b', 'r') as fh:
    ...     brainfuck_code = fh.read()
    ...
    >>> Brainfuck.interpret(brainfuck_code)
    Hello World!


Here is how you use the bfi module to execute some Brainfuck code without
reading/writing the user's terminal; input is passed a parameter to
``interpret()``, and any output is returned as a string.

::

    >>> input_data = "test input"
    >>> ret = bfi.interpret(brainfuck_code, stdin=input_data, buffer_stdout=True)
    >>> print ret
    Hello World!

Reference
---------

The bfi module only has one method of interest, the ``interpret`` method:

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

**Exceptions:** Throws ``BrainfuckSyntaxError`` for unmatched ``[`` or ``]``
characters. Throws ``BrainfuckMemoryError`` for a bad cell access (cell pointer
outside the tape).vi Br 

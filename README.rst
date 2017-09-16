Brainfuck interpreter
=====================

This is a python-based interpreter for the
`Brainfuck <https://en.wikipedia.org/wiki/Brainfuck>`_ esoteric programming
language. ``bfi`` implements the standard optimisations for clear loop, copy
loop, multiply loop and scan loop constructs, and is reasonably fast. The
"towers of hanoi" Brainfuck program (``hanoi.b``) completes in about 2 minutes
(compared to over an hour using a python-based interpreter with no
optimisations),  and the mandelbrot fractal set viewer (``mandel.b``) completes
in about 30 minutes (compared to over 2 hours using a python-based interpreter
with no optimisations).

Some minor extra features;

* Allows a maximum run-time to be set, preventing infinite loops (useful for
  auto-generated brainfuck code)
* stdin data can optionally be passed to the Brainfuck program as a string
  parameter when invoking the interpreter method, and stdout data from the
  Brainfuck program can optionally be buffered and returned as a string

Check out `BrainfuckIntern <https://github.com/eriknyquist/BrainfuckIntern>`_,
an implementation of a genetic algorithm that writes Brainfuck programs,
using ``bfi`` to provide information for a useful fitness evaluation on generated
Brainfuck programs

Implementation details
----------------------

* No change on EOF
* Tape size is configurable, default is 30,000 cells
* Cells are one byte, valid values between 0-255. Overflow/underflow wraps
  around

Installing
----------

Use ``pip`` to install:

::

    pip install bfi

Using the interpreter from the command-line
--------------------------------------------

Once installed, the brainfuck interpreter can be invoked from the command line
using the ``bfi`` command. Just run ``bfi`` and pass a brainfuck source file.
Several sample Brainfuck programs are provided in the ``examples`` directory
within the installed package (in your system's python2.7/dist-packages
directory- on linux-based systems, for example, the full path might be
/usr/local/lib/python2.7/dist-packages/bfi/examples).

In the sample commands below, we will run "Lost Kingdom", a text-based adventure
game written in Brainfuck:

::

    $> cd <dist-packages-directory>/bfi/examples
    $> bfi LostKingdom.b


Using the interpreter in your own code
--------------------------------------

Here is how you use the ``bfi`` module to execute some Brainfuck code
normally (reading data directly from stdin and writing directly to stdout):

::

    >>> import bfi
    >>> with open('samples/hello_world.b', 'r') as fh:
    ...     brainfuck_code = fh.read()
    ...
    >>> Brainfuck.interpret(brainfuck_code)

    Hello World!


Here is how you use the ``bfi`` module to execute some Brainfuck code without
reading/writing the user's terminal; input is passed a parameter to
``interpret()``, and any output is returned as a string.

::

    >>> input_data = "test input"
    >>> ret = bfi.interpret(brainfuck_code, stdin=input_data, buffer_stdout=True)
    >>> print ret

    Hello World!

Reference
---------

``bfi.interpret``
#################

.. code:: python

   bfi.interpret(program, stdin=None, time_limit=None, tape_size=300000, buffer_stdout=False)

Simplest usage of ``bfi``. Calls ``bfi.parse`` and ``bfi.execute`` to execute
a string of brainfuck source code

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

**Exceptions:** Raises ``bfi.BrainfuckSyntaxError`` for unmatched ``[`` or ``]``
characters. Raises ``bfi.BrainfuckMemoryError`` for a bad cell access

``bfi.parse``
#############

.. code:: python

   bfi.parse(program)

Reads a string of brainfuck source and compiles to intermediate opcodes

* **Parameter** ``program`` : String. Brainfuck source code to be parsed

**Return value:** list of compiled opcodes

**Exceptions** Raises ``bfi.BrainfuckSyntaxError`` for unmatched ``[`` or ``]``
characters.

``bfi.execute``
###############

.. code:: python

   bfi.execute(opcodes, <keyword_args>)

Executes a list of compiled opcodes

* **Parameter** ``opcodes`` : List. Opcodes to be executed

* **Parameter** ``<keyword_args>``: ``bfi.execute`` takes the same keyword
  arguments as ``bfi.interpret``

**Return value:** If ``buffer_stdout`` is set, a string containing the output
data is returned. Otherise, an empty string is returned. If ``time_limit`` is
reached before the interpreter completes, ``None`` is returned.

**Exceptions** Raises ``bfi.BrainfuckMemoryError`` for bad cell access

Gratuitous unnecessary extras
-----------------------------

In order to make Brainfuck code execute more efficiently, it is compiled into
an intermediate form that takes advantage of common brainfuck idioms and
constructs. This intermediate form consists of 12 opcodes, 8 of which are
similar to the original 8 brainfuck instructions. Here is a description of the
12 opcodes, and what they do:

+-----------------------------------+-----------------------------------------+
|            **Opcode**             |             **Description**             |
+-----------------------------------+-----------------------------------------+
|          ``left <num>``           | Decrements the cell pointer by ``<num>``|
|                                   | cells pointer outside the tape).        |
+-----------------------------------+-----------------------------------------+
|          ``right <num>``          | Increments the cell pointer by ``<num>``|
|                                   | cells                                   |
+-----------------------------------+-----------------------------------------+
|          ``sub <num>``            | Decrements value of current cell by     |
|                                   | ``<num>`` cells                         |
+-----------------------------------+-----------------------------------------+
|          ``add <num>``            | Increments value of current cell by     |
|                                   | ``<num>`` cells                         |
+-----------------------------------+-----------------------------------------+
|         ``open <location>``       | ``<location>`` is an index into the list|
|                                   | of program opcodes. If the value of     |
|                                   | current cell is zero, jump to           |
|                                   | ``<location>``. Otherwise, continue     |
|                                   | execution normally (Same functionality  |
|                                   | as brainfuck "[" instruction, except    |
|                                   | jump location is stored with opcode)    |
+-----------------------------------+-----------------------------------------+
|         ``close <location>``      | ``<location>`` is an index into the list|
|                                   | of program opcodes. If the value of     |
|                                   | current cell is zero, continue execution|
|                                   | normally. Otherwise, jump to            |
|                                   | ``<location>`` (Same functionality as   |
|                                   | brainfuck "]" instruction, except jump  |
|                                   | location is stored with opcode)         |
+-----------------------------------+-----------------------------------------+
|             ``input``             | Read one character of input and write to|
|                                   | current cell                            |
+-----------------------------------+-----------------------------------------+
|             ``output``            | Print value of current cell as ASCII    |
|                                   | character                               |
+-----------------------------------+-----------------------------------------+
|             ``clear``             | Set value of current cell to zero       |
+-----------------------------------+-----------------------------------------+
|  ``copy {<off>:<mult>, ... }``    | For each key/value pair, set the value  |
|                                   | of the cell at (current cell + ``<off>``|
|                                   | ) to be (value of current cell *        |
|                                   | ``<mult>``)                             |
+-----------------------------------+-----------------------------------------+
|             ``scanl``             | Decrement the cell pointer until it     |
|                                   | points at a cell containing 0           |
+-----------------------------------+-----------------------------------------+
|             ``scanr``             | Increment the cell pointer until it     |
|                                   | points at a cell containing 0           |
+-----------------------------------+-----------------------------------------+

If you *really want to*, you can actually view a brainfuck program in this
intermediate form, by using the ``bfi.parse`` method and printing the resulting
opcodes:

::

    >>> with open('bfi/examples/mandel.b', 'r') as fh:
    ...     program = fh.read()
    ... 
    >>> opcodes = bfi.parse(program)
    >>> for c in opcodes: print c
    ...

    add 13
    copy {1: 2, 4: 5, 5: 2, 6: 1}
    right 5
    add 6
    right 1
    sub 3
    right 10
    add 15
    open 18
    open 11

    ... (long output, truncated...)

And of course, you can execute the compiled opcodes as many times as you like
using ``bfi.execute``.

Example Brainfuck programs
--------------------------

I have included several random Brainfuck programs that I've found in various
places. I didn't write any of these programs, I just copied them as-is
from other public sources. Descriptive comments (and author's name, in some
cases) can be seen in the Brainfuck source files themselves.

A description of the example Brainfuck programs included with this package
follows:

* **bfcl.bf**: A Brainfuck-to-ELF translator, in Brainfuck. Reads in Brainfuck
  source from stdin and writes a Linux ELF file to stdout

* **bitwidth.bf** Assorted tests for Brainfuck interpreter/compiler correctness

* **collatz.b** A demonstration of the Collatz problem in Brainfuck

* **eoftest.b** Tests EOF behaviour of brainfuck interpreters/compilers

* **fib.b** Prints a neverending fibonacci sequence

* **gameoflife.b** Conway's Game of Life in Brainfuck

* **hanoi.b** Towers of Hanoi in Brainfuck

* **hello_world.b** Classic "hello, world!" in Brainfuck

* **LostKingdom.b** A text-based adventure game in Brainfuck

* **mandel.b** An ASCII  mandelbrot fractal set viewer in Brainfuck

* **numwarp.b** Prints an enlarged ASCII representation of numbers entered by
  the user

* **primes.bf** Prints prime numbers

* **rot13.b** Prints the ROT13 encoding of the string entered by the user

* **sierpinksi.b** Displays the Sierpinksi triangle

* **TheBrainfuckedLoneWolf.b** ASCII asteroids-inspired top-down shooter game
  in Brainfuck

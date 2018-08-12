fast Brainfuck interpreter in pure python
=========================================

This is a pure python interpreter for the
`Brainfuck <https://en.wikipedia.org/wiki/Brainfuck>`_ esoteric programming
language. ``bfi`` implements the standard optimisations for clear loop, copy
loop, multiply loop and scan loop constructs, and is reasonably fast without
requiring any special python implementations or compiled extension modules.
Supports Python 2x and 3x.

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

Speed benchmark
---------------

Here is a quick comparison between ``bfi`` and two other popular pure-python
brainfuck interpreters on github. The time show is the time that each
interpreter took to complete the "Towers of Hanoi" program (``hanoi.b``,
available in the ``examples`` directory):

+---------------------------------------------------------------------------------+-------------------------------+
| **Interpreter name**                                                            | **Time to complete hanoi.b**  |
+=================================================================================+===============================+
| bfi                                                                             | 1 minute, 30 seconds          |
+---------------------------------------------------------------------------------+-------------------------------+
| `pocmo's interpreter <https://github.com/pocmo/Python-Brainfuck>`_              | 28 minutes, 51 seconds        |
+---------------------------------------------------------------------------------+-------------------------------+
| `alexprengere's intrepreter <https://github.com/alexprengere/PythonBrainFuck>`_ | 1 hour, 7 minutes, 54 seconds |
+---------------------------------------------------------------------------------+-------------------------------+

(I should note here that alexprengere's interpreter can actually go
much faster than this, but not without using the alternative PyPy interpreter,
or compiling some stuff. Speeds here are shown without such optimisations.
All tests were done using the standard CPython 2.7.14 interpreter)

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

Documentation for the python API is here: `<https://bfi.readthedocs.io>`_

Gratuitous unnecessary extras
-----------------------------

In order to make Brainfuck code execute more efficiently, it is compiled into
an intermediate form that takes advantage of common brainfuck idioms and
constructs. This intermediate form consists of 11 opcodes, 8 of which are
similar to the original 8 brainfuck instructions. The following table describes
the opcodes:

+-----------------------------------+-----------------------------------------+
|            **Opcode**             |             **Description**             |
+===================================+=========================================+
|          ``move <off> <num>``     | Moves the cell pointer by ``<num>``     |
|                                   | cells. ``<off>`` is unused              |
+-----------------------------------+-----------------------------------------+
|          ``sub <off> <num>``      | Moves the cell pointer by ``<off>``, and|
|                                   | decrements value of current cell by     |
|                                   | ``<num>`` cells                         |
+-----------------------------------+-----------------------------------------+
|          ``add <off> <num>``      | Moves the cell pointer by ``<off>``, and|
|                                   | increments value of current cell by     |
|                                   | ``<num>`` cells                         |
+-----------------------------------+-----------------------------------------+
|         ``open <off> <location>`` | ``<location>`` is an index into the list|
|                                   | of program opcodes. If the value of     |
|                                   | current cell is zero, jump to           |
|                                   | ``<location>``. Otherwise, continue     |
|                                   | execution normally (Same functionality  |
|                                   | as brainfuck "[" instruction, except    |
|                                   | jump location is stored with opcode).   |
|                                   | ``<off>`` is unused                     |
+-----------------------------------+-----------------------------------------+
|         ``close <off> <location>``| ``<location>`` is an index into the list|
|                                   | of program opcodes. If the value of     |
|                                   | current cell is zero, continue execution|
|                                   | normally. Otherwise, jump to            |
|                                   | ``<location>`` (Same functionality as   |
|                                   | brainfuck "]" instruction, except jump  |
|                                   | location is stored with opcode). In all |
|                                   | cases the cell pointer will be moved by |
|                                   | ``<off>``                               |
+-----------------------------------+-----------------------------------------+
|             ``input <off>``       | Moves the cell pointer by ``<off>``,    |
|                                   | then reads one character of input and   |
|                                   | writes to current cell                  |
+-----------------------------------+-----------------------------------------+
|             ``output <off>``      | Moves the cell pointer by ``<off>``,    |
|                                   | then prints value of current cell as    |
|                                   | an ASCII character                      |
+-----------------------------------+-----------------------------------------+
|             ``clear <off>``       | Moves the cell pointer by ``<off>``,    |
|                                   | then sets the value of current cell to  |
|                                   | zero                                    |
+-----------------------------------+-----------------------------------------+
|  ``copy <off> {<o>:<m>,... }``    | Moves the cell pointer by ``<off>``,    |
|                                   | then for each key/value pair, sets the  |
|                                   | value of the cell at (current cell +    |
|                                   | ``<o>``) to be (value of current cell * |
|                                   | ``<m>``)                                |
+-----------------------------------+-----------------------------------------+
|             ``scanl <off>``       | Moves the cell pointer by ``<off>``,    |
|                                   | then decrements the cell pointer until  |
|                                   | it points at a cell containing 0        |
+-----------------------------------+-----------------------------------------+
|             ``scanr <off>``       | Moves the cell pointer by ``<off>``,    |
|                                   | then increments the cell pointer until  |
|                                   | it points at a cell containing 0        |
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

    add 0 13
    copy 0 {1: 2, 4: 5, 5: 2, 6: 1}
    add 5 6
    sub 1 3
    add 10 15
    open 0 12
    open 0 7
    close 9 6
    add 0 1
    open 0 10

    ... (long output, truncated ...)

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

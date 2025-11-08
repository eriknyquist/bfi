.. |brain| unicode:: 0x1F9E0

Fast Brainfuck interpreter in pure python |brain|
=================================================

.. |tests_badge| image:: https://github.com/eriknyquist/bfi/actions/workflows/tests.yml/badge.svg
.. |version_badge| image:: https://badgen.net/bfi/v/bfi
.. |license_badge| image:: https://badgen.net/pypi/license/bfi
.. |downloads_badge| image:: https://static.pepy.tech/badge/bfi

|tests_badge| |version_badge| |license_badge| |downloads_badge|

This is a pure python interpreter for the
`Brainfuck <https://en.wikipedia.org/wiki/Brainfuck>`_ esoteric programming
language. ``bfi`` is quite fast without requiring any special python implementations
or compiled extension modules. ``bfi`` Supports Python 2x and 3x.

``bfi`` achieves a significant speedup in the execution of brainfuck
programs by first compiling brainfuck source code into an intermediate form.
This intermediate form takes advantage of common brainfuck programming constructs
to execute much faster than if we were to interpret & execute the brainfuck source directly.

Take moving the cell pointer, as a relativey simple example; to execute ``<<<<<<<<<<``,
we could iterate over each ``<`` character, and perform 10 separate "cell pointer decrement"
operations. This would be the slow option. Alternatively, we could collapse those 10 instructions
into a single instruction to decrement the cell pointer by 10 in a single operation. This is
generally how the opcodes for the intermediate form work. All runs of cell pointer
increment/decrements are collapsed like this, as well as several other similar optimizations.


Speed benchmark
---------------

Here is a quick comparison between ``bfi`` and two other popular pure-python
brainfuck interpreters on github. The time shown is the time that each
interpreter took to complete the "Towers of Hanoi" program (``hanoi.b``,
available in the ``examples`` directory):

+---------------------------------------------------------------------------------+-------------------------------+
| **Interpreter name**                                                            | **Time to complete hanoi.b**  |
+=================================================================================+===============================+
| bfi                                                                             | 1 minute, 9 seconds           |
+---------------------------------------------------------------------------------+-------------------------------+
| `pocmo's interpreter <https://github.com/pocmo/Python-Brainfuck>`_              | 28 minutes, 51 seconds        |
+---------------------------------------------------------------------------------+-------------------------------+
| `alexprengere's intrepreter <https://github.com/alexprengere/PythonBrainFuck>`_ | 1 hour, 7 minutes, 54 seconds |
+---------------------------------------------------------------------------------+-------------------------------+

(I should note here that alexprengere's interpreter can actually go
much faster than this, but not without using the alternative PyPy interpreter,
or compiling some stuff. Speeds here are shown without such modifications.
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
using the ``bfi`` command, or using ``python -m bfi``. Just run ``bfi`` and pass
a brainfuck source file. Several sample Brainfuck programs are provided in the
``examples`` directory within the installed package-- use ``bfi -e`` to show the
paths of all installed example files:

::

    $> bfi -e

    C:\Users\Gamer\AppData\Roaming\Python\Python311\site-packages\bfi\examples\bfcl.bf
    C:\Users\Gamer\AppData\Roaming\Python\Python311\site-packages\bfi\examples\bitwidth.bf
    C:\Users\Gamer\AppData\Roaming\Python\Python311\site-packages\bfi\examples\collatz.b
    C:\Users\Gamer\AppData\Roaming\Python\Python311\site-packages\bfi\examples\eoftest.b
    C:\Users\Gamer\AppData\Roaming\Python\Python311\site-packages\bfi\examples\fib.b
    C:\Users\Gamer\AppData\Roaming\Python\Python311\site-packages\bfi\examples\gameoflife.b
    C:\Users\Gamer\AppData\Roaming\Python\Python311\site-packages\bfi\examples\hanoi.b
    C:\Users\Gamer\AppData\Roaming\Python\Python311\site-packages\bfi\examples\hello_world.b
    C:\Users\Gamer\AppData\Roaming\Python\Python311\site-packages\bfi\examples\LostKingdom.b
    C:\Users\Gamer\AppData\Roaming\Python\Python311\site-packages\bfi\examples\mandel.b
    C:\Users\Gamer\AppData\Roaming\Python\Python311\site-packages\bfi\examples\numwarp.b
    C:\Users\Gamer\AppData\Roaming\Python\Python311\site-packages\bfi\examples\primes.bf
    C:\Users\Gamer\AppData\Roaming\Python\Python311\site-packages\bfi\examples\rot13.b
    C:\Users\Gamer\AppData\Roaming\Python\Python311\site-packages\bfi\examples\sierpinski.b
    C:\Users\Gamer\AppData\Roaming\Python\Python311\site-packages\bfi\examples\TheBrainfuckedLoneWolf.b

In the sample commands below, we will run "Lost Kingdom", a text-based adventure
game written in Brainfuck:

::

    $> bfi C:\Users\Gamer\AppData\Roaming\Python\Python311\site-packages\bfi\examples\LostKingdom.b


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

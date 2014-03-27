=====
Macht
=====

A `2048`_ clone in python with Terminal UI

.. image:: https://mediacru.sh/vxW8AH7nzr6B.gif
   :target: https://mediacru.sh/vxW8AH7nzr6B

Install
-------

Using the `pip` package manager: ::

    pip install macht


Or: ::

    python ./setup.py install

Play
----
::

    macht

Or without installing (in the project directory): ::

    python -m macht

Use either the arrow keys or the ``wasd`` keys or the ``hjkl`` keys to move the tiles.

Options
-------

Specify the board size: ::

    macht 5x5

Play on multiple grids simultaneously: ::

     macht 3x3 3x3 3x3

Play with a different base number: ::

     macht --base 3

To display a help message use the ``-h/--help`` option.

.. _`2048`: http://gabrielecirulli.github.io/2048/
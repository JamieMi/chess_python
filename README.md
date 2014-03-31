chess_python
============

An attempt at a chess game - I'm doing this in parallel projects in Python and C++, although this version has got a little ahead of the C++ original. Please forgive the naivety of my beginner's Python. The GUI is presented using tkinter.

Pieces are simply bitmaps - if any bitmaps aren't all available, the pieces are presented as characters. To run in console mode, just set the variable GUI to False.

Note that the computer can be played against itself, or the computer can be asked to play a move at any point - it proves quite useful to me in testing! Note the AI uses no transposition table at the moment.

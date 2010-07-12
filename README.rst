MagicManhole
============

Provides normal ColoredManhole features (python REPL with automatic
syntax coloring and history), plus some readline-y niceness like C-a
(beginning-of-line), C-e (end-of-line), C-h (backspace), C-u
(unix-line-discard), C-w (unix-word-rubout), and C-y (yank).

Todo
----

 * tab-completion a la rlcompleter_ module
 * telnet login/password protection

.. _rlcompleter: http://docs.python.org/library/rlcompleter.html

Example
-------

Example usage as a `.tac`_::

  from MagicManhole import MagicManhole

  application = service.Application("ripcordd")
  hole = MagicManhole(globals())
  hole.setServiceParent(application)

Connecting::

  telnet localhost 6022

.. _`.tac`: http://twistedmatrix.com/documents/current/core/howto/application.html

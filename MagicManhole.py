# MagicManhole.py
#
# generic telnet-based colored manhole setup for a twisted app
# the paul <p@thepaul.org>

from twisted.application import internet, service
from twisted.internet import protocol
from twisted.conch import manhole, insults, telnet
import string

class ReadlineyManhole(manhole.ColoredManhole):
    wordseparators = '/()+-[]{}:;\'"?<>.,^&*%#!\\|`' + string.whitespace

    def connectionMade(self):
        manhole.ColoredManhole.connectionMade(self)
        # support C-a, C-e, C-h, C-u with their normal readline/bash-type
        # behaviors
        self.keyHandlers.update({
            '\x01': self.handle_HOME,
            '\x05': self.handle_END,
            '\x08': self.handle_BACKSPACE,
            '\x15': self.handle_KILLLINE,
            '\x17': self.handle_KILLWORD,
            '\x19': self.handle_YANK
        })
        self.yankbuffer = []
        self.lastWasKillWord = False

    def handle_KILLLINE(self):
        oldcontents = self.yankbuffer
        self.yankbuffer = self.lineBuffer[:self.lineBufferIndex]
        if self.lastWasKillWord:
            self.yankbuffer += oldcontents
        del self.lineBuffer[:self.lineBufferIndex]
        self.handle_HOME()
        self.terminal.eraseToLineEnd()

    def handle_KILLWORD(self):
        oldpos = self.lineBufferIndex
        while self.lineBufferIndex > 0 \
        and self.lineBuffer[self.lineBufferIndex-1].isspace():
            self.lineBufferIndex -= 1
        ate_a_word = False
        while self.lineBufferIndex > 0 \
        and self.lineBuffer[self.lineBufferIndex-1] not in self.wordseparators:
            self.lineBufferIndex -= 1
            ate_a_word = True
        if self.lineBufferIndex > 0 and not ate_a_word:
            self.lineBufferIndex -= 1
        oldcontents = self.yankbuffer
        self.yankbuffer = self.lineBuffer[self.lineBufferIndex:oldpos]
        del self.lineBuffer[self.lineBufferIndex:oldpos]
        if self.lastWasKillWord:
            self.yankbuffer += oldcontents
        for i in range(oldpos - self.lineBufferIndex):
            self.terminal.cursorBackward()
            self.terminal.deleteCharacter()
        self.isThisKillWord = True

    def handle_YANK(self):
        if len(self.yankbuffer) == 0:
            return
        # save a bit of work with the syntax coloring
        lastpart = len(self.yankbuffer) - 1
        while lastpart > 0 and self.yankbuffer[lastpart].isspace():
            lastpart -= 1
        for c in self.yankbuffer[:lastpart]:
            self.characterReceived(c, True)
        for c in self.yankbuffer[lastpart:]:
            self.characterReceived(c, False)

    def keystrokeReceived(self, keyID, modifier):
        self.isThisKillWord = False
        manhole.ColoredManhole.keystrokeReceived(self, keyID, modifier)
        self.lastWasKillWord = bool(self.isThisKillWord)

def MagicManholeFactory(namespace):
    f = protocol.ServerFactory()
    f.protocol = lambda: telnet.TelnetTransport(
        telnet.TelnetBootstrapProtocol,
        insults.insults.ServerProtocol,
        ReadlineyManhole,
        namespace
    )
    return f

def MagicManhole(namespace, port=6022, interface='localhost'):
    """
    Create and register a service offering a telnet server on the given
    port and interface. When a connection is made there, an interactive
    Python REPL will be provided with items from the given namespace
    available.

    Note that the given namespace will be copied, not used directly.
    """

    return internet.TCPServer(port, MagicManholeFactory(namespace),
                              interface=interface)

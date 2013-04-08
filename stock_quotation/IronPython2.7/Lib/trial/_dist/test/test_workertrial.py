# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for L{twisted.trial._dist.workertrial}.
"""

import errno
import sys
from cStringIO import StringIO

from twisted.protocols.amp import AMP
from twisted.test.proto_helpers import StringTransport
from twisted.trial.unittest import TestCase
from twisted.trial._dist.workertrial import WorkerLogObserver, main
from twisted.trial._dist import (
    workertrial, _WORKER_AMP_STDIN, _WORKER_AMP_STDOUT, workercommands,
    managercommands)



class FakeAMP(AMP):
    """
    A fake amp protocol.
    """



class WorkerLogObserverTestCase(TestCase):
    """
    Tests for L{WorkerLogObserver}.
    """

    def test_emit(self):
        """
        L{WorkerLogObserver} forwards data to L{managercommands.TestWrite}.
        """
        calls = []

        class FakeClient(object):

            def callRemote(self, method, **kwargs):
                calls.append((method, kwargs))

        observer = WorkerLogObserver(FakeClient())
        observer.emit({'message': ['Some log']})
        self.assertEqual(
            calls, [(managercommands.TestWrite, {'out': 'Some log'})])



class MainTestCase(TestCase):
    """
    Tests for L{main}.
    """

    def setUp(self):
        self.readStream = StringIO()
        self.writeStream = StringIO()
        self.patch(workertrial, 'startLoggingWithObserver',
                   self.startLoggingWithObserver)
        self.addCleanup(setattr, sys, "argv", sys.argv)
        sys.argv = ["trial"]


    def fdopen(self, fd, mode=None):
        """
        Fake C{os.fdopen} implementation which returns C{self.readStream} for
        the stdin fd and C{self.writeStream} for the stdout fd.
        """
        if fd == _WORKER_AMP_STDIN:
            self.assertIdentical(None, mode)
            return self.readStream
        elif fd == _WORKER_AMP_STDOUT:
            self.assertEqual('w', mode)
            return self.writeStream
        else:
            raise AssertionError("Unexpected fd %r" % (fd,))


    def startLoggingWithObserver(self, emit, setStdout):
        """
        Override C{startLoggingWithObserver} for not starting logging.
        """
        self.assertFalse(setStdout)


    def test_empty(self):
        """
        If no data is ever written, L{main} exits without writing data out.
        """
        main(self.fdopen)
        self.assertEqual('', self.writeStream.getvalue())


    def test_forwardCommand(self):
        """
        L{main} forwards data from its input stream to a L{WorkerProtocol}
        instance which writes data to the output stream.
        """
        client = FakeAMP()
        clientTransport = StringTransport()
        client.makeConnection(clientTransport)
        client.callRemote(workercommands.Run, testCase="doesntexist")
        self.readStream = clientTransport.io
        self.readStream.seek(0, 0)
        main(self.fdopen)
        self.assertIn(
            "No module named 'doesntexist'", self.writeStream.getvalue())


    def test_readInterrupted(self):
        """
        If reading the input stream fails with a C{IOError} with errno
        C{EINTR}, L{main} ignores it and continues reading.
        """
        excInfos = []

        class FakeStream(object):
            count = 0

            def read(oself, size):
                oself.count += 1
                if oself.count == 1:
                    raise IOError(errno.EINTR)
                else:
                    excInfos.append(sys.exc_info())
                return ''

        self.readStream = FakeStream()
        main(self.fdopen)
        self.assertEqual('', self.writeStream.getvalue())
        self.assertEqual([(None, None, None)], excInfos)


    def test_otherReadError(self):
        """
        L{main} only ignores C{IOError} with C{EINTR} errno: otherwise, the
        error pops out.
        """

        class FakeStream(object):
            count = 0

            def read(oself, size):
                oself.count += 1
                if oself.count == 1:
                    raise IOError("Something else")
                return ''

        self.readStream = FakeStream()
        self.assertRaises(IOError, main, self.fdopen)

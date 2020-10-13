"""
BSD 2-Clause License

Copyright (c) 2020, Davide De Tommaso (dtmdvd@gmail.com)
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

https://en.wikipedia.org/wiki/Logic_gate
"""

from quantica.core import QPlace, QNet, QTransition
import threading
import logging

class QGate(object):

    def __init__(self, name):
        self.__A__ = None
        self.__B__ = None
        self.__Q__ = None
        self._net = QNet(name, logging_level=logging.INFO)
        self._pA = self._net.createPlace('pA')
        self._pB = self._net.createPlace('pB')
        self._pQ = self._net.createPlace('pQ')
        self.__lock__ = threading.Lock()

    @property
    def A(self):
        return self.__A__

    @property
    def B(self):
        return self.__B__

    @property
    def Q(self):
        return self.__Q__

    @property
    def pA(self):
        return self._pA

    @property
    def pB(self):
        return self._pB

    @property
    def pQ(self):
        return self._pQ

    @property
    def qnet(self):
        return self._net

    def __setinput__(self, A: bool, B: bool):
        self._net.reset()
        self._net.produce(self._pA, int(A))
        self._net.produce(self._pB, int(B))
        self._net.next_until_end()

    def __getoutput__(self):
        q = self._net.getTokens(self._pQ)
        return bool(q)

    def set(self, A: bool, B: bool=True):
        with self.__lock__:
            self.__setinput__(A, B)
            self.__Q__ = self.__getoutput__()
            return self.__Q__

class QOR(QGate):

    def __init__(self):
        QGate.__init__(self, 'QOR')
        t1 = self.qnet.createTransition()
        t2 = self.qnet.createTransition()
        self.qnet.connect(self.pA, t1, 1)
        self.qnet.connect(self.pB, t2, 1)
        self.qnet.connect(t1, self.pQ, 1)
        self.qnet.connect(t2, self.pQ, 1)

class QAND(QGate):

    def __init__(self):
        QGate.__init__(self, 'QAND')
        t = self.qnet.createTransition()
        self.qnet.connect(self.pA, t, 1)
        self.qnet.connect(self.pB, t, 1)
        self.qnet.connect(t, self.pQ, 1)

class QBUFFER(QGate):

    def __init__(self):
        QGate.__init__(self, 'QBUFFER')
        t = self.qnet.createTransition()
        self.qnet.connect(self.pA, t, 1)
        self.qnet.connect(t, self.pQ, 1)

class QNOT(QGate):

    def __init__(self):
        QGate.__init__(self, 'QNOT')
        p3 = self.qnet.createPlace(init_tokens=1)
        t1 = self.qnet.createTransition()
        self.qnet.connect(p3, t1, 1)
        self.qnet.connect(t1, self.pQ, 1)

        p4 = self.qnet.createPlace()
        t2 = self.qnet.createTransition()
        self.qnet.connect(p4, t2, 1)
        self.qnet.connect(t2, p4, 1)
        self.qnet.connect(t2, self.pQ, 1)


        t3 = self.qnet.createTransition()
        self.qnet.connect(self.pA, t3, 1)
        self.qnet.connect(t3, self.pA, 1)
        self.qnet.connect(self.pQ, t3, 1)

        p5 = self.qnet.createPlace()
        self.qnet.connect(t3, p5, 1)
        self.qnet.connect(p5, t2, 1)


class QNAND(QGate):

    def __init__(self):
        QGate.__init__(self, 'QNAND')
        p3 = self.qnet.createPlace(init_tokens=1)
        t1 = self.qnet.createTransition()
        self.qnet.connect(p3, t1, 1)
        self.qnet.connect(t1, self.pQ, 1)

        p4 = self.qnet.createPlace()
        t2 = self.qnet.createTransition()
        self.qnet.connect(p4, t2, 1)
        self.qnet.connect(t2, p4, 1)
        self.qnet.connect(t2, self.pQ, 1)

        p5 = self.qnet.createPlace()
        t3 = self.qnet.createTransition()
        self.qnet.connect(p5, t3, 1)
        self.qnet.connect(t3, p5, 1)
        self.qnet.connect(t3, self.pQ, 1)

        p6 = self.qnet.createPlace()
        self.qnet.connect(p6, t2, 1)
        self.qnet.connect(p6, t3, 1)

        t4 = self.qnet.createTransition()
        self.qnet.connect(t4, p6, 1)
        self.qnet.connect(self.pQ, t4, 1)

        self.qnet.connect(t4, self.pA, 1)
        self.qnet.connect(self.pA, t4, 1)
        self.qnet.connect(t4, self.pB, 1)
        self.qnet.connect(self.pB, t4, 1)

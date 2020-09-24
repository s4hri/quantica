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
"""

"""
ex1-producerconsumer.py

Producer-Consumer example presented in
http://petrinet.org/#ProducerConsumer
"""

from core import QPlace, QNet, QTransition


class Producer(QNet):

    def __init__(self):
        QNet.__init__(self, nid='Producer')
        self.T0 = self.createTransition()
        self.P0 = self.createPlace(init_tokens=1)
        self.T1 = self.createTransition()
        self.P1 = self.createPlace()

        self.connect(self.T0, self.P0, weight=1)
        self.connect(self.P0, self.T1, weight=1)
        self.connect(self.T1, self.P1, weight=1)
        self.connect(self.P1, self.T0, weight=1)


class Buffer(QNet):

    def __init__(self):
        QNet.__init__(self, nid='Buffer')
        self.P2 = self.createPlace()

class Consumer(QNet):

    def __init__(self):
        QNet.__init__(self, nid='Consumer')
        self.P3 = self.createPlace()
        self.P4 = self.createPlace(init_tokens=1)
        self.T2 = self.createTransition()
        self.T3 = self.createTransition()
        self.connect(self.T2, self.P3, weight=1)
        self.connect(self.P3, self.T3, weight=1)
        self.connect(self.T3, self.P4, weight=1)
        self.connect(self.P4, self.T2, weight=1)


class ProdCons(QNet):

    def __init__(self):
        QNet.__init__(self, nid='ProdCons')
        self.producer = Producer()
        self.consumer = Consumer()
        self.buf = Buffer()

        self.addNet(self.producer)
        self.addNet(self.consumer)
        self.addNet(self.buf)

        self.connect(self.producer.T1, self.buf.P2, weight=1)
        self.connect(self.buf.P2, self.consumer.T2, weight=1)

net = ProdCons()

print(net.state())
for i in iter(net):
    input(i.state())

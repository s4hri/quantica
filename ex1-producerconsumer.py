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

from quantica import QPlace, QNet, QTransition


class Producer(QNet):

    def __init__(self):
        QNet.__init__(self)
        self.T0 = QTransition(label="T0")
        self.T1 = QTransition(label="T1")
        self.P0 = QPlace(label="P0", init_tokens=1)
        self.P1 = QPlace(label="P1")

        self.connect(self.T0, self.P0, weight=1)
        self.connect(self.P0, self.T1, weight=1)
        self.connect(self.T1, self.P1, weight=1)
        self.connect(self.P1, self.T0, weight=1)


class Consumer(QNet):

    def __init__(self):
        QNet.__init__(self)
        self.T2 = QTransition(label="T2")
        self.T3 = QTransition(label="T3")
        self.P3 = QPlace(label="P3")
        self.P4 = QPlace(label="P4", init_tokens=1)

        self.connect(self.T2, self.P3, weight=1)
        self.connect(self.P3, self.T3, weight=1)
        self.connect(self.T3, self.P4, weight=1)
        self.connect(self.P4, self.T2, weight=1)


class ProducerConsumer(QNet):

    def __init__(self):
        QNet.__init__(self)
        producer = Producer()
        consumer = Consumer()
        P2 = QPlace(label="P2")
        self.register([producer, consumer])
        self.connect(producer.T1, P2, weight=1)
        self.connect(P2, consumer.T2, weight=1)

net = ProducerConsumer()

for step in iter(net):
    input(step)

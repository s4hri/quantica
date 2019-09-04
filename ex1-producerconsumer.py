"""
BSD 2-Clause License

Copyright (c) 2019, Davide De Tommaso (dtmdvd@gmail.com)
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
http://petrinet.org/petrinets/producer-consumer.html
"""

from quantica import QPlace, QNet, QTransition


class Producer(QNet):

    def __init__(self):
        QNet.__init__(self)
        t1 = QTransition(label="t1")
        t2 = QTransition(label="t2")
        p1 = QPlace(label="Producer1", init_tokens=1, time_window=1.0)
        p2 = QPlace(label="Producer2", time_window=1.0)

        self.connect(t1, p1, weight=1)
        self.connect(p1, t2, weight=1)
        self.connect(t2, p2, weight=1)
        self.connect(p2, t1, weight=1)


class Consumer(QNet):

    def __init__(self):
        QNet.__init__(self)
        t1 = QTransition(label="t1")
        t2 = QTransition(label="t2")
        p1 = QPlace(label="Consumer1", time_window=1.0)
        p2 = QPlace(label="Consumer2", init_tokens=1, time_window=1.0)

        self.connect(t1, p1, weight=1)
        self.connect(p1, t2, weight=1)
        self.connect(t2, p2, weight=1)
        self.connect(p2, t1, weight=1)


class ProducerConsumer(QNet):

    def __init__(self):
        QNet.__init__(self)
        producer = Producer()
        consumer = Consumer()

        buffered_link = QPlace(label="Buffer")
        self.register([producer, consumer])
        self.connect(producer.getQNodeByLabel("t2"), buffered_link, 1)
        self.connect(buffered_link, consumer.getQNodeByLabel("t1"), 1)

net = ProducerConsumer()
print(net)
for step in iter(net):
    print(step)

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
ex3-diningphylophers.py

Dining Philophers problem using Petri network as shown in
https://upload.wikimedia.org/wikipedia/commons/7/78/4-philosophers.gif
"""

from quantica import QPlace, QNet, QTransition
import logging
import random

class Philosopher(QNet):

    def __init__(self, name):
        QNet.__init__(self)
        self.name = name
        self.x = QTransition(label="x")
        self.y = QTransition(label="y")
        self.t = QPlace(label=name+"_t", target=self.think, init_tokens=1)
        self.e = QPlace(label=name+"_e", target=self.eat, quanta_timeout=random.randrange(1.0, 5.0))

        self.connect(self.t, self.x, weight=1)
        self.connect(self.x, self.e, weight=1)
        self.connect(self.e, self.y, weight=1)
        self.connect(self.y, self.t, weight=1)

    def think(self):
        logging.info("[%s] Thinking ..." % self.name)

    def eat(self):
        logging.info("[%s] Eating ..." % self.name)


class DiningPhylosophers(QNet):

        def __init__(self):
            QNet.__init__(self)
            ari = Philosopher("Aristotele")
            sof = Philosopher("Sofocle")
            pla = Philosopher("Platone")
            era = Philosopher("Eraclito")

            fork1 = QPlace(label="Fork 1", init_tokens=1)
            fork2 = QPlace(label="Fork 2", init_tokens=1)
            fork3 = QPlace(label="Fork 3", init_tokens=1)
            fork4 = QPlace(label="Fork 4", init_tokens=1)

            self.register([ari, sof, pla, era])

            self.connect(ari.y, fork1, weight=1)
            self.connect(ari.y, fork2, weight=1)
            self.connect(fork1, ari.x, weight=1)
            self.connect(fork2, ari.x, weight=1)

            self.connect(sof.y, fork2, weight=1)
            self.connect(sof.y, fork3, weight=1)
            self.connect(fork2, sof.x, weight=1)
            self.connect(fork3, sof.x, weight=1)

            self.connect(pla.y, fork3, weight=1)
            self.connect(pla.y, fork4, weight=1)
            self.connect(fork3, pla.x, weight=1)
            self.connect(fork4, pla.x, weight=1)

            self.connect(era.y, fork4, weight=1)
            self.connect(era.y, fork1, weight=1)
            self.connect(fork4, era.x, weight=1)
            self.connect(fork1, era.x, weight=1)


net = DiningPhylosophers()

for step in iter(net):
    print(net)

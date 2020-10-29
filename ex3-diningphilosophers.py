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

from quantica.core import QPlace, QNet, QTransition
import logging
import random
import time

class Philosopher(QNet):

    def __init__(self, label):
        QNet.__init__(self, label=label, logging_level=logging.INFO)
        self._x = self.createTransition('x')
        self._y = self.createTransition('y')
        self._t = self.createPlace('_t', target_task=self.think, init_tokens=1)
        self._e = self.createPlace('_e', target_task=self.eat)

        self.connect(self._t, self._x, weight=1)
        self.connect(self._x, self._e, weight=1)
        self.connect(self._e, self._y, weight=1)
        self.connect(self._y, self._t, weight=1)

    def think(self):
        logging.info("[%s] Thinking ..." % self.getLabel())
        time.sleep(2.0)

    def eat(self):
        logging.info("[%s] Eating ..." % self.getLabel())
        time.sleep(2.0)


class DiningPhylosophers(QNet):

        def __init__(self):
            QNet.__init__(self, 'DiningPhylosophers', logging_level=logging.INFO)
            ari = Philosopher("Aristotele")
            sof = Philosopher("Sofocle")
            pla = Philosopher("Platone")
            era = Philosopher("Eraclito")

            fork0 = self.createPlace("Fork0", init_tokens=1)
            fork1 = self.createPlace("Fork1", init_tokens=1)
            fork2 = self.createPlace("Fork2", init_tokens=1)
            fork3 = self.createPlace("Fork3", init_tokens=1)

            self.addNet(ari)
            self.addNet(sof)
            self.addNet(pla)
            self.addNet(era)

            self.connect(ari._y, fork0, weight=1)
            self.connect(ari._y, fork1, weight=1)
            self.connect(fork0, ari._x, weight=1)
            self.connect(fork1, ari._x, weight=1)

            self.connect(sof._y, fork1, weight=1)
            self.connect(sof._y, fork2, weight=1)
            self.connect(fork1, sof._x, weight=1)
            self.connect(fork2, sof._x, weight=1)

            self.connect(pla._y, fork2, weight=1)
            self.connect(pla._y, fork3, weight=1)
            self.connect(fork2, pla._x, weight=1)
            self.connect(fork3, pla._x, weight=1)

            self.connect(era._y, fork3, weight=1)
            self.connect(era._y, fork0, weight=1)
            self.connect(fork3, era._x, weight=1)
            self.connect(fork0, era._x, weight=1)


net = DiningPhylosophers()

net.start_async()

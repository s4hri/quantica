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
ex8-semaphore.py

Traffic Light example presented in
http://petrinet.org/#TrafficLights
"""

from quantica.core import QNet

class TrafficLight(QNet):

    def __init__(self, label='TrafficLight'):
        QNet.__init__(self, label=label)
        self.TR1 = self.createTransition('To-Red-1')
        self.TG1 = self.createTransition('To-Green-1')
        self.PG1 = self.createPlace('Green-1', init_tokens=1)
        self.PR1 = self.createPlace('Red-1')

        self.TR2 = self.createTransition('To-Red-2')
        self.TG2 = self.createTransition('To-Green-2')
        self.PG2 = self.createPlace('Green-2')
        self.PR2 = self.createPlace('Red-2', init_tokens=1)

        self.QUEUE = self.createPlace('Queue')

        self.connect(self.PG1, self.TR1, weight=1)
        self.connect(self.TG1, self.PG1, weight=1)
        self.connect(self.TR1, self.PR1, weight=1)
        self.connect(self.PR1, self.TG1, weight=1)

        self.connect(self.PG2, self.TR2, weight=1)
        self.connect(self.TR2, self.PR2, weight=1)
        self.connect(self.PR2, self.TG2, weight=1)
        self.connect(self.TG2, self.PG2, weight=1)

        self.connect(self.TR1, self.QUEUE, weight=1)
        self.connect(self.QUEUE, self.TG1, weight=1)
        self.connect(self.QUEUE, self.TG2, weight=1)
        self.connect(self.TR2, self.QUEUE, weight=1)

net = TrafficLight()
input(net.state())
for state in net:
    input(state)

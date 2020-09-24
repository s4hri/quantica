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

ex2-splitjoin.py

Split-Join

Expressing events happening in parallel is often necessary.
This net shows how a single, sequential process can be split into two branches
which run in parallel and then sync. The concept of parallel computing is an
important one.

http://petrinet.org/petrinets/split-join.html
"""

from core import QPlace, QNet, QTransition

class SplitJoin(QNet):

    def __init__(self):
        QNet.__init__(self, nid='SplitJoin')
        self.P0 = self.createPlace(init_tokens=1, label='P0')
        self.T1 = self.createTransition(label='T1')

        self.P1 = self.createPlace(label='P1')
        self.T2 = self.createTransition(label='T2')
        self.P2 = self.createPlace(label='P2')

        self.P4 = self.createPlace(label='P4')
        self.T3 = self.createTransition(label='T3')
        self.P5 = self.createPlace(label='P5')

        self.T0 = self.createTransition(label='T0')
        self.P3 = self.createPlace(label='P3')

        self.connect(self.P0, self.T1, 1)

        self.connect(self.T1, self.P1, 1)
        self.connect(self.T1, self.P4, 1)

        self.connect(self.P1, self.T2, 1)
        self.connect(self.T2, self.P2, 1)

        self.connect(self.P4, self.T3, 1)
        self.connect(self.T3, self.P5, 1)

        self.connect(self.P2, self.T0, 1)
        self.connect(self.P5, self.T0, 1)
        self.connect(self.T0, self.P3, 1)

net = SplitJoin()

for step in iter(net):
    input(step.state())

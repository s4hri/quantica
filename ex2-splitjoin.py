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

ex2-splitjoin.py

Split-Join

Expressing events happening in parallel is often necessary.
This net shows how a single, sequential process can be split into two branches
which run in parallel and then sync. The concept of parallel computing is an
important one.

http://petrinet.org/petrinets/split-join.html
"""

from quantica import QPlace, QNet, QTransition


class SplitJoin(QNet):

    def __init__(self):
        QNet.__init__(self)
        pin = QPlace(label='P_in', init_tokens=1)
        tin = QTransition(label='T_in')

        p1_1 = QPlace(label='P1_1')
        t1_1 = QTransition(label='T1_1')
        p2_1 = QPlace(label='P2_1')

        p1_2 = QPlace(label='P1_2')
        t1_2 = QTransition(label='T1_2')
        p2_2 = QPlace(label='P2_2')

        tout = QTransition(label='T_out')
        pout = QPlace(label='P_out')

        self.connect(pin, tin, 1)

        self.connect(tin, p1_1, 1)
        self.connect(tin, p1_2, 1)

        self.connect(p1_1, t1_1, 1)
        self.connect(t1_1, p2_1, 1)

        self.connect(p1_2, t1_2, 1)
        self.connect(t1_2, p2_2, 1)

        self.connect(p2_1, tout, 1)
        self.connect(p2_2, tout, 1)
        self.connect(tout, pout, 1)

net = SplitJoin()
print(net)
for step in iter(net):
    print(step)

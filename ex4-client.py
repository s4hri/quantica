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

from quantica.core import QPlace, QNet, QTransition, QNetRemote

class Buffer(QNet):

    def __init__(self):
        QNet.__init__(self, label='Buffer')
        self.P2 = self.createPlace('P2')

class Consumer(QNet):

    def __init__(self):
        QNet.__init__(self, label='Consumer')
        self.P3 = self.createPlace('P3')
        self.P4 = self.createPlace('P4', init_tokens=1)
        self.T2 = self.createTransition('T2')
        self.T3 = self.createTransition('T3')
        self.connect(self.T2, self.P3, weight=1)
        self.connect(self.P3, self.T3, weight=1)
        self.connect(self.T3, self.P4, weight=1)
        self.connect(self.P4, self.T2, weight=1)


class ProdCons(QNet):

    def __init__(self):
        QNet.__init__(self, label='ProdCons')
        self.producer = QNetRemote(('localhost', 8000))
        self.consumer = Consumer()
        self.buf = Buffer()

        self.addNet(self.producer)
        self.addNet(self.buf)
        self.addNet(self.consumer)

        self.connect('T1.Producer', 'P2.Buffer', weight=1)
        self.connect('P2.Buffer', 'T2.Consumer', weight=1)

net = ProdCons()

input(net.state())
for state in net:
    input(state)

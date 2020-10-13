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

from quantica.core import QPlace, QNet, QTransition
import threading
import time

class QTimed(QNet):

    def __init__(self, interval_ms):
        QNet.__init__(self, 'QTimed')
        self._idle_thread = threading.Thread(target=self.__idle__, args=(interval_ms/1000.0,))
        P0 = self.createPlace(init_tokens=1)
        T0 = self.createTransition()
        P1 = self.createPlace(target_task=self.__ctrl__)
        self.T1 = self.createTransition()
        self.connect(P0, T0, 1)
        self.connect(T0, P1, 1)
        self.connect(P1, self.T1, 1)

    @property
    def T(self):
        return self.T1

    def __idle__(self, interval_ms):
        t0 = time.perf_counter()
        while True:
            if (time.perf_counter() - t0) < interval_ms:
                time.sleep(0.0001)
                continue
            else:
                break

    def __ctrl__(self):
        self._idle_thread.start()
        self._idle_thread.join()

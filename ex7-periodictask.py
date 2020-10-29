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

from quantica.core import QNet
from quantica.models import QTimed
import time
import threading
import logging

TASK_PERIOD_MS = 1000.0
TASK_DURATION_MS = 100.0

def onset():
    logging.info("Task ONSET")

def offset():
    logging.info("Task OFFSET")

qnet = QNet('QTimed', logging_level=logging.INFO)
X0 = qnet.createPlace('X0', init_tokens=5)
X1 = qnet.createPlace('X1', init_tokens=0, target_task=onset)
X2 = qnet.createPlace('X2', init_tokens=0)
X3 = qnet.createPlace('X3', init_tokens=0, target_task=offset)

t_onset = QTimed('onset', TASK_PERIOD_MS)
t_offset = QTimed('offset', TASK_DURATION_MS)
qnet.addNet(t_onset)
qnet.addNet(t_offset)
qnet.connect(X0, t_onset.T_IN, 1)
qnet.connect(t_onset.T_OUT, X1, 1)
qnet.connect(t_onset.T_OUT, X2, 1)
qnet.connect(X2, t_offset.T_IN, 1)
qnet.connect(t_offset.T_OUT, X3, 1)

qnet.start_async()

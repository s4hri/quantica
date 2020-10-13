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
ex5-logic.py

Discrete Logic using Quantica

https://en.wikipedia.org/wiki/Logic_gate
"""

from quantica.discretelogic import QOR, QAND, QBUFFER, QNOT, QNAND

q = QOR()
print("OR) A=0, B=0, Q=%d" % q.set(A=False, B=False))
print("OR) A=1, B=0, Q=%d" % q.set(A=True, B=False))
print("OR) A=0, B=1, Q=%d" % q.set(A=False, B=True))
print("OR) A=1, B=1, Q=%d" % q.set(A=True, B=True))

q = QAND()
print("AND) A=0, B=0, Q=%d" % q.set(A=False, B=False))
print("AND) A=1, B=0, Q=%d" % q.set(A=True, B=False))
print("AND) A=0, B=1, Q=%d" % q.set(A=False, B=True))
print("AND) A=1, B=1, Q=%d" % q.set(A=True, B=True))

q = QBUFFER()
print("BUFFER) A=0, Q=%d" % q.set(A=False))
print("BUFFER) A=1, Q=%d" % q.set(A=True))

q = QNOT()
print("NOT) A=0, Q=%d" % q.set(A=False))
print("NOT) A=1, Q=%d" % q.set(A=True))

q = QNAND()
print("NAND) A=0, B=0, Q=%d" % q.set(A=False, B=False))
print("NAND) A=1, B=0, Q=%d" % q.set(A=True, B=False))
print("NAND) A=0, B=1, Q=%d" % q.set(A=False, B=True))
print("NAND) A=1, B=1, Q=%d" % q.set(A=True, B=True))

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

import asyncio
import numpy as np
import logging
import random
from abc import abstractmethod

FORMAT = '%(created).9f %(levelname)-5s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)

class QNode:
    def __init__(self, nid: str, label: str=None):
        self.nid = nid
        if label is None:
            label = nid
        self.label = label

class QPlace(QNode):
    def __init__(self, nid: str, label: str=None, init_tokens: int=0, target_task=None):
        QNode.__init__(self, nid, label)
        self.tokens = init_tokens
        self.target_task = target_task

    def consume(self, n):
        logging.debug("[QPlace:%s] consuming %d token(s)..." % (self.nid, n))
        self.tokens -= n
        if self.tokens > 0:
            self.task()

    def produce(self, n):
        logging.debug("[QPlace:%s] producing %d token..." % (self.nid, n))
        self.tokens += n
        logging.debug("[QPlace:%s] has %d token..." % (self.nid, self.tokens))
        if self.tokens > 0:
            self.task()

    def task(self):
        logging.debug("[QPlace:%s] processing %d tokens..." % (self.nid, self.tokens))
        if not self.target_task is None:
            self.target_task()


class QTransition(QNode):
    def __init__(self, nid: str, label: str=None):
        QNode.__init__(self, nid, label)

class QMatrix(object):
    def __init__(self):
        self.__M__ = np.array([])

    @property
    def nrows(self):
        return self.__M__.shape[0]

    @property
    def ncols(self):
        if self.__M__.shape[0] > 0:
            return self.__M__.shape[1]
        return 0

    def getPlaces(self, net):
        return sorted(net.places)

    def getTransitions(self, net):
        return sorted(net.transitions)

    def getTransitionColumn(self, net, tnid):
        return sorted(net.transitions).index(tnid)

    def getPlaceRow(self, net, pnid):
        return sorted(net.places).index(pnid)

    def getElement(self, i, j):
        return self.__M__[i,j]

    def setElement(self, i, j, value):
        self.__M__[i,j] = value

    def getColumn(self, i):
        return self.__M__[:,i]

    @property
    def value(self):
        return self.__M__

    def set(self, M):
        self.__M__ = np.array(M)

    @abstractmethod
    def update(self, net):
        raise NotImplementedError("This has to be implemented")

class QInputMatrix(QMatrix):
    def __init__(self):
        QMatrix.__init__(self)

    def update(self, net):
        I = []
        for pnid in self.getPlaces(net):
            row = []
            for tnid in self.getTransitions(net):
                row.append(net.weight(pnid, tnid))
            I.append(row)
        self.set(I)

class QOutputMatrix(QMatrix):
    def __init__(self):
        QMatrix.__init__(self)

    def update(self, net):
        O = []
        for pnid in self.getPlaces(net):
            row = []
            for tnid in self.getTransitions(net):
                row.append(net.weight(tnid, pnid))
            O.append(row)
        self.set(O)

class QIncidenceMatrix(QMatrix):
    def __init__(self):
        QMatrix.__init__(self)

    def update(self, net):
        self.__M__ = net.O.value - net.I.value

class QNet(QNode):

    def __init__(self, nid: str, label: str=None):
        QNode.__init__(self, nid, label)
        self.places = {}
        self.transitions = {}
        self.weights = {}
        self.__I__ = QInputMatrix()
        self.__O__ = QOutputMatrix()
        self.__C__ = QIncidenceMatrix()


    def __update__(self):
        self.I.update(self)
        self.O.update(self)
        self.C.update(self)

    def __iter__(self):
        return self

    def __next__(self):
        v = self.__getEnabledTransitions__()
        if len(v) > 0:
            random.shuffle(v)
            self.fire(v[0])
        return self

    def __getEnabledTransitions__(self):
        v = []
        for tnid in self.transitions.keys():
            enabled = True
            Tcol = self.I.getColumn(self.I.getTransitionColumn(self, tnid))
            for pnid in self.places.keys():
                if self.x(pnid) < self.weight(pnid, tnid):
                    enabled = False
            if enabled == True:
                v.append(tnid)
        return v

    @property
    def arcs(self):
        return self.weights.keys()

    @property
    def I(self):
        return self.__I__

    @property
    def O(self):
        return self.__O__

    @property
    def C(self):
        return self.__C__

    def x(self, pnid):
        return self.places[pnid].tokens

    def addNode(self, node: QNode):
        if isinstance(node, QTransition):
            self.transitions[node.nid] = node
        elif isinstance(node, QPlace):
            self.places[node.nid] = node
        self.__update__()

    def addNet(self, net):

        nodes = {**net.places, **net.transitions}
        remap_nid = {}

        for pnid in sorted(net.places):
            nid = self.__generatePlaceNid__()
            remap_nid[pnid] = nid
            self.__remapNid__(net, pnid, nid)
            self.addNode(net.places[pnid])

        for tnid in sorted(net.transitions):
            nid = self.__generateTransitionNid__()
            remap_nid[tnid] = nid
            self.__remapNid__(net, tnid, nid)
            self.addNode(net.transitions[tnid])

        for old_key, new_key in remap_nid.items():
            self.__remapKey__(net, old_key, new_key)

        self.__remapLabel__(net)
        nodes = {**net.places, **net.transitions}

        for src_nid, dst_nid in net.weights.keys():
            self.connect(nodes[src_nid], nodes[dst_nid], net.weights[(src_nid, dst_nid)])

    def __remapLabel__(self, net):
        for p in net.places.values():
            p.label = net.label + '/' + p.label

        for t in net.transitions.values():
            t.label = net.label + '/' + t.label

    def __remapNid__(self, net, old_nid, new_nid):
        if old_nid in net.places.keys():
            net.places[old_nid].nid = new_nid

        if old_nid in net.transitions.keys():
            net.transitions[old_nid].nid = new_nid

    def __remapKey__(self, net, old_key, new_key):
        if old_key in net.places.keys():
            net.places[new_key] = net.places.pop(old_key)

        if old_key in net.transitions.keys():
            net.transitions[new_key] = net.transitions.pop(old_key)

        new_weights = {}
        kw = list(net.weights.keys())
        for src_nid, dst_nid in kw:
            if old_key == src_nid:
                net.weights[(new_key, dst_nid)] = net.weights.pop((src_nid, dst_nid))
            elif old_key == dst_nid:
                net.weights[(src_nid, new_key)] = net.weights.pop((src_nid, dst_nid))

    def __generatePlaceNid__(self):
        return 'P' + str(len(self.places))

    def __generateTransitionNid__(self):
        return 'T' + str(len(self.transitions))

    def createPlace(self, init_tokens=0, label=None, target_task=None):
        p = QPlace(self.__generatePlaceNid__(), label, init_tokens, target_task=target_task)
        self.addNode(p)
        return p

    def createTransition(self, label=None):
        t = QTransition(self.__generateTransitionNid__(), label)
        self.addNode(t)
        return t

    def fire(self, tnid):
        logging.info("[%s] Transition %s fired! " %(self.__class__.__name__, tnid))
        for pnid in self.places.keys():
            res = self.weight(tnid, pnid) - self.weight(pnid, tnid)
            if res > 0:
                self.places[pnid].produce(res)
            elif res < 0:
                self.places[pnid].consume(-res)

    def weight(self, src_nid, dst_nid):
        if (src_nid, dst_nid) in self.weights.keys():
            return self.weights[(src_nid, dst_nid)]
        return 0

    def connect(self, src: QNode, dst: QNode, weight: int):
        if (src.nid, dst.nid) in self.arcs:
            raise Exception('Connection between %s and %s already present!' % (src.nid, dst.nid))
        self.weights[(src.nid, dst.nid)] = weight
        self.__update__()
        logging.debug("[%s] connected [%s] to [%s] ... " % (self.__class__.__name__, src.nid, dst.nid))

    def state(self):
        state = []
        for k, v in self.places.items():
            state.append("%s(%s)=%d" % (k, v.label, v.tokens))
        return state

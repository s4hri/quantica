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
"""

import abc
import time
import logging
import random
from multiprocessing import Process, Queue
from multiprocessing.pool import Pool
from threading import Condition, Thread, Lock
from sortedcontainers import SortedDict

FORMAT = '%(created).9f %(levelname)-5s %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)


# A QNode defines an abstraction of a Petri network's node.
# It is the parent class of QTransition and QPlace
class QNode:

    def __init__(self, nid: int, label: str=None):
        self.__nid__ = nid
        self.__label__ = label

    @property
    def label(self):
        return self.__label__

    @property
    def nid(self):
        return self.__nid__

    def setNID(self, nid):
        self.__nid__ = nid
        if self.__label__ is None:
            self.__label__ = nid


# A QPlace defines a Petri network's place.
class QPlace(QNode):

    def __init__(self, target=None, label: str=None, init_tokens: int=0, time_window: float=0):
        QNode.__init__(self, nid=None, label=label)
        self.__tokens__ = init_tokens
        self.__target__ = target
        self.__time_window__ = time_window
        self.__lock__ = Lock()

    @property
    def tokens(self):
        return self.__tokens__

    def __process__(self, n):
        for i in range(0, n):
            t0 = time.process_time_ns()
            self.__target_task__()
            t1 = time.process_time_ns()
            if self.__time_window__ > 0:
                offset = (t1-t0)/1000000000. #offset is in seconds
                if offset < self.__time_window__:
                    time.sleep(self.__time_window__ - offset)

    def __target_task__(self):
        if self.__target__ is None:
            logging.debug("[QPlace:%s] executing task  ..." % self.label)
        else:
            self.__target__()

    def consume(self, n):
        self.__lock__.acquire()
        self.__tokens__ -= n
        self.__lock__.release()

    def generate(self, n):
        self.__lock__.acquire()
        p = Process(target=self.__process__, args=(n,))
        p.start()
        p.join()
        self.__tokens__ += n
        self.__lock__.release()


# A QPlace defines a Petri network's transition.
class QTransition(QNode):

    def __init__(self, label: str=None):
        QNode.__init__(self, nid=None, label=label)

# A QPlace defines a Petri network.
class QNet:

    def __init__(self):
        self.__places__ = []
        self.__transitions__ = []
        self.__arcs__ = {}
        self.__I__ = [] #  Input matrix
        self.__O__ = [] #  Output matrix
        self.__ready__ = Condition()

    @property
    def I(self):
        return self.__I__

    @property
    def O(self):
        return self.__O__

    @property
    def X(self):
        X = []
        for place in self.__places__:
            X.append(place.tokens)
        return X

    def __iter__(self):
        return self

    def __next__(self):
        v = self.__getEnabledTransitions__()
        if len(v) == 0:
            raise StopIteration
        random.shuffle(v)
        self.__fire__(v[0])
        return self

    def __str__(self):
        res = "\nQNET STATE" + "\n"
        res += " > Place labels: " + str([x.label for x in self.__places__]) + "\n"
        res += " > Place tokens: " + str([x.tokens for x in self.__places__]) + "\n"
        return res

    def __connect__(self, src_nid: str, dst_nid: str, weight: int):
        logging.debug("[%s] connecting [%s] to [%s] ... " %(self.__class__.__name__, src_nid, dst_nid))
        self.__updateIO__(src_nid, dst_nid, weight)

    def __fire__(self, transition: QTransition):
        logging.debug("[%s] %s fired! " %(self.__class__.__name__, transition.label))
        idx = self.__transitions__.index(transition)
        threads = []

        for i in range(0, len(self.__I__)):
            iw = self.__I__[i][idx]
            ow = self.__O__[i][idx]
            place = self.__places__[i]
            if ow > 0:
                t = Thread(target=place.generate, args=(ow,))
                threads.append(t)
                t.start()
            if iw > 0:
                t = Thread(target=place.consume, args=(iw,))
                threads.append(t)
                t.start()

        for t in threads:
            t.join()

    def __getEnabledTransitions__(self):
        v = []
        for transition in self.__transitions__:
            if self.__isEnabled__(transition):
                v.append(transition)
        return v

    def __isEnabled__(self, transition: QTransition):
        idx = self.__transitions__.index(transition)
        for i in range(0, len(self.X)):
            if self.X[i] < self.__I__[i][idx]:
                return False
        return True

    def __registerNode__(self, node: QNode):
        if isinstance(node, QTransition):
            node.setNID(id(node))
            self.__transitions__.append(node)
        elif isinstance(node, QPlace):
            node.setNID(id(node))
            self.__places__.append(node)
        elif isinstance(node, QNet):
            self.register(node.__places__)
            self.register(node.__transitions__)
            for src_nid, dst_nid in node.arcs().keys():
                self.__connect__(src_nid, dst_nid, node.arcs()[(src_nid, dst_nid)])

    def __updateIO__(self, src: str, dst: str, weight: int):

        if src is None or dst is None:
            logging.error("These nodes are not registered in the network. Please do register them before connecting.")
            return

        self.__arcs__[(src, dst)] = weight
        self.__I__ = []
        self.__O__ = []

        for place in self.__places__:
            irow = []
            orow = []
            for transition in self.__transitions__:
                irow.append( self.weight(place.nid, transition.nid) )
                orow.append( self.weight(transition.nid, place.nid) )
            self.__I__.append(irow)
            self.__O__.append(orow)

    def arcs(self):
        return self.__arcs__

    def connect(self, src: QNode, dst: QNode, weight: int):
        self.register([src, dst])
        self.__connect__(src.nid, dst.nid, weight)

    def getQNodeByLabel(self, label):
        for place in self.__places__:
            if label == place.label:
                return place
        for transition in self.__transitions__:
            if label == transition.label:
                return transition
        return None

    def places(self):
        return self.__places__

    def register(self, nodes):
        for node in nodes:
            if not node in self.__places__ and not node in self.__transitions__:
                self.__registerNode__(node)

    def transitions(self):
        return self.__transitions__

    def weight(self, src_nid: str, dst_nid: str):
        if (src_nid, dst_nid) in self.__arcs__.keys():
            return self.__arcs__[(src_nid, dst_nid)]
        return 0

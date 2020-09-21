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

from abc import ABC, abstractmethod
from multiprocessing.managers import BaseManager
from multiprocessing.connection import Connection, wait
from multiprocessing.pool import Pool
from multiprocessing import Process, Pipe
from threading import Lock, Thread, Condition

import time
import logging
import asyncio
import random
import threading

FORMAT = '%(created).9f %(levelname)-5s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)

class QArc:

    def __init__(self, src_nid: str, dst_nid: str, pipe: Pipe, weight: int):
        self.__src_nid__ = src_nid
        self.__dst_nid__ = dst_nid
        self.__dst_conn__, self.__src_conn__ = pipe
        self.__weight__ = weight

    @property
    def dst_conn(self):
        return self.__dst_conn__

    @property
    def src_conn(self):
        return self.__src_conn__

    @property
    def dst_nid(self):
        return self.__dst_nid__

    @property
    def src_nid(self):
        return self.__src_nid__

    @property
    def weight(self):
        return self.__weight__

class QMonitor:

    def __init__(self, node):
        self.__node__ = node
        self.__readers_in__ = {}
        self.__readers_out__ = {}

    def refresh_inputs(self):
        for k, v in self.__node__.IN.items():
            self.__readers_in__[v.dst_conn] = k
        Thread(target=self.__monitor_in__).start()


    def refresh_outputs(self):
        for k, v in self.__node__.OUT.items():
            self.__readers_out__[v.src_conn] = k
        Thread(target=self.__monitor_out__).start()

    def __monitor_in__(self):
        while self.__readers_in__:
            for r in wait(self.__readers_in__.keys()):
                msg = r.recv()
                if msg == 'reset':
                    return
                elif type(msg) == int:
                    self.__node__.generate(int(msg), self.__readers_in__[r])

    def __monitor_out__(self):
        while self.__readers_out__:
            for r in wait(self.__readers_out__.keys()):
                msg = r.recv()
                if msg == 'reset':
                    return
                elif type(msg) == int:
                    self.__node__.consume(int(msg))


# A QNode defines an abstraction of a Petri network's node.
# It is the parent class of QTransition and QPlace
class QNode(ABC):

    def __init__(self, nid: str):
        self.__nid__ = nid
        self.__inputs__ = {} # QArc objects representing inputs nodes
        self.__outputs__ = {} # QArc objects representing outputs nodes
        self.__qmon__ = QMonitor(self)

    def __ready__(self, n):
        writers = list( map(lambda x: x.src_conn, self.__outputs__.values()) )
        for w in writers:
            w.send(n)

    @property
    def nid(self):
        return self.__nid__

    @property
    def IN(self):
        return self.__inputs__

    @property
    def OUT(self):
        return self.__outputs__

    def addIN(self, arc: QArc):
        if self.IN:
            list(self.IN.values())[0].src_conn.send('reset')
        self.IN[arc.src_nid] = arc
        time.sleep(0.001)
        self.__qmon__.refresh_inputs()

    def addOUT(self, arc: QArc):
        if self.OUT:
            list(self.OUT.values())[0].dst_conn.send('reset')
        self.OUT[arc.dst_nid] = arc
        time.sleep(0.001)
        self.__qmon__.refresh_outputs()

    def ready(self, n):
        self.__ready__(n)

    @abstractmethod
    def consume(self, n):
        raise NotImplementedError("This has to be implemented")

    @abstractmethod
    def generate(self, n, src_nid):
        raise NotImplementedError("This has to be implemented")

class QPlace(QNode):

    def __init__(self, nid: str, target=None, init_tokens: int=0, quanta_timeout: float=0):
        QNode.__init__(self, nid)
        self.__tokens__ = init_tokens
        self.__target__ = target
        self.__quanta_timeout__ = quanta_timeout
        self.__lock__ = Lock()

    @property
    def tokens(self):
        return self.__tokens__

    def __process__(self, n):
        for i in range(0, n):
            t0 = time.perf_counter()
            self.__target_task__()
            t1 = time.perf_counter()
            if self.__quanta_timeout__ > 0:
                offset = t1-t0
                if offset < self.__quanta_timeout__:
                    time.sleep(self.__quanta_timeout__ - offset)

    def __target_task__(self):
        logging.debug("[QPlace:%s] executing task  ..." % self.nid)
        if not self.__target__ is None:
            self.__target__()

    def consume(self, n):
        logging.debug("[QPlace:%s] consuming %d token..." % (self.nid, n))
        self.__lock__.acquire()
        self.__tokens__ -= n
        self.__lock__.release()

    def generate(self, n, src_nid=None):
        logging.debug("[QPlace:%s] generating %d token..." % (self.nid, n))
        self.__process__(n)
        self.__lock__.acquire()
        self.__tokens__ += n
        self.__lock__.release()
        self.ready(n)

# A QTransition defines a Petri network's transition.
class QTransition(QNode):
    def __init__(self, nid: str):
        QNode.__init__(self, nid)
        self.__gates__ = {}
        self.fire_cv = Condition()

    def generate(self, n, src_nid):
        if not src_nid in self.__gates__.keys():
            self.__gates__[src_nid] = n
        else:
            self.__gates__[src_nid] += n

    def consume(self, n):
        pass

    def isEnabled(self):
        for src_id, arc in self.IN.items():
            if src_id in self.__gates__.keys():
                if arc.weight > self.__gates__[src_id]:
                    return False
            else:
                return False
        return True

    def fire(self):
        logging.info("[%s] %s fired! " %(self.__class__.__name__, self.nid))

        for k,v in self.IN.items():
            v.dst_conn.send(self.__gates__[k])

        for k, v in self.__gates__.items():
            self.__gates__[k] = 0

        self.ready()

    def ready(self):
        writers = list( self.__outputs__.values() )
        for w in writers:
            w.src_conn.send(w.weight)

class QNet(QNode):

    def __init__(self, label: str):
        QNode.__init__(self, nid=label)
        self.__places__ = {}
        self.__transitions__ = {}

    def __addTransition__(self, node: QTransition):
        if node.nid in self.__transitions__.keys():
            logging.error("Label %s already present for QTransition" % label)
            return False
        self.__transitions__[node.nid] = node
        return True

    def __addPlace__(self, node: QPlace):
        if node.nid in self.__places__.keys():
            logging.error("Label %s already present for QPlace" % label)
            return False
        self.__places__[node.nid] = node
        return True

    def __connectToRemoteNet__(self, address, authkey):
        with Client(address, authkey=authkey) as conn:
            self.addOUT(conn)

    def __listener__(self, address, authkey):
        with Listener(address, authkey=authkey) as listener:
            with listener.accept() as conn:
                src_nid = conn.recv()
                self.addIN(conn)

    def __getEnabledTransitions__(self):
        v = []
        for nid, t in self.__transitions__.items():
            if t.isEnabled():
                v.append(nid)
        return v

    def __run__(self):
        for step in iter(self):
            time.sleep(0.001)
            logging.info(self.state())

    def __iter__(self):
        return self

    def __next__(self):
        v = self.__getEnabledTransitions__()
        if len(v) > 0:
            random.shuffle(v)
            self.__transitions__[v[0]].fire()
        return self

    def createPlace(self, label: str, init_tokens: int=0, quanta_timeout: float=0):
        nid = "%s/%s" % (self.nid, label)
        place = QPlace(nid, init_tokens=init_tokens, quanta_timeout=quanta_timeout)
        if self.__addPlace__(place):
            return place
        return false

    def createTransition(self, label: str):
        nid = "%s/%s" % (self.nid, label)
        transition = QTransition(nid)
        if self.__addTransition__(transition):
            return transition
        return None

    def connect(self, src: QNode, dst: QNode, weight: int):
        arc = QArc(src.nid, dst.nid, Pipe(), weight)
        dst.addIN(arc)
        src.addOUT(arc)
        logging.debug("[%s] connected [%s] to [%s] ... " % (self.__class__.__name__, src.nid, dst.nid))

    def generate(self, n, src_nid=None):
        pass

    def consume(self, n):
        pass

    def start(self):
        for nid, place in self.__places__.items():
            if place.tokens > 0:
                place.ready(place.tokens)
        Thread(target=self.__run__).start()

    def state(self):
        state = []
        for k, v in self.__places__.items():
            state.append("%s=%d" % (k, v.tokens))
        return state

"""

import time
import logging
import random
from multiprocessing import Process, Queue
from threading import Thread, Lock

FORMAT = '%(created).9f %(levelname)-5s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)

class QManager(ABC):

    @abstractmethod
    def call(self, dst_nid, func, args=()):
        raise NotImplementedError("This has to be implemented")

class LocalManager(QManager):

    def __init__(self):
        self.__nodes__ = {}

    def register(self, node):
        nid = id(node)
        logging.debug("[%s] A QNode has been registered with nid=%d and label=%s" %(self.__class__.__name__, nid, node.label))
        self.__nodes__[nid] = node
        return nid

    def call(self, dst_nid, func, args):
        if dst_nid in self.__nodes__.keys():
            res = getattr(self.__nodes__[dst_nid], func)(*args)
        return res

    def getNode(self, nid):
        return self.__nodes__[nid]


QM_LOCAL = LocalManager()

# A QNode defines an abstraction of a Petri network's node.
# It is the parent class of QTransition and QPlace
class QNode(ABC):
    def __init__(self, label: str=None, qmanager=QM_LOCAL):
        self.__label__ = label
        self.__inputs__ = {} # weighted arcs from source nodes
        self.__outputs__ = {} # weighted arcs to destination nodes
        self.__manager__ = QM_LOCAL
        self.__nid__ = self.__manager__.register(self)
        if label is None:
            self.__label__ = ("%s-%d") % (self.__class__.__name__, self.__nid__)

    @property
    def label(self):
        return self.__label__

    @property
    def nid(self):
        return self.__nid__

    @property
    def IN(self):
        return self.__inputs__

    @property
    def OUT(self):
        return self.__outputs__

    def addIN(self, nid, weight):
        if not nid in self.IN.keys():
            self.IN[nid] = weight
        return True

    def addOUT(self, nid, weight):
        if not nid in self.OUT.keys():
            self.OUT[nid] = weight
        return True

    def connectTo(self, dst_nid, weight):
        res = self.__manager__.call(dst_nid, 'addIN', args=(self.nid, weight,))
        if res == False:
            logging.error("[QNode: %s] Connection to %d failed" % (self.label, dst_nid))
        else:
            self.addOUT(dst_nid, weight)
        return res

    def getLabel(self):
        return self.__label__

    @abstractmethod
    def consume(self, n):
        raise NotImplementedError("This has to be implemented")

    @abstractmethod
    def generate(self, n):
        raise NotImplementedError("This has to be implemented")


# A QPlace defines a Petri network's place.
class QPlace(QNode):
    def __init__(self, target=None, label: str=None, init_tokens: int=0, quanta_timeout: float=0):
        QNode.__init__(self, label=label)
        self.__tokens__ = init_tokens
        self.__target__ = target
        self.__quanta_timeout__ = quanta_timeout
        self.__lock__ = Lock()

    @property
    def ready(self):
        return self.__ready__

    @property
    def tokens(self):
        return self.__tokens__

    def getTokens(self):
        return self.__tokens__

    def __process__(self, n):
        for i in range(0, n):
            t0 = time.perf_counter()
            self.__target_task__()
            t1 = time.perf_counter()
            if self.__quanta_timeout__ > 0:
                offset = t1-t0
                if offset < self.__quanta_timeout__:
                    time.sleep(self.__quanta_timeout__ - offset)

    def __target_task__(self):
        logging.debug("[QPlace:%s] executing task  ..." % self.label)
        if not self.__target__ is None:
            self.__target__()

    def consume(self, n):
        self.__lock__.acquire()
        self.__tokens__ -= n
        self.__lock__.release()

#    def generate(self, n, generations):
    def generate(self, n):
        logging.debug("[QPlace:%s] generating %d token..." % (self.label, n))
        self.__process__(n)
        self.__lock__.acquire()
        self.__tokens__ += n
        self.__lock__.release()
        #generations.put(self.label, False)


# A QPlace defines a Petri network's transition.
class QTransition(QNode):
    def __init__(self, label: str=None):
        QNode.__init__(self, label=label)

    def consume(self, n):
        print("tr cons")

    def generate(self, n):
        print("tr gen")

    def isEnabled(self):
        for nid, iw in self.IN.items():
            tokens = self.__manager__.call(nid, 'getTokens', args=())
            if tokens < iw:
                return False
        return True

    def fire(self):
        logging.info("[%s] %s fired! " %(self.__class__.__name__, self.label))
        for nid, iw in self.IN.items():
            Thread(target=self.__manager__.call, args=(nid, 'consume', (iw,),) ).start()
        for nid, ow in self.OUT.items():
            Thread(target=self.__manager__.call, args=(nid, 'generate', (ow,),) ).start()
        #Thread(target=place.generate, args=(ow, self.__generations__, )).start()

# A QNet represents a Petri network.
# A Petri network (graph) is defined by PG = (P, T, A, w).
# - P: places (QNet.__places__: list)
# - T: transitions (QNet.__transitions__: list)
# - A: arcs relation (QNet.__arcs__: list of tuples)
# - w: weight function for each arc (QNet.weight)

class QNet(QNode):

    def __init__(self, label: str=None):
        QNode.__init__(self, label=label)
        self.__places__ = set()
        self.__transitions__ = set()
        self.__subnets__ = set()
        self.__generations__ = None

    @property
    def X(self):
        X = {}
        for nid in self.__places__:
            tokens = self.__manager__.call(nid, 'getTokens', args=())
            label = self.__manager__.call(nid, 'getLabel', args=())
            X[label] = tokens
        return X

    def consume(self, n):
        print("consume")

    def generate(self, n):
        print("generate")

    def __iter__(self):
        return self

    def __next__(self):
        #if self.__generations__ is None:
        #    self.__generations__ = Queue()
        #    self.__generations__.put(0)
        #    return self
        #self.__generations__.get()

        for net in self.__subnets__:
            self.__manager__.call(net, '__next__', args=())
        v = self.__getEnabledTransitions__()
        if len(v) > 0:
            random.shuffle(v)
            self.__manager__.call(v[0], 'fire', args=())
        return self

    def __str__(self):
        return "%s: %s" % (self.label, str(self.X))

    def __getEnabledTransitions__(self):
        v = []
        for nid in self.__transitions__:
            if self.__manager__.call(nid, 'isEnabled', args=()):
                v.append(nid)
        return v

    def __addNode__(self, node: QNode):
        if isinstance(node, QTransition):
            self.__transitions__.add(node.nid)
        elif isinstance(node, QPlace):
            self.__places__.add(node.nid)
        elif isinstance(node, QNet):
            self.__subnets__.add(node.nid)
            #self.register(node.__places__)
            #self.register(node.__transitions__)
            #for src_nid, dst_nid in node.arcs().keys():
            #    self.__connect__(src_nid, dst_nid, node.arcs()[(src_nid, dst_nid)])

    def connect(self, src: QNode, dst: QNode, weight: int):
        if isinstance(src, QNet):
            pass
        if isinstance(dst, QNet):
            pass
        res = src.connectTo(dst.nid, weight)
        if res == True:
            self.__addNode__(src)
            self.__addNode__(dst)
            logging.debug("[%s] connected [%s] to [%s] ... " % (self.__class__.__name__, src.label, dst.label))
"""

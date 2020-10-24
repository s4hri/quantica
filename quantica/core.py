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

import numpy as np
import logging
import random
import threading
from abc import abstractmethod

from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import xmlrpc.client

from urllib.parse import urlparse
from multiprocessing import Process

import time
FORMAT = '%(created).9f %(levelname)-5s %(message)s'

class QNode:
    def __init__(self, label: str):
        self.__label__ = label

    def getLabel(self):
        return self.__label__

    def setLabel(self, label):
        self.__label__ = label

class QPlace(QNode):
    def __init__(self, label: str, init_tokens: int=0, target_task=None, max_tokens_allowed=None):
        QNode.__init__(self, label)
        self.__init_tokens__ = init_tokens
        self.reset()
        self.__target_task__ = target_task
        self.__max_tokens_allowed__ = max_tokens_allowed
        self.__lock__ = threading.Lock()

    def addTokens(self, n):
        with self.__lock__:
            self.__tokens__ += n

    def consume(self, n):
        logging.debug("[QPlace:%s] consuming %d token(s)..." % (self.getLabel(), n))
        self.addTokens(-n)

    def getTokens(self):
        with self.__lock__:
            return self.__tokens__

    def isMaxLimitReached(self):
        if not self.__max_tokens_allowed__ is None:
            if self.__tokens__ == self.__max_tokens_allowed__:
                return True
        return False

    def produce(self, n):
        logging.debug("[QPlace:%s] producing %d token(s)..." % (self.getLabel(), n))
        if (self.getTokens() + n) > 0:
            self.task()
        self.addTokens(n)
        logging.debug("[QPlace:%s] has %d token..." % (self.getLabel(), self.getTokens()))

    def reset(self):
        self.__tokens__ = self.__init_tokens__

    def task(self):
        if not self.__target_task__ is None:
            logging.debug("[QPlace:%s] executing task ..." % self.getLabel())
            self.__target_task__()

class QTransition(QNode):
    def __init__(self, label: str):
        QNode.__init__(self, label)

class QMatrix(object):
    def __init__(self):
        self.__M__ = np.array([])

    @property
    def ncols(self):
        if self.__M__.shape[0] > 0:
            return self.__M__.shape[1]
        return 0

    @property
    def nrows(self):
        return self.__M__.shape[0]

    @property
    def value(self):
        return self.__M__

    def getColumn(self, i):
        return self.__M__[:,i]

    def getElement(self, i, j):
        return self.__M__[i,j]

    def getRow(self, i):
        return self.__M__[i]

    def setElement(self, i, j, value):
        self.__M__[i,j] = value

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
        for p_uri in net.getPlacesURIs():
            row = []
            for t_uri in net.getTransitionsURIs():
                row.append(net.weight(p_uri, t_uri))
            I.append(row)
        self.set(I)

class QOutputMatrix(QMatrix):
    def __init__(self):
        QMatrix.__init__(self)

    def update(self, net):
        O = []
        for p_uri in net.getPlacesURIs():
            row = []
            for t_uri in net.getTransitionsURIs():
                row.append(net.weight(t_uri, p_uri))
            O.append(row)
        self.set(O)

class QIncidenceMatrix(QMatrix):
    def __init__(self):
        QMatrix.__init__(self)

    def update(self, net):
        self.__M__ = net.O - net.I

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

class QNodeList(object):

    def __init__(self):
        self.__nodes__ = {}

    def __getitem__(self, index):
        return self.__nodes__[index]

    def __setitem__(self, index, value):
        self.__nodes__[index] = value

    def __len__(self):
        return len(self.__nodes__)

    def items(self):
        return self.__nodes__.items()

    def keys(self):
        return self.__nodes__.keys()

    def values(self):
        return self.__nodes__.values()

from socketserver import ThreadingMixIn
from xmlrpc.server import SimpleXMLRPCServer

class SimpleThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass

class QNet(QNode):

    def __init__(self, label, address=None, logging_level=logging.DEBUG, format=FORMAT):
        QNode.__init__(self, label)
        logging.basicConfig(level=logging_level, format=FORMAT)
        self.__places__ = QNodeList()
        self.__transitions__ = QNodeList()
        self.__weights__ = {}
        self.__URIs__ = {}
        self.__subnet_URIs__ = {}
        self.__I__ = QInputMatrix()
        self.__O__ = QOutputMatrix()
        self.__C__ = QIncidenceMatrix()
        self.__x__ = QMatrix()
        self.__address__ = address
        self.__pending_threads__ = []
        if not address is None:
            threading.Timer(0.0, self.__rpcserver__).start()

    def __getNidFromURI__(self, uri):
        return self.__URIs__[uri]

    def __getSubnetURI__(self, net, uri):
        for k, v in self.__subnet_URIs__[net.getLabel()].items():
            if v == uri:
                return k
        return None

    def __rpcserver__(self):
        with SimpleThreadedXMLRPCServer(self.__address__, requestHandler=RequestHandler, allow_none=True) as server:
            server.register_introspection_functions()
            server.register_instance(self)
            server.serve_forever()

    def __update__(self):
        self.__I__.update(self)
        self.__O__.update(self)
        self.__C__.update(self)

    def __iter__(self):
        return self

    def __next__(self, asyn=False):

        v = self.getEnabledTransitions()

        if len(v) > 0:
            self.fire(v[0])
            x = []
            for uri in self.getPlacesURIs():
                place = self.getNode(uri)

                if isinstance(place, QPlace):
                    res = place.getTokens()
                else:
                    res = place.getTokens(self.__subnet_URIs__[place.getLabel()][uri])

                x.append(res)
            self.__x__.set(x)

            if asyn is False:
                for t in self.__pending_threads__:
                    t.join()

            return self.state()

        if len(v) == 0 and asyn is False:
            raise StopIteration

    def isMaxLimitReached(self, uri):
        place = self.getNode(uri)
        if isinstance(place, QPlace):
            return place.isMaxLimitReached()
        return place.isMaxLimitReached(self.__subnet_URIs__[place.getLabel()][uri])

    def isTransitionEnabled(self, t_uri):
        I_column_sum = 0
        O_column_sum = 0

        for p_uri in self.getPlacesURIs():
            I_column_sum += self.weight(p_uri, t_uri)
            O_column_sum += self.weight(t_uri, p_uri)
        if I_column_sum == 0:
            return False
        if O_column_sum == 0:
            return False

        enabled = True
        for p_uri in self.getPlacesURIs():
            place = self.getNode(p_uri)
            if isinstance(place, QPlace):
                if place.isMaxLimitReached() and self.weight(t_uri, p_uri) > 0:
                    return False
                if place.getTokens() < self.weight(p_uri, t_uri):
                    enabled = False
            else:
                remap_puri = self.__subnet_URIs__[place.getLabel()][p_uri]
                if place.isMaxLimitReached(remap_puri) and self.weight(t_uri, p_uri) > 0:
                    return False
                if place.getTokens(remap_puri) < self.weight(p_uri, t_uri):
                    enabled = False
        return enabled

    def getEnabledTransitions(self):
        v = []
        for uri in self.getTransitionsURIs():
            res = self.isTransitionEnabled(uri)
            if res == True:
                v.append(uri)
        random.shuffle(v)
        return v

    def getPlacesURIs(self):
        return sorted(list(self.__places__.keys()))

    def getTransitionsURIs(self):
        return sorted(list(self.__transitions__.keys()))

    def getArcs(self):
        return list(self.arcs)

    def getPlaces(self):
        return self.__places__

    def getTransitions(self):
        return self.__transitions__

    def getNode(self, uri):
        if uri in self.getPlacesURIs():
            return self.__places__[uri]
        if uri in self.getTransitionsURIs():
            return self.__transitions__[uri]
        return None

    def getTokens(self, uri):
        place = self.getNode(uri)
        if isinstance(place, QPlace):
            return place.getTokens()
        return place.getTokens(self.__subnet_URIs__[place.getLabel()][uri])

    def getNodeLabel(self, uri):
        if uri in self.getPlacesURIs():
            if isinstance(self.getNode(uri), QNet):
                return self.__subnet_URIs__[self.getNode(uri).getLabel()][uri]
            return self.__places__[uri].getLabel()
        elif uri in self.getTransitionsURIs():
            if isinstance(self.getNode(uri), QNet):
                return self.__subnet_URIs__[self.getNode(uri).getLabel()][uri]
            return self.getNode(uri).getLabel()
        else:
            raise Exception("Requested URI does not exist")

    def start(self):
        while True:
            self.__next__(asyn=True)

    @property
    def arcs(self):
        return self.__weights__.keys()

    @property
    def I(self):
        return self.__I__.value

    @property
    def O(self):
        return self.__O__.value

    @property
    def C(self):
        return self.__C__.value

    @property
    def nplaces(self):
        return len(self.__places__)

    @property
    def ntransitions(self):
        return len(self.__transitions__)

    @property
    def x(self):
        return self.__x__.value.transpose()

    def addNode(self, node: QNode, uri: str):
        if (uri in self.getPlacesURIs()) or (uri in self.getTransitionsURIs()):
            raise Exception('URI <%s> already present! Please use a unique URI instead' % uri)
        if isinstance(node, QTransition):
            self.__transitions__[uri] = node
        elif isinstance(node, QPlace):
            self.__places__[uri] = node
        self.__update__()

    def addNet(self, net):
        if net.getLabel() in self.__subnet_URIs__.keys():
            raise Exception("QNet <%s> already exists. Please use a unique identifier" % net.getLabel())

        self.__subnet_URIs__[net.getLabel()] = {}
        for p_uri in net.getPlacesURIs():
            uri = self.__generateURI__(label=net.getNodeLabel(p_uri), suffix=net.getLabel())
            self.__places__[uri] = net #QNodes present in external QNet
            self.__subnet_URIs__[net.getLabel()][uri] = p_uri

        for t_uri in net.getTransitionsURIs():
            uri = self.__generateURI__(label=net.getNodeLabel(t_uri), suffix=net.getLabel())
            self.__transitions__[uri] = net #QNodes present in external QNet
            self.__subnet_URIs__[net.getLabel()][uri] = t_uri

        for src_uri, dst_uri in net.getArcs():
            mapped_src_uri = self.__getSubnetURI__(net, src_uri)
            mapped_dst_uri = self.__getSubnetURI__(net, dst_uri)
            self.connect(mapped_src_uri, mapped_dst_uri, net.weight(src_uri, dst_uri))

    def __generateURI__(self, label, suffix=''):
        if len(suffix) == 0:
            return label
        return "%s.%s" % (label, suffix)

    def reset(self):
        for place in self.__places__.values():
            place.reset()

    def createPlace(self, label=None, init_tokens=0, target_task=None, max_tokens_allowed=None):
        if label is None:
            label = 'P' + str(self.nplaces)
        p = QPlace(label, init_tokens, target_task=target_task, max_tokens_allowed=max_tokens_allowed)
        uri = self.__generateURI__(label, suffix=self.getLabel())
        self.addNode(p, uri)
        return uri

    def createTransition(self, label=None, uri=None):
        if label is None:
            label = 'T' + str(self.ntransitions)
        t = QTransition(label=label)
        uri = self.__generateURI__(label, suffix=self.getLabel())
        self.addNode(t, uri)
        return uri

    def fire(self, t_uri):
        logging.debug("[%s] Transition %s fired! " % (self.getLabel(), t_uri))
        thread_list = []
        self.__pending_threads__ = []

        for p_uri in self.getPlacesURIs():
            res = self.weight(t_uri, p_uri) - self.weight(p_uri, t_uri)

            if res < 0:
                self.consume(p_uri, res)

            elif res > 0:
                t = threading.Thread(target=self.produce, args=(p_uri, res,))
                t.start()
                self.__pending_threads__.append(t)

    def produce(self, p_uri, weight):
        place = self.__places__[p_uri]
        if isinstance(place, QPlace):
            place.produce(weight)
        else:
            place.produce(self.__subnet_URIs__[place.getLabel()][p_uri], weight)

    def consume(self, p_uri, weight):
        place = self.__places__[p_uri]
        if isinstance(place, QPlace):
            place.consume(-weight)
        else:
            place.consume(self.__subnet_URIs__[place.getLabel()][p_uri], weight)

    def weight(self, src_uri, dst_uri):
        if (src_uri, dst_uri) in self.__weights__.keys():
            return self.__weights__[(src_uri, dst_uri)]
        return 0

    def connect(self, src_uri: str, dst_uri: str, weight: int):
        if (src_uri, dst_uri) in self.arcs:
            raise Exception('Connection between %s and %s already present!' % (src_uri, dst_uri))
        self.__weights__[(src_uri, dst_uri)] = weight
        self.__update__()
        logging.debug("[%s] connected [%s] to [%s] ... " % (self.getLabel(), src_uri, dst_uri))

    def state(self):
        state = []
        for uri in self.getPlacesURIs():
            tokens = self.getTokens(uri)
            state.append("%s=%d" % (uri, tokens))
        return state

    def next_until_end(self):
        for _ in self:
            pass

class QNetRemote:

    def __init__(self, address):
        self._address = address
        self._server = xmlrpc.client.ServerProxy("http://%s:%d" % (address[0], address[1]))
        self._server_acquired = threading.Event()

    def __getattr__(self, name: str):
        with xmlrpc.client.ServerProxy("http://%s:%d" % (self._address[0], self._address[1])) as proxy:
            return proxy.__getattr__(name)

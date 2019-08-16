import abc
import time
import queue
from multiprocessing import Event, Pipe, Process, Queue, Manager
from multiprocessing.connection import Connection
from threading import Condition, Thread, Timer


class Quanta:

    def __init__(self, n, produced_onset):
        self.__n__ = n
        self.__produced_onset__ = produced_onset

    @property
    def n(self):
        return self.__n__

    @property
    def produced_onset(self):
        return self.__produced_onset__

class QNode:
    pass

class QLink:

    def __init__(self, weight: int):
        self.__weight__ = weight
        self.__conn_in__, self.__conn_out__ = Pipe(duplex=False)
        self.__src__ = None
        self.__dst__ = None

    @property
    def connection(self):
        return self.__conn_out__

    @property
    def weight(self):
        return self.__weight__

    def connect(self, src: QNode, dst: QNode):
        self.__src__ = src
        self.__dst__ = dst
        producer_condition = self.__src__.producer_condition
        consumer_condition = self.__dst__.consumer_condition
        self.__src__.addOutput(self.__conn_out__)
        self.__dst__.addInput(self.__conn_in__)
        Thread(target=self.__monitor__, args=(producer_condition, consumer_condition,)).start()


    def __monitor__(self, producer_condition: Condition, consumer_condition: Condition):
        while True:
            with producer_condition:
                producer_condition.wait()
                self.connection.send(Quanta(self.__weight__, self.__src__.produced_onset))
                with consumer_condition:
                    consumer_condition.notify_all()

class QNode:

    def __init__(self):
        self.__producer_condition__ = Condition()
        self.__consumer_condition__ = Condition()
        self.__inputs__ = []
        self.__outputs__ = []
        self.__produced_onset__ = None
        Thread(target=self.__monitor__).start()

    @property
    def producer_condition(self):
        return self.__producer_condition__

    @property
    def consumer_condition(self):
        return self.__consumer_condition__

    @property
    def produced_onset(self):
        return self.__produced_onset__

    def connectTo(self, dst: QNode, weight: int=1):
        link = QLink(weight)
        link.connect(self, dst)

    def addInput(self, conn: Connection):
        self.__inputs__.append(conn)

    def addOutput(self, conn: Connection):
        self.__outputs__.append(conn)

    def __monitor__(self):
        while True:
            with self.consumer_condition:
                self.consumer_condition.wait()
                quanta = None
                for conn in self.__inputs__:
                    if conn.poll():
                        quanta = conn.recv()
                if not quanta is None:
                    self.__run__(quanta)

    @abc.abstractmethod
    def __run__(self, quanta):
        pass

class QPlace(QNode):

    def __init__(self, process_rate: int=0):
        QNode.__init__(self)
        self.__process_rate__ = process_rate
        self.__start_ts__ = None

    @abc.abstractmethod
    def __user_task__(self):
        pass

    def __process__(self, quanta):
        self.__start_ts__ = quanta.produced_onset
        for i in range(0, quanta.n):
            self.__user_task__()
            if self.__process_rate__ > 0:
                ts_off = time.perf_counter() - self.__start_ts__
                time.sleep(1./self.__process_rate__ - ts_off)
                self.__start_ts__ = time.perf_counter()

    def __run__(self, quanta):
        p = Process(target=self.__process__, args=(quanta,))
        p.start()
        p.join()


class QTransition(QNode):

    def __run__(self):
        print("run qtrans")

    def fire(self):
        with self.producer_condition:
            self.__produced_onset__ = time.perf_counter()
            self.producer_condition.notify_all()

class QNet:

    def __init__(self):
        pass

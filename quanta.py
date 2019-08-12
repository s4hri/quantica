from abc import ABC
from multiprocessing import Process, Pipe

class Manager:

    def __init__(self):
        pass


class Node(ABC):

    def connect(self, pipe_in: multiprocessing.Pipe, pipe_out: multiprocessing.Pipe):
        self.__pipe_in__parent_conn__, self.__pipe_in__child_conn__ = pipe_in
        self.__pipe_out__parent_conn__, self.__pipe_out__child_conn__ = pipe_out
        self.__connected__ = True
        self.run()

    @abstractmethod
    def foo(self, n):
        # operating on a quantum n times
        pass

    def run(self):
        while self.__connected__:
            # waiting for serving n quanta
            n = self.__pipe_in__child_conn__.recv()
            p = Process(target=self.foo, args=(n,))
            p.start()
            p.join()
            # producing n quanta
            self.__pipe_out__parent_conn__.send(n)

        self.__pipe_in__child_conn__.close()
        self.__pipe_out__parent_conn__.close()

    def disconnect(self):
        self.__connected__ = False

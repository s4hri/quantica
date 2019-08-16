# 1 transition -> 2 places
# 2 parallel processes running sync at 1Hz

from quanta import QPlace, QLink, QTransition
import time

class MyPlace(QPlace):

    def __init__(self):
        QPlace.__init__(self, process_rate=1)

    def __user_task__(self):
        print("%.4f) Hello quanta! I am %d" % (time.perf_counter(), id(self)) )

t = QTransition()
p = MyPlace()
p2 = MyPlace()
t.connectTo(p, weight=10)
t.connectTo(p2, weight=10)
input(": generate quanta")
t.fire()

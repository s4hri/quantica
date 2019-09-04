# Quantica
Distributed computing based on Petri networks (PNs)

# What is quantica?
Quantica is an Python open-source framework for modeling distributed computing
based on PNs.

Quantica is compatible with Python3.7

# How does it work ?
As explained in PN's theory, a network consists of places and
transitions. Transitions are event-based conditions which allow the places to
be enabled. Places are the basic units of code execution. The code execution in
Places is determined by the presence of tokens.

In Quantica whenever a QPlace (a Place in PN) receives a token, it executes the
relative task immediately as a separate process. If 'N' tokens are received
at the same time, the QPlace executes 'N' times the same task. If specified, the
parameter 'time_window' allows to specify the execution time duration of the
relative task.

# How to start

```python
from quantica import QPlace, QTransition, QNet
```


## 1. Example of a Petri network

This example shows how to implement a simple Petri network with 2 places and 1 transition
The parameter 'time_window' set at 2.0 seconds defines the time duration
of the relative task of place p2 'custom_task' for each token.

```python
from quantica import QPlace, QTransition, QNet


class ExampleNet(QNet):

    def __init__(self):
        QNet.__init__(self)
        p1 = QPlace(label='p1', init_tokens=1)
        t1 = QTransition(label='t1')
        p2 = QPlace(label='p2', target=self.custom_task, time_window=2.0)

        self.connect(p1, t1, weight=1)
        self.connect(t1, p2, weight=2)

    def custom_task(self):
        print("custom task executing...")

net = ExampleNet()
print(net)
for step in iter(net):
      print(step)
```

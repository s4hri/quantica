# Quantica
Distributed computing based on Petri networks (PNs)

# What is quantica?
Quantica is an Python open-source framework for modeling distributed computing
based on PNs theory.

Quantica is compatible with Python versions >= 3.8

# How does it work ?
As explained in PN's theory, a network consists of places and transitions. Transitions are event-based conditions which allow the places to be enabled.

# Custom code execution
Places are the basic units of custom code execution. The code execution in
Places is determined by the presence of tokens. In Quantica whenever a QPlace (a place in PN theory) receives a token, it executes its relative task immediately.

# How to create a QNet ?
A simple network constisting of a place and a transition is shown below

```
from quantica.core import QNet

net = QNet('MyQNet')
P0 = net.createPlace(init_tokens=1)
T0 = net.createTransition()
net.connect(P0, T0, weight=1)
```

# Acknowledgement
This work has been inspired by the lectures of Prof. Orazio Mirabella (University of Catania) and is based on the theory covered in the slides of Automation Control of Professor Alessandro De Luca (University of Rome - La Sapienza).

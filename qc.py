import random
import itertools
import math
import numpy as np

# hadamard gate
H = (1/(2**0.5)) * np.array([[1,1], [1,-1]])
I = np.identity(4)
A = np.kron(H,I)

def normalize(z):
    return (1.0 / (sum(abs(z)**2) ** 0.5)) * z

v = np.arange(1,9)
w = normalize(v)

def cond_prob(state, query={}, fixed={}):
    num = 0
    denom = 0
    dim = int(math.log2(len(state)))

    for x in itertools.product([0,1], repeat=dim):
        if any(x[index] != b for (index,b) in fixed.items()):
            continue
        i = sum(d << i for (i,d) in enumerate(reversed(x)))
        denom += abs(state[i]) ** 2
        if all(x[index] == b for (index,b) in query.items()):
            num += abs(state[i]) ** 2

    if num == 0:
        return 0

    return num / denom

def measure(q):
    p_e1 = q[0][0]**2 + q[0][1]**2
    p_e0 = q[1][0]**2 + q[1][1]**2

    e1 = np.array([[1,0],[0,0]])
    e0 = np.array([[0,0],[1,0]])
    
    def weighted_choice(choices):
        total = sum(w for c, w in choices)
        r = random.uniform(0,total)
        upto = 0
        for c,w in choices:
            if upto + w >= r:
                return c
            upto += w

    measurement = weighted_choice( [[e1, p_e1], [e0, p_e0]] )
    # TODO simulate collapse of measured qubit
    return measurement

e0 = np.array([[0,0],[1,0]])
e1 = np.array([[1,0],[0,0]])

print H.dot(e1)
print measure(H.dot(e1))

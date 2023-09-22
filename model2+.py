import re
import sys
from pycsp3 import *

k = 1 # Default value of the cyclic-bandwidth
cons1 = 1 # Default value of constraint  x[0] == cons1

# We check if k wasn't given as argument (presence of k=<number> when calling
# model2.py). If it is the case then we consider that k over the default value of k
# Same for  cons1  such as x[0] == cons1
rule = re.compile("k=[0-9]+")
cons1r = re.compile("cons1=[0-9]+")
for arg in sys.argv[1:]:
    if rule.match(arg):
        k = int(arg.split("=")[1])
    if cons1r.match(arg):
        cons1 = int(arg.split("=")[1])

n, E, edges = data

x = VarArray(size=n, dom=range(n))

table = {(i, j) for i in range(n) for j in range(n)
                if min(abs(i - j), n - abs(i - j)) <= k
                   and i != j}

satisfy(
    x[0] == cons1,
    x[2] < x[n-1],
    AllDifferent(x),
    [(x[u], x[v]) in table for u, v in edges]
)

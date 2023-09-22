import re
import sys
from pycsp3 import *

k = 1 # Default value of the cyclic-bandwidth

# We check if k wasn't given as argument (presence of k=<number> when calling
# model2.py). If it is the case then we consider that k over the default value of k
expr_k = "k=[0-9]+"
rule = re.compile(expr_k)
for arg in sys.argv[1:]:
    if rule.match(arg):
        k = int(arg.split("=")[1])

n, E, edges = data

x = VarArray(size=n, dom=range(n))

table = {(i, j) for i in range(n) for j in range(n)
                if min(abs(i - j), n - abs(i - j)) <= k
                   and i != j}

satisfy(
    AllDifferent(x),
    [(x[u], x[v]) in table for u, v in edges]
)

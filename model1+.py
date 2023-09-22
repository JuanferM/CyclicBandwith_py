import re
import sys
from pycsp3 import *

n, E, edges = data

# Check if value  cons1  of constraint x[0] == 1 isn't given as argument
# By default,  cons1 = 1
cons1 = 1

cons1r = re.compile("cons1=[0-9]+")
for arg in sys.argv[1:]:
    if cons1r.match(arg):
        cons1 = int(arg.split("=")[1])

x = VarArray(size=n, dom=range(n))

satisfy(
    x[0] == cons1,
    x[2] < x[n-1],
    AllDifferent(x)
)

minimize(
   Maximum(Minimum(abs(x[u] - x[v]), n - abs(x[u] - x[v])) for u, v in edges)
)

from pycsp3 import *

n, E, edges = data

x = VarArray(size=n, dom=range(n))

satisfy(
    AllDifferent(x)
)

minimize(
   Maximum(Minimum(abs(x[u] - x[v]), n - abs(x[u] - x[v])) for u, v in edges)
)

#!/usr/bin/python

import io
import os
import re
import sys
import json
import gzip
import shutil
import os.path
import string as mS
import random as mR
import numpy as np
from time import time

k = 1 # Default value of the cyclic-bandwidth
datapath = "" # Name of the data file
# Name of the output file
outpath = ''.join(mR.choice(mS.ascii_uppercase + mS.digits) for _ in range(24))
outpath += ".cnf"
solve = False
wr = False


# -----------------------------------------------------------
#    First we load k, datapath and outpath if necessary
# -----------------------------------------------------------

# We check if k wasn't given as argument (presence of k=<number> when calling
# model2.py). If it is the case then we consider that k over the default value of k
# We do the same for datapath and outpath
drule = re.compile("-data=")
orule = re.compile("-output=")
srule = re.compile("-solve")
krule = re.compile("k=[0-9]+")
wrrule = re.compile("-wr")

for arg in sys.argv[1:]:
    if drule.match(arg):
        datapath = arg.split("=")[1]
    elif orule.match(arg):
        outpath = arg.split("=")[1]
    elif krule.match(arg):
        k = int(arg.split("=")[1])
    elif srule.match(arg):
        solve = True
    elif wrrule.match(arg):
        wr = True

del(drule, orule, krule, srule)

assert datapath != "", "Chemin du fichier contenant les données non spécifié."

# TIME START
elapsedT = time()


# -----------------------------------------------------------
#           Now we can load the JSON data file
# -----------------------------------------------------------

with open(datapath) as f:
    data = json.load(f)


# -----------------------------------------------------------
#                       Data preprocessing
# -----------------------------------------------------------

n, E, edges = data.values()
del(data)

# L'ensemble P est défini après pour minimiser l'usage de RAM

# Ensemble des clauses
# !! (la dernière variable de x est la variable qui est toujours
# fixée à Vrai. On écrit les clauses dans le
# un buffer petit à petit (une fois que l'espace RAM est assez occupé,
# c-à-d que nIter > maxiter, on enregistre dans le fichier)
T = n**2+1
buff = io.StringIO()
out = open(outpath, "w")
def flushToFile(f, s, i, maxiter):
    if i > maxiter:
        s.seek(0)
        shutil.copyfileobj(s, f)
        s = io.StringIO()
        i = 0
    return s, i

niter = 1
# Valeur arbitraire, dépend fortement de la capacité en RAM, entres autres
maxiter = 600000
buff.write(f"{T} 0\n")
numclauses = 1

# -----------------------------------------------------------
#                    Construction des clauses
# -----------------------------------------------------------

# On rajoute maintenant la 2e, 3e et 4e clauses
for i in range(n):
    c2 = [] # Deuxième "grande" clause
    for j in range(n):
        c3, c4 = [-(n*i+j)-1], [-(n*i+j)-1] # 3e et 4e grande clause
        for k in range(n):
            if k != j:
                c3.append(-(n*i+k)-1)
                c4.append(-(n*k+i)-1)
        c2.append(n*i+j+1)
        c3.append(0)
        c4.append(0)
        buff, niter = flushToFile(out, buff, niter, maxiter)
        buff.write(" ".join([str(item) for item in c3]) + "\n")
        buff.write(" ".join([str(item) for item in c4]) + "\n")
        niter += 2
        numclauses += 2
    c2.append(0)
    buff, niter = flushToFile(out, buff, niter, maxiter)
    buff.write(" ".join([str(item) for item in c2]) + "\n")
    niter += 1
    numclauses += 1

P = np.full((n, n), False)
for i in range(n):
    for j in range(n):
        if min(abs(j - i), n - abs(j - i)) <= k:
            P[i][j] = True

# On rajoute la 5e et dernière clause
for (u, v) in edges:
    for i in range(n):
        for j in range(n):
            if P[i][j]:
                buff, niter = flushToFile(out, buff, niter, maxiter)
                buff.write(f"{-(n*u+i)-1} {-(n*v+j)-1} {T} 0\n")
                niter += 1
                numclauses += 1
            else:
                buff, niter = flushToFile(out, buff, niter, maxiter)
                buff.write(f"{-(n*u+i)-1} {-(n*v+j)-1} {-T} 0\n")
                niter += 1
                numclauses += 1

del(P)

# -----------------------------------------------------------
#           Exportation au format DIMACS CNF
# -----------------------------------------------------------

instance = datapath.split("/")[-1].split(".")[0]

content = buff.getvalue()
buff.close()
if content != "":
    out.write(content)
out.close()

with open(outpath, "r") as readOut:
    with gzip.open(outpath+".gz", "w") as out:
        out.write(f"c {instance}\n".encode())
        out.write(f"p cnf {T} {numclauses}\n".encode())
        out.write(readOut.read().encode())
os.remove(outpath)

# TIME STOPS
elapsedT = time() - elapsedT

print(f"  * Generated the file {outpath} in \033[1;32m{elapsedT:.2f}\u001B[0m seconds.")


# -----------------------------------------------------------
#           Solving if the option -solve is passed
# -----------------------------------------------------------
if solve:
    from pysat.formula import CNF
    from pysat.solvers import Glucose4

    result = None
    elapsedT = time()
    ins = CNF()
    ins.from_file(outpath+".gz", compressed_with="gzip")

    with Glucose4(ins.clauses) as s:
        result = s.solve()
    elapsedT = time()-elapsedT
    del(ins)
    os.remove(outpath+".gz")

    if wr:
        print(f"  $ {result}")
    print(f"  * Solved {outpath} in \033[1;32m{elapsedT:.2f}\u001B[0m seconds.")

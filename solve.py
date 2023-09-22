#!/usr/bin/python

import re
import sys
import pickle
from time import time
from random import randint
from math import ceil, floor
from multiprocessing import Pool
from os import listdir, cpu_count
from os.path import isfile, join, exists
from subprocess import Popen, PIPE

cpuc = cpu_count()
if cpuc != None:
    nproc = int((1/2) * cpuc)
else:
    nproc = 1
argv = sys.argv
issat = False
degpath = ""
randdeg = False
timeout = 9223372036854775807
lb, ub = -1, 20

assert len(argv) >= 2, "Passez le chemin du répertoire dans lequel se trouve \
les modèles à passer au solveur."

path = argv[1]

assert exists(path), "Le chemin spécifié n'existe pas"
# Get all the filenames in path
filenames = [f for f in listdir(path) if isfile(join(path, f)) and f[0] != '.']

nprule = re.compile("nproc=[0-9]+")
torule = re.compile("t=[0-9]+[s]")
satrule = re.compile("[sS][aA][tT]")
degrule = re.compile("deg=")
rdegrule = re.compile("RAND_DEG")
optional = []
for arg in argv[1:]:
    if nprule.match(arg):
        nproc = int(arg.split("=")[1])
    elif torule.match(arg):
        timeout = arg.split("=")[1]
    elif satrule.match(arg):
        issat = True
    elif degrule.match(arg):
        degpath = arg.split("=")[1]
    elif rdegrule.match(arg):
        randdeg = True
    else:
        if arg != path:
            optional.append(arg)
otherargs = " ".join(optional)
del(optional)

if not issat:
    timedout = re.compile("d INCOMPLETE EXPLORATION")
    crealtime = re.compile("c real time")
else:
    from pysat.formula import CNF
    from pysat.solvers import Glucose4

def singlerun(filename):
    global path, timeout, issat, degpath, lb, ub
    t = -1

    degrees = None
    if degpath != "":
        fname = degpath + filename.split(".")[0].split("-")[1] + ".deg"
        with open(fname, "rb") as f:
            degrees = pickle.load(f)
        lb = ceil(max(degrees)/2)
        ub = floor(len(degrees)/2)

    if not issat:
        global nottimedout, crealtime
        cmd = f"java -jar ACE.jar {path+filename} -t={timeout} -lb={lb} -ub={ub}"
        process = Popen(cmd.split(), stdout=PIPE)
        (output, err) = process.communicate()
        output = output.decode(sys.stdout.encoding)
        exit_code = process.wait()

        timed = False
        print(output)
        lines = output.splitlines()
        for l in lines[-3:]:
            if timedout.search(l) and not timed:
                timed = True
            if crealtime.search(l) and not timed:
                t = float(l.split(":")[1])

        t = "TIMEOUT" if timed else t
    else:
        t = time()
        ins = CNF()
        ins.from_file(path+filename, compressed_with="gzip")
        with Glucose4(ins.clauses) as s:
            s.solve()
        t = time()-t
    if type(t) == float:
        print(f"  * Solved {path+filename} completed in \033[1;32m{t:.2f}\u001B[0m seconds.")
    else:
        print(f"  * Solved {path+filename} completed in \033[1;32m{t}\u001B[0m seconds.")

if __name__ == '__main__':
    pool = Pool(processes=nproc)
    pool.map(singlerun, filenames)

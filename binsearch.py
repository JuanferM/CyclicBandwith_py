#/usr/bin/python

import re
import sys
import pickle
import string as st
import numpy as np
from time import time, sleep
from math import ceil, floor
from random import randint, choice
import multiprocessing as mp
from subprocess import check_output, DEVNULL, CalledProcessError
from os import listdir, cpu_count, remove
from os.path import isfile, join, exists
from signal import signal, SIGPIPE, SIG_DFL

signal(SIGPIPE, SIG_DFL)

argv = sys.argv
issat = False
printerrors = False
degpath = ""
cpuc = cpu_count()
if cpuc != None:
    nproc = int(0.5 * cpuc)
else:
    nproc = 1
timeout = 9223372036854775807
lb, ub = -1, 20
modelwr = ["model3", "model3+"]

assert len(argv) >= 3, "Passez le nom du modèle à exécuter en paramètre et le \
chemin du dossier contenant les fichiers json."

cons1 = 1
path = argv[2]
model = argv[1].split(".py")[0]
central = False

assert exists(path), "Le chemin spécifié n'existe pas"
# Get all the filenames in path
filenames = [f for f in listdir(path) if isfile(join(path, f)) and f[0] != '.']

nprule = re.compile("nproc=[0-9]+")
torule = re.compile("t=[0-9]+")
satrule = re.compile("[sS][aA][tT]")
degrule = re.compile("deg=")
cons1r = re.compile("cons=[0-9]+")
centrr = re.compile("central")
solfilesr = re.compile("solver.+\.[(log)|(xml)|(xml\.gz)]")

optional = []
for arg in argv[2:]:
    if nprule.match(arg):
        nproc = int(arg.split("=")[1])
    elif torule.match(arg):
        timeout = str(int(arg.split("=")[1])*1000)
    elif satrule.match(arg):
        issat = True
    elif degrule.match(arg):
        degpath = arg.split("=")[1]
    elif cons1r.match(arg):
        cons1 = int(arg.split("=")[1])
    elif centrr.match(arg):
        central = True
    else:
        if arg != path:
            optional.append(arg)
otherargs = " ".join(optional)
del(optional, nprule, torule, satrule, degrule, cons1r)

if not issat:
    solutionUNS = re.compile("s UNSATISFIABLE")
    solutionUNK = re.compile("s UNKNOWN")

def singlerun(filename, k, lb, ub):
    global model, path, issat, solutionUNS, solutionUNK, modelwr, timeout, printerrors

    wr = ""
    output = ''.join(choice(st.ascii_uppercase + st.digits) for _ in range(12))
    output = "solver_" + output + ".xml"
    if model in modelwr:
        wr = "-wr"
    if not issat:
        genXML = f"python3 {model}.py -data={path+filename} -output={output} k={k} {wr} cons1={cons1}"
        try:
            _ = check_output(genXML.split(), stderr=DEVNULL).decode(sys.stdout.encoding)
        except CalledProcessError as e:
            if printerrors:
                print(filename, str(e))
        cmd = f"java -jar ACE.jar {output} -t={timeout} -lb={lb} -ub={ub}"
        try:
            output = check_output(cmd.split(), stderr=DEVNULL).decode(sys.stdout.encoding)
        except CalledProcessError as e:
            if printerrors:
                print(filename, str(e))
    else:
        # TODO use Glucose for model3[+]
        pass

    solution = True
    lines = output.splitlines()
    for l in lines:
        if not issat:
            if solutionUNS.search(l) or solutionUNK.search(l):
                solution = False
                break
        else:
            if "$" in l:
                solution = eval(l.split("$")[1].split()[0])

    return solution

def dichotomy(filename, lb, ub):
    if lb < ub:
        mk = int((ub+lb)/2)
        solution = singlerun(filename, mk, lb, ub)

        if mk > 0 and solution:
            return dichotomy(filename, lb, mk-1)
        else:
            return dichotomy(filename, mk+1, ub)
    else:
        return ub

def runBinarySearch(filename):
    global lb, ub
    elapsedT = time()
    if degpath != "":
        degrees = None
        fname = degpath + filename.split(".")[0] + ".deg"
        with open(fname, "rb") as f:
            degrees = pickle.load(f)
        maxdeg = max(degrees)
        lb = ceil(maxdeg/2)
        ub = floor(len(degrees)/2)
        if central:
            cons1 = np.argmax(degrees)

    k = dichotomy(filename, lb, ub)

    elapsedT = time() - elapsedT
    if k > 0:
        print(f"  * Solved {path+filename} in \033[1;32m{elapsedT:.2f}\u001B[0m seconds with \u001b[34;1mk={k}\u001B[0m.")
    else:
        print(f"  * {path+filename} not solved (\033[1;32m{elapsedT:.2f}\u001B[0m seconds).")

    # Delete files
    fnames = [f for f in listdir(".") if isfile(join(".", f)) and f[0] != '.']
    for fname in fnames:
        if solfilesr.match(fname):
            remove(fname)

if __name__ == '__main__':
    with mp.Pool(nproc) as procs:
        procs.map(runBinarySearch, filenames)

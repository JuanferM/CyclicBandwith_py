#!/usr/bin/python

import re
import sys
from multiprocessing import Pool
from os import listdir, makedirs, system, cpu_count
from os.path import isfile, join, exists

cpuc = cpu_count()
if cpuc != None:
    nproc = int((1/2) * cpuc)
else:
    nproc = 1
argv = sys.argv

assert len(argv) >= 3, "Passez le nom du modèle à exécuter en paramètre et le \
chemin du dossier contenant les fichiers json."

k = -1
path = argv[2]
model = argv[1].split(".py")[0]

output_ext = ".xml"
satmodels = ["model3", "model3+"]
modelneedingk = ["model2", "model3", "model2+", "model3+"]

nprule = re.compile("nproc=[0-9]+")
for arg in argv[1:]:
    if nprule.match(arg):
        nproc = int(arg.split("=")[1])

if model in modelneedingk:
    print("Soit k la valeur du cyclic-bandwidth")
    k = int(input(f"Pour quelle valeur de k voulez-vous exécuter {model}.py ?\n \
        k = "))
    assert k > 0, "k doit être un nombre positif non nul!"

modelpath = model+'/' if k == -1 else model+'/'+str(k)+'/'

if model in satmodels:
    output_ext = ".cnf"

# If directory with the same name as the model doesn't exist create it
if not exists(path):
    makedirs(path)
if not exists(modelpath):
    makedirs(modelpath)

# Get all the filenames in path
filenames = [f for f in listdir(path) if isfile(join(path, f)) and f[0] != '.']

def singlerun(filename):
    global model, path, modelpath, k
    if k == -1:
        outpath = modelpath + model + "-" + filename.split(".")[0] + output_ext
        system(f"python3 {model}.py -data={path+filename} -output={outpath}")
    else:
        outpath = modelpath + model + f"-k{k}-" + filename.split(".")[0] + output_ext
        system(f"python3 {model}.py -data={path+filename} -output={outpath} k={k}")

if __name__ == '__main__':
    pool = Pool(processes=nproc)
    pool.map(singlerun, filenames)

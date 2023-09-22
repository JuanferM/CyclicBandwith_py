#!/usr/bin/python

import re
import csv
import sys
from os import listdir
from os.path import isfile, join, exists

argv = sys.argv
path = ""
outputfilename = ""

assert len(argv)-2 <= 1, "Vous devez passer le chemin vers le répertoire contenant \
les sorties de génération de fichier"

orule = re.compile("-output=")
for arg in argv[1:]:
    if orule.match(arg):
        outputfilename = arg.split("=")[1]

if outputfilename == "":
    outputfilename = "output"

path = argv[1]

assert exists(path), "Le chemin spécifié n'existe pas"

filenames = sorted([f for f in listdir(path) if isfile(join(path, f)) and f[0] != '.'])

results = {}
kcount = {}
for filename in filenames:
    k, modelname = "", ""
    with open(path+filename, "r") as f:
        text = f.readlines()
        lines = [l for l in text[1:] if "*" in l]
        for l in lines:
            text = l.split("completed in")
            instancepath = text[0].split()[-1]
            seconds = text[1].split()[0]
            settings = instancepath.split("/")[-1].split("-")
            if len(settings) == 2:
                modelname, instancename = settings
            else:
                modelname, k, instancename = settings
            instancename = instancename.split(".")[0]
            if instancename not in results:
                results[instancename] = {}
                results[instancename][modelname] = {}
                results[instancename][modelname][k] = seconds
            else:
                if modelname not in results[instancename]:
                    results[instancename][modelname] = {}
                if k not in results[instancename][modelname]:
                    results[instancename][modelname][k] = seconds

        if modelname not in kcount:
            kcount[modelname] = {}
            kcount[modelname][k] = 1
        else:
            if k not in kcount[modelname]:
                kcount[modelname][k] = 1
            else:
                kcount[modelname][k] += 1

header, trueheader = ["Instances"], ["Instances"]
firstline, headerline = ",", ""
expectedLineLength = 0
for (model, k) in kcount.items():
    l = len(k)
    firstline += model + "," * l
    expectedLineLength += l
    if l == 1 and type(k) is not dict:
        header.append(model)
        trueheader.append("")
    else:
        trueheader += k.keys()
        header += [model+s for s in k.keys()]

headerline = ",".join(trueheader).replace("k", "k = ")
del(trueheader)

data = {}
for instance in results.keys():
    D = {}
    for model in results[instance].keys():
        D["Instances"] = instance
        for (k, v) in results[instance][model].items():
            D[model+k] = v
    if len(D)-1 == expectedLineLength:
        if instance in data:
            data[instance].append(D)
        else:
            data[instance] = D

with open(outputfilename+".csv", "w") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=header)
    writer.writeheader()
    for instance, row in sorted(data.items()):
        writer.writerow(row)

lines = []
with open(outputfilename+".csv", "r") as samefile:
    lines = samefile.readlines()

with open(outputfilename+".csv", "w") as csvfile:
    csvfile.write(f"{firstline}\n")
    csvfile.write(f"{headerline}\n")
    csvfile.write("".join(lines[1:]))



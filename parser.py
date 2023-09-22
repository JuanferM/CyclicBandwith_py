#!/usr/bin/python

import json
import numpy as np
import pickle as pk
from os import listdir, makedirs, system
from os.path import isfile, join, exists

# Load instance from file filename at path
def loadInstance(filename, path = "data/", verbose = True):
    assert filename != "", "Donner le nom du fichier"

    graph = {}
    filename = path + filename

    with open(filename, "r") as f:
        data = f.readlines()
        instance = data[0].split(":")[1][:-1] # Instance name
        if verbose:
            print("Loading instance : " + instance)

        sizedata = data[1].split()
        graph["V"] = int(sizedata[1]) # No of vertices
        graph["E"] = int(sizedata[2]) # No of edges
        graph["edges"] = []

        for i in range(2, len(data)):
            edge = data[i].split()
            graph["edges"].append((int(edge[0])-1, int(edge[1])-1))

        if verbose:
            print("Done.")

    return json.dumps(graph, indent = 4)

# Convert all raw instances to json and store json files in path "json/"
def convertAllInstances(path = "data/", stopath = "json/", verbose = True):
    # Get all the filenames in path
    filenames = [f for f in listdir(path) if isfile(join(path, f))]

    # If stopath doesn't exist, create it
    if not exists(stopath):
        makedirs(stopath)

    # Convert to JSON
    for filename in filenames:
        json_object = loadInstance(filename, path, verbose)
        fpath = stopath + filename.split(".")[0] + ".json"
        with open(fpath, "w") as out:
            out.write(json_object)

def computeInstanceDegree(filename, path = "data/", verbose = True):
    assert filename != "", "Donner le nom du fichier"

    degrees = None
    filename = path + filename

    with open(filename, "r") as f:
        data = f.readlines()
        instance = data[0].split(":")[1][:-1]
        if verbose:
            print("Loading instance : " + instance)

        sizedata = data[1].split()
        degrees = np.zeros((int(sizedata[1]), 1))

        for i in range(2, len(data)):
            sourcevertex = data[i].split()[0]
            degrees[int(sourcevertex)-1] += 1

        if verbose:
            print("Done.")

    return degrees

def computeAllDegree(path = "data/", stopath = "deg/", verbose = True):
    # Get all the filenames in path
    filenames = [f for f in listdir(path) if isfile(join(path, f))]

    # If stopath doesn't exist, create it
    if not exists(stopath):
        makedirs(stopath)

    # Save with package pickle
    for filename in filenames:
        deg = computeInstanceDegree(filename, path, verbose)
        fpath = stopath + filename.split(".")[0] + ".deg"
        with open(fpath, "wb") as out:
            pk.dump(deg, out)

convertAllInstances()
computeAllDegree()

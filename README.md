# CyclicBandwith_py
Constraint Programming Models to solve the Cyclic Bandwith Problem in Python

# TODO
* Finish documentation (i.e. the arguments of each script, notably the
  arguments of `binsearch.py`)

# Requirements
PyCSP3 :
```
pip install pycsp3
```


# Steps to run a model

## Step 1 : Parse data

Several instances of the cyclic bandwith problem can be found in `data`.
Use the script `parser.py` to parse those data :
```
python3 parser.py
```
The parser will create directories `deg` and `json` containing, respectively,
the maximum degree of each instance and json files describing each instances
(number of vertices, number of edges, edges).

## Step 2 : Run a model on the json files 

Use the `run_model.py` script to run a model of your choice on the json 
files, e.g. :
```
python3 run_model.py model2+.py json/
```
The models will generate XCSP3 instances (in a directory of the same name as
the model) that can be provided to a solver.

## Step 3 : Run ACE solver on the xml files generated

Use the `solve.py` script to solve all the XCSP3 instances in the given
directory, e.g. :
```
python3 solve.py model2+/
```

You should redirect the execution of this command to an output file :
```
python3 solve.py model2+/4/ > outputs/model2_results.txt
```
(will store the output of the command to the directory `outputs`)

## Step 4 : Use the output file to generate a csv file containing the results
```
python3 outtocsv.py outputs/
```
will create a csv file `output.csv` with the results of the resolution.


# How to run the binary search algorithm to find the optimal k cyclic bandwith
```
python3 binsearch.py model2+.py json/
```

## Arguments
* `t` : timeout in seconds
* `nproc` : number of core to use
* `deg` : use maximum degrees to guide search (path to `deg` directory)
* `SAT` : model in use is a SAT model


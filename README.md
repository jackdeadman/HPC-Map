# HPC Map

## What is this?
A small library to wrap the Kaldi command scripts "run.pl" and "queue.pl". This allows for native python functions to be distributed across processes and nodes in a cluster.

## Why use this?
This allows for python code to run on grids such as SGE in an expressive way without the need to create bash files.

## When to use this?
When you know you want to deploy your python program on a Grid but will develop the code locally first. The program allows you to easily switch between using multiple processes (e.g. locally) and multiple nodes on a cluster.

## When not to use this?
If you know your code is going to run on a single computer then you are better off using a library like [joblib](https://joblib.readthedocs.io/en/latest/).

## Example
### Running Locally
```python
from pathlib import Path
from hpc import HPCMap
elements = 10
data = list(range(1, elements+1))

# Run the job locally using multiple processes
runner = HPCMap(cmd="run.pl", default_jobs=elements, scratch=Path('./exp'))

# Supports closures
amount = 2
def fn(x):
    return x * amount

mapper = runner.map("Multiplier", data, fn)
summed = mapper.reduce(lambda a, b: a+b)
print(summed) # Prints 110
```
### Running on SGE
```python
# Change one variable
runner = HPCMap(cmd="queue.pl", default_jobs=elements, scratch=Path('./exp'))
```

# HPC Map

## Installation
```
git clone https://github.com/jackdeadman/HPC-Map`
cd HPC-Map
pip install -e .
```

## Test installation
- Locally: `python hpc/hpc.py`
- Cluster: `python hpc/hpc.py cluster`

## What is this?
A small library to wrap the Kaldi command scripts "run.pl" and "queue.pl". This allows for native python functions to be distributed across processes and nodes in a cluster.

## Why use this?
This allows for python code to run on grids such as SGE in an expressive way without the need to create bash files.

## When to use this?
When you know you want to deploy your python program on a Grid but will develop the code locally first. The program allows you to easily switch between using multiple processes (e.g. locally) and multiple nodes on a cluster.

## When not to use this?
If you know your code is going to run on a single computer then you are better off using a library like [joblib](https://joblib.readthedocs.io/en/latest/). If your code is a large pipeline and involves lots of distributed processes then something like [CGAT-core](https://cgat-core.readthedocs.io/en/latest/) would be better. This library aims to be a dropin tool to bridge the gap between large distributed programs and single core programs.

## Toy Example
### Running Locally
```python
from pathlib import Path
from hpc import HPCMap
elements = 10
data = list(range(1, elements+1))

# Run the job locally using multiple processes
runner = HPCMap(cmd="run.pl", scratch=Path('./exp'))

# Supports closures
amount = 2
def fn(x):
    return x * amount

# One job per element
mapper = runner.map("Multiplier", data, fn)

summed = mapper.reduce(lambda a, b: a+b)
print(summed) # Prints 110

# Or specify the number of jobs
mapper = runner.map("Multiplier", data, lambda els: list(map(fn, els)), jobs=5)
# Mapper contains a list of the results from each job
```
### Running on SGE
```python
# Change one variable
runner = HPCMap(cmd="queue.pl", scratch=Path('./exp'))
```

## Usages
- List of paths to wav files and compute features
- List of scenarios and compute simulations

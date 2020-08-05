from dataclasses import dataclass, field
from typing import Any
from pathlib import Path
from tempfile import gettempdir
#from constants import ROOT_DIR
import dill
import os
import sys
from functools import reduce
import subprocess

ROOT_DIR = Path(__file__).parent

@dataclass
class MappedResponse:
    template_string: str
    num_jobs: int

    def results(self):
        for i in range(self.num_jobs):
            filename = self.template_string.replace('JOB', str(i+1))
            with open(filename, 'rb') as f:
                res = dill.load(f)
            yield res

    def reduce(self, func):
        return reduce(func, self.results())

@dataclass
class HPCMap:
    """
    Helper class to run jobs on HPC, uses kaldi hpc scripts as a backend
    """
    cmd: str = "run.pl" # run.pl | queue.pl
    scratch: Path = field(default_factory=lambda: Path(gettempdir()))

    def __post_init__(self):
        self.scratch = Path(self.scratch)
        self.scratch.mkdir(exist_ok=True, parents=True)

    @property
    def cmd_script(self):
        #return Path("/home/jack/Desktop/scripts") / self.cmd
        return ROOT_DIR / 'bin' / self.cmd


    @property
    def python(self):
        return sys.executable

    def map(self, name: str, data: Any, function, jobs=None):
        function_file = self.scratch / (name + '.func')
        data_file = self.scratch / (name + '.JOB.data')
        output_file = self.scratch / (name + '.JOB.res')
        squeeze_data = False
        if jobs is None:
            jobs = len(data)
            squeeze_data = True

        assert len(data) >= jobs, "Too many jobs for the amount of data"

        with open(function_file, 'wb') as f:
            dill.dump(function, f, recurse=True)

        # Slice up the data into separate files
        for job_id in range(1, jobs+1):
            sub = data[job_id-1::jobs]
            if squeeze_data:
                assert len(sub) == 1, "Cannot squeeze data if it has multiple elements"
                sub = sub[0]

            with open(str(data_file).replace('JOB', str(job_id)), 'wb') as f:
                dill.dump(sub, f)

        python_code = f"""
import dill
with open('{function_file}', 'rb') as f:
    func = dill.load(f)
with open('{data_file}', 'rb') as f:
    data = dill.load(f)
res = func(data)
with open('{output_file}', 'wb') as f:
    dill.dump(res, f)
        """

        cmd = f"{self.python} -c \"{python_code}\""
        run_string = f"{self.cmd_script} JOB=1:{jobs} {self.scratch/name}.JOB {cmd}"
        try:
            subprocess.check_output(run_string, shell=True)
        except subprocess.CalledProcessError as e:
            raise ValueError("Failed to map over data")

        return MappedResponse(str(output_file), jobs)



if __name__ == '__main__':
    cmd = 'run.pl'
    if len(sys.argv) > 1:
        cmd = 'queue.pl'
    elements = 10
    data = list(range(1, elements+1))
    job_runner = HPCMap(cmd=cmd, scratch=Path('./exp'))

    amount = 2
    def fn(x):
        return x * amount

    mapper = job_runner.map("Multiplier", data, fn)
    summed = mapper.reduce(lambda a, b: a+b)
    print(summed)

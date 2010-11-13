import os
import subprocess
from os.path import splitext

python_prog = "/usr/bin/python"
prog = "./pymorphous.py"
testsdir = "./examples/pymorphous"

tests = os.listdir(testsdir)
tests = filter(lambda t: splitext(t)[1] == '.py', tests)
tests = map(lambda t: testsdir + '/' + t, tests)

for t in tests:
    print t
    retcode = subprocess.call([python_prog,prog,t])
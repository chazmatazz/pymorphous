import ast
import sys
import os
from os.path import splitext

if len(sys.argv) < 2:
    print "pymorphous: no input file specified!"
    sys.exit(1)

infile = sys.argv[1]
if not os.path.exists(infile):
    print "File to compile not found: %s" % infile
    sys.exit(1)

ifile = open(infile, 'r')
source = ifile.read()

a = ast.parse(source)

code = compile(a, "<string>", "exec")
exec code
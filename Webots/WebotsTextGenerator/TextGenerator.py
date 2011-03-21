# Copyright (C) 2011 by Charles Dietrich, KJ Khalsa
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import re

def readFromFile(file):
    f = open(file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def writeToFile(file, lines):
    f = open (file, 'w')
    f.writelines(lines)
    f.close()

def appendToFile(file, lines):
    f = open (file, 'a')
    f.writelines(lines)
    f.close()

def valsToString(start, values):
    s = start
    for v in values:
        s+= " " + str(v)
    s += "\n"
    return s

def generateLocs():
    col = range(5)
    row = range(10)
    locs = []
    for r in row:
        for c in col:
            if r%2 == 1:
                c+= 0.5 #column odd, starting half a space over
            locs.append([0, -0.18*r, -1.09*c])
    return locs

def main():
    inputFile = 'pythonSampleRobot.txt'
    outputFile = 'output.txt'
    lines = readFromFile(inputFile)
    locs = generateLocs()
    for l in locs:
        tempLines=[]
        for line in lines:
            tempLines.append(line)
        d = {'  translation':l}
        tempLines = newLines(tempLines, d)
        appendToFile(outputFile, tempLines)

def newLines(lines, d):
    lineNumber = 0
    for line in lines:
        for k in d.keys(): 
            if re.match(k, line)!= None:
                lines[lineNumber] = valsToString(k, d[k])
                break
        lineNumber += 1
    return lines
if __name__ == "__main__": main()

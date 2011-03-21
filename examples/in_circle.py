# Copyright (C) 2011 by Charles Dietrich
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
from pymorphous.core import *
import numpy

class InCircles(Device):
    """
    is the device in a circle?
    
    ;; To see circles drawn in low, medium, and high resolution, run:
    ;;   proto -n 200 -r 20 -l "(+ (blue (in-circle (tup -40 -20) 30)) (green (in-circle (tup 0 0) 20)))"
    ;;   proto -n 1000 -r 15 -l "(+ (blue (in-circle (tup -40 -20) 30)) (green (in-circle (tup 0 0) 20)))"
    ;;   proto -n 5000 -r 5 -l "(+ (blue (in-circle (tup -40 -20) 30)) (green (in-circle (tup 0 0) 20)))"
    """
    def step(self):
        self.blue = self.in_circle(numpy.array([50, 50, 0]), 30)
        self.green = self.in_circle(numpy.array([0,0,0]), 40)
        
    def in_circle(self, origin, radius):
        """
        (def in-circle (o r)
          (let ((dv (- (probe (coord) 1) o)))
            (< (probe (vdot dv dv) 0) (* r r))))
        """
        dv = self.coord - origin
        return numpy.dot(dv, dv) < radius * radius
        
spawn_cloud(klass=InCircles)
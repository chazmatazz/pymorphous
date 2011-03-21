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
import random

class NavGrad(Device):
    """ 
    Display the distance from a few randomly selected devices
    """
    def setup(self):
        self.blue_device = random.random() < 0.1
        
    def step(self):
        """
        ;; For an example of using nav-grad, run:
        ;;   proto -n 500 -r 15 -m -l -s 0.02 -sv "(let ((g (gradient (sense 1))) (which (once (< (rnd 0 1) 0.1)))) (if which (blue 1) 0) (green (< g (inf))) (mov (mux which (nav-grad g) (tup 0 0)))"
        ;; About 1/10 of the devices will turn blue.  Click on a device and
        ;; hit 't'.  As the gradient (green) spreads through the network, the
        ;; blue devices will begin moving to that spot.        
        """
        self.blue = self.blue_device
        g = self.gradient(self.sense0)
        if g < float("inf"):
            self.green = g
        self.move(mux(self.blue_device, self.nav_grad(g), zero_vec))

spawn_cloud(klass=NavGrad)

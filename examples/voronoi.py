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
"""
Voronoi by Andrew Kessel
https://github.com/amkessel/AMK-proto-examples/blob/master/voronoi-decomposition-simple.proto
"""
from pymorphous.core import *
import random

class Voronoi(Device):
    def step(self):
        self.dists = {}
        for i in range(3):
            self.dists[i] = self.gradient(self.senses[i], extra_key=i)
        self.closest = min(self.dists,key = lambda a: self.dists.get(a))
        if self.dists[self.closest] < 50: #max_distance
            self.leds[self.closest] = 5

spawn_cloud(klass=Voronoi)
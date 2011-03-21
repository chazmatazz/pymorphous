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

import math

class SphericalProgression(Device):
    """
    Generate independent blocks that move in polar coordinates
    Designed to work best with led_wave_wall (W)
    """
    def setup(self, radius=50, theta_start=0, phi_start=0.1, theta_increment=0.1, phi_increment=0):
        self.radius = radius
        self.theta_increment = theta_increment
        self.phi_increment = phi_increment
        
        self.theta = theta_start
        self.phi = phi_start
        
    def step(self):
        """ output spherical coordinates """
        self.red = self.radius
        self.green = self.theta
        self.blue = self.phi
        
        self.theta = (self.theta+self.theta_increment) % (2 * math.pi)
        self.phi = (self.phi+self.phi_increment) % (2 * math.pi)

spawn_cloud(klass=SphericalProgression)
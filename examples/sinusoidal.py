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

class Sinusoidal(Device):
    """
    alpha = sin(a1*t1) * sin(sin(b1*t2+c1)*t3) , and the same idea for beta.

    In other words, when all other factors set to 0, the overall motion is
    sinusoidal over a certain period (t3).
    
    The amplitude is sinusoidally modulated by sin(a1*t1)--with its own period
    of t1, while the frequency is sinusoidally modulated by sin(b1*t2+c1), with
    yet a different period of t2.
    
    Regarding the location function: each of the columns of objects has its
    motion delayed relative to the rightmost column. The delay also varies
    sinusoidally from 0 to x, with still a different period.
    """
    
    a1 = .1
    b1 = .1
    c1 = .1
    
    a2 = .1
    b2 = .1
    c2 = .1
    
    t1_period = 20
    t2_period = 20
    t3_period = 20
    
    def setup(self):
        self.t1 = 0
        self.t2 = 0
        self.t3 = 0
        
    def step(self):
        """ output spherical coordinates """
        self.red = 50
        self.green = math.sin(self.a1*self.t1) * math.sin(math.sin(self.b1*self.t2+self.c1)*self.t3 + self.x/50)
        self.blue = math.sin(self.a2*self.t1) * math.sin(math.sin(self.b2*self.t2+self.c2)*self.t3 + self.y/50)
        self.t1 += 1.0/self.t1_period
        self.t2 += 1.0/self.t2_period
        self.t3 += 1.0/self.t3_period

spawn_cloud(klass=Sinusoidal)
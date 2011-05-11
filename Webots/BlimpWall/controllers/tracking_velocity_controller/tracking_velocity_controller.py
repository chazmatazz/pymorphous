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
import sys
sys.path.append('/home/kizzle/Dropbox/pymorphous')
from pymorphous.core import *

class WallTracking(Device):
    timeout = 3
    threshold = .01
    def setup(self):
        
        self.prev_sense = 0
        
        self.tracking_start_time = -1
        
        self.field = Field()
        
        self.delta = None
        
        self.is_next = False

    @property
    def tracking(self):
        return self.tracking_start_time > -1
    
    @property
    def elapsed_time(self):
        return self.time - self.tracking_start_time
    
    def is_close(self, coord):
        v = self.coord - coord
        return numpy.dot(v, v) <= self.threshold
    
    def is_my_coord(self, coord):
        v = self.coord - coord
        return numpy.dot(v, v) == 0
    
    def step(self):
        self.red = self.sense0
        self.green = 255 * self.tracking
        self.blue = 255 * self.is_next
        
        if self.sense0:
            if not self.prev_sense: #rising edge
                self.tracking_start_time = self.time
        else:
            if self.elapsed_time > self.timeout:
                self.tracking_start_time = -1
        
        self.delta = None
        self.is_next = False
        
        max_tracking_start_time = -1
        most_recent_coord = None
        for (k, v) in self.field.items():
            if v:
                (coord, tracking_start_time, delta) = v
                if not self.is_my_coord(coord): # loop over neighbors only (redundant?)
                    if (self.tracking and tracking_start_time > -1 and tracking_start_time < self.tracking_start_time 
                        and tracking_start_time > max_tracking_start_time):
                        max_tracking_start_time = tracking_start_time
                        most_recent_coord = coord
                    if tracking_start_time > -1 and delta != None and self.is_close(coord + delta):
                        self.is_next = True
        if most_recent_coord != None:
            self.delta = self.coord - most_recent_coord
            #print self.coord,self.tracking_start_time, self.delta
        
        #self.is_next = self.is_next and not self.tracking
        
        self.field = self.nbr((self.coord, self.tracking_start_time, self.delta))
            
        self.prev_sense = self.sense0
        
        
spawn_cloud(klass=WallTracking)

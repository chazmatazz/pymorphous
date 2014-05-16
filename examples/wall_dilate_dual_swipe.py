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
from pymorphous.core import *

class WallDualSwipe(Device):
    """
    Swipe right to clear, left to make cloudy
    """
    timeout = 1
    min_line_length = 3
    delta_y = 0
    def setup(self):
        self.prev_sense = 0
        self.tracking_start_time = -1
        self.field = Field()
        self.left_count = -1
        self.right_count = -1
        self.clear = False

    @property
    def tracking(self):
        return self.tracking_start_time > -1
    
    @property
    def elapsed_time(self):
        return self.time - self.tracking_start_time
    
    def is_left_nbr(self, coord):
        return coord[0] < self.coord[0] and abs(coord[1] - self.coord[1]) <= self.delta_y
    
    def is_right_nbr(self, coord):
        return coord[0] > self.coord[0] and abs(coord[1] - self.coord[1]) <= self.delta_y
    
    @property
    def left_detected(self):
        return self.left_count >= self.min_line_length
    
    @property 
    def right_detected(self):
        return self.right_count >= self.min_line_length
    
    def step(self):
        self.red = self.sense0
        self.green = self.tracking
        self.blue = not self.clear
        
        if self.sense0:
            if not self.prev_sense: #rising edge
                self.tracking_start_time = self.time
        else:
            if self.elapsed_time > self.timeout:
                self.tracking_start_time = -1
        
        if self.tracking:
            max_left_count = 0
            max_right_count = 0
            for (k,v) in self.field.items():
                coord = k.coord
                if v:
                    (left_count, right_count, tracking_start_time) = v
                    if tracking_start_time > -1 and tracking_start_time <= self.tracking_start_time: #previous input
                        if self.is_left_nbr(coord):
                            max_left_count = max(max_left_count, left_count)
                        if self.is_right_nbr(coord):
                            max_right_count = max(max_right_count, right_count)
            self.left_count = max_left_count + 1
            self.right_count = max_right_count + 1
        else:
            self.left_count = -1
            self.right_count = -1

        if self.clear:
            if self.right_detected:
                self.clear = False
        else:
            if self.left_detected:
                self.clear = True
                

        self.field = self.nbr((self.left_count, self.right_count, self.tracking_start_time))
        
        self.prev_sense = self.sense0
        
        
spawn_cloud(klass=WallDualSwipe)


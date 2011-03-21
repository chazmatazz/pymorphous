# Copyright (C) 2011 by Charles Dietrich, MIT Proto Authors
# Licensed under the Lesser GNU Public License
# http://www.gnu.org/licenses/lgpl.html
from pymorphous.core import *
import random
import numpy

class FlockDemo(Device):
    """ 
    Flocking of all devices
    """  
    def step(self):
        """
        (def flock-demo (free)
          (let ((g (green (gradient (sense 2)))))
            (mov
             (if (or free (sense 1)) 
               (flock (vmul 0.1 (nav-grad g))) 
               (vmul 0.1 (disperse))))))
        """
        self.move(self.flock(0.1 * self.nav_grad(self.gradient(self.sense1))))
        
spawn_cloud(klass=FlockDemo)

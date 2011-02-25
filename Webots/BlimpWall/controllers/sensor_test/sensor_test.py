# File:         sensor_test2.py
# Date:         February 14th, 2011
# Description:  Changes LED lights
# Author:       khalsak@colorado.edu
#

import sys
sys.path.append('/home/kizzle/Dropbox/pymorphous')
from pymorphous.core import *

class SensorTest(Device): 

        
    def step(self):
        num_nbrs = self.sum_hood(self.nbr(1))
        val = self.sense0/4
        self.green = val
        if num_nbrs>0:
          self.red = self.sum_hood(self.nbr(val))/num_nbrs
        #print self.sense0
        
spawn_cloud(klass=SensorTest)

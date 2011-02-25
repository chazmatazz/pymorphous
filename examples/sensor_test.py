
from pymorphous.core import *

class SensorTest(Device): 

        
    def step(self):
        num_nbrs = self.sum_hood(self.nbr(1))
        val = self.sense0 / 4
        self.green = val
        if num_nbrs > 0:
          self.red = self.sum_hood(self.nbr(val)) / num_nbrs
        
spawn_cloud(klass=SensorTest)

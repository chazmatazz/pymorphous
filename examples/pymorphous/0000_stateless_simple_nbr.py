from pymorphous import *

class BlueNeighborCount(Device):
    def setup(self):
        self.x = 1

    def step(self):
        self.blue(self.sum_hood(self.nbr(self.x)))
          
spawn_cloud(num_devices = 1000, klass=BlueNeighborCount)
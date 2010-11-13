from pymorphous import *

class BlueNeighborCount(Device):
    def step(self):
        self.blue(self.sum_hood(self.nbr(1, hash=1)))
          
spawn_cloud(num_devices=100, klass=BlueNeighborCount)
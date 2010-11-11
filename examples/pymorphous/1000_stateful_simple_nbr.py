from pymorphous import *

class BlueNeighborSense1(Device):
    def step(self):
        self.blue(self.sum_hood(self.nbr(self.sense(1))))
        
spawn_cloud(num_devices=1000, klass=BlueNeighborSense1)
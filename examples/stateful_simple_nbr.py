from pymorphous import *

class BlueNeighborSense1(Device):
    def step(self):
        self.blue = self.sum_hood(self.nbr(self.senses[0]))
        
spawn_cloud(klass=BlueNeighborSense1)
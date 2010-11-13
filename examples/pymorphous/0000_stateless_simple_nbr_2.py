from pymorphous import *
from random import *

class SelectedNeighborCount(Device):
    def setup(self):
        self.selected = random() < 0.1
    def step(self):
        self.green(self.selected)
        self.blue(self.sum_hood(self.nbr(self.selected, hash=1)))
          
spawn_cloud(num_devices=100, klass=SelectedNeighborCount)
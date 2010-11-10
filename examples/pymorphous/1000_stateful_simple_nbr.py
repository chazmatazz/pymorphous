from pymorphous import *

class BlueNeighborSense1(Device):
    def run(self):
        let([(x, self.sense(1))], self.blue(sum_hood(self.nbr(x))))
        
spawn_cloud(num_devices=1000, klass=BlueNeighborSense1)
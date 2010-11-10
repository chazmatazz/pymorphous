from pymorphous import *

class BlueSense1(Device):
    def run(self):
        let([(x, self.sense(1))], self.blue(x))
        
spawn_cloud(num_devices=1000, klass=BlueSense1)
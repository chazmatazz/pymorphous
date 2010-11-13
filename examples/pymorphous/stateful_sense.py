from pymorphous import *

class BlueSense1(Device):
    def step(self):
        self.blue = self.senses[0]
        
spawn_cloud(num_devices=100, klass=BlueSense1)
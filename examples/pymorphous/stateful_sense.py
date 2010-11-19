from pymorphous import *

class BlueSense1(Device):
    def step(self):
        self.blue = self.senses[0]
        
spawn_cloud(klass=BlueSense1)
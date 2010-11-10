from pymorphous import *

class BlueSense1(Device):
    def run(self):
        self.blue(self.sense(1))
        
spawn_cloud(num_devices=1000, klass=BlueSense1)
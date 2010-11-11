from pymorphous import *

class BlueCounter(Device):
    def setup(self):
        self.c = 0
        
    def step(self):
        self.blue(self.c)
        self.c += 1

spawn_cloud(num_devices=1000, klass=BlueCounter)    
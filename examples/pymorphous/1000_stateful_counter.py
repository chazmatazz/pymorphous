from pymorphous import *

class BlueCounter(Device):
    def initialize(self):
        self.c = 0
        
    def run(self):
        self.blue(c)
        c += 1

spawn_cloud(num_devices=1000, klass=BlueCounter)    
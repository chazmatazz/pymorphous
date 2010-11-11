from pymorphous import *

class Move(Device):
    def step(self):
        self.move(random()-0.5, random()-0.5)
        
spawn_cloud(num_devices=1000, klass=Move)
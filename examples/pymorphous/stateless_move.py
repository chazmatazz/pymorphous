from pymorphous import *
import random

class Move(Device):
    def step(self):
        self.move([random.random()-0.5, random.random()-0.5, 0])
        
spawn_cloud(klass=Move)
from pymorphous import *
import random

class MinPlusDemo(Device):
    def setup(self):
        self.senses[0] = random.random()
        
    def step(self):
        self.red = self.senses[0]
        self.green = self.min_hood_plus(self.nbr(self.senses[0]))

spawn_cloud(klass=MinPlusDemo)
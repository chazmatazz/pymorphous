from pymorphous import *
import random

class GradientDemo(Device):
    def setup(self):
        self.senses[0] = random.random() < 0.1
        self.gradient = self.Gradient(self)
        
    def step(self):
        self.red = self.senses[0]
        self.green = self.gradient.value(self.senses[0])*10

spawn_cloud(klass=GradientDemo)
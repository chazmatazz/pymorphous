from pymorphous import *
import random

class GradientDemo(Device):
    """ 
    Display the distance from a few randomly selected devices
    """
    def setup(self):
        self.senses[0] = random.random() < 0.01
        self.gradient = self.Gradient(self)
        
    def step(self):
        self.red = self.senses[0]
        self.green = self.gradient.value(self.senses[0])

spawn_cloud(klass=GradientDemo)
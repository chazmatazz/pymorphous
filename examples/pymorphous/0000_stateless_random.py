from pymorphous import *
from random import *

class RandomDemo(Device):
    """
    Display test
    """
    def setup(self):
        self.val = int(100*random())

    def step(self):
        self.blue(self.val)

spawn_cloud(num_devices=1000, klass=RandomDemo)

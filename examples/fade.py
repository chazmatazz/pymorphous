from pymorphous.core import *

class Fade(Device):
    def setup(self):
        self.val = 0
        
    def step(self):
        if self.sense0:
            self.val = self.sense0
        self.val /= 1.01
        self.blue = self.val
        
spawn_cloud(klass=Fade)
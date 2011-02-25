from pymorphous.core import *

class Draw(Device):
    def setup(self):
        self.val = 0
        
    def step(self):
        if self.sense0:
            self.val = self.sense0
        self.blue = self.val
        
spawn_cloud(klass=Draw)
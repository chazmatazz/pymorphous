from pymorphous import *
import random

class Fieldize(Device):
    def step(self):
        self.blue = self.sum_hood(self.fieldize(1))
        
spawn_cloud(klass=Fieldize)
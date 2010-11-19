from pymorphous import *

class IntHood(Device):
    def step(self):
        self.red = self.sum_hood(self.nbr(1))

spawn_cloud(klass=IntHood)
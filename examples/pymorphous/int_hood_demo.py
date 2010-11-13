from pymorphous import *

class IntHood(Device):
    def step(self):
        self.red = self.sum_hood(self.nbr(1))

spawn_cloud(num_devices=500, klass=IntHood)
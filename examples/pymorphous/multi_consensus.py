from pymorphous import *
import random

class MultiConsensus(Device):
    def setup(self):
        self.vals = [random.random() * 50, random.random() * 100, random.random() * 200]
        
    def step(self):
        for i in range(len(self.vals)):
            self.leds[i] = self.vals[i]
            # must call with extra_key to disambiguate call site
            self.vals[i] = self.consensus(0.01, self.vals[i], extra_key=i)

spawn_cloud(num_devices=100, klass=MultiConsensus)
from pymorphous import *

class MultiConsensusDemo(Device):
    """
    Multi Consensus demo
    """
    def setup(self, epsilon):
        self.epsilon = epsilon
        self.vals = [random(0,50), random(0,100), random(0,200)]
        
    def step(self):
        # needs extra_hash
        for i in range(0, len(self.vals)):
            self.led(i, self.vals[i])
            self.vals[i] = self.consensus(self.epsilon, self.vals[i], extra_hash = i)

spawn_cloud(num_devices=1000, klass=MultiConsensusDemo, args=[0.02])


from pymorphous import *

class MultiConsensusDemo(ExtrasDevice):
    """
    Multi Consensus demo
    """
    def init(self, epsilon):
        self.epsilon = epsilon
        self.vals = [random(0,50), random(0,100), random(0,200)]
        
    def run(self):
        # not doable, how do we track nbr in consensus?
        for i in range(0, len(self.vals)):
            self.vals[i] = self.consensus(self.epsilon, self.vals[i])
            self.led(i, self.vals[i])

spawn_cloud(num_devices=1000, klass=MultiConsensusDemo, args=[0.02])


from pymorphous import *

class DualConsensusDemo(Device):
    """
    Dual Consensus demo
    """
    def setup(self, epsilon):
        self.epsilon = epsilon
        self.val1 = random(0,50)
        self.val2 = random(0,100)
        
    def step(self):
        # have to track consensus calls individually
        self.blue(self.val1)
        self.red(self.val2)
        self.val1 = self.consensus(self.epsilon, self.val1, hash=1)
        self.val2 = self.consensus(self.epsilon, self.val2, hash=2)

spawn_cloud(num_devices=1000, klass=DualConsensusDemo, args=[0.02])


from pymorphous import *

class BlueConsensusDemo(ExtrasDevice):
    """
    Consensus demo from paper
    """
    def setup(self, epsilon):
        self.epsilon = epsilon
        self.val = random(0,50)
        
    def step(self):
        self.blue(self.val)
        self.val = self.consensus(self.epsilon, self.val, hash=1)

spawn_cloud(num_devices=1000, klass=BlueConsensusDemo, args=[0.02])


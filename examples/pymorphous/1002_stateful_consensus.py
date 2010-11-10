from pymorphous import *

class BlueConsensusDemo(ExtrasDevice):
    """
    Consensus demo from paper
    """
    def init(self, epsilon):
        self.epsilon = epsilon
        self.val = random(0,50)
        
    def run(self):
        self.val = self.consensus(self.epsilon, self.val)
        self.blue(self.val)

spawn_cloud(num_devices=1000, klass=BlueConsensusDemo, args=[0.02])


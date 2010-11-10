from pymorphous import *

class DualConsensusDemo(ExtrasDevice):
    """
    Dual Consensus demo
    """
    def init(self, epsilon):
        self.epsilon = epsilon
        self.val1 = random(0,50)
        self.val2 = random(0,100)
        
    def run(self):
        self.val1 = self.consensus(self.epsilon, self.val1)
        self.blue(self.val1)
        self.val2 = self.consensus(self.epsilon, self.val2)
        self.red(self.val2)

spawn_cloud(num_devices=1000, klass=DualConsensusDemo, args=[0.02])


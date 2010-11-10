from pymorphous import *
# the device to run

class BlueConsensusDemo(ExtrasDevice):
    """
    Consensus demo from paper
    """
    def run(self, epsilon): 
        self.blue(self.consensus(epsilon, once(random(0,50))))

# stuff to run the simulation

spawn_cloud(num_devices=1000, klass=BlueConsensusDemo, args=[0.02])


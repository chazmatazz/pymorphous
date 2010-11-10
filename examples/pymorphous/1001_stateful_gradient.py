from pymorphous import *
# the device to run

class BlueGradientDemo(LibDevice):
    """
    Gradient demo smoketest
    """
    def run(self, threshold):
        let([(x, 1 if once(random(0,1) < threshold) else 0)], 
            self.blue(self.gradient(x)))

# stuff to run the simulation

spawn_cloud(num_devices=1000, klass=BlueGradientDemo, args=[0.01])


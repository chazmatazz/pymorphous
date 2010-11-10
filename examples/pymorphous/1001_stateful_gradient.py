from pymorphous import *

class BlueGradientDemo(LibDevice):
    """
    Gradient demo smoketest
    """
    def init(self, threshold):
        self.selected = 1 if random(0,1) < threshold else 0
        self.gradient = self.Gradient()

    def run(self):
        self.blue(self.gradient.value(self.selected))

spawn_cloud(num_devices=1000, klass=BlueGradientDemo, args=[0.01])


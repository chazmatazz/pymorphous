from pymorphous import *

# the device to run

class BlueCounter(Device):
    def run(self):
        letfed([(c, 0, lambda c: c + 1)], self.blue(c))

# stuff to run the simulation

spawn_cloud(num_devices=1000, klass=BlueCounter)    
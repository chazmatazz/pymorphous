from pymorphous.core import *

import math

class SineWave(Device):
    """
    Generate independent blocks that move in polar coordinates
    Designed to work best with led_wave_wall (W)
    """
    def setup(self):
        self.t = 0
        
    def step(self):
        """ output spherical coordinates """
        self.red = 50
        self.green = .1 * math.sin(2*self.t+self.x/10)
        self.blue = .1 * math.sin(2*self.t+self.y/10)
        self.t += .1

spawn_cloud(klass=SineWave)
from pymorphous.core import *

import math

class SphericalProgression(Device):
    """
    Generate independent blocks that move in polar coordinates
    Designed to work best with led_wave_wall (W)
    """
    def setup(self, radius=50, theta_start=0, phi_start=0.1, theta_increment=0.1, phi_increment=0):
        self.radius = radius
        self.theta_increment = theta_increment
        self.phi_increment = phi_increment
        
        self.theta = theta_start
        self.phi = phi_start
        
    def step(self):
        """ output spherical coordinates """
        self.red = self.radius
        self.green = self.theta
        self.blue = self.phi
        
        self.theta = (self.theta+self.theta_increment) % (2 * math.pi)
        self.phi = (self.phi+self.phi_increment) % (2 * math.pi)

spawn_cloud(klass=SphericalProgression)
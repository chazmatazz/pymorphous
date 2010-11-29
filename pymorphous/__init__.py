"""
Defines the public interface for pymorphous:
Field
NbrKeyError
BaseDevice
spawn_cloud
"""

import pymorphous.constants

try:
    import settings
except ImportError:
    import default_settings as settings

if settings.target_runtime == 'simulator':
    if settings.runtime.use_graphics == pymorphous.constants.UNSPECIFIED:
        try:
            from pymorphous.simulator_graphics import graphics
            settings.runtime.use_graphics = graphics
        except ImportError:
            pass    
    import pymorphous.simulator_runtime as implementation
elif settings.target_runtime == 'webots_wall':
    import pymorphous.webots_wall_runtime as implementation
else:
    raise Exception("no suitable runtime found")

Field = implementation._Field
NbrKeyError = implementation._NbrKeyError

class BaseDevice(implementation._BaseDevice):
    def __init__(self, *args, **kwargs):
        super(BaseDevice, self).__init__(*args, **kwargs)
    
    def __repr__(self):
        return "#%s" % self.id
    
    @property
    def red(self):
        return self.leds[0]
    
    @red.setter
    def red(self, val):
        self.leds[0] = val
        
    @property
    def green(self):
        return self.leds[1]
    
    @green.setter
    def green(self, val):
        self.leds[1] = val
        
    @property
    def blue(self):
        return self.leds[2]
    
    @blue.setter
    def blue(self, val):
        self.leds[2] = val

    @property
    def sense0(self):
        return self.senses[0]
    
    @sense0.setter
    def sense0(self, val):
        self.senses[0] = val
        
    @property
    def sense1(self):
        return self.senses[1]
    
    @sense1.setter
    def sense1(self, val):
        self.senses[1] = val
        
    @property
    def sense2(self):
        return self.senses[2]
    
    @sense2.setter
    def sense2(self, val):
        self.senses[2] = val
        
    def sum_hood(self, field):
        return sum(field.not_none_values()+[0])
    
    def min_hood(self, field):
        return min(field.not_none_values()+[float('inf')])
    
    def max_hood(self, field):
        return max(field.not_none_values()+[float('-inf')])
    
    def sum_hood_plus(self, field):
        """ return the sum over the field without self """
        return self.sum_hood(self.deself(field))
    
    def min_hood_plus(self, field):
        """ return the min over the field without self """
        return self.min_hood(self.deself(field))
    
    def max_hood_plus(self, field):
        """ return the max over the field without self """
        return self.max_hood(self.deself(field))

def spawn_cloud(*args, **kwargs):
    return implementation._spawn_cloud(settings, *args, **kwargs)

from pymorphous.lib import *
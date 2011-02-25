# File:         led_test.py
# Date:         December 10th, 2010
# Description:  Changes LED lights
# Author:       khalsak@colorado.edu
#

import sys
sys.path.append('/home/kizzle/Dropbox/pymorphous')
from pymorphous.core import *

#class Enumerate(object):
#  def __init__(self, names):
#    for number, name in enumerate(names.split()):
#      setattr(self, name, number)

class Blink(Device): 

    def setup(self):
        self.state = True
        
    def step(self):
        if self.state==0: self.state=2
        else: self.state=0
        self.green = self.state
        
spawn_cloud(klass=Blink)

# WbDeviceTag ir0, ir1, led[3];
# led[0] = wb_robot_get_device("led0");
# random_color = (int) (10 * ((float) rand() / RAND_MAX));
# wb_led_set(led[0], random_color);

#0-nothing
#1- red
#2- green
#3- blue
#4- yellow/orange
#5- teal
#6- magenta
#7- yellow
#8- magenta
#9- dark yellow
#10- off

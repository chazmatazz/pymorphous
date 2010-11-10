class Vector:
  
  def __init__(self, data):
    self.data = data
    
  def __repr__(self):
    return repr(self.data)  
    
  def __add__(self, other):
    data = []
    for j in range(len(self.data)):
      data.append(self.data[j] + other.data[j])
    return Vector(data)

  def __sub__(self, other):
    data = []
    for j in range(len(self.data)):
      data.append(self.data[j] - other.data[j])
    return Vector(data)

def field(lst):
    pass

class Device:
    def __init__(self, x, y, radio_range):
        self.leds = [0, 0, 0]
        self.senses = [0, 0, 0]
        self.probes = [0, 0, 0]
        self.x = x
        self.y = y
        self.radio_range = radio_range
        self.program_counter = 0
    
    def blue(self, val):
        self.leds[2] = val
        
    def sense(self, i):
        return self.senses[i]

    def probe(self, value, i):
        self.probes[i] = value
        return self.probes[i]
    
    def move(self, x, y):
        self.x += x
        self.y += y
    
    def coord(self):
        return Vector([x,y])
    
    def fold_hood(self, f, neighbor_field):
        return reduce(f, neighbor_field)

    def nbr(self, var):
        pass
    
    def nbr_range(self):
        pass
    
    def nbr_lag(self):
        pass
    
    def dt(self):
        pass

def spawn_cloud(klass=None, args=None, num_devices=None, devices=None, grid=False, step=0, radio_range=20):
    
    def run_klass(klass, args):
        pass
    
    if devices:
        pass
    else:
        devices = []
        for i in range(0, num_devices):
            devices += [(run_klass(klass, args))]
            
from pymorphous.lib import *
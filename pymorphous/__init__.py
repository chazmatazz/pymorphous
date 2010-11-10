class Device:
    def __init__(self, x, y, radio_range):
        self.blue = 0
        self.sense = {'1': 0}
        self.x = x
        self.y = y
        self.radio_range = radio_range
        self.program_counter = 0
    
    def blue(self, val):
        self.blue = val
        
    def sense(self, id):
        return sense[id]

    def move(self, x, y):
        self.x += x
        self.y += y
        
    def letfed(self, decls, body):
        pass
    
def fold_hood(f, neighbor_field):
    return reduce(f, neighbor_field)

def nbr(field):
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
from pymorphous.extras import *
import random
import numpy
import math
from PySFML import sf
import inspect

id_counter = 0

def getid():
    global id_counter
    id = id_counter
    id_counter += 1
    return id

class NbrKeyError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
class BaseDevice(object):
    def __init__(self, pos, id, step_size, radio_range, cloud):
        self._pos = pos
        self.id = id
        self.step_size = step_size
        self.radio_range = radio_range
        self.cloud = cloud
        self.leds = [0, 0, 0]
        self.senses = [0, 0, 0]
        self._nbrs = []
        self._vals = {}
        self._keys = set()
    
    def move(self, vector):
        self.cloud.moved = True
        self._pos += vector
    
    @property
    def x(self):
        return self._pos[0]
    
    @x.setter
    def x(self, value):
        self.cloud.moved = True
        self._pos[0] = value

    @property
    def y(self):
        return self._pos[1]
    
    @y.setter
    def y(self, value):
        self.cloud.moved = True
        self._pos[1] = value
        
    @property
    def z(self):
        return self._pos[2]
    
    @z.setter
    def z(self, value):
        self.cloud.moved = True
        self._pos[2] = value  
    
    @property
    def pos(self):
        return self._pos
    
    @pos.setter
    def pos(self, new_pos):
        self.cloud.moved = True
        self._pos = new_pos
    
    def nbr(self, val, extra_key=None):
        key = self._stack_location()
        return self._nbr("%s%s" % (key, extra_key), val)
    
    def _stack_location(self):
        # file:line_number:index_of_last_atttempted_instruction_in_bytecode
        # the last attempted instruction in bytecode is not safe
        return repr(["%s:%d:%d" % (f[1], f[2], f[0].f_lasti) for f in inspect.stack()])

    def _nbr(self, key, val):
        if key in self._keys:
            raise NbrKeyError("key %s found twice" % key)
        self._keys |= set([key])
        self._vals[key] = val
        ret = {}
        for nbr in self._nbrs + [self]:
            try:
                ret[nbr] = nbr._vals[key]
            except KeyError:
                pass
        return ret
    
    def nbr_range(self):
        ret = {}
        for nbr in self._nbrs + [self]:
            delta = self.pos - nbr.pos
            ret[nbr] = math.sqrt(numpy.dot(delta, delta))
        return ret
    
    def nbr_lag(self):
        ret = {}
        for nbr in self._nbrs + [self]:
            if nbr == self:
                ret[nbr] = 0
            else:
                ret[nbr] = nbr.dt
        return ret
    
    @property
    def dt(self):
        return 0.01 if self.step_size==0 else self.step_size
        
    def _step(self):
        self.step()
        
    def _advance(self):
        self._keys = set()
    
    def _draw(self, window):
        window.Draw(sf.Shape.Circle(self.pos[0]*1000, 
                                    self.pos[1]*1000,
                                    10,
                                    sf.Color(255,255,255,255)))
        window.Draw(sf.Shape.Circle(self.pos[0]*1000, 
                                    self.pos[1]*1000,
                                    0.1*1000,
                                    sf.Color(255,0,0,100)))
        text = sf.String(repr(self.leds))
        text.SetSize(20)
        text.Move(self.pos[0]*1000, self.pos[1]*1000)
        window.Draw(text)

    def __repr__(self):
        return "id: %s, leds: %s, senses: %s, pos: %s" % (
                        self.id, repr(self.leds), repr(self.senses), 
                        repr(self.pos))
        
class spawn_cloud(object):      
    def __init__(self, klass=None, args=None, num_devices=None, devices=None, 
                step_size=0, radio_range=0.05, width=1000, height=1000, 
                window_title=None, _3D=False):
    
        window = sf.RenderWindow(sf.VideoMode(width, height), 
                                 window_title if window_title else klass.__name__)
        
        if not devices:
            devices = []
            for i in range(0, num_devices):
                d = klass(pos = numpy.array([random.random(), random.random(), random.random() if _3D else 0]),
                          id = getid(), 
                          step_size = step_size, 
                          radio_range = radio_range, 
                          cloud = self)
                devices += [d]
                if hasattr(d, "setup"):
                    if args:
                        d.setup(*args)
                    else:
                        d.setup()
                
        
        self.moved = True
            
        running = True
        while running:
            event = sf.Event()
            while window.GetEvent(event):
                if event.Type == sf.Event.Closed:
                    running = False
                
            if self.moved:
                for d in devices:
                    d._nbrs = []
                    for e in devices:
                        if d != e:
                            delta = e.pos - d.pos
                            dist = math.sqrt(numpy.dot(delta, delta))
                            if dist < d.radio_range:
                                d._nbrs += [e]
            
            self.moved = False
            
            for d in devices:
                d._step()
            
            for d in devices:
                d._advance()
                
            window.Clear()
            for d in devices:
                d._draw(window)
            window.Display()
            
            
from pymorphous.lib import *
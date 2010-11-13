from random import *
from PySFML import sf
import numpy

def field(lst):
    pass

id_counter = 0

def getid():
    global id_counter
    id = id_counter
    id_counter += 1
    return id

class BaseDevice:
    def __init__(self, x, y):
        self.id = getid()
        self.leds = [0, 0, 0]
        self.senses = [0, 0, 0]
        self.pos = numpy.array([x,y])
        self._nbrs = set()
        self._vals = {}
    
    def red(self, val):
        self.leds[0] = val
        
    def green(self, val):
        self.leds[1] = val
        
    def blue(self, val):
        self.leds[2] = val
        
    def sense(self, i):
        return self.senses[i]
    
    def move(self, x, y):
        self.x += x
        self.y += y
    
    def coord(self):
        return self.pos
    
    @property
    def x(self):
        return self.pos[0]
    
    @x.setter
    def x(self, value):
        self.pos[0] = value

    @property
    def y(self):
        return self.pos[1]
    
    @y.setter
    def y(self, value):
        self.pos[1] = value  
        
    def fold_hood(self, f, neighbor_field):
        return reduce(f, neighbor_field)

    def nbr(self, val, hash=None, extra_hash=None):
        """
        Identify the call site with hash, send (hash, val) to neighbors
        retrieve field of (hash, val) from neighbors
        match up hash, return val
        the idea of extra_hash is to disambiguate same call site (e.g. multi consensus) 
        """
        if hash:
            self._vals[hash] = val
        else:
            raise Exception("not implemented")
        lst = []
        for nbr in self._nbrs:
            try:
                lst += [nbr._vals[hash]]
            except KeyError:
                pass
        return lst
    
    def nbr_range(self):
        """ returns a field of distances to neighbors """
        pass
    
    def nbr_lag(self):
        """ returns a field of time lags to neighbors """
        pass
    
    def dt(self):
        return self.step_size

    def _step(self):
        self.step()
    
    def _draw(self, window):
        x = self.x*1000
        y = self.y*1000
        window.Draw(sf.Shape.Circle(x, y, 10,
                                    sf.Color(255,255,255,255)))
        text = sf.String(repr(self.leds))
        text.SetSize(10)
        text.Move(x,y)
        window.Draw(text)
        
    def __repr__(self):
        return "id: %s, leds: %s, senses: %s, coord: %s" % (
                        self.id, repr(self.leds), repr(self.senses), 
                        repr(self.coord()))
        
def spawn_cloud(klass=None, args=None, num_devices=None, devices=None, 
                step_size=0, radio_range=0.05, width=1000, height=1000, 
                window_title="PyMorphous"):
    if not devices:
        devices = []
        for i in range(0, num_devices):
            x = random()
            y = random()
            d = klass(x=x, y=y)
            if hasattr(d, "setup"):
                if args:
                    d.setup(*args)
                else:
                    d.setup()
            devices += [d]
            
    window = sf.RenderWindow(sf.VideoMode(width, height), window_title)
    running = True
    while running:
        event = sf.Event()
        while window.GetEvent(event):
            if event.Type == sf.Event.Closed:
                running = False
        
        # this is expensive
        for d in devices:
            d._nbrs = set()
            for e in devices:
                delta = d.coord() - e.coord()
                if numpy.dot(delta, delta) < radio_range:
                    d._nbrs |= set([e])
                    
        
        for d in devices:
            d._step()
        
        window.Clear()
        for d in devices:
            d._draw(window)
        window.Display()
            
            
from pymorphous.lib import *
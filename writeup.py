import random
import numpy
import math
from PySFML import sf
import inspect

def field_sum(lst):
    ret = {}
    for e in lst:
        if isinstance(e, dict):
            for k in e:
                if not hasattr(ret, str(k)):
                    ret[k] = e[k]
                else:
                    ret[k] += e[k]
    for e in lst:
        if not isinstance(e, dict):
            ret[k] += e      
    return ret

def field_product(lst):
    ret = {}
    for e in lst:
        if isinstance(e, dict):
            for k in e:
                if not hasattr(ret, str(k)):
                    ret[k] = e[k]
                else:
                    ret[k] *= e[k]
    for e in lst:
        if not isinstance(e, dict):
            ret[k] *= e
    return ret

def field_sub(c1, c2):
    ret = {}
    if isinstance(c1, dict) and not isinstance(c2, dict):
        _c1 = c1
        _c2 = {}
        for k in _c1:
            _c2[k] = c2
    elif not isinstance(c1, dict) and isinstance(c2, dict):
        _c1 = {}
        _c2 = c2
        for k in _c2:
            _c1[k] = c1
    else:
        _c1 = c1
        _c2 = c2
        
    for k in _c1:
        try:
            ret[k] = _c1[k] - _c2[k]
        except KeyError:
            pass

    return ret

def field_lteq(c1, c2):
    ret = {}
    if isinstance(c1, dict) and not isinstance(c2, dict):
        _c1 = c1
        _c2 = {}
        for k in _c1:
            _c2[k] = c2
    elif not isinstance(c1, dict) and isinstance(c2, dict):
        _c1 = {}
        _c2 = c2
        for k in _c2:
            _c1[k] = c1
    else:
        _c1 = c1
        _c2 = c2
        
    for k in _c1:
        try:
            ret[k] = _c1[k] <= _c2[k]
        except KeyError:
            pass

    return ret

def mux(test, then, else_):
    if test:
        return then
    else:
        return else_

class NbrKeyError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Device:
    def __init__(self, pos, id):
        self.pos = pos
        self.id = id
        self.leds = [0,0,0]
        self.senses = [0,0,0]
        self.nbrs = []
        self.data = {}
        self.keys = set()
        self.dt = 0.1
        self.radio_range = 0.1
        
    def nbr(self, val, extra_key=None):
        key = self._stack_location()
        return self._nbr("%s%s" % (key, extra_key), val)
    
    def _stack_location(self):
        # file:line_number:index_of_last_atttempted_instruction_in_bytecode
        # the last attempted instruction in bytecode is not safe
        return repr(["%s:%d:%d" % (f[1], f[2], f[0].f_lasti) for f in inspect.stack()])

    def _nbr(self, key, val):
        if key in self.keys:
            raise NbrKeyError("key %s found twice" % key)
        self.keys |= set([key])
        self.data[key] = val
        ret = {}
        for nbr in self.nbrs + [self]:
            try:
                ret[nbr] = nbr.data[key]
            except KeyError:
                pass
        return ret
    
    def nbr_range(self):
        ret = {}
        for nbr in self.nbrs + [self]:
            delta = self.pos - nbr.pos
            ret[nbr] = math.sqrt(numpy.dot(delta, delta))
        return ret
    
    def nbr_lag(self):
        ret = {}
        for nbr in self.nbrs + [self]:
            if nbr == self:
                ret[nbr] = 0
            else:
                ret[nbr] = 0.1
        return ret
    
    def _advance(self):
        self.keys = set()
        
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

    def sum_hood(self, field):
        return sum([field[k] for k in field])
    
    def min_hood(self, field):
        return min([field[k] for k in field])
    
    def max_hood(self, field):
        return max([field[k] for k in field])
    
    def sum_hood_plus(self, field):
        """ return the sum over the field without self """
        f = field.copy()
        f[self] = 0
        return self.sum_hood(f)
    
    def min_hood_plus(self, field):
        """ return the min over the field without self """
        f = field.copy()
        f[self] = float('inf')
        return self.min_hood(f)
    
    def max_hood_plus(self, field):
        """ return the max over the field without self """
        f = field.copy()
        f[self] = float('-inf')
        return self.max_hood(f)
    
class Consensus(Device):
    def consensus(self, val, extra_key=None):
        """ Laplacian """
        return val + 0.01 * self.sum_hood(field_sub(self.nbr(val, extra_key), val))
    
    def setup(self):
        self.val = random.random() * 1000
        
    def step(self):
        self.leds[0] = self.val
        # note that we don't call with extra hash
        self.val = self.consensus(self.val)
 
class DualConsensus(Consensus):
    def setup(self):
        self.vals = [random.random() * 50, random.random() * 100]
        
    def step(self):
        self.leds[0] = self.vals[0]
        # note that we don't call with extra hash
        self.vals[0] = self.consensus(self.vals[0])
        self.leds[1] = self.vals[1]
        self.vals[1] = self.consensus(self.vals[1])

class TripleConsensusSingleLine(Consensus):
    def setup(self):
        self.vals = [random.random() * 50, random.random() * 100, random.random() * 200]
        
    def step(self):
        self.leds = [self.vals[0], self.vals[1], self.vals[2]]
        # note that we don't call with extra hash
        self.vals = [self.consensus(self.vals[0]), self.consensus(self.vals[1]), self.consensus(self.vals[2])]
        
class MultiConsensus(Consensus):
    def setup(self):
        self.vals = [random.random() * 50, random.random() * 100, random.random() * 200]
        
    def step(self):
        for i in range(len(self.vals)):
            self.leds[i] = self.vals[i]
            # must call with extra_key to disambiguate call site
            self.vals[i] = self.consensus(self.vals[i], extra_key=i)

class IntHood(Device):
    def step(self):
        self.leds[0] = self.sum_hood(self.nbr(1))

class MinPlusDemo(Device):
    
    def setup(self):
        self.senses[0] = random.random()
        
    def step(self):
        self.leds[0] = self.senses[0]
        self.leds[1] = self.min_hood_plus(self.nbr(self.senses[0]))

class GradientDemo(Device):
    
    class Gradient:
        """
        (def gradient (src)
          (1st (rep (tup d v) (tup (inf) 0)
            (mux src (tup 0 0)        ; source
              (mux (max-hood+
                (<= (+ (nbr d) (nbr-range) (* v (+ (nbr-lag) (dt)))) d))
                (tup (min-hood+ (+ (nbr d) (nbr-range))) 0)
                (let ((v0 (/ (radio-range) (* (dt) 12)))) (tup (+ d (* v0 (dt))) v0)))))))
        """
        def __init__(self, device):
            self.device = device
            self.d = float('inf')
            self.v = 0
            
        def value(self, src):
            new_d = field_sum([self.device.nbr(self.d), self.device.nbr_range(), field_product([self.v, field_sum([self.device.nbr_lag(), self.device.dt])])])
            then_tup = (self.device.min_hood_plus(field_sum([self.device.nbr(self.d), self.device.nbr_range()])), 0)
            v0 = self.device.radio_range / (self.device.dt * 12)
            else_tup = (self.d + v0 * self.device.dt, v0)
            else_ = mux(self.device.max_hood_plus(field_lteq(new_d, self.d)), then_tup, else_tup)
            (self.d, self.v) = mux(src, (0,0), else_)
            return self.d
    
    def setup(self):
        self.senses[0] = random.random() < 0.5
        self.gradient = self.Gradient(self)
        
    def step(self):
        self.leds[0] = self.senses[0]
        self.leds[1] = self.gradient.value(self.senses[0])

def spawn_cloud(klass):
    # create devices, each with a position
    devices = [klass(numpy.array([random.random(), random.random()]), i) for i in range(100)]

    window = sf.RenderWindow(sf.VideoMode(1000, 1000), klass.__name__)

    # set the neighbors of each device
    for d in devices:
        for e in devices:
            if d != e:
                delta = e.pos - d.pos
                dist = math.sqrt(numpy.dot(delta, delta))
                if dist < 0.1:
                    d.nbrs += [e]
    
    for d in devices:
        if(hasattr(d, "setup")):
           d.setup()

    running = True
    while running:
        event = sf.Event()
        while window.GetEvent(event):
            if event.Type == sf.Event.Closed:
                running = False
        
        for d in devices:
            d.step()
        
        for d in devices:
            d._advance()

        window.Clear()
        for d in devices:
            d._draw(window)
        window.Display()
        
for klass in [GradientDemo, MinPlusDemo, IntHood, Consensus, DualConsensus, MultiConsensus, TripleConsensusSingleLine]:
    spawn_cloud(klass)
            
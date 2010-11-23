import random
import numpy
import inspect
import sys
from scipy.spatial import KDTree
import operator

PRINT_MS = False
SAFE = False

class Field(dict):
    def __init__(self, *args):
        dict.__init__(self, *args)
    
    def _op(self, other, op):
        ret = Field()
        if isinstance(other, Field):
            for k in self.keys():
                if self[k]!=None and other[k]!=None:
                    ret[k] = op(self[k], other[k])
                else:
                    ret[k] = None       
        else:
            for k in self.keys():
                if self[k]!=None:
                    ret[k] = op(self[k], other)
                else:
                    ret[k] = None
        return ret
    
    def _rop(self, other, op):
        ret = Field()
        if isinstance(other, Field):
            for k in self.keys():
                if self[k]!=None and other[k]!=None:
                    ret[k] = op(other[k], self[k])
                else:
                    ret[k] = None       
        else:
            for k in self.keys():
                if self[k]!=None:
                    ret[k] = op(other, self[k])
                else:
                    ret[k] = None
        return ret
    
    def _iop(self, other, iop):
        print self, iop, other
        if isinstance(other, Field):
            for k in self.keys():
                if self[k]!=None and other[k]!=None:
                    iop(self[k], other[k])
                else:
                    self[k] = None
        else:
            for k in self.keys():
                if self[k]!=None:
                    iop(self[k], other)
                else:
                    self[k] = None
        return self
    
    def __add__(self, other):
        return self._op(other, operator.add)
    
    def __sub__(self, other):
        return self._op(other, operator.sub)
    
    def __radd__(self, other):
        return self._rop(other, operator.add)
    
    def __rsub__(self, other):
        return self._op(other, operator.sub)
    
    def __iadd__(self, other):
        return self._iop(other, operator.iadd)
    
    def __isub__(self, other):
        return self._iop(other, operator.isub)
    
    def __div__(self, other):
        return self._op(other, operator.div)
    
    def __mul__(self, other):
        return self._op(other, operator.mul)
    
    def __rdiv__(self, other):
        return self._rop(other, operator.div)
    
    def __rmul__(self, other):
        return self._rop(other, operator.mul)
    
    def __idiv__(self, other):
        return self._iop(other, operator.idiv)
    
    def __imul__(self, other):
        return self._iop(other, operator.imul)
    
    def __le__(self, other):
        return self._op(other, operator.le)
    
    def __ge__(self, other):
        return self._op(other, operator.ge)
    
    def not_none_values(self):
        ret = []
        for v in self.values():
            if v!=None:
                ret += [v]
        return ret
    
class NbrKeyError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class BaseDevice(object):
    def __init__(self, pos, id, radio_range, cloud):
        # pos is a numpy.array
        self._pos = pos
        self.id = id
        self._radio_range = radio_range
        self.cloud = cloud
        self.leds = [0, 0, 0]
        self.senses = [0, 0, 0]
        self._nbrs = []
        self._dict = {}
        self._old_dict = {}
        self._dt = 0
        self.root_frame = None
    
    @property
    def radio_range(self):
        return self._radio_range
    
    @radio_range.setter
    def radio_range(self, value):
        self.cloud.connectivity_changed = True
        self._radio_range = value
        
    def move(self, vector):
        self.cloud.connectivity_changed = True
        self._pos += vector
    
    @property
    def x(self):
        return self._pos[0]
    
    @x.setter
    def x(self, value):
        self.cloud.connectivity_changed = True
        self._pos[0] = value

    @property
    def y(self):
        return self._pos[1]
    
    @y.setter
    def y(self, value):
        self.cloud.connectivity_changed = True
        self._pos[1] = value
        
    @property
    def z(self):
        return self._pos[2]
    
    @z.setter
    def z(self, value):
        self.cloud.connectivity_changed = True
        self._pos[2] = value  
    
    @property
    def pos(self):
        return self._pos
    
    @pos.setter
    def pos(self, new_pos):
        self.cloud.connectivity_changed = True
        self._pos = new_pos
    
    def nbr(self, val, extra_key=None):
        if SAFE:
            key = repr(["%s:%d" % (f[1], f[2]) for f in inspect.stack(context=0)])
        else:
            frame = None
            frames = []
            i = 1
            while (not frame or frame.f_code.co_filename != self.root_frame.f_code.co_filename 
                and frame.f_lineno != self.root_frame.f_lineno):
                frame = sys._getframe(i)
                i += 1
                frames += [frame]
            key = repr(["%s:%d" % (f.f_code.co_filename, f.f_lineno) for f in frames])
        if extra_key:
            return self._nbr("%s%s" % (key, extra_key), val)
        else:
            return self._nbr(key, val)
    
    def _nbr(self, key, val):
        if key in self._dict.keys():
            raise NbrKeyError("key %s found twice" % key)
        self._dict[key] = val
        ret = Field()
        for nbr in self._nbrs + [self]:
            try:
                ret[nbr] = nbr._old_dict[key]
            except KeyError:
                ret[nbr] = None
        return ret
    
    def nbr_range(self):
        ret = Field()
        for nbr in self._nbrs + [self]:
            delta = self.pos - nbr.pos
            ret[nbr] = numpy.dot(delta, delta)**0.5
        return ret
    
    def nbr_lag(self):
        ret = Field()
        for nbr in self._nbrs + [self]:
            if nbr == self:
                ret[nbr] = 0
            else:
                ret[nbr] = nbr.dt
        return ret
    
    def deself(self, field):
        f = Field(field.copy())
        del f[self]
        return f
    
    @property
    def dt(self):
        return self._dt
        
    def _step(self, dt):
        if not self.root_frame:
            self.root_frame = sys._getframe(1)
        self._dt = dt
        self.step()
        self._old_dict = self._dict
        self._dict = {}
        
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
    
class Cloud(object):      
    def __init__(self, klass=None, args=None, num_devices=1000, devices=None, 
                steps_per_frame=1, desired_fps=50, radio_range=0.1, width=1000, height=1000, 
                window_title=None, _3D=False, headless=False, display_leds=True):
        assert(steps_per_frame == int(steps_per_frame) and steps_per_frame > 0)
        
        if not devices:
            devices = []
            for i in range(num_devices):
                d = klass(pos = numpy.array([random.random(), random.random(), random.random() if _3D else 0]),
                          id = i,
                          radio_range = radio_range, 
                          cloud = self)
                devices += [d]
                if hasattr(d, "setup"):
                    if args:
                        d.setup(*args)
                    else:
                        d.setup()
        self.devices = devices
              
        self.connectivity_changed = True
        
        self.mss = []

        self.steps_per_frame = steps_per_frame
        self.desired_fps = desired_fps
        self.width = width
        self.height = height
        self.window_title = window_title if window_title else klass.__name__
        self.radio_range = radio_range
        self.headless = headless
        self.display_leds = display_leds

    def update(self, time_passed):
        epsilon = 0.01
        time_passed = time_passed if time_passed!=0 else epsilon
        for i in range(self.steps_per_frame):
            milliseconds = float(time_passed)/self.steps_per_frame
            if PRINT_MS:
                self.mss += [milliseconds]
                _mss = self.mss[10:]
                if(len(_mss) % 100):
                    print "milliseconds=%s" % _mss[len(_mss)-1]
            if self.connectivity_changed:
                point_matrix = numpy.array([d.pos for d in self.devices])
                kdtree = KDTree(point_matrix)
                for d in self.devices:
                    d._nbrs = []
                for (i,j) in kdtree.query_pairs(self.radio_range):
                    self.devices[i]._nbrs += [self.devices[j]]
                    self.devices[j]._nbrs += [self.devices[i]]
            self.connectivity_changed = False
            for d in self.devices:
                d._step(milliseconds)

from pymorphous.lib import *
from pymorphous.draw import *

def spawn_cloud(*args, **kwargs):
    cloud = Cloud(*args, **kwargs)
    if cloud.headless:
        last_time = time.time()
        while True:
            now = time.time()
            delta = now - last_time
            cloud.update(delta)
            last_time = now
    else:
        display_cloud(cloud)
import random
import numpy
import inspect
import sys
from scipy.spatial import KDTree
import operator
import math

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
    def __init__(self, coord, id, cloud):
        # coord is a numpy.array
        self._coord = coord
        self._velocity = numpy.array([0,0,0])
        self.id = id
        self.cloud = cloud
        self.leds = [0, 0, 0]
        self.senses = [0, 0, 0]
        self._nbrs = []
        self._dict = {}
        self._old_dict = {}
        self._dt = 0
        self._nbr_range = Field()
        self.root_frame = None
    
    @property
    def radio_range(self):
        return self.cloud.radio_range
    
    def move(self, velocity):
        self._velocity = velocity
    
    @property
    def velocity(self):
        return self._velocity
    
    @property
    def x(self):
        return self._coord[0]
    
    @x.setter
    def x(self, value):
        self.cloud.coord_changed = True
        self._coord[0] = value

    @property
    def y(self):
        return self._coord[1]
    
    @y.setter
    def y(self, value):
        self.cloud.coord_changed = True
        self._coord[1] = value
        
    @property
    def z(self):
        return self._coord[2]
    
    @z.setter
    def z(self, value):
        self.cloud.coord_changed = True
        self._coord[2] = value  
    
    @property
    def coord(self):
        return self._coord
    
    @coord.setter
    def coord(self, new_coord):
        self.cloud.coord_changed = True
        self._coord = new_coord
    
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
    
    @property
    def nbr_range(self):
        return self._nbr_range
    
    @property
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
        if numpy.any(self.velocity):
            self.coord_changed = True
            self.coord += self.velocity
        
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
    
    @blue.setter
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



class _Constants(object):
    """ Constants """
    def __init__(self):
        self.LED_STACKING_MODE_DIRECT = 0
        self.LED_STACKING_MODE_OFFSET = 1
        self.LED_STACKING_MODE_INDEPENDENT = 2
        
CONSTANTS = _Constants()

from pymorphous.lib import *
from pymorphous.simulator import *

class _Defaults(object):
    """
    So that we can override these in a test suite
    """
    def __init__(self):
        self.NUM_DEVICES = 1000
        self.STEPS_PER_FRAME = 1
        self.DESIRED_FPS = 50
        self.DIM = [132,100,0]
        self.BODY_RAD = None
        self.RADIO_RANGE = 15
        self.WINDOW_WIDTH = 1000
        self.WINDOW_HEIGHT = 1000
        self.WINDOW_TITLE = None
        self._3D = False
        self.HEADLESS = False
        self.SHOW_LEDS = True
        self.LED_FLAT = False
        self.LED_STACKING_MODE = CONSTANTS.LED_STACKING_MODE_DIRECT
        self.SHOW_BODY = True
        self.SHOW_RADIO = False
        self.GRID = False
        self.USE_GRAPHICS = simulator

DEFAULTS = _Defaults()

class Cloud(object):      
    def __init__(self, 
                 klass=None, 
                 args=None, 
                 num_devices=DEFAULTS.NUM_DEVICES, 
                 devices=None, 
                 steps_per_frame=DEFAULTS.STEPS_PER_FRAME, 
                 desired_fps=DEFAULTS.DESIRED_FPS, 
                 dim=DEFAULTS.DIM, 
                 body_rad=DEFAULTS.BODY_RAD,
                 radio_range=DEFAULTS.RADIO_RANGE, 
                 window_width=DEFAULTS.WINDOW_WIDTH, 
                 window_height=DEFAULTS.WINDOW_HEIGHT, 
                 window_title=DEFAULTS.WINDOW_TITLE, 
                 _3D=DEFAULTS._3D, 
                 headless=DEFAULTS.HEADLESS, 
                 show_leds=DEFAULTS.SHOW_LEDS,
                 led_flat=DEFAULTS.LED_FLAT, 
                 led_stacking_mode=DEFAULTS.LED_STACKING_MODE, 
                 show_body=DEFAULTS.SHOW_BODY, 
                 show_radio=DEFAULTS.SHOW_RADIO, 
                 grid=DEFAULTS.GRID, 
                 use_graphics=DEFAULTS.USE_GRAPHICS):
        assert(klass or devices)
        assert(steps_per_frame == int(steps_per_frame) and steps_per_frame > 0)
        
        if _3D:
            dim[2] = 100
            
        if len(dim) == 1:
            self.dim = dim + DEFAULTS.DIM[1:]
        elif len(dim) == 2:
            self.dim = dim + DEFAULTS.DIM[2:]
        else:
            self.dim = dim
        
        self.grid = grid
        
        if not devices:
            devices = []
            if self.grid:
                d = 3 if self.dim[2] else 2
                side_len = math.floor(num_devices**(1.0/d))
            for i in range(num_devices):
                if self.grid:
                    if self.dim[2]!=0:
                        coord = numpy.array([self.width*math.floor(i/(side_len*side_len)),
                                           self.height*((i/side_len) % side_len),
                                           self.depth*(i % side_len)])/side_len
                        coord -= numpy.array([self.width/2, self.height/2, self.depth/2])
                    else:
                        coord = numpy.array([self.width*math.floor(i/side_len), 
                                           self.height*(i % side_len), 0])/side_len
                        coord -= numpy.array([self.width/2, self.height/2, 0])
                else:
                    coord = numpy.array([(random.random()-0.5)*self.width, 
                                       (random.random()-0.5)*self.height, 
                                       (random.random()-0.5)*self.depth])
                d = klass(coord = coord,
                          id = i,
                          cloud = self)
                devices += [d]
                if hasattr(d, "setup"):
                    if args:
                        d.setup(*args)
                    else:
                        d.setup()
        self.devices = devices
        
        self.steps_per_frame = steps_per_frame
        self.desired_fps = desired_fps

            
        self.body_rad = body_rad if body_rad else (0.087*(self.width*self.height/len(devices)))**0.5
        
        self.radio_range = radio_range
        self.window_width = window_width
        self.window_height = window_height
        self.window_title = window_title if window_title else klass.__name__

        self.headless = headless
        self.show_leds = show_leds
        self.led_flat = led_flat
        self.led_stacking_mode = led_stacking_mode
        self.show_body = show_body
        self.show_radio= show_radio
        self.use_graphics = use_graphics
              
        self.coord_changed = True
        
        self.mss = []

    @property
    def width(self):
        return self.dim[0]
    
    @property
    def height(self):
        return self.dim[1]
    
    @property
    def depth(self):
        return self.dim[2]
    
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
            if self.coord_changed:
                point_matrix = numpy.array([d.coord for d in self.devices])
                kdtree = KDTree(point_matrix)
                for d in self.devices:
                    d._nbrs = []
                for (i,j) in kdtree.query_pairs(self.radio_range):
                    self.devices[i]._nbrs += [self.devices[j]]
                    self.devices[j]._nbrs += [self.devices[i]]
                for d in self.devices:
                    d._nbr_range = Field()
                    for n in d._nbrs + [d]:
                        delta = d.coord - n.coord
                        d._nbr_range[n] = numpy.dot(delta, delta)**0.5
            self.coord_changed = False
            for d in self.devices:
                d._step(milliseconds)

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
        cloud.use_graphics(cloud)
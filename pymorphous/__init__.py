import random
import numpy
#import inspect
import sys
from Bio.KDTree import KDTree

PRINT_MS = False

class NbrKeyError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
class BaseDevice(object):
    def __init__(self, pos, id, radio_range, cloud):
        self._pos = pos
        self.id = id
        self._radio_range = radio_range
        self.cloud = cloud
        self.leds = [0, 0, 0]
        self.senses = [0, 0, 0]
        self._nbrs = []
        self._vals = {}
        self._keys = set()
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
        #key = repr(["%s:%d" % (f[1], f[2]) for f in inspect.stack(context=0)])
        frame = None
        frames = []
        i = 1
        while (not frame or frame.f_code.co_filename != self.root_frame.f_code.co_filename 
            and frame.f_lineno != self.root_frame.f_lineno):
            frame = sys._getframe(i)
            i += 1
            frames += [frame]
        key = repr(["%s:%d" % (f.f_code.co_filename, f.f_lineno) for f in frames])
        return self._nbr("%s%s" % (key, extra_key), val)
    
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
            ret[nbr] = numpy.dot(delta, delta)**0.5
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
        return self._dt
        
    def _step(self, dt):
        if not self.root_frame:
            self.root_frame = sys._getframe(1)
        self._dt = dt
        self.step()
        
    def _advance(self):
        self._keys = set()
        
    def __repr__(self):
        return "id: %s, leds: %s, senses: %s, pos: %s" % (
                        self.id, repr(self.leds), repr(self.senses), 
                        repr(self.pos))
        
class Cloud(object):      
    def __init__(self, klass=None, args=None, num_devices=500, devices=None, 
                steps_per_frame=1, desired_fps=50, radio_range=0.05, width=1000, height=1000, 
                window_title=None, _3D=False):
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
        

    def update(self, time_passed):
        for i in range(self.steps_per_frame):
            milliseconds = float(time_passed)/self.steps_per_frame
            if PRINT_MS:
                self.mss += [milliseconds]
                _mss = self.mss[10:]
                if(len(_mss) % 100):
                    print "milliseconds=%s" % _mss[len(_mss)-1]
            if self.connectivity_changed:
                point_matrix = numpy.array([d._pos for d in self.devices]) # ??
                kdtree = KDTree(3, 10)
                kdtree.set_coords(point_matrix)
                kdtree.all_search(d.radio_range)
                for d in self.devices:
                    d._nbrs = []
                for (i,j) in kdtree.all_get_indices():
                    self.devices[i]._nbrs += [self.devices[j]]
                    self.devices[j]._nbrs += [self.devices[i]]
            self.connectivity_changed = False
            for d in self.devices:
                d._step(milliseconds)
            for d in self.devices:
                d._advance()

from pymorphous.lib import *
from pymorphous.draw import *
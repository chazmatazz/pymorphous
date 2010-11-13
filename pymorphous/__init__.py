import random
import numpy
import math
import pyglet
from pyglet.gl import *
import inspect

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
        key = self._stack_location()
        return self._nbr("%s%s" % (key, extra_key), val)
    
    def _stack_location(self):
        # file:line_number
        return repr(["%s:%d" % (f[1], f[2]) for f in inspect.stack(context=0)])

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
        return self._dt
        
    def _step(self, dt):
        self._dt = dt
        self.step()
        
    def _advance(self):
        self._keys = set()
        
    def __repr__(self):
        return "id: %s, leds: %s, senses: %s, pos: %s" % (
                        self.id, repr(self.leds), repr(self.senses), 
                        repr(self.pos))
      
class DefaultSkin(object):
    def setup(self):
        # One-time GL setup
        glClearColor(1, 1, 1, 1)
        glColor3f(1, 0, 0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
    
        # Uncomment this line for a wireframe view
        #glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    
        # Simple light setup.  On Windows GL_LIGHT0 is enabled by default,
        # but this is not the case on Linux or Mac, so remember to always 
        # include it.
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHT1)
    
        # Define a simple function to create ctypes arrays of floats:
        def vec(*args):
            return (GLfloat * len(args))(*args)
    
        glLightfv(GL_LIGHT0, GL_POSITION, vec(.5, .5, 1, 0))
        glLightfv(GL_LIGHT0, GL_SPECULAR, vec(.5, .5, 1, 1))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, vec(1, 1, 1, 1))
        glLightfv(GL_LIGHT1, GL_POSITION, vec(1, 0, .5, 0))
        glLightfv(GL_LIGHT1, GL_DIFFUSE, vec(.5, .5, .5, 1))
        glLightfv(GL_LIGHT1, GL_SPECULAR, vec(1, 1, 1, 1))
    
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, vec(0.5, 0, 0.3, 1))
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, vec(1, 1, 1, 1))
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 50)


    
    def body(self, device, batch, group):
        pass
    
    def state(self, device, batch, group):
        pass
    
    def metrics(self, dt, batch, group):
        pass

class spawn_cloud(object):      
    def __init__(self, klass=None, args=None, num_devices=None, devices=None, 
                step_size = 0, radio_range=0.05, width=1000, height=1000, 
                window_title=None, _3D=False, skin=DefaultSkin()):
        
        if not devices:
            devices = []
            for i in range(0, num_devices):
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
                
        
        self.connectivity_changed = True
        
        window = pyglet.window.Window()
        batch = pyglet.graphics.Batch()
        body_group = pyglet.graphics.OrderedGroup(0)
        state_group = pyglet.graphics.OrderedGroup(1)
        metrics_group = pyglet.graphics.OrderedGroup(2)
        skin.setup()
        
        dts = [[]]
        def update(dt):
            dts[0] += [dt]
            _dts = dts[0][2:]
            if(len(_dts) == 10):
                print "dts=%s, average=%f" % (_dts, sum(_dts)/len(_dts))
                exit()
            if self.connectivity_changed:
                for d in devices:
                    d._nbrs = []
                    for e in devices:
                        if d != e:
                            delta = e.pos - d.pos
                            if numpy.dot(delta, delta) < d.radio_range * d.radio_range:
                                d._nbrs += [e]
                for d in devices:
                    skin.body(device=d, batch=batch, group=body_group)
            self.connectivity_changed = False
            
            skin.metrics(dt=dt, batch=batch, group=metrics_group)
            for d in devices:
                skin.state(device=d, batch=batch, group=state_group)
            for d in devices:
                d._step(dt)
            for d in devices:
                d._advance()
                
        pyglet.clock.schedule_interval(update, 1/100. if step_size==0 else step_size)
                
        @window.event
        def on_draw():
            batch.draw()
            
        pyglet.app.run()
            
from pymorphous.lib import *
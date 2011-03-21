# Copyright (C) 2011 by Charles Dietrich, KJ Khalsa
# Licensed under the Lesser GNU Public License
# http://www.gnu.org/licenses/lgpl.html
""" 
Defines the wall device
exposes an implementation
"""

import time
import sys
import inspect
import controller
import uuid
import pickle
import numpy

from pymorphous.implementation.simulator.runtime import _Field, _NbrKeyError

_USE_SAFE_NBR = False
TIMEOUT = 32000000000
class _Message(object):
    def __init__(self, id, time, data):
        self.id = id
        self.time = time
        self.data = data
        
class GenericRobot(controller.Robot):
  timeStep = 320 #originally 32

  def initialize(self, klass, settings, *args):
    
    self.o = klass(settings, str(uuid.uuid4()), self)
    if hasattr(self.o, 'setup'):
        if args:
            self.o.setup(*args)
        else:
            self.o.setup()
  def run(self):  
    while True:
        #a=self.getLED('led0')
        #a.set(2)
        self.o.dostep()
        if self.step(self.timeStep) == -1: break
        

class _BaseDevice(object):
    def __init__(self, settings, id, webot_robot, *args, **kwargs):
	
	self._webot_robot = webot_robot
        self.settings = settings
        self._id = id
        self._fields = {} # dict of fields
        self._new_fields = {} # dict of fields
        self._data = {} # dict of values
        self._time = time.time()
        self._nbrs = {} # map neighbor to time
        self._root_frame = None
        self._leds = self._Leds(self)
        self._senses = self._Senses(self)
	self._num_transmitters = 6
	self.time = time.time()
	self.gps = self._webot_robot.getGPS('gps')
	self.gps.enable(self._webot_robot.timeStep)
	for i in range(self._num_transmitters):
		self._webot_robot.getReceiver("receiver" + str(i + 1)).enable(self._webot_robot.timeStep)  
    
    @property
    def id(self):
        return self._id
    
    class _Leds(object):
        def __init__(self, parent):
            self.parent = parent
	
	def convertRGB(self, rgb):
	    return rgb[2] + rgb[1] * 256 + rgb[0] * 256 * 256  

        def __setitem__(self, key, value):
	    if value :
		if value < 0: value = 0
		elif value > 255: value = 255
		temp = [0, 0, 0]
	    	temp[key] = int(value)
		tempColor = self.convertRGB(temp)
		self.parent._webot_robot.getLED("led" + str(key)).set(tempColor)
		#self.parent._webot_robot.getLED("led" + str(key)).set(key+1)
	    else: self.parent._webot_robot.getLED("led" + str(key)).set(0)
        def __getitem__(self, key):
            return self.parent._webot_robot.getLED("led" + str(key))

    @property
    def leds(self):
        return self._leds
    
    @leds.setter
    def leds(self, value):
        for i in range(3):
            self._leds[i] = value[i]
    
    class _Senses(object):
        def __init__(self, parent):
            self.parent = parent
	    self._num_sensors = 1
	    for i in range(self._num_sensors):
	    	self.parent._webot_robot.getDistanceSensor('sensor' + str(i + 1)).enable(self.parent._webot_robot.timeStep)

        def __getitem__(self, key):
            return self.parent._webot_robot.getDistanceSensor('sensor' + str(key + 1)).getValue()

    @property
    def senses(self):
        return self._senses
    
    @senses.setter
    def senses(self, value):
        for i in range(3):
            self._senses[i] = value[i]
   

    @property
    def radio_range(self):
        return 0
    
    def move(self, velocity):
        self._velocity = velocity
    
    @property
    def velocity(self):
        return self._velocity
    
    @property
    def x(self):
        return self.coord[0]
    
    @x.setter
    def x(self, value):
        self.coord[0] = value

    @property
    def y(self):
        return self.coord[1]
    
    @y.setter
    def y(self, value):
        self.coord[1] = value
        
    @property
    def z(self):
        return self.coord[2]
    
    @z.setter
    def z(self, value):
        self.coord[2] = value
    
    @property
    def coord(self):
        return numpy.array(self.gps.getValues())
    
    @coord.setter
    def coord(self, new_coord):
        self._coord = new_coord
    
    def nbr(self, value, extra_key=None):
        if _USE_SAFE_NBR:
            key = repr(["%s:%d" % (f[1], f[2]) for f in inspect.stack(context=0)])
        else:
            frame = None
            frames = []
            i = 1
            while (not frame or frame.f_code.co_filename != self._root_frame.f_code.co_filename 
                and frame.f_lineno != self._root_frame.f_lineno):
                frame = sys._getframe(i)
                i += 1
                frames += [frame]
            key = repr(["%s:%d" % (f.f_code.co_filename, f.f_lineno) for f in frames])
        if extra_key:
            return self._nbr("%s%s" % (key, extra_key), value)
        else:
            return self._nbr(key, value)
            
    def _nbr(self, b, value):        
        if hasattr(self._data, b):
            raise _NbrKeyError("Runtime exception in nbr")
        self._data[b] = value
	try:        
		return self._fields[b]
	except:
		return _Field()
    
    @property
    def nbr_range(self):
        return _Field()
    
    @property
    def nbr_lag(self):
        return _Field()
    
    def deself(self, field):
        return field
    
    @property
    def dt(self):
        return 0.01
        
    def dostep(self, dt):
        if not self._root_frame:
            self._root_frame = sys._getframe(1)
        self._dt = dt
        self.step()
        self._old_dict = self._dict
        self._dict = {}


    
    
    def dostep(self):
 	if not self._root_frame:
            self._root_frame = sys._getframe(1)	
	for i in range(self._num_transmitters):
		r = self._webot_robot.getReceiver("receiver" + str(i + 1))
		while r.getQueueLength() > 0:
			buffer = r.getData()
			message = pickle.loads(buffer)
			self._nbrs[message.id] = message.time
			for (b, v) in message.data.items():
			    try:
			    	self._new_fields[b][message.id] = v
			    except:
				self._new_fields[b] = _Field()
				self._new_fields[b][message.id] = v
			r.nextPacket()
     
        self.step()
        self._time = time.time()
	self.time = self._time
        
	for i in range(self._num_transmitters):
	    msg = pickle.dumps(_Message(self.id, self._time, self._data))
	    self._webot_robot.getEmitter("emitter" + str(i + 1)).send(msg)
        
	self._data = {}       
	# time out old nbrs and field values
	for (n, t) in self._nbrs.items():
	    if t + TIMEOUT < self._time:
		del self._nbrs[n]
	for (b, f) in self._fields.items():
	    for (id, v) in f.items():
		try:
		   self._nbrs[id]
		except:		
		   del f[id]
	for (b, f) in self._fields.items():
	    if len(f) == 0:
		del self._fields[b]

	# bring in the new field values
	for (b, f) in self._new_fields.items():
	    try:
		for (id, v) in f.items():
	            self._fields[b][id] = v
	    except:
		 self._fields[b] = f
	        

def _spawn_cloud(settings, klass=None, args=None, **kwargs):
    m = GenericRobot()
    m.initialize(klass, settings)
    m.run()


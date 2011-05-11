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
import math

from pymorphous.implementation.simulator.runtime import _Field, _NbrKeyError
from pymorphous.implementation.webots_wall.robots import GenericRobot
_USE_SAFE_NBR = False
TIMEOUT = 8
class _Message(object):
    def __init__(self, id, time, data):
        self.id = id
        self.time = time
        self.data = data
                

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
	self._num_transmitters = 1
	self.time = time.time()
	self.gps = self._webot_robot.getGPS('gps')
	self.gps.enable(self._webot_robot.timeStep)
	self.compass = False
	if self.compass:
		self.compass = self._webot_robot.getCompass('compass')
		self.compass.enable(self._webot_robot.timeStep)
	self._velocity = numpy.array([0.0,0.0,0.0])
	self._actual_velocity = numpy.array([0.0,0.0,0.0])
	self._epsilon = 0.4
	self._speed_counter = 0 #var for keeping track of time steps; used for object avoidance
	self._backup_counter = 0 #used for object avoidance
	self._forward_counter = 0 #used to go forward a set amount of time after getting stuck
	self._previous_loc = None #used to detect robot getting stuck
	self._offset = 0 #used to temporarily move in a random direction when stuck
	self._offset_start_time = -1 #start time of offset, used to expire offset and reset it to 0 
	self._offset_timeout = 4
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

    @property # unused??
    def senses(self):
        return self._senses 
    
    @senses.setter #unused ?
    def senses(self, value):
        for i in range(3):
            self._senses[i] = value[i]
   

    @property
    def radio_range(self):
        return 0
    
    def move(self, velocity):
	if self._backup_counter >0:
		self._webot_robot.setSpeed(-10-self._offset,-10+self._offset)
		self._backup_counter -= 1
		if self._backup_counter ==1: 
			self._offset_start_time = -1 #about to end backing up,resetting offset
			self._offset =0
			self._forward_counter = numpy.random.randint(7,14)
	elif self._forward_counter>0: 
		self._webot_robot.setSpeed(50,50)
		self._forward_counter-=1
	else:#only go forward if we're not trying to get unstuck
		self._velocity = velocity
		north = self.compass.getValues()
		rad = math.atan2(north[0], north[2])
		if numpy.any(velocity):
			if abs(velocity[2])<.1: velocity[2] = abs(velocity[2]) #avoid very small negative values affecting atan2
			desired_rad = math.atan2(-velocity[2],-velocity[0]) #switched to make consistant with compass
			delta = desired_rad-rad	
			if abs(delta) > self._epsilon:
				self._webot_robot.setSpeed(10*delta,-10*delta)	
			else:
				speed = math.sqrt(numpy.dot(velocity,velocity))
				if numpy.equal(self._previous_loc, self.coord)[0]: #could be stuck
					self._speed_counter += 1				
					if self._speed_counter >3:
						self._backup_counter = numpy.random.randint(11,15); #backup for a random number of timesteps
						self._speed_counter = 0;
						if self.sense1>self.sense2: self._offset = numpy.random.uniform(.30,.40)*25
						else: self._offset = numpy.random.uniform(-.40,-.30)*25
				
				else: self._speed_counter =0				
				if self._offset_start_time !=-1:
					if (self._time - self._offset_start_time) > self._offset_timeout: #check and reset offset since it is outdated
						self._offset = 0
						self._offset_start_time = -1
				self._previous_loc = self.coord
				self._webot_robot.setSpeed(speed, speed) #move and avoid objects
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
	        

def _spawn_cloud(settings, klass=None, args=None, robot = GenericRobot, **kwargs):
    m = robot()
    m.initialize(klass, settings)
    m.run()


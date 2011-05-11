# z: -5, 5 x: 0.15, 5.15
#import sys
#import random
#sys.path.append('/home/kizzle/Dropbox/pymorphous')
#from pymorphous.core import *


        #print self.sense0
        
#spawn_cloud(klass=MoveTest, robot = DifferentialWheelsRobot)

import sys
sys.path.append('/home/kizzle/Dropbox/pymorphous')
from pymorphous.core import *
from pymorphous.implementation.webots_wall.robots import DifferentialWheelsRobot

class MoveTest(Device): 

    def step(self):
        self.move([75,0, .1])
        self.red = 255
        self.green = self.sense2
        #print self.sense1-self.sense2
        
class CommunicationTest(Device): 

        
    def step(self):
        a = self.sum_hood_plus(self.nbr(1))
        if a>=0: self.red = 255
        if a>=1: self.green = 255
        if a>=2: self.blue = 255

class BlimpTracking(Device):
  def setup(self):
    
    self.timeout = 3
    self.loc_timeout = 12
    self.threshold = .3
    self.offset_timeout = 12
    
    self.prev_sense = 0
    self.prev_next = False
    self.tracking_start_time = -1
    
    self.field = Field()
    
    self.delta = None
    
    self.is_next = False
    
    self.start_time = self.time
    self.ready = False
    
    self.velocity_vector = None
    
    self.remember_velocity = None # var to keep track of current. Used to head in direction of last known direction of blimp heading
    
    self.move_vector = None
    
    
    self.offset = None
    self.known_loc = None
    self.loc_time = -1
    self.offset_start_time = -1
    
    self.random_counter =5 #var to slightly change velocity vector every 3 timesteps

  @property
  def tracking(self):
      return self.tracking_start_time > -1
  
  @property
  def elapsed_time(self):
      return self.time - self.tracking_start_time
  
  def is_close(self, coord):
      v = self.coord - coord
      return numpy.dot(v, v) <= self.threshold
  
  def is_my_coord(self, coord):
      v = self.coord - coord
      return numpy.dot(v, v) == 0
  
  def weight(self, a, dont_increase = False): #don't increase if we want the robot to slow down when approaching the blimp
    tempX = abs(a[0])
    tempY = abs(a[1])
    tempZ = abs(a[2])
    sum = tempX + tempY + tempZ
    if sum == 0: return a

    w = float(sum)/80.0 #scale factor of array
    if w<1.0 and dont_increase and sum<0.5: w = 1.0 #don't increase when sum is small
    return a/w
  def step(self):
    
    #if a>=0: self.red = 255
    #if a>=1: self.green = 255
    #if a>=2: self.blue = 255
    #if self.offset != None: print self.offset
    if self.time>self.start_time+2: self.ready = True
    if not self.ready: return #delay for sensors to get set up
    
    if self.sense0:
        self.known_loc = self.coord
        self.loc_time = self.time
        if not self.prev_sense: #rising edge
            self.tracking_start_time = self.time
    else:
        if self.elapsed_time > self.timeout:
            self.tracking_start_time = -1
        
    self.red = 255*self.tracking#sense0
    self.green = 255 #* self.tracking
    self.blue = 255 * self.is_next
    
    self.delta = None
    self.is_next = False
    loc = None
    loc_vector = None
    
    max_tracking_start_time = -1
    most_recent_coord = None
    
    if self.move_vector != None: self.move(self.move_vector)
    
    for (k, v) in self.field.items():
      if v:
        (coord, tracking_start_time, delta, offset, offset_start_time, known_loc, loc_time) = v
        if not self.is_my_coord(coord): # loop over neighbors only (redundant?)
                
          if offset!= None:
            
            if self.offset == None: #use nbr's offset since we don't have one
              self.offset = offset
              self.offset_start_time = offset_start_time
              
            elif self.offset_start_time < offset_start_time: #nbr vector is more recent than current vector
              deltaT = offset_start_time - self.offset_start_time + 1.0
              
              self.offset = (self.offset*deltaT + offset)/ (deltaT + 1.0) #weighted update
              self.offset_start_time = (self.offset_start_time*deltaT + offset_start_time)/ (deltaT + 1.0)
          
          if known_loc != None:
            if self.known_loc == None: #use nbr's known loc since we don't have one
              self.known_loc = known_loc
              self.loc_time = loc_time
            
            elif self.loc_time < loc_time: #nbr loc is more recent than current known loc
              deltaT = loc_time - self.loc_time +1.0
              
              self.known_loc = (self.known_loc + known_loc*deltaT)/ (deltaT + 1.0) #weighted update
              self.loc_time = (self.loc_time + loc_time*deltaT)/ (deltaT + 1.0)
            
        #if self.tracking: print self.move_vector
        if self.tracking and tracking_start_time > -1 and tracking_start_time < self.tracking_start_time:
            if max_tracking_start_time == -1 or tracking_start_time < max_tracking_start_time:
              max_tracking_start_time = tracking_start_time #get oldest nbr's coords
              most_recent_coord = coord
        if tracking_start_time > -1 and delta != None and self.is_close(coord + delta):
            self.is_next = True #nbr's coord+ delta is close to me, I marking myself as next 
            if not self.prev_next:
              self.prev_next = True
              self.offset = 4*delta
              self.offset_start_time = self.time
              #self.offset = self.weight(10*delta, True)
            else: self.prev_next = False
            #print delta, 10*delta
            #print coord, self.coord, delta
    #id: (loc, time)
    
    
    if self.known_loc == None and self.remember_velocity != None: #head in direction of offset, since known locs are out of date
      a = self.sum_hood_plus(self.nbr(1))
      print "a= ", a
      if self.random_counter ==15:
        #print "random"
        r = 0#.5 #amount of randomness
        rx = numpy.random.uniform(-r,r) #random amount to add to the x axis
        rz = numpy.random.uniform(-r,r) #random amount to add to the z axis
        randomness = numpy.array([rx, 0, rz])
        #self.remember_velocity = self.remember_velocity + randomness
      loc_vector = self.remember_velocity
      loc_vector = self.weight(loc_vector)
      self.random_counter -= 1
      if self.random_counter <0: self.random_counter = 15
    #update known loc using offset
    if (self.known_loc != None and self.offset!=None):
      offset_age = self.time - self.offset_start_time #weight the offset based on how old it is
      
      loc = self.known_loc + self.offset*((self.offset_timeout-offset_age)/self.offset_timeout) #decrease offset to 0 over offset_timeout 
      loc_vector = loc - self.coord
    
    if self.known_loc != None and loc_vector == None: #create move vector without an offset, since we don't have an offset
      loc_vector = self.known_loc - self.coord
    
    #loc_vector = 50*loc_vector
    if loc_vector!=None:
      loc_vector = self.weight(loc_vector, True)
      #print "coord = ", self.coord, "loc_v = ", loc_vector
    self.move_vector = loc_vector
    
    if self.move_vector != None:
      tempX = self.move_vector[0]
      tempY = self.move_vector[1]
      tempZ = self.move_vector[2]
    
      if (abs(tempX) + abs(tempY) + abs(tempZ)) > 1.0:
        self.remember_velocity = self.move_vector

    
    if most_recent_coord != None:
      self.delta = self.coord - most_recent_coord
      #print self.coord,self.tracking_start_time, self.delta
    
    #self.is_next = self.is_next and not self.tracking
    
    self.field = self.nbr((self.coord, self.tracking_start_time, self.delta, self.offset, self.offset_start_time, self.known_loc, self.loc_time))
        
    self.prev_sense = self.sense0
        
#spawn_cloud(klass=CommunicationTest, robot = DifferentialWheelsRobot)
#spawn_cloud(klass=MoveTest, robot = DifferentialWheelsRobot)
spawn_cloud(klass=BlimpTracking, robot = DifferentialWheelsRobot)

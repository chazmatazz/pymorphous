import controller
import uuid

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
        
class DifferentialWheelsRobot(controller.DifferentialWheels):
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


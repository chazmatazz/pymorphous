from pymorphous import *

class Move(Device):
    def initialize(self, x, y):
        self.x = x
        self.y = y
        
    def run(self):
        self.move(self.x, self.y)
        
spawn_cloud(num_devices=1000, grid=True, klass=Move, args=[1,1])

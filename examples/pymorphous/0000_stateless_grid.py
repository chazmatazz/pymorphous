from pymorphous import *

class Move(Device):
    def run(self, x, y):
        self.move(x, y)
        
spawn_cloud(num_devices=1000, grid=True, klass=Move, args=[1,1])

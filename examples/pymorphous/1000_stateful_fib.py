from pymorphous import *

def fib(n):
    if(n <= 1):
        return 1
    else: 
        return fib(n-1)+fib(n-2)
        
class BlueStateFib(Device):
    def initialize(self):
        self.n = 0
        
    def run(self):
        self.blue(fib(n))
        n += 1
        
spawn_cloud(num_devices=10, step=0.01, klass=BlueStateFib)
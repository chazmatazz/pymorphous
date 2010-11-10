from pymorphous import *

def fib(n):
    if(n <= 1):
        return 1
    else: 
        return fib(n-1)+fib(n-2)
        
class BlueStateFib(Device):
    def run(self, n):
        letfed([(n, 0, lambda n: n+1)], self.blue(fib(n)))
        
spawn_cloud(num_devices=10, step=0.01, klass=BlueStateFib)
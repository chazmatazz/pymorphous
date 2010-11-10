from pymorphous import *

def fib(n):
    if(n <= 1):
        return 1
    else: 
        return fib(n-1)+fib(n-2)
        
class BlueFib(Device):
    def run(self, n):
        self.blue(self.fib(n))
        
str = raw_input("Enter n:")
d = int(str)

spawn_cloud(num_devices = 10, klass=BlueFib, args=[d])
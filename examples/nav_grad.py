from pymorphous.core import *
import random

class NavGrad(Device):
    """ 
    Display the distance from a few randomly selected devices
    """
    def setup(self):
        self.blue_device = random.random() < 0.1
        
    def step(self):
        """
        ;; For an example of using nav-grad, run:
        ;;   proto -n 500 -r 15 -m -l -s 0.02 -sv "(let ((g (gradient (sense 1))) (which (once (< (rnd 0 1) 0.1)))) (if which (blue 1) 0) (green (< g (inf))) (mov (mux which (nav-grad g) (tup 0 0)))"
        ;; About 1/10 of the devices will turn blue.  Click on a device and
        ;; hit 't'.  As the gradient (green) spreads through the network, the
        ;; blue devices will begin moving to that spot.        
        """
        self.blue = self.blue_device
        g = self.gradient(self.sense0)
        if g < float("inf"):
            self.green = g
        self.move(mux(self.blue_device, self.nav_grad(g), zero_vec))

spawn_cloud(klass=NavGrad)

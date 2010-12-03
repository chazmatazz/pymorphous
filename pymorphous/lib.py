from pymorphous.core import *

def mux(test, then, else_):
    if test:
        return then
    else:
        return else_

class Device(BaseDevice):
    def consensus(self, epsilon, val, extra_key=None):
        """ Laplacian 
         (def consensus (epsilon init)
          (rep val init
           (+ val
            (* epsilon
             (sum-hood (- (nbr val) val))))))
        """
        return val + epsilon * self.sum_hood(self.nbr(val, extra_key) - val)
    
    class Gradient:
        """
        (def gradient (src)
          (1st (rep (tup d v) (tup (inf) 0)
            (mux src (tup 0 0)        ; source
              (mux (max-hood+
                (<= (+ (nbr d) (nbr-range) (* v (+ (nbr-lag) (dt)))) d))
                (tup (min-hood+ (+ (nbr d) (nbr-range))) 0)
                (let ((v0 (/ (radio-range) (* (dt) 12)))) (tup (+ d (* v0 (dt))) v0)))))))
        """
        def __init__(self, device):
            self.device = device
            self.d = float('inf')
            self.v = 0
            
        def value(self, src):
            new_d = self.device.nbr(self.d) + self.device.nbr_range + self.v * (self.device.nbr_lag + self.device.dt)
            then_tup = (self.device.min_hood_plus(self.device.nbr(self.d) + self.device.nbr_range), 0)
            v0 = self.device.radio_range / (self.device.dt * 12)
            else_tup = (self.d + v0 * self.device.dt, v0)
            else_ = mux(self.device.max_hood_plus(new_d <= self.d), then_tup, else_tup)
            (self.d, self.v) = mux(src, (0,0), else_)
            return self.d
        

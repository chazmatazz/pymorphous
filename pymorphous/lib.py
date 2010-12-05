from pymorphous.core import *

def mux(test, then, else_):
    if test:
        return then
    else:
        return else_

class Device(BaseDevice):
    def __init__(self, *args, **kwargs):
        super(Device, self).__init__(*args, **kwargs)
        self._gradients = {}
    
    def consensus(self, epsilon, val, extra_key=None):
        """ Laplacian 
         (def consensus (epsilon init)
          (rep val init
           (+ val
            (* epsilon
             (sum-hood (- (nbr val) val))))))
        """
        return val + epsilon * self.sum_hood(self.nbr(val, extra_key) - val)
    
    def gradient(self, src, extra_key=None):
        """
        (def gradient (src)
          (1st (rep (tup d v) (tup (inf) 0)
            (mux src (tup 0 0)        ; source
              (mux (max-hood+
                (<= (+ (nbr d) (nbr-range) (* v (+ (nbr-lag) (dt)))) d))
                (tup (min-hood+ (+ (nbr d) (nbr-range))) 0)
                (let ((v0 (/ (radio-range) (* (dt) 12)))) (tup (+ d (* v0 (dt))) v0)))))))
        """
        key = self.getkey(extra_key)
        try:
            (d,v) = self._gradients[key]
        except KeyError:
            self._gradients[key] = (float('inf'), 0)
            (d,v) = self._gradients[key]
        new_d = self.nbr(d, extra_key) + self.nbr_range + v * (self.nbr_lag + self.dt)
        then_tup = (self.min_hood_plus(self.nbr(d, extra_key) + self.nbr_range), 0)
        v0 = self.radio_range / (self.dt * 12)
        else_tup = (d + v0 * self.dt, v0)
        else_ = mux(self.max_hood_plus(new_d <= d), then_tup, else_tup)
        self._gradients[key] = mux(src, (0,0), else_)
        (d,v) = self._gradients[key]
        return d
           
        

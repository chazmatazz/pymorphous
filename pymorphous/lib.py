from pymorphous import *

def mux(test, then, else_):
    if test:
        return then
    else:
        return else_

def inf():
    return float("inf")

class Device(BaseDevice):
    def sum_hood(self, neighbor_field):
        return sum(neighbor_field)

    def max_hood(self, neighbor_field):
        return max(neighbor_field)
    
    def max_hood_plus(self, neighbor_field):
        # FIXME
        return max(neighbor_field - set([self]))
        
    def min_hood(self, neighbor_field):
        return min(neighbor_field)
    
    def min_hood_plus(self, neighbor_field):
        # FIXME
        return min(neighbor_field - set([self]))
    
    def consensus(self, epsilon, val, hash=None):
        """
         (def consensus (epsilon init)
          (rep val init
           (+ val
            (* epsilon
             (sum-hood (- (nbr val) val))))))
        """
        return val + epsilon * self.sum_hood(self.nbr(val, hash) - val)
    
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
        def __init__(self):
            self.d = inf()
            self.v = 0
            
        def value(self, src, hash=None):
            new_d = self.nbr(d, hash) + self.nbr_range() + self.v * (self.nbr_lag() + self.dt())
            then_tup = (self.min_hood_plus(self.nbr(d) + self.nbr_range()), 0)
            v0 = self.radio_range / (self.dt() * 12)
            else_tup = (d + v0 * self.dt(), v0)
            else_ = mux(self.max_hood_plus(new_d <= self.d), then_tup, else_tup)
            (self.d, self.v) = mux(src, (0,0), else_)
            return self.d

from pymorphous import *

def field_sum(lst):
    ret = {}
    for e in lst:
        if isinstance(e, dict):
            for k in e:
                if not hasattr(ret, str(k)):
                    ret[k] = e[k]
                else:
                    ret[k] += e[k]
    for e in lst:
        if not isinstance(e, dict):
            ret[k] += e      
    return ret

def field_product(lst):
    ret = {}
    for e in lst:
        if isinstance(e, dict):
            for k in e:
                if not hasattr(ret, str(k)):
                    ret[k] = e[k]
                else:
                    ret[k] *= e[k]
    for e in lst:
        if not isinstance(e, dict):
            ret[k] *= e
    return ret

def field_sub(c1, c2):
    ret = {}
    if isinstance(c1, dict) and not isinstance(c2, dict):
        _c1 = c1
        _c2 = {}
        for k in _c1:
            _c2[k] = c2
    elif not isinstance(c1, dict) and isinstance(c2, dict):
        _c1 = {}
        _c2 = c2
        for k in _c2:
            _c1[k] = c1
    else:
        _c1 = c1
        _c2 = c2
        
    for k in _c1:
        try:
            ret[k] = _c1[k] - _c2[k]
        except KeyError:
            pass

    return ret

def field_lteq(c1, c2):
    ret = {}
    if isinstance(c1, dict) and not isinstance(c2, dict):
        _c1 = c1
        _c2 = {}
        for k in _c1:
            _c2[k] = c2
    elif not isinstance(c1, dict) and isinstance(c2, dict):
        _c1 = {}
        _c2 = c2
        for k in _c2:
            _c1[k] = c1
    else:
        _c1 = c1
        _c2 = c2
        
    for k in _c1:
        try:
            ret[k] = _c1[k] <= _c2[k]
        except KeyError:
            pass

    return ret

def mux(test, then, else_):
    if test:
        return then
    else:
        return else_

class Device(BaseDevice):
    @property
    def red(self):
        return self.leds[0]
    
    @red.setter
    def red(self, val):
        self.leds[0] = val
        
    @property
    def green(self):
        return self.leds[1]
    
    @green.setter
    def green(self, val):
        self.leds[1] = val
        
    @property
    def blue(self):
        return self.leds[2]
    
    @blue.setter
    def blue(self, val):
        self.leds[2] = val
            
    def sum_hood(self, field):
        return sum([field[k] for k in field])
    
    def min_hood(self, field):
        return min([field[k] for k in field])
    
    def max_hood(self, field):
        return max([field[k] for k in field])
    
    def sum_hood_plus(self, field):
        """ return the sum over the field without self """
        f = field.copy()
        f[self] = 0
        return self.sum_hood(f)
    
    def min_hood_plus(self, field):
        """ return the min over the field without self """
        f = field.copy()
        f[self] = float('inf')
        return self.min_hood(f)
    
    def max_hood_plus(self, field):
        """ return the max over the field without self """
        f = field.copy()
        f[self] = float('-inf')
        return self.max_hood(f)
    
    def consensus(self, epsilon, val, extra_key=None):
        """ Laplacian 
         (def consensus (epsilon init)
          (rep val init
           (+ val
            (* epsilon
             (sum-hood (- (nbr val) val))))))
        """
        return val + epsilon * self.sum_hood(field_sub(self.nbr(val, extra_key), val))
    
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
            new_d = field_sum([self.device.nbr(self.d), self.device.nbr_range(), field_product([self.v, field_sum([self.device.nbr_lag(), self.device.dt])])])
            then_tup = (self.device.min_hood_plus(field_sum([self.device.nbr(self.d), self.device.nbr_range()])), 0)
            v0 = self.device.radio_range / (self.device.dt * 12)
            else_tup = (self.d + v0 * self.device.dt, v0)
            else_ = mux(self.device.max_hood_plus(field_lteq(new_d, self.d)), then_tup, else_tup)
            (self.d, self.v) = mux(src, (0,0), else_)
            return self.d
    

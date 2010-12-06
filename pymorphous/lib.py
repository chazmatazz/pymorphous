from pymorphous.core import *
import numpy

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
        
    @property
    def disperse(self):
        """
        ;; disperse does not scale properly with neighborhood size!
        
        (def newdisperse ()
          (int-hood 
           (let* ((vec (nbr-vec)) (dist-sqr (vdot vec vec)))
             (if (< dist-sqr 0.01)
               (tup 0 0 0)
               (* (neg (/ 0.05 dist-sqr)) vec)))))
        
        (def olddisperse ()
          (fold-hood (fun (t p)
                   (let* ((r (nbr-range)))
                   (let* (;; (r (radio-range))
                      (vec (nbr-vec))
                      (dist-sqr (vdot vec vec))
                      ;; 25000
                      (s (if (< dist-sqr 0.01) 0 (/ 5 dist-sqr)))) 
                     (+ t (* (neg s) vec)))))
                 (tup 0 0 0) 0))
        
        (def disperse () (newdisperse))
        """
        # using newdisperse
        vec = self.nbr_vec
        dist_sqr = self.nbr_range**2
        f = Field()
        for (k,v) in vec.items():
            if dist_sqr[k] == 0:
                f[k] = numpy.array([0,0,0])
            else:
                f[k] = -v * 0.05/dist_sqr[k]
        return self.int_hood(f)
        
    @property
    def color(self):
        """ convert id to rgb """
        f = 10
        r = self.id % f
        g = (self.id % (f**2)) - r
        b = (self.id % (f**3)) - (r + g)
        return [r*1.0/f, g*1.0/(f**2), b*1.0/(f**3)]

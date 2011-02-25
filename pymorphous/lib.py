from pymorphous.core import *
import numpy

zero_vec = numpy.array([0,0,0])
def listize(fieldlist):
    ret = Field()
    for (k,v) in fieldlist[0].items():
        ret[k] = [v]
    
    for f in fieldlist[1:]:
        for (k,v) in ret.items():
            try:
                ret[k] += [f[k]]
            except:
                del ret[k]
    return ret
    
def mux(test, then, else_):
    if test:
        return then
    else:
        return else_

def normalize(vec):
    m = numpy.max(numpy.abs(vec))
    if m == 0:
        return vec
    else:
        return vec/m
        
class Device(BaseDevice):
    def __init__(self, *args, **kwargs):
        super(Device, self).__init__(*args, **kwargs)
        self._gradients = {}
        self._flock = {}
    
    def consensus(self, epsilon, val, extra_tag=None):
        """ Laplacian 
        
         (def consensus (epsilon init)
          (rep val init
           (+ val
            (* epsilon
             (sum-hood (- (nbr val) val))))))
        """
        return val + epsilon * self.sum_hood(self.nbr(val, extra_tag) - val)
    
    def gradient(self, src, extra_tag=None):
        """
        (def gradient (src)
          (1st (rep (tup d v) (tup (inf) 0)
            (mux src (tup 0 0)        ; source
              (mux (max-hood+
                (<= (+ (nbr d) (nbr-range) (* v (+ (nbr-lag) (dt)))) d))
                (tup (min-hood+ (+ (nbr d) (nbr-range))) 0)
                (let ((v0 (/ (radio-range) (* (dt) 12)))) (tup (+ d (* v0 (dt))) v0)))))))
        """
        tag = self.get_tag(extra_tag)
        try:
            (d,v) = self._gradients[tag]
        except KeyError:
            self._gradients[tag] = (float('inf'), 0)
            (d,v) = self._gradients[tag]
        new_d = self.nbr(d, extra_tag) + self.nbr_range + v * (self.nbr_lag + self.dt)
        then_tup = (self.min_hood_plus(self.nbr(d, extra_tag) + self.nbr_range), 0)
        v0 = self.radio_range / (self.dt * 12)
        else_tup = (d + v0 * self.dt, v0)
        else_ = mux(self.max_hood_plus(new_d <= d), then_tup, else_tup)
        self._gradients[tag] = mux(src, (0,0), else_)
        (d,v) = self._gradients[tag]
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
    
    def nav_grad(self, grad_val):
        """
        (def nav-grad (grad-val)
          (let ((vec-sums
             (fold-hood 
              (fun (res grad-v)
                (if (< grad-v grad-val)
                (tup (vadd (1st res) (nbr-vec)) (+ (2nd res) 1))
                res))
              (tup (tup 0 0) 0)
              grad-val)))
            (if (> (elt vec-sums 1) 0)
            (vmul (/ 1 (2nd vec-sums)) (1st vec-sums)) 
            (tup 0 0))))
        """
        def f(res, t):
            (grad_v, oth_vec) = t
            if grad_v < grad_val:
                return (res[0] + oth_vec, res[1] + 1)
            else:
                return res
        (v, c) = self.fold_hood_star(f, (zero_vec, 0), listize([self.nbr(grad_val),self.nbr_vec]))
        if c != 0:
            return v*1.0/c
        else:
            return zero_vec
    
    def flock(self, dir, extra_tag=None):
        """
        (def flock (dir)
          (rep v 
           (tup 0 0 0)
           (let ((d
              (normalize
               (int-hood
                (if (< (nbr-range) 5)
                  (vmul -1 (normalize (nbr-vec)))
                  (if (> (nbr-range) 10)
                (vmul 0.2 (normalize (nbr-vec)))
                (normalize (nbr v))))))))
             (normalize 
              (+ dir (mux (> (vdot d d) 0) d v))))))
        """
        tag = self.get_tag(extra_tag)
        try:
            v = self._flock[tag]
        except KeyError:
            self._flock[tag] = zero_vec
            v = self._flock[tag]
        
        nbr_range = self.nbr_range
        nbr_vec = self.nbr_vec
        nbr_v = self.nbr(v)
        f = Field()
        for (k,e) in nbr_v.items():
            if nbr_range[k] < 5:
                #print "too close"
                f[k] = -1 * normalize(nbr_vec[k])
            elif nbr_range[k] > 10:
                #print "too far"
                f[k] = 0.2 * normalize(nbr_vec[k])
            else:
                #print "ok"
                if e != None:
                    f[k] = normalize(e)
            
        d = normalize(self.int_hood(f))
        self._flock[tag] = normalize(dir + mux(numpy.dot(d,d) > 0, d, v))
        return self._flock[tag]
    
    
    
    @property
    def color(self):
        """ convert id to rgb """
        f = 10
        r = self.id % f
        g = (self.id % (f**2)) - r
        b = (self.id % (f**3)) - (r + g)
        return [r*1.0/f, g*1.0/(f**2), b*1.0/(f**3)]

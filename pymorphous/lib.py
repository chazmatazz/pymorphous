from pymorphous import *

def sum_hood(neighbor_field):
    return fold_hood(lambda a, b: a+b, neighbor_field)

def max_hood_plus(self, neighbor_field):
    return fold_hood(lambda a, b: b if a is self else max(a,b), neighbor_field)
    
def min_hood_plus(neighbor_field):
    return fold_hood(lambda a, b: b if a is self else min(a,b), neighbor_field)
    
def rep(var, init, evolve):
    return letfed([(var, init, evolve)], None)

def let(decls, body):
    lst = []
    
    for (k,v) in decls:
        lst += [(k,v,lambda a: a)]
    return letfed(lst, body)
    
class LibDevice(Device):
    def gradient(self, src):
        """
        (def gradient (src)
          (1st (rep (tup d v) (tup (inf) 0)
            (mux src (tup 0 0)        ; source
              (mux (max-hood+
                (<= (+ (nbr d) (nbr-range) (* v (+ (nbr-lag) (dt)))) d))
                (tup (min-hood+ (+ (nbr d) (nbr-range))) 0)
                (let ((v0 (/ (radio-range) (* (dt) 12)))) (tup (+ d (* v0 (dt))) v0)))))))
        """
        return rep((d,v), (inf(), 0), 
               mux(src, (0,0), 
                   mux(max_hood_plus(
                      (min_hood_plus(nbr(d) + nbr_range()), 0)
                      if (nbr(d) + nbr_range() + v * nbr_lag() + dt())
                      else (let([(v0, radio_range()/(dt()*12))], (d + v0 * dt(), v0)))
                         )
                      )
                   )
               )[0]
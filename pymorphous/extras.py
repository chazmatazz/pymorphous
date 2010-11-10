from pymorphous import *
from pymorphous.lib import *

class ExtrasDevice(LibDevice):
    def consensus(self, epsilon, init):
        """
         (def consensus (epsilon init)
          (rep val init
           (+ val
            (* epsilon
             (sum-hood (- (nbr val) val))))))
        """

        return rep(val, init, 
                   val + epsilon * sum_hood(nbr(val) - val))

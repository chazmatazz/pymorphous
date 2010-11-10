from pymorphous import *

class InCircles(ExtrasDevice):
    """
    is the device in a circle?
    
    ;; To see circles drawn in low, medium, and high resolution, run:
    ;;   proto -n 200 -r 20 -l "(+ (blue (in-circle (tup -40 -20) 30)) (green (in-circle (tup 0 0) 20)))"
    ;;   proto -n 1000 -r 15 -l "(+ (blue (in-circle (tup -40 -20) 30)) (green (in-circle (tup 0 0) 20)))"
    ;;   proto -n 5000 -r 5 -l "(+ (blue (in-circle (tup -40 -20) 30)) (green (in-circle (tup 0 0) 20)))"
    """
    def run(self):
        self.blue(self.in_circle((-40, -20), 30))
        self.green(self.in_circle((0,0), 20))
        
    def in_circle(self, origin, radius):
        """
        (def in-circle (o r)
          (let ((dv (- (probe (coord) 1) o)))
            (< (probe (vdot dv dv) 0) (* r r))))
        """
        dv = self.coord() - origin # vector subtraction
        return vdot(dv, dv) < radius * radius
        
spawn_cloud(num_devices=1000, klass=InCircles)
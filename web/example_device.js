/**
 * Device example
 * input: coordinate
 */
function Device(co) {
    
    var mul = .1;
    var a1 = mul;
    var b1 = mul;
    var c1 = mul;
    
    var a2 = mul;
    var b2 = mul;
    var c2 = mul;
    
    var period = 20;
    var t1_period = period;
    var t2_period = period;
    var t3_period = period;
    
    var c = co;
    var col = [0,0,0];
    var t1;
    var t2;
    var t3;
    
    function coord() {
      return c;
    }
    function color() {
    	return col;
    }
    function setup() {
      t1 = 0;
      t2 = 0;
      t3 = 0;
    }
    function step() {
      col[0] = 50;
      col[1] = Math.sin(a1*t1) * Math.sin(Math.sin(b1*t2+c1)*t3 + c[0]/50);
      col[2] = Math.sin(a2*t1) * Math.sin(Math.sin(b2*t2+c2)*t3 + c[1]/50);
      t1 += 1.0/t1_period;
      t2 += 1.0/t2_period;
      t3 += 1.0/t3_period;
    }
    return {
      coord: coord,
      setup: setup,
      step: step,
      color: color
    };
  }
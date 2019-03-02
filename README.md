## About
PyMorphous is a spatial computing library and runtime for Python. See [Runtime Description](https://github.com/chazmatazz/pymorphous/wiki/Runtime-Description) for a high-level description of the spatial computing functionality available.

PyMorphous programs will run in a simulator (Windows, Mac OS X, Linux) as well as on the Atmel AVR XMEGA (and possibly other microcontrollers). The simulator works now; hardware support is progressing (see [Hardware Runtime](https://github.com/chazmatazz/pymorphous/wiki/Hardware-Runtime) for implementation details).

## License Information
In addition to being licensed under the LGPLv3, the PyMorphous graphics engines and some examples are additionally available under the MIT License. See LicenseInformation and individual files for more information.

## Simulator Video
[![](https://img.youtube.com/vi/UgCXVvSalzg/0.jpg)](https://www.youtube.com/watch?feature=player_embedded&v=UgCXVvSalzg)

## Relationship to prior work
The PyMorphous runtime adapts the concept of fields and the nbr function from MIT Proto, created by the Space Time Programming Group at MIT. The simulator adapts the behavior of the MIT Proto simulator, as specified in the MIT Proto documentation. Additional information is available in LicenseInformation.

The primary developers of MIT Proto are Jacob Beal and Jonathan Bachrach. Complete credits for MIT Proto can be found on the proto website.

## Examples
```
from pymorphous.core import *

class IntHood(Device): """ calculate the number of neighbors of the current device, and display it as a red LED """ def step(self): self.red = self.sum_hood(self.nbr(1))

spawn_cloud(klass=IntHood)
```

```
from pymorphous.core import * import random

class GradientDemo(Device): """ Display the distance from a few randomly selected devices """ def setup(self): self.senses[0] = random.random() < 0.01 self.gradient = self.Gradient(self)

def step(self):
    self.red = self.senses[0]
    self.green = self.gradient.value(self.senses[0])
spawn_cloud(klass=GradientDemo)
```

## Running the Simulator
See [Installation](https://github.com/chazmatazz/pymorphous/wiki/Installation) for installation instructions. Then try: `python run_pymorphous.py examples/consensus.py`

See also the QuickStart. When you are done with that, see [Thinking In Pymorphous](https://github.com/chazmatazz/pymorphous/wiki/Thinking-in-Pymorphous).

[Slideshow](https://docs.google.com/presentation/d/1Qj6OwTpf1jylKiaMqnqaEoHUwDbMGt4FmUoC39H1bys/present?slide=id.i0)

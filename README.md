# PondPy
PondPy is a package built to aid in the design of low-slope roof bays for 
ponding stability and impounded rain loading. It utilizes a series of
purpose-built finite element and ponding analysis classes and methods to be
as intuitive as possible for the modern engineer.

### Installation
Install pondpy with pip:
```bash
pip install pondpy
```

### Usage
The PondPyModel class is designed to work with several purpose-built classes
that help the user organize their input into a form that are readily utilized
to build and analyze the model. These are the ```PrimaryFraming```,
```SecondaryFraming```, and ```Loading``` classes. In addition, the package is
designed to work with the ```steelpy``` and ```joistpy``` packages, though any
object containing the requiring information attribures (i.e. moment of inertia,
cross-sectional area, elastic modulus, etc.) could be used in lieu of either
package.

To create and analyze a roof bay model, first import the required dependencies
and classes:
```python
from joistpy import sji
from steelpy import aisc

from pondpy.analysis.fem_analysis import (
    SteelBeamSize,
    SteelJoistSize,
)

from pondpy.analysis.pond_analysis import (
    PrimaryMember,
    PrimaryFraming,
    SecondaryMember,
    SecondaryFraming,
    Loading
)

from pondpy.pondpy import PondPyModel
```

Next, define the steel shapes and joist designations in your model.
```python
w12x16 = SteelBeamSize('W12X16', aisc.W_shapes.W12X16)
w16x26 = SteelBeamSize('W16X26', aisc.W_shapes.W16X26)
k_14k1 = SteelJoistSize('14K1', sji.K_Series.K_14K1)
```

Next, define the primary and secondary framing in the roof bay framing system. 
Note that all inputs should be in kips and inches.
```python
p_length = 20*12 # length of primary members in inches
s_length = 20*12 # length of secondary members in inches

# Support types are designated by tuples representing (Tx, Ty, Rz).
# A 0 indicates the degree of freedom is unrestrained while a 1 indicates a 
# restrained degree of freedom.
p_support = [[0, (1, 1, 0)], [p_length, (1, 1, 0)]]
s_support = [[0, (1, 1, 0)], [s_length, (1, 1, 0)]]

p_girder1 = PrimaryMember(p_length, w16x26, p_support)
p_girder2 = PrimaryMember(p_length, w16x26, p_support)
s_beam1 = SecondaryMember(s_length, w12x16, s_support)
s_beam2 = SecondaryMember(s_length, w12x16, s_support)
s_joist1 = SecondaryMember(s_length, k_14k1, s_support)
s_joist2 = SecondaryMember(s_length, k_14k1, s_support)
s_joist3 = SecondaryMember(s_length, k_14k1, s_support)

p_framing = PrimaryFraming([p_girder1, p_girder2])
s_framing = SecondaryFraming([s_beam1, s_joist1, s_joist2, s_joist3, s_beam2])
```
Note that each member should be individually defined as shown above. Otherwise,
the loadings will not be applied correctly to the members.

The roof slope can optionally be set in the ```SecondaryFraming``` object by
using the keyword ```slope``` and entering the roof slope in inches/foot. The
default value is ```0.25```.

Next, define the loading in the roof bay.
```python
p_framing = PrimaryFraming([p_girder1, p_girder2])
s_framing = SecondaryFraming([s_beam1, s_joist1, s_joist2, s_joist3, s_beam2])

q_dl = 20/1000/144 # Surface dead load in ksi
q_rl = 22.4/1000/144 # Surface rain load at secondary drainage inlet in ksi

loading = Loading(q_dl, q_rl)
```
The input rain load should include the static head and the hydraulic head, but
no ponding head.

Finally, define the ```PondPyModel``` object and analyze the model.
```python
pondpy_model = PondPyModel(p_framing, s_framing, loading)

pondpy_model.perform_analysis()
```
Optional arguments for the ```PondPyModel``` include:

    - ```mirrored_left```: bool indicating whether the roof bay is mirrored
      on the left side; default is ```False```

    - ```mirrored_right``` : bool indicating whether the roof bay is mirrored
      on the right side; default is ```False```

    - ```stop_criterion``` : float indicating the error in total impounded
      water weight at which the iterative analysis should be terminated;
      default is ```0.0001```

    - ```max_iter``` : int indicating the maximum number of iterations that
      should be performed
      
    - ```show_results``` : bool indicating whether the iteration results should
      be printed to the terminal upon completion of the analysis;
      default is ```True```

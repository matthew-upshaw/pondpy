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
from steel import aisc

from pondpy.analysis.pond_analysis import (
    PrimaryFraming,
    SecondaryFraming,
    Loading
)
```
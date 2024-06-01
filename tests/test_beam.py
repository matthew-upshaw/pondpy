import pytest
from joistpy import sji
from steelpy import aisc

from pondpy import (
    Beam,
    DistLoad,
    PointLoad,
    SteelBeamSize,
    SteelJoistSize,
)

w12x16 = aisc.W_shapes.W12X16
k_14k1 = sji.K_Series.K_14K1

beam = SteelBeamSize('W12X16', w12x16)
joist = SteelJoistSize('14K1', k_14k1)

length = 20*12
supports = [(0, (1, 1, 0)), (length, (1, 1, 0))]

dload = DistLoad(location=(0, length), magnitude=((0, 0), (-2, -2), (0, 0)))
pload = PointLoad(location=length/2, magnitude=(0, -5, 0))

@pytest.fixture
def default_beam():
    return Beam(length=length, size=beam, supports=supports)

@pytest.fixture
def custom_beam():
    return Beam(length=length, size=beam, supports=supports, ploads=[pload], dloads=[dload])

@pytest.fixture
def default_joist():
    return Beam(length=length, size=joist, supports=supports)

@pytest.fixture
def custom_joist():
    return Beam(length=length, size=joist, supports=supports, ploads=[pload], dloads=[dload])

def test_default_beam_initialization(default_beam):
    assert default_beam.length == 240
    assert default_beam.size == beam
    assert default_beam.supports == supports
    assert default_beam.ploads == []
    assert default_beam.dloads == []
    assert default_beam.e_mod == beam.e_mod
    assert default_beam.mom_inertia == beam.properties.Ix
    assert default_beam.area == beam.properties.area

def test_custom_beam_initialization(custom_beam):
    assert custom_beam.length == 240
    assert custom_beam.size == beam
    assert custom_beam.supports == supports
    assert custom_beam.ploads == [pload]
    assert custom_beam.dloads == [dload]
    assert custom_beam.e_mod == beam.e_mod
    assert custom_beam.mom_inertia == beam.properties.Ix
    assert custom_beam.area == beam.properties.area

def test_default_joist_initialization(default_joist):
    assert default_joist.length == 240
    assert default_joist.size == joist
    assert default_joist.supports == supports
    assert default_joist.ploads == []
    assert default_joist.dloads == []
    assert default_joist.e_mod == joist.e_mod
    assert default_joist.mom_inertia == joist.properties.get_mom_inertia(span=length/12)
    assert default_joist.area == joist.properties.weight/490*144

def test_custom_joist_initialization(custom_joist):
    assert custom_joist.length == 240
    assert custom_joist.size == joist
    assert custom_joist.supports == supports
    assert custom_joist.ploads == [pload]
    assert custom_joist.dloads == [dload]
    assert custom_joist.e_mod == joist.e_mod
    assert custom_joist.mom_inertia == joist.properties.get_mom_inertia(span=length/12)
    assert custom_joist.area == joist.properties.weight/490*144
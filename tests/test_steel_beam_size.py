import pytest
from steelpy import aisc

from pondpy import SteelBeamSize

w12x16 = aisc.W_shapes.W12X16

@pytest.fixture
def default_steel_beam():
    properties = w12x16.properties
    return SteelBeamSize(name='W12X16', properties=properties)

@pytest.fixture
def custom_steel_beam():
    properties = w12x16.properties
    return SteelBeamSize(name='W12X16', properties=properties, e_mod=30000, section_type='Custom')

def test_default_initialization(default_steel_beam):
    assert default_steel_beam.name == 'W12X16'
    assert default_steel_beam.properties == w12x16.properties
    assert default_steel_beam.e_mod == 29000
    assert default_steel_beam.section_type == 'AISC'

def test_custom_initialization(custom_steel_beam):
    assert custom_steel_beam.name == 'W12X16'
    assert custom_steel_beam.properties == w12x16.properties
    assert custom_steel_beam.e_mod == 30000
    assert custom_steel_beam.section_type == 'Custom'

def test_string_representation(default_steel_beam, custom_steel_beam):
    assert str(default_steel_beam) == 'W12X16'
    assert str(custom_steel_beam) == 'W12X16'


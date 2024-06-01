import pytest
from steelpy import aisc

from pondpy import SteelBeamSize

w12x16 = aisc.W_shapes.W12X16

@pytest.fixture
def default_steel_beam():
    properties = w12x16
    return SteelBeamSize(name='W12X16', properties=properties)

@pytest.fixture
def custom_steel_beam():
    properties = w12x16
    return SteelBeamSize(name='W12X16', properties=properties, e_mod=30000, section_type='AISC')

@pytest.fixture
def valid_properties():
    return w12x16

def test_default_initialization(default_steel_beam):
    assert default_steel_beam.name == 'W12X16'
    assert default_steel_beam.properties == w12x16
    assert default_steel_beam.e_mod == 29000
    assert default_steel_beam.section_type == 'AISC'

def test_custom_initialization(custom_steel_beam):
    assert custom_steel_beam.name == 'W12X16'
    assert custom_steel_beam.properties == w12x16
    assert custom_steel_beam.e_mod == 30000
    assert custom_steel_beam.section_type == 'AISC'

def test_string_representation(default_steel_beam, custom_steel_beam):
    assert str(default_steel_beam) == 'W12X16'
    assert str(custom_steel_beam) == 'W12X16'

def test_invalid_name(valid_properties):
    with pytest.raises(TypeError):
        SteelBeamSize(name=None, properties=valid_properties)

def test_invalid_properties():
    with pytest.raises(TypeError):
        SteelBeamSize(name='W12X16', properties=None)

def test_invalid_e_mod(valid_properties):
    with pytest.raises(TypeError):
        SteelBeamSize(name='W12X16', properties=valid_properties, e_mod=None)

def test_invalid_section_type(valid_properties):
    with pytest.raises(TypeError):
        SteelBeamSize(name='W12X16', properties=valid_properties, section_type=None)

def test_invalid_section_type_name(valid_properties):
    with pytest.raises(TypeError):
        SteelBeamSize(name='W12X16', properties=valid_properties, section_type='Section')
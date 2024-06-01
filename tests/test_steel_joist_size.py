import pytest
from joistpy import sji

from pondpy import SteelJoistSize

k_14k1 = sji.K_Series.K_14K1

@pytest.fixture
def default_steel_joist():
    properties = k_14k1.properties
    return SteelJoistSize(name='14K1', properties=properties)

@pytest.fixture
def custom_steel_joist():
    properties = k_14k1.properties
    return SteelJoistSize(name='14K1', properties=properties, e_mod=30000, section_type='Custom')

def test_default_initialization(default_steel_joist):
    assert default_steel_joist.name == '14K1'
    assert default_steel_joist.properties == k_14k1.properties
    assert default_steel_joist.e_mod == 29000
    assert default_steel_joist.section_type == 'SJI'

def test_custom_initialization(custom_steel_joist):
    assert custom_steel_joist.name == '14K1'
    assert custom_steel_joist.properties == k_14k1.properties
    assert custom_steel_joist.e_mod == 30000
    assert custom_steel_joist.section_type == 'Custom'

def test_string_representation(default_steel_joist, custom_steel_joist):
    assert str(default_steel_joist) == '14K1'
    assert str(custom_steel_joist) == '14K1'
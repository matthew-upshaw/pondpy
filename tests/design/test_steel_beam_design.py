import pytest
from steelpy import aisc

from pondpy import SteelBeamDesign

beam = aisc.W_shapes.W16X26
w10x12 = aisc.W_shapes.W10X12
w10x22 = aisc.W_shapes.W10X22
hss4x4 = aisc.HSS_shapes.HSS4X4X1_4

@pytest.fixture
def steel_beam_design():
    return SteelBeamDesign(section=beam, unbraced_length=0)

@pytest.fixture
def steel_beam_design_custom():
    return SteelBeamDesign(section=beam, unbraced_length=0, yield_stress=36)

def test_steel_beam_design_initialization(steel_beam_design):
    assert steel_beam_design.section == beam
    assert steel_beam_design.unbraced_length == 0
    assert steel_beam_design.yield_stress == 50

def test_steel_beam_design_custom_initialization(steel_beam_design_custom):
    assert steel_beam_design_custom.section == beam
    assert steel_beam_design_custom.unbraced_length == 0
    assert steel_beam_design_custom.yield_stress == 36

def test_invalid_section():
    with pytest.raises(TypeError):
        SteelBeamDesign(section='W16X26', unbraced_length=0)

def test_invalid_unbraced_length_type():
    with pytest.raises(TypeError):
        SteelBeamDesign(section=beam, unbraced_length='1')

def test_invalid_unbraced_length_value():
    with pytest.raises(ValueError):
        SteelBeamDesign(section=beam, unbraced_length=-0.1)

def test_invalid_yield_stress_type():
    with pytest.raises(TypeError):
        SteelBeamDesign(section=beam, unbraced_length=0, yield_stress='50')

def test_invalid_yield_stress_value():
    with pytest.raises(ValueError):
        SteelBeamDesign(section=beam, unbraced_length=0, yield_stress=0)

def test_get_moment_capacity_yield():
    design_yield = SteelBeamDesign(section=w10x22, unbraced_length=0)
    design_yield.get_moment_capacity()

def test_get_moment_capacity_ltb1():
    design_ltb1 = SteelBeamDesign(section=w10x22, unbraced_length=5*12)
    design_ltb1.get_moment_capacity()

def test_get_moment_capacity_ltb2():
    design_ltb2 = SteelBeamDesign(section=w10x22, unbraced_length=20*12)
    design_ltb2.get_moment_capacity()

def test_get_moment_capacity_flb():
    design_flb = SteelBeamDesign(section=w10x12, unbraced_length=0)
    design_flb.get_moment_capacity()

def test_invalid_section_for_moment():
    with pytest.raises(ValueError):
        SteelBeamDesign(section=hss4x4, unbraced_length=0).get_moment_capacity()

def test_get_shear_capacity_1():
    design_shear1 = SteelBeamDesign(section=w10x12, unbraced_length=0)
    design_shear1.get_shear_capacity()

def test_get_shear_capacity_2():
    design_shear2 = SteelBeamDesign(section=beam, unbraced_length=0)
    design_shear2.get_shear_capacity()

def test_invalid_section_for_shear():
    with pytest.raises(ValueError):
        SteelBeamDesign(section=hss4x4, unbraced_length=0).get_shear_capacity()
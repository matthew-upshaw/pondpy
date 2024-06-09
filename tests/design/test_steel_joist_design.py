import pytest
from joistpy import sji

from pondpy import SteelJoistDesign

joist = sji.K_Series.K_14K1
kcs_joist = sji.KCS_Series.KCS_14KCS1

@pytest.fixture
def steel_joist_design():
    return SteelJoistDesign(designation=joist, span=20*12)

def test_steel_joist_design_initialization(steel_joist_design):
    assert steel_joist_design.designation == joist
    assert steel_joist_design.span == 20*12
    assert steel_joist_design.w_total == 284.0

def test_invalid_designation():
    with pytest.raises(TypeError):
        SteelJoistDesign(designation='14K1', span=20*12)

def test_invalid_span_type():
    with pytest.raises(TypeError):
        SteelJoistDesign(designation=joist, span='29')

def test_invalid_span_value():
    with pytest.raises(ValueError):
        SteelJoistDesign(designation=joist, span=29*12)

def test_get_moment_capacity(steel_joist_design):
    moment_cap = steel_joist_design.get_moment_capacity()
    assert isinstance(moment_cap, float)
    assert moment_cap == 284*20**2/8/1000

def test_get_shear_capacity(steel_joist_design):
    shear_cap = steel_joist_design.get_shear_capacity()
    assert isinstance(shear_cap, tuple)
    assert len(shear_cap) == 2
    assert shear_cap[0] == 0.25*284*20/2/1000
    assert shear_cap[1] == 284*20/2/1000

def test_get_shear_plot_points(steel_joist_design):
    steel_joist_design.get_shear_plot_points()

def test_get_kcs_shear_capacity():
    kcs_joist_test = SteelJoistDesign(designation=kcs_joist, span=20*12)
    shear_cap = kcs_joist_test.get_shear_capacity()
    assert isinstance(shear_cap, tuple)
    assert len(shear_cap) == 2
    assert shear_cap[0] == 2900/1000
    assert shear_cap[1] == 2900/1000

def tes_get_kcs_shear_plot_points():
    kcs_joist_test = SteelJoistDesign(designation=kcs_joist, span=20*12)
    kcs_joist_test.get_shear_plot_points()

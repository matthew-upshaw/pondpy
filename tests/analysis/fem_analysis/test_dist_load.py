import pytest

from pondpy import DistLoad

location = (0, 10)
magnitude = ((0, 0), (-2, -2), (0, 0))

@pytest.fixture()
def valid_dload():
    return DistLoad(location=location, magnitude=magnitude)

def test_dload_initialization(valid_dload):
    assert valid_dload.location == location
    assert valid_dload.magnitude == magnitude

def test_invalid_location_type():
    with pytest.raises(TypeError):
        DistLoad(location=None, magnitude=magnitude)
        
def test_invalid_location_length():
    with pytest.raises(TypeError):
        DistLoad(location=(0), magnitude=magnitude)
        
def test_invalid_location_component():
    with pytest.raises(TypeError):
        DistLoad(location=('0', '10'), magnitude=magnitude)

def test_invalid_magnitude_type():
    with pytest.raises(TypeError):
        DistLoad(location=location, magnitude=None)
        
def test_invalid_magnitude_length():
    with pytest.raises(TypeError):
        DistLoad(location=location, magnitude=((0, 0, 0), (0, 0, 0)))
        
def test_invalid_magnitude_component_type():
    with pytest.raises(TypeError):
        DistLoad(location=location, magnitude=(None, None, None))
        
def test_invalid_magnitude_component_length():
    with pytest.raises(TypeError):
        DistLoad(location=location, magnitude=((5), (5), (5)))
        
def test_invalid_magnitude_inner_component():
    with pytest.raises(TypeError):
        DistLoad(location=location, magnitude=(('0', '0', '0'), ('0', '0', '0'), ('0', '0', '0')))
        
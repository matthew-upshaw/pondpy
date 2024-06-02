import pytest

from pondpy import PointLoad

location = 5
magnitude = (0, -5, 9)

@pytest.fixture
def valid_pload():
    return PointLoad(location=location, magnitude=magnitude)
    
def test_pload_initialization(valid_pload):
    assert valid_pload.location == location
    assert valid_pload.magnitude == magnitude
    
def test_invalid_location():
    with pytest.raises(TypeError):
        PointLoad(location='5', magnitude=magnitude)
        
def test_invalid_magnitude_type():
    with pytest.raises(TypeError):
        PointLoad(location=location, magnitude=None)
        
def test_invalid_magnitude_length():
    with pytest.raises(TypeError):
        PointLoad(location=location, magnitude=(0, 0))
        
def test_invalid_magnitude_components():
    with pytest.raises(TypeError):
        PointLoad(location=location, magnitude=('0', '5', '0'))

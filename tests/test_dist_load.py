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

def test_invalid_location():
    with pytest.raises(TypeError):
        DistLoad(location=(None, 0.0), magnitude=magnitude)

def test_invalid_magnitude():
    with pytest.raises(TypeError):
        DistLoad(location=location, magnitude=((0.0, None), (0, 0, 0), (None, None)))
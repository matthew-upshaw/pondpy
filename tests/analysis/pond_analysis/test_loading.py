import pytest

from pondpy import Loading

dead_load = 20/144/1000
rain_load = 25.2/144/1000

@pytest.fixture
def loading_default():
    return Loading(dead_load=dead_load, rain_load=rain_load)

@pytest.fixture
def loading_custom():
    return Loading(dead_load=dead_load, rain_load=rain_load, include_sw=False)

def test_loading_default_initialization(loading_default):
    assert loading_default.dead_load == dead_load
    assert loading_default.rain_load == rain_load
    assert loading_default.include_sw == True

def test_loading_custom_initialization(loading_custom):
    assert loading_custom.dead_load == dead_load
    assert loading_custom.rain_load == rain_load
    assert loading_custom.include_sw == False

def test_invalid_dead_load():
    with pytest.raises(TypeError):
        Loading(dead_load=None, rain_load=rain_load, include_sw=True)

def test_invalid_rain_load():
    with pytest.raises(TypeError):
        Loading(dead_load=dead_load, rain_load=None, include_sw=True)

def test_invalid_include_sw():
    with pytest.raises(TypeError):
        Loading(dead_load=dead_load, rain_load=rain_load, include_sw='False')
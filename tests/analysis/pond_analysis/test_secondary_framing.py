import pytest
from joistpy import sji

from pondpy import (
    SecondaryMember,
    SecondaryFraming,
    SteelJoistSize,
)

k_14k1 = sji.K_Series.K_14K1

joist = SteelJoistSize('14K1', k_14k1)

length = 20*12
supports = [(0, (1, 1, 0)), (length, (1, 1, 0))]

secondary_member = SecondaryMember(length=length, size=joist, supports=supports)

@pytest.fixture
def secondary_framing_default():
    return SecondaryFraming(secondary_members=[secondary_member])

@pytest.fixture
def secondary_framing_custom():
    return SecondaryFraming(secondary_members=[secondary_member], slope=0.50)

def test_secondary_framing_default_initialization(secondary_framing_default):
    assert secondary_framing_default.secondary_members == [secondary_member]
    assert secondary_framing_default.slope == 0.25

def test_secondary_framing_custom_initialization(secondary_framing_custom):
    assert secondary_framing_custom.secondary_members == [secondary_member]
    assert secondary_framing_custom.slope == 0.50

def test_invalid_secondary_members_type():
    with pytest.raises(TypeError):
        SecondaryFraming(secondary_members=None)

def test_invalid_secondary_members_component():
    with pytest.raises(TypeError):
        SecondaryFraming(secondary_members=[None, None])

def test_invalid_slope():
    with pytest.raises(TypeError):
        SecondaryFraming(secondary_members=[secondary_member], slope='0.25')

def test_string_representation(secondary_framing_default):
    assert str(secondary_framing_default) == 'Secondary framing members: [\'14K1\']'

import pytest
from steelpy import aisc

from pondpy import (
    PrimaryMember,
    PrimaryFraming,
    SteelBeamSize,
)

w12x16 = aisc.W_shapes.W12X16

beam = SteelBeamSize('W12X16', w12x16)

length = 20*12
supports = [(0, (1, 1, 0)), (length, (1, 1, 0))]

primary_member = PrimaryMember(length=length, size=beam, supports=supports)

@pytest.fixture
def primary_framing():
    return PrimaryFraming(primary_members=[primary_member])

def test_primary_framing_intialization(primary_framing):
    assert primary_framing.primary_members == [primary_member]

def test_invalid_primary_members_type():
    with pytest.raises(TypeError):
        PrimaryFraming(primary_members=None)

def test_invalid_primary_members_component():
    with pytest.raises(TypeError):
        PrimaryFraming(primary_members=[None, None])

def test_string_representation(primary_framing):
    assert str(primary_framing) == 'Primary framing members: [\'W12X16\']'

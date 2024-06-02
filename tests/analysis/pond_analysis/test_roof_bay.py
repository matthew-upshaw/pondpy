import pytest
from joistpy import sji
from steelpy import aisc

from pondpy import (
    DistLoad,
    Loading,
    PrimaryMember,
    PrimaryFraming,
    RoofBay,
    SecondaryMember,
    SecondaryFraming,
    SteelBeamSize,
    SteelJoistSize,
)

dead_load = 20/144/1000
rain_load = 25.2/144/1000

loading = Loading(dead_load=dead_load, rain_load=rain_load)

w12x16 = aisc.W_shapes.W12X16
k_14k1 = sji.K_Series.K_14K1

beam = SteelBeamSize('W12X16', w12x16)
joist = SteelJoistSize('14K1', k_14k1)

length = 20*12
supports = [(0, (1, 1, 0)), (length, (1, 1, 0))]

primary_member = PrimaryMember(length=length, size=beam, supports=supports)
secondary_member = SecondaryMember(length=length, size=joist, supports=supports)

primary_framing = PrimaryFraming(primary_members=[primary_member, primary_member])
secondary_framing = SecondaryFraming(secondary_members=[secondary_member, secondary_member])

@pytest.fixture
def roof_bay_default():
    return RoofBay(
        primary_framing=primary_framing,
        secondary_framing=secondary_framing,
        loading=loading
    )

@pytest.fixture
def roof_bay_custom():
    return RoofBay(
        primary_framing=primary_framing,
        secondary_framing=secondary_framing,
        loading=loading,
        mirrored_left=True,
        mirrored_right=True,
    )

def test_roof_bay_default_initialization(roof_bay_default):
    assert roof_bay_default.primary_framing == primary_framing
    assert roof_bay_default.secondary_framing == secondary_framing
    assert roof_bay_default.loading == loading
    assert roof_bay_default.mirrored_left == False
    assert roof_bay_default.mirrored_right == False
    assert roof_bay_default.secondary_spacing == 240.0
    assert len(roof_bay_default.secondary_dl) == 2
    for i_smember, _ in enumerate(roof_bay_default.secondary_framing.secondary_members):
        for item in roof_bay_default.secondary_dl[i_smember]:
            assert isinstance(item, DistLoad)
    assert roof_bay_default.secondary_tribw == [120.0, 120.0]
    assert len(roof_bay_default.primary_sw) == 2
    for i_pmember, _ in enumerate(roof_bay_default.primary_framing.primary_members):
        for item in roof_bay_default.primary_sw[i_pmember]:
            assert isinstance(item, DistLoad)

def test_roof_bay_custom_initialization(roof_bay_custom):
    assert roof_bay_custom.primary_framing == primary_framing
    assert roof_bay_custom.secondary_framing == secondary_framing
    assert roof_bay_custom.loading == loading
    assert roof_bay_custom.mirrored_left == True
    assert roof_bay_custom.mirrored_right == True
    assert roof_bay_custom.secondary_spacing == 240.0
    assert len(roof_bay_custom.secondary_dl) == 2
    for i_smember, _ in enumerate(roof_bay_custom.secondary_framing.secondary_members):
        for item in roof_bay_custom.secondary_dl[i_smember]:
            assert isinstance(item, DistLoad)
    assert roof_bay_custom.secondary_tribw == [240, 240.0]
    assert len(roof_bay_custom.primary_sw) == 2
    for i_pmember, _ in enumerate(roof_bay_custom.primary_framing.primary_members):
        for item in roof_bay_custom.primary_sw[i_pmember]:
            assert isinstance(item, DistLoad)

def test_invalid_primary_framing():
    with pytest.raises(TypeError):
        RoofBay(
            primary_framing=None,
            secondary_framing=secondary_framing,
            loading=loading,
        )
        
def test_invalid_secondary_framing():
    with pytest.raises(TypeError):
        RoofBay(
            primary_framing=primary_framing,
            secondary_framing=None,
            loading=loading
        )

def test_invalid_loading():
    with pytest.raises(TypeError):
        RoofBay(
            primary_framing=primary_framing,
            secondary_framing=secondary_framing,
            loading=None
        )

def test_invalid_mirrored_left():
    with pytest.raises(TypeError):
        RoofBay(
            primary_framing=primary_framing,
            secondary_framing=secondary_framing,
            loading=loading,
            mirrored_left='False',
            mirrored_right=False
        )

def test_invalid_mirrored_right():
    with pytest.raises(TypeError):
        RoofBay(
            primary_framing=primary_framing,
            secondary_framing=secondary_framing,
            loading=loading,
            mirrored_left=False,
            mirrored_right='False'
        )

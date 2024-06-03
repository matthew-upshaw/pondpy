import pytest
from joistpy import sji
from steelpy import aisc

from pondpy import (
    BeamModel,
    DistLoad,
    SteelBeamSize,
    SteelJoistSize,
    PondPyModel,
    PrimaryMember,
    PrimaryFraming,
    RoofBay,
    RoofBayModel,
    SecondaryMember,
    SecondaryFraming,
    Loading,
)

w12x16 = SteelBeamSize('W12X16', aisc.W_shapes.W12X16)
w16x26 = SteelBeamSize('W16X26', aisc.W_shapes.W16X26)
k_14k1 = SteelJoistSize('14K1', sji.K_Series.K_14K1)

p_length = 20*12 # length of primary members in inches
s_length = 20*12 # length of secondary members in inches

# Support types are designated by tuples representing (Tx, Ty, Rz).
# A 0 indicates the degree of freedom is unrestrained while a 1 indicates a 
# restrained degree of freedom.
p_support = [[0, (1, 1, 0)], [p_length, (1, 1, 0)]]
s_support = [[0, (1, 1, 0)], [s_length, (1, 1, 0)]]

p_girder1 = PrimaryMember(p_length, w16x26, p_support)
p_girder2 = PrimaryMember(p_length, w16x26, p_support)
s_beam1 = SecondaryMember(s_length, w12x16, s_support)
s_beam2 = SecondaryMember(s_length, w12x16, s_support)
s_joist1 = SecondaryMember(s_length, k_14k1, s_support)
s_joist2 = SecondaryMember(s_length, k_14k1, s_support)

primary_framing = PrimaryFraming([p_girder1, p_girder2])
secondary_framing = SecondaryFraming([s_beam1, s_joist1, s_joist2, s_beam2])

q_dl = 20/1000/144 # Surface dead load in ksi
q_rl = 22.4/1000/144 # Surface rain load at secondary drainage inlet in ksi

loading = Loading(q_dl, q_rl)

@pytest.fixture
def pondpy_model_default():
    return PondPyModel(
        primary_framing=primary_framing,
        secondary_framing=secondary_framing,
        loading=loading
    )

@pytest.fixture
def pondpy_model_custom():
    return PondPyModel(
        primary_framing=primary_framing,
        secondary_framing=secondary_framing,
        loading=loading,
        mirrored_left=True,
        mirrored_right=True,
        stop_criterion=0.01,
        max_iter = 5,
        show_results=False
    )

def test_pondpy_model_default_initialization(pondpy_model_default):
    assert pondpy_model_default.loading == loading
    assert pondpy_model_default.max_iter == 50
    assert pondpy_model_default.mirrored_left == False
    assert pondpy_model_default.mirrored_right == False
    assert isinstance(pondpy_model_default.roof_bay, RoofBay)
    assert isinstance(pondpy_model_default.roof_bay_model, RoofBayModel)
    assert pondpy_model_default.primary_framing == primary_framing
    assert pondpy_model_default.secondary_framing == secondary_framing
    assert pondpy_model_default.show_results == True
    assert pondpy_model_default.stop_criterion == 0.001

def test_pondpy_model_custom_initializaton(pondpy_model_custom):
    assert pondpy_model_custom.loading == loading
    assert pondpy_model_custom.max_iter == 5
    assert pondpy_model_custom.mirrored_left == True
    assert pondpy_model_custom.mirrored_right == True
    assert isinstance(pondpy_model_custom.roof_bay, RoofBay)
    assert isinstance(pondpy_model_custom.roof_bay_model, RoofBayModel)
    assert pondpy_model_custom.primary_framing == primary_framing
    assert pondpy_model_custom.secondary_framing == secondary_framing
    assert pondpy_model_custom.show_results == False
    assert pondpy_model_custom.stop_criterion == 0.01

def test_invalid_loading():
    with pytest.raises(TypeError):
        PondPyModel(
            primary_framing=primary_framing,
            secondary_framing=secondary_framing,
            loading=None,
            mirrored_left=False,
            mirrored_right=False,
            stop_criterion=0.0001,
            max_iter=50,
            show_results=True
        )

def test_invalid_max_iter():
    with pytest.raises(TypeError):
        PondPyModel(
            primary_framing=primary_framing,
            secondary_framing=secondary_framing,
            loading=loading,
            mirrored_left=False,
            mirrored_right=False,
            stop_criterion=0.0001,
            max_iter=0,
            show_results=True
        )

def test_invalid_mirrored_left():
    with pytest.raises(TypeError):
        PondPyModel(
            primary_framing=primary_framing,
            secondary_framing=secondary_framing,
            loading=loading,
            mirrored_left='True',
            mirrored_right=False,
            stop_criterion=0.0001,
            max_iter=50,
            show_results=True
        )

def test_invalid_mirrored_right():
    with pytest.raises(TypeError):
        PondPyModel(
            primary_framing=primary_framing,
            secondary_framing=secondary_framing,
            loading=loading,
            mirrored_left=False,
            mirrored_right='True',
            stop_criterion=0.0001,
            max_iter=50,
            show_results=True
        )

def test_invalid_primary_framing():
    with pytest.raises(TypeError):
        PondPyModel(
            primary_framing=None,
            secondary_framing=secondary_framing,
            loading=loading,
            mirrored_left=False,
            mirrored_right=False,
            stop_criterion=0.0001,
            max_iter=50,
            show_results=True
        )

def test_invalid_secondary_framing():
    with pytest.raises(TypeError):
        PondPyModel(
            primary_framing=primary_framing,
            secondary_framing=None,
            loading=loading,
            mirrored_left=False,
            mirrored_right=False,
            stop_criterion=0.0001,
            max_iter=50,
            show_results=True
        )

def test_invalid_show_results():
    with pytest.raises(TypeError):
        PondPyModel(
            primary_framing=primary_framing,
            secondary_framing=secondary_framing,
            loading=loading,
            mirrored_left=False,
            mirrored_right=False,
            stop_criterion=0.0001,
            max_iter=50,
            show_results='True'
        )

def test_invalid_stop_criterion():
    with pytest.raises(TypeError):
        PondPyModel(
            primary_framing=primary_framing,
            secondary_framing=secondary_framing,
            loading=loading,
            mirrored_left=False,
            mirrored_right=False,
            stop_criterion=0.0,
            max_iter=50,
            show_results=True
        )

def test_perform_analysis(pondpy_model_default):
    pondpy_model_default.perform_analysis()

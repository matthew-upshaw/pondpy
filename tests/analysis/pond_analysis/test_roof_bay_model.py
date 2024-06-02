import pytest
from flaky import flaky
from joistpy import sji
from steelpy import aisc

from pondpy import (
    AnalysisError,
    BeamModel,
    SteelBeamSize,
    SteelJoistSize,
    PrimaryMember,
    PrimaryFraming,
    RoofBay,
    RoofBayModel,
    SecondaryMember,
    SecondaryFraming,
    Loading,
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

roof_bay = RoofBay(primary_framing=primary_framing, secondary_framing=secondary_framing, loading=loading)

@pytest.fixture
def roof_bay_model_default():
    return RoofBayModel(roof_bay=roof_bay)

@pytest.fixture
def roof_bay_model_custom():
    return RoofBayModel(roof_bay=roof_bay, max_node_spacing=12)

def test_roof_bay_model_default_intialization(roof_bay_model_default):
    assert roof_bay_model_default.analysis_complete == False
    assert roof_bay_model_default.analysis_ready == True
    assert isinstance(roof_bay_model_default.initial_impounded_depth, dict)
    assert roof_bay_model_default.max_node_spacing == 6
    assert isinstance(roof_bay_model_default.primary_models, list)
    assert len(roof_bay_model_default.primary_models) == 2
    for model in roof_bay_model_default.primary_models:
        assert isinstance(model, BeamModel)
    assert roof_bay_model_default.roof_bay == roof_bay
    assert isinstance(roof_bay_model_default.secondary_models, list)
    assert len(roof_bay_model_default.secondary_models) == 2
    for model in roof_bay_model_default.secondary_models:
        assert isinstance(model, BeamModel)

def test_roof_bay_model_custom_intialization(roof_bay_model_custom):
    assert roof_bay_model_custom.analysis_complete == False
    assert roof_bay_model_custom.analysis_ready == True
    assert isinstance(roof_bay_model_custom.initial_impounded_depth, dict)
    assert roof_bay_model_custom.max_node_spacing == 12
    assert isinstance(roof_bay_model_custom.primary_models, list)
    assert len(roof_bay_model_custom.primary_models) == 2
    for model in roof_bay_model_custom.primary_models:
        assert isinstance(model, BeamModel)
    assert roof_bay_model_custom.roof_bay == roof_bay
    assert isinstance(roof_bay_model_custom.secondary_models, list)
    assert len(roof_bay_model_custom.secondary_models) == 2
    for model in roof_bay_model_custom.secondary_models:
        assert isinstance(model, BeamModel)

def test_invalid_roof_bay():
    with pytest.raises(TypeError):
        RoofBayModel(roof_bay=None)

def test_invalid_max_node_spacing():
    with pytest.raises(TypeError):
        RoofBayModel(roof_bay=roof_bay, max_node_spacing='12')

def test_analyze_roof_bay(roof_bay_model_default):
    rl = roof_bay_model_default._get_secondary_rl(roof_bay_model_default.initial_impounded_depth)
    roof_bay_model_default.analyze_roof_bay(rain_load=rl)
    assert roof_bay_model_default.analysis_complete == True

@flaky
def test_valid_generate_plots(roof_bay_model_default):
    rl = roof_bay_model_default._get_secondary_rl(roof_bay_model_default.initial_impounded_depth)
    roof_bay_model_default.analyze_roof_bay(rain_load=rl)
    plot_dict = roof_bay_model_default.generate_plots()
    assert isinstance(plot_dict, dict)

def test_invalid_generate_plots(roof_bay_model_default):
    with pytest.raises(AnalysisError):
        plot_dict = roof_bay_model_default.generate_plots()

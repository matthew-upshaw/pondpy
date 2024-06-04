import matplotlib
import numpy as np
import pytest
from flaky import flaky
from steelpy import aisc

from pondpy import (
    AnalysisError,
    Beam,
    BeamModel,
    DistLoad,
    PointLoad,
    SteelBeamSize,
)

length = 20*12
supports = [(0, (1, 1, 0)), (length, (1, 1, 0))]

w12x16 = aisc.W_shapes.W12X16
beam_size = SteelBeamSize('W12X16', w12x16)
beam = Beam(length=length, size=beam_size, supports=supports)

dload = DistLoad(location=(0, 10), magnitude=((0, 0), (-5, -5), (0, 0)))
pload = PointLoad(location=0, magnitude=(0, -5, 0))

@pytest.fixture
def beam_model_default():
    return BeamModel(beam=beam)

@pytest.fixture
def beam_model_custom():
    return BeamModel(beam=beam, max_node_spacing=12, ini_analysis=False)

def test_default_initialization(beam_model_default):
    assert beam_model_default.analysis_complete == False
    assert beam_model_default.analysis_ready == True
    assert beam_model_default.beam == beam
    assert len(beam_model_default.dof_num) == 41
    assert len(beam_model_default.elem_dload) == 40
    assert len(beam_model_default.elem_nodes) == 40
    assert beam_model_default.element_forces.shape == (40, 6)
    assert beam_model_default.fef_load_vector.shape == (119, 1)
    assert beam_model_default.global_displacement.shape == (119, 1)
    assert beam_model_default.global_stiffness_matrix.shape == (119, 119)
    assert beam_model_default.ini_analysis == True
    assert len(beam_model_default.local_stiffness_matrices) == 40
    assert beam_model_default.max_node_spacing == 6
    assert len(beam_model_default.model_nodes) == 41
    assert beam_model_default.n_dof == 119
    assert beam_model_default.nodal_load_vector.shape == (119, 1)
    assert len(beam_model_default.node_elem_fef) == 41
    assert len(beam_model_default.node_pload) == 41
    assert len(beam_model_default.node_support) == 41
    assert beam_model_default.points_of_interest == [0, 240]
    assert beam_model_default.support_nodes == [0, 40]
    assert beam_model_default.support_reactions.shape == (41, 3)

def test_custom_initialization(beam_model_custom):
    assert beam_model_custom.analysis_complete == False
    assert beam_model_custom.analysis_ready == False
    assert beam_model_custom.beam == beam
    assert beam_model_custom.dof_num == []
    assert beam_model_custom.elem_dload == []
    assert beam_model_custom.elem_loads == []
    assert beam_model_custom.elem_nodes == []
    assert beam_model_custom.element_forces.shape == (0, 0)
    assert beam_model_custom.fef_load_vector.shape == (0, 0)
    assert beam_model_custom.global_displacement.shape == (0, 0)
    assert beam_model_custom.global_stiffness_matrix.shape == (0, 0)
    assert beam_model_custom.ini_analysis == False
    assert beam_model_custom.local_stiffness_matrices == []
    assert beam_model_custom.model_nodes == []
    assert beam_model_custom.n_dof == 0
    assert beam_model_custom.nodal_load_vector.shape == (0, 0)
    assert beam_model_custom.node_elem_fef == []
    assert beam_model_custom.node_pload == []
    assert beam_model_custom.node_support == []
    assert beam_model_custom.points_of_interest == []
    assert beam_model_custom.support_nodes == []
    assert beam_model_custom.support_reactions.shape == (0, 0)

def test_invalid_beam_object():
    with pytest.raises(TypeError):
        BeamModel(beam=None, ini_analysis=True, max_node_spacing=6)

def test_invalid_initialize_analysis():
    with pytest.raises(TypeError):
        BeamModel(beam=beam, ini_analysis=None, max_node_spacing=6)

def test_invalid_max_node_spacing():
    with pytest.raises(TypeError):
        BeamModel(beam=beam, ini_analysis=True, max_node_spacing='6')

def test_add_beam_dload(beam_model_default):
    beam_model_default.perform_analysis()
    beam_model_default.add_beam_dload([dload])
    assert beam_model_default.analysis_ready == True
    assert beam_model_default.analysis_complete == False

def test_invalid_add_beam_dload_dload(beam_model_default):
    with pytest.raises(TypeError):
        beam_model_default.add_beam_dload(dload=None, add_type='add')

def test_invalid_add_beam_dload_add_type(beam_model_default):
    with pytest.raises(TypeError):
        beam_model_default.add_beam_dload(dload=[dload], add_type='None')

def test_add_beam_pload(beam_model_default):
    beam_model_default.perform_analysis()
    beam_model_default.add_beam_pload([pload])
    assert beam_model_default.analysis_ready == True
    assert beam_model_default.analysis_complete == False

def test_invalid_add_beam_pload_pload(beam_model_default):
    with pytest.raises(TypeError):
        beam_model_default.add_beam_pload(pload=None, add_type='add')

def test_invalid_add_beam_pload_add_type(beam_model_default):
    with pytest.raises(TypeError):
        beam_model_default.add_beam_pload(pload=[pload], add_type='None')

def test_valid_perform_analysis():
    beam_model = BeamModel(beam=beam)
    beam_model.perform_analysis()
    assert beam_model.analysis_complete == True

def test_valid_perform_analysis_user_initialized():
    beam_model = BeamModel(beam=beam, ini_analysis=False, max_node_spacing=6)
    beam_model.initialize_analysis()
    beam_model.perform_analysis()
    assert beam_model.analysis_complete == True

def test_invalid_perform_analysis():
    with pytest.raises(AnalysisError):
        beam_model = BeamModel(beam=beam, ini_analysis=False, max_node_spacing=6)
        beam_model.perform_analysis()

@flaky
def test_valid_plot_bmd():
    beam_model = BeamModel(beam=beam)
    beam_model.perform_analysis()
    bmd_plot, _ = beam_model.plot_bmd()
    assert isinstance(bmd_plot, matplotlib.figure.Figure)

def test_invalid_plot_bmd():
    with pytest.raises(AnalysisError):
        beam_model = BeamModel(beam=beam, ini_analysis=True, max_node_spacing=6)
        beam_model.plot_bmd()

@flaky
def test_valid_plot_defl():
    beam_model = BeamModel(beam=beam)
    beam_model.perform_analysis()
    defl_plot, _ = beam_model.plot_deflected_shape()
    assert isinstance(defl_plot, matplotlib.figure.Figure)

def test_invalid_plot_bmd():
    with pytest.raises(AnalysisError):
        beam_model = BeamModel(beam=beam, ini_analysis=True, max_node_spacing=6)
        beam_model.plot_deflected_shape()

@flaky
def test_valid_plot_sfd():
    beam_model = BeamModel(beam=beam)
    beam_model.perform_analysis()
    sfd_plot, _ = beam_model.plot_sfd()
    assert isinstance(sfd_plot, matplotlib.figure.Figure)

def test_invalid_plot_sfd():
    with pytest.raises(AnalysisError):
        beam_model = BeamModel(beam=beam, ini_analysis=True, max_node_spacing=6)
        beam_model.plot_sfd()

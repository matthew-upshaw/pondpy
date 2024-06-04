import pytest

from pondpy import ReportBuilder

@pytest.fixture
def report_builder_default():
    return ReportBuilder(
        output_folder='output',
    )

@pytest.fixture
def report_builder_custom():
    return ReportBuilder(
        output_folder='output',
        filename='filename',
        filetype='html'
    )

def test_report_builder_default_initialization(report_builder_default):
    assert report_builder_default.output_folder == 'output'
    assert report_builder_default.filename == 'pondpy_results'
    assert report_builder_default.filetype == 'html'

def test_report_builder_custom_initialization(report_builder_custom):
    assert report_builder_custom.output_folder == 'output'
    assert report_builder_custom.filename == 'filename'
    assert report_builder_custom.filetype == 'html'

def test_invalid_output_folder():
    with pytest.raises(TypeError):
        ReportBuilder(
            output_folder=None,
            filename='file',
            filetype='html'
        )

def test_invalid_filename():
    with pytest.raises(TypeError):
        ReportBuilder(
            output_folder='output',
            filename=None,
            filetype='html'
        )

def test_invalid_filetype_type():
    with pytest.raises(TypeError):
        ReportBuilder(
            output_folder='output',
            filename='filename',
            filetype=None
        )

def test_invalid_filetype_ext():
    with pytest.raises(ValueError):
        ReportBuilder(
            output_folder='output',
            filename='filename',
            filetype='pdf'
        )

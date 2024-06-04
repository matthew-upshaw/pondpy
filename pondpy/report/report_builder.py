import datetime
import os

from .helpers.generate_pdf import generate_pdf
from .helpers.get_version_from_pyproject import get_version_from_pyproject
from .helpers.render_html import render_html

ALLOWED_FILETYPES = ['html', 'pdf']

module_dir = os.path.dirname(__file__)
template_path = os.path.join(module_dir,'templates\\report_template.html')
favicon_path = os.path.join(module_dir, 'templates\\favicon.ico')
logo_path = os.path.join(module_dir, 'templates\\pondpy.svg')
toml_path = os.path.join(module_dir, '..', '..', 'pyproject.toml')

class ReportBuilder:
    '''
    A class to organize data from a PondPyModel object and put it into a
    PDF report for viewing by the user.

    ...

    Attributes
    ----------
    favicon_path : str
        string representing the path to the pondpy favicon
    filename : str
        string represengting the output filename
    filetype : str
        string representing the desired output file type
    generated_at : datetime.datetime
        datetime.datetime object representing the time the report was generated
    logo_path : str
        string representing the path to the pondpy logo
    output_folder : str
        string representing the location to which the report should be saved
    version_no : str
        string representing the version number of the package

    Methods
    -------
    save_report(context)
        Generates the report and saves it to the location specified by the
        output_folder, filename, and filetype attributes.
    '''
    def __init__(self, output_folder, filename='pondpy_results', filetype='html'):
        '''
        Constructs the required attributes for the ReportBuilder object.

        Parameters
        ----------
        filename : str, optional
            string represengting the output filename
        filetype : str, optional
            string representing the desired output file type
        output_folder : str
            string representing the location to which the report should be saved

        Returns
        -------
        None
        '''
        if not isinstance(filename, str):
            raise TypeError('filename must be a string')
        if not isinstance(filetype, str):
            raise TypeError('filetype must be a string')
        if filetype not in ALLOWED_FILETYPES:
            raise ValueError('filetype must be either "pdf" or "html"')
        if not isinstance(output_folder, str):
            raise TypeError('output_folder must be a string')

        self.favicon_path = favicon_path
        self.filename = filename
        self.filetype = filetype
        self.generated_at = datetime.datetime.now()
        self.logo_path = logo_path
        self.output_folder = output_folder
        self.version_no = get_version_from_pyproject(toml_path=toml_path)

    def save_report(self, context):
        '''
        Generates the report and saves it to the location specified by the
        output_folder, filename, and filetype attributes.

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        _create_folder(folder_path=self.output_folder)

        html_string = render_html(template_path=template_path, context=context)
        output_path = os.path.join(self.output_folder, self.filename+'.'+self.filetype)

        if self.filetype == 'pdf':
            generate_pdf(html_content=html_string, output_path=output_path)
        elif self.filetype == 'html':
            with open(output_path, 'w') as output_file:
                output_file.write(html_string)

        print(f'Report successfully generated and saved to {output_path}')
        
def _create_folder(folder_path):
    '''
    Creates the folder path if it does not already exist.

    Parameters
    ----------
    folder_path : str
        string representing the path to the folder to be checked and/or created

    Returns
    -------
    None
    '''
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

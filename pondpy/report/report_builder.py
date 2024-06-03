import os

from .helpers.generate_pdf import generate_pdf
from .helpers.render_html import render_html

ALLOWED_FILETYPES = ['html', 'pdf']

module_dir = os.path.dirname(__file__)
template_path = os.path.join(module_dir,'templates\\report_template.html')
class ReportBuilder:
    '''
    A class to organize data from a PondPyModel object and put it into a
    PDF report for viewing by the user.

    ...

    Attributes
    ----------
    output_path : str
        string representing the location to which the pdf should be saved
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

        self.filename = filename
        self.filetype = filetype
        self.output_folder = output_folder

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

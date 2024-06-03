from weasyprint import HTML

def generate_pdf(html_content, output_path):
    '''
    Generates the pdf report from the html_content string and outputs it to
    the specified output_path.

    Parameters
    ----------
    html_content : str
        string representing the html content to be printed
    output_path : str
        string representing the location to which the pdf should be saved

    Returns
    -------
    None
    '''
    if not isinstance(html_content, str):
        raise TypeError('html_content must be a string')
    if not isinstance(output_path, str):
        raise TypeError('output_path must be a string')

    HTML(string=html_content).write_pdf(output_path)
import os
from jinja2 import Environment, FileSystemLoader

def datetime_format(value, format="%Y-%m-%d, %H:%M:%S"):
    '''
    Formats the datetime.datetime object for redering in the html template.

    Parameters
    ----------
    value : datetime.datetime
        datetime.datetime object 
    format : str
        string representing the format to be output

    Returns
    -------
    formatted_datetime : datetime.datetime
        formatted datetime.datetime object
    '''
    return value.strftime(format)

def render_html(template_path, context):
    '''
    Renders the html to be printed using the report template and python
    context passed into it.

    Parameters
    ----------
    context : dict
        dictionary containing the context to be placed into the html template
    template_path : str
        string representing the filepath to the html template

    Returns
    str : str
        string representing the rendered html
    -------

    '''
    full_template_path = os.path.abspath(template_path)

    if not isinstance(context, dict):
        raise TypeError('context must be a dict')
    if not isinstance(template_path, str):
        raise TypeError('template_path must be a string')
    if not os.path.exists(full_template_path):
        raise FileNotFoundError(f'The template file at {full_template_path} does not exist.')
    if not full_template_path.lower().endswith('.html'):
        raise ValueError(f'The template file at {full_template_path} is not an HTML file.')
    
    template_dir = os.path.dirname(full_template_path)
    template_file = os.path.basename(full_template_path)

    env = Environment(loader=FileSystemLoader(template_dir))
    env.filters["datetime_format"] = datetime_format
    template = env.get_template(template_file)

    return template.render(context)
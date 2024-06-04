import toml

def get_version_from_pyproject(toml_path):
    '''
    Returns the package version from the pyproject.toml file.

    Paramters
    ---------
    toml_path : str
        string representing the path to the pyproject.toml file
    
    Returns
    -------
    version_no : str
        string representing the package version
    '''
    try:
        with open(toml_path, 'r') as toml_file:
            pyproject_data = toml.load(toml_file)
            return pyproject_data['tool']['poetry']['version']
    except (FileNotFoundError, KeyError) as e:
        print(f'Error reading version from pyproject.toml: {e}')
        return 'unknown'
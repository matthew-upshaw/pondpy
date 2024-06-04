import matplotlib
import os

def save_figure(figure, filename, output_folder):
    '''
    Saves the matplotlib.figure.Figure object passed into the function to a png
    at the specified output_folder with the specified filename.

    Parameters
    ----------
    figure : matplotlib.figure.Figure
        matplotlib.figure.Figure object to be saved
    filename : str
        string representing the filename of the saved image
    output_folder : str
        string representing the path to the output_folder to which the image
        should be saved

    Return
    ------
    None
    '''
    if not isinstance(figure, matplotlib.figure.Figure):
        raise TypeError('figure must be matplotlib.figure.Figure object')
    if not isinstance(filename, str):
        raise TypeError('filename must be a string')
    if not isinstance(output_folder, str):
        raise TypeError('output_folder must be a string')

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    img_path = os.path.join(output_folder, filename)
    figure.savefig(img_path)
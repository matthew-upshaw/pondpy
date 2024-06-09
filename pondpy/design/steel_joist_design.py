import joistpy
import numpy as np

class SteelJoistDesign:
    '''
    A class that represents design criteria for a steel joist.

    ...

    Attributes
    ----------
    designation : joistpy.joistpy.Designation
        joistpy designation object for the steel joist under consideration
    span : int or float
        span of the steel joist

    Methods
    -------
    get_moment_capacity()
        Calculates the ASD moment capacity for the steel joist under consideration
        using the total safe load from SJI load tables for the given span.
    get_shear_capacity()
        Calculates the ASD minimum and maximum shear capacity for the steel joist
        under consideration using the total safe load from SJI load tables for 
        the given span.
    '''
    def __init__(self, designation, span):
        '''
        Constructs all the necessary attributes for the steel joist design object.

        Parameters
        ----------
        designation : joistpy.joistpy.Designation
            joistpy designation object for the steel joist under consideration
        max_interval_spacing : int or float
            max spacing along the joist for which the moment and shear capacity
            should be calculated
        span : float
            span of the steel joist
        '''
        if not isinstance(designation, joistpy.joistpy.Designation):
            raise TypeError('designation must be a valid joistpy.joistpy.Designation object')
        if not isinstance(span, (int, float)):
            raise TypeError('span must be int or float')
        
        self.designation = designation
        self.span = span

        self._check_valid_span()

    def _check_valid_span(self):
        '''
        Checks that the span length is valid for the joist designation under
        consideratoin

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        if self.designation.get_wtotal(span=self.span/12) == 0.0:
            raise ValueError(f'Joist span exceeds allowable span for {self.designation.name}')
        else: self.w_total = self.designation.get_wtotal(span=self.span/12)

    def get_moment_capacity(self):
        '''
        Calculates the ASD moment capacity for the steel joist under consideration
        using the total safe load from SJI load tables for the given span.

        Parameters
        ----------
        None

        Returns
        -------
        moment_capacity : float
            the moment capacity for the steel joist under consideration using
            the total safe load from SJI load tables for the given span
        '''
        return (self.w_total*(self.span/12)**2)/8/1000
    
    def get_shear_capacity(self):
        '''
        Calculates the ASD minimum and maximum shear capacity for the steel joist
        under consideration using the total safe load from SJI load tables for 
        the given span.

        Parameters
        ----------
        None

        Returns
        -------
        shear_capacity : tuple
            the (minimum, maximum) shear capacity for the steel joist
            under consideration using the total safe load from SJI load tables
            for the given span
        '''
        if 'KCS' in self.designation.name:
            max_shear = self.designation.shear_capacity/1000
            min_shear = self.designation.shear_capacity/1000
        else:
            max_shear = self.w_total*(self.span/12)/2/1000
            min_shear = 0.25*max_shear

        return (min_shear, max_shear)
    
    def get_shear_plot_points(self):
        '''
        Calculates the shear capacity at critical points along the span of
        the joist under consideration for use in plotting the shear capacity
        envelope.

        Parameters
        ----------
        None

        Returns
        -------
        shear_plot_points : numpy.ndarray
            numpy array containing points along the span and shear capacity
            at those points
        '''
        _, max_shear = self.get_shear_capacity()

        if 'KCS' in self.designation.name:
            distance = np.array([0, 0, 1, 1, 0, 0])
            shear_value = np.array([0, 1, 1, -1, -1, 0])
        else:
            distance = np.array([0, 3 / 8, 1 / 2 - 0.01, 1 / 2 + 0.01, 5 / 8, 1])

            shear_value = np.piecewise(
                distance,
                [
                    distance <= 3/8,
                    (3/8 < distance) & (distance <=1/2),
                    (1/2 < distance) & (distance <= 5/8),
                    5/8 < distance,
                ],
                [
                    lambda distance: (distance-3/8)/(0-3/8)*(1-0.25)+0.25,
                    0.25,
                    -0.25,
                    lambda distance: (distance-5/8)/(1-5/8)*(-1+0.25)-0.25,
                ],
            )

        return np.array([distance, shear_value*max_shear])

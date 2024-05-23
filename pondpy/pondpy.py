import pdb

from joistpy import sji
from scipy import integrate
from steelpy import aisc

from analysis.fem_analysis import (
    SteelBeamSize,
    SteelJoistSize,
)

from analysis.pond_analysis import (
    Loading,
    PrimaryFraming,
    PrimaryMember,
    RoofBay,
    RoofBayModel,
    SecondaryFraming,
    SecondaryMember,
)

class PondPyModel:
    '''
    A class to represent a pondpy analysis object.

    ...

    Attributes
    ----------
    loading : loading
        Loading object representing the loading criteria for the roof bay
    max_iter : int
        maximum number of iterations for the iterative analysis
    mirrored_left : bool
        indicates whether the roof bay is mirrored on the left
    mirrored_right : bool
        indicates whether the roof bay is mirrored on the right
    roof_bay : roofbay
        roof bay model to used to create the roof bay model
    roof_bay_model : roofbaymodel
        roof bay model object to be used for the iterative analysis
    primary_framing : list
        list of PrimaryFraming objects representing the primary framing for the roof bay
    secondary_framing : list
        list of SecondaryFraming objects representing the secondary framing for the roof bay
    stop_criterion : float
        criterion to stop the iterative analysis

    Methods
    -------
    _create_roof_bay_model():
        Creates the roof bay model to be used in the iterative analysis.
    '''
    def __init__(self, primary_framing, secondary_framing, loading, mirrored_left=False, mirrored_right=False, stop_criterion=0.01, max_iter=20):
        '''
        Constructs the required input attributes for the PondPy object.

        Parameters
        ----------
        loading : loading
            Loading object representing the loading criteria for the roof bay
        max_iter : int, optional
            maximum number of iterations for the iterative analysis
        mirrored_left : bool, optional
            indicates whether the roof bay is mirrored on the left
        mirrored_right : bool, optional
            indicates whether the roof bay is mirrored on the right
        roof_bay : roofbay
            roof bay model to used to create the roof bay model
        roof_bay_model : roofbaymodel
            roof bay model object to be used for the iterative analysis
        primary_framing : list
            list of PrimaryFraming objects representing the primary framing for the roof bay
        secondary_framing : list
            list of SecondaryFraming objects representing the secondary framing for the roof bay
        stop_criterion : float, optional
            criterion to stop the iterative analysis
        '''
        self.loading = loading
        self.max_iter = max_iter
        self.mirrored_left = mirrored_left
        self.mirrored_right = mirrored_right
        self.primary_framing = primary_framing
        self.secondary_framing = secondary_framing
        self.stop_criterion = stop_criterion

        self._create_roof_bay_model()  

    def _calculate_impounded_weight(self, impounded_depth):
        '''
        Calculates the weight of the impounded water on the roof bay.

        Parameters
        ----------
        impounded_depth : dict
            dictionary containing impounded water depth at model nodes for both primary and secondary members

        Returns
        -------
        impounded_weight : float
            weight of impounded water on roof bay in kips
        '''
        impounded_area = []
        for i_smodel, s_model in enumerate(self.roof_bay_model.secondary_models):
            s_nodes = s_model.model_nodes
            depth_at_node = impounded_depth['Secondary'][i_smodel]

            cur_impounded_area = integrate.simpson(y=depth_at_node, x=s_nodes)
            
            impounded_area.append(cur_impounded_area) # in^2

        p_nodes = [self.roof_bay.secondary_spacing*i_smodel for i_smodel in range(len(self.roof_bay_model.secondary_models))]

        impounded_volume = integrate.simpson(y=impounded_area, x=p_nodes) # in^3
        impounded_weight = ((impounded_volume/(12**3))*62.4)/1000

        return impounded_weight

    def _create_roof_bay_model(self):
        '''
        Creates the roof bay model to be used in the iterative analysis.

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        self.roof_bay = RoofBay(self.primary_framing, self.secondary_framing, self.loading, self.mirrored_left, self.mirrored_right)
        self.roof_bay_model = RoofBayModel(self.roof_bay)

# Define sizes for primary and secondary members
w16x26 = SteelBeamSize('W16X26', aisc.W_shapes.W16X26)
k_12k1 = SteelJoistSize('12K1', sji.K_Series.K_12K1)

# Define loading for the roof bay
loading = Loading(20/1000/144, 22/1000/144, include_sw=True)

# Define the primary and secondary framing
framing_p = [PrimaryMember(20*12, w16x26, [[0,(1,1,0)],[20*12,(1,1,0)]], ploads=[], dloads=[]) for _ in range(2)]
framing_s = [SecondaryMember(20*12, k_12k1, [[0,(1,1,0)],[20*12,(1,1,0)]], ploads=[], dloads=[]) for _ in range(5)]
primary_framing = PrimaryFraming(framing_p)
secondary_framing = SecondaryFraming(framing_s)

model = PondPyModel(primary_framing, secondary_framing, loading)

pdb.set_trace()

from joistpy import sji
from scipy import integrate
from steelpy import aisc
import time
import pdb

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
    impounded_depth : dict
        dictionary containing impounded water depth at model nodes for both primary and secondary members
    loading : loading object
        Loading object representing the loading criteria for the roof bay
    max_iter : int
        maximum number of iterations for the iterative analysis
    mirrored_left : bool
        indicates whether the roof bay is mirrored on the left
    mirrored_right : bool
        indicates whether the roof bay is mirrored on the right
    roof_bay : roof bay object
        roof bay model to used to create the roof bay model
    roof_bay_model : roof bay model object
        roof bay model object to be used for the iterative analysis
    primary_framing : primary framing object
        primary framing object representing the primary framing for the roof bay
    secondary_framing : secondary framing object
        secondsry framing object representing the secondary framing for the roof bay
    show_results : bool
        indicates whether or not to print the results to the console
    stop_criterion : float
        criterion to stop the iterative analysis

    Methods
    -------
    perform_analysis():
        Performs the iterative analysis of the PondPy object.
    '''
    def __init__(self, primary_framing, secondary_framing, loading, mirrored_left=False, mirrored_right=False, stop_criterion=0.0001, max_iter=50, show_results=True):
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
        show_results : bool, optional
            indicates whether or not to print the results to the console
        stop_criterion : float, optional
            criterion to stop the iterative analysis
        '''
        self.loading = loading
        self.max_iter = max_iter
        self.mirrored_left = mirrored_left
        self.mirrored_right = mirrored_right
        self.primary_framing = primary_framing
        self.secondary_framing = secondary_framing
        self.show_results = show_results
        self.stop_criterion = stop_criterion

        self._create_roof_bay_model()
        self.impounded_depth = self.roof_bay_model.initial_impounded_depth

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
    
    def _calculate_next_impounded_depth(self):
        '''
        Calculates the impounded water depth at model nodes for both primary and secondary members for the next iteration

        Parameters
        ----------
        None

        Returns
        -------
        impounded_depth : dict
            dictionary containing impounded water depth at model nodes for both primary and secondary members
        '''
        # First find the deflection at each end of each secondary member
        end_deflections = []
        for i_smodel, _ in enumerate(self.roof_bay_model.secondary_models):
            cur_deflections = []
            for p_model in self.roof_bay_model.primary_models:
                node = p_model.model_nodes.index(self.roof_bay_model.roof_bay.secondary_spacing*i_smodel)
                g_dof = p_model.dof_num[node][1]
                if g_dof != 0:
                    defl = p_model.global_displacement[g_dof-1][0]
                elif g_dof == 0:
                    defl = 0.0
                
                cur_deflections.append(defl)

            end_deflections.append(cur_deflections)

        # Next calculate the height of node j relative to node i for each secondary member, including deflection
        # Then store the straight-line slope for each member
        ini_slope = self.roof_bay.secondary_framing.slope/12
        defl_slope = []
        for i_smodel, s_model in enumerate(self.roof_bay_model.secondary_models):
            height_i = end_deflections[i_smodel][0]
            height_j = s_model.beam.length*ini_slope + end_deflections[i_smodel][1]

            rel_h = height_j - height_i

            defl_slope.append(rel_h/s_model.beam.length) # Store the straight-line slope in in/in

        # Next calculate the length of ponding for each secondary member
        ponding_length = []
        ponding_depth_i = []
        for i_smodel in range(len(defl_slope)):
            ini_depth_i = self.roof_bay_model.initial_impounded_depth['Secondary'][i_smodel][0]
            depth_i = ini_depth_i - end_deflections[i_smodel][0]

            ponding_length.append(depth_i/defl_slope[i_smodel])
            ponding_depth_i.append(depth_i)

        # Next determine the depth of water considering the straight-line depth and deflection
        # at each node for each secondary member.
        impounded_depth_s = {}
        for i_smodel, s_model in enumerate(self.roof_bay_model.secondary_models):
            cur_nodes = s_model.model_nodes
            cur_disp = []
            for i_node in range(len(s_model.model_nodes)):
                G_dof = s_model.dof_num[i_node][1]
                if G_dof != 0:
                    cur_disp.append(s_model.global_displacement[G_dof-1][0])
                else:
                    cur_disp.append(0.0)

            nodal_depth = []
            for i_node, node in enumerate(cur_nodes):
                if node <= ponding_length[i_smodel]:
                    cur_depth = (ponding_depth_i[i_smodel] - defl_slope[i_smodel]*node) - cur_disp[i_node]
                elif node > ponding_length[i_smodel]:
                    cur_depth = 0.0

                nodal_depth.append(cur_depth)

            impounded_depth_s[i_smodel] = nodal_depth

        # Next determine the depth of water considering the straight-line depth and deflection
        # at each node for each primary member.
        # Note: Impounded depth for the primary members is not required for analysis. All rain
        # loads are assumed to be transferred to the primary members by the secondary members.
        impounded_depth_p = {}
        for i_pmodel, p_model in enumerate(self.roof_bay_model.primary_models):
            cur_disp = []
            for i_node in range(len(p_model.model_nodes)):
                G_dof = p_model.dof_num[i_node][1]
                if G_dof != 0:
                    cur_disp.append(p_model.global_displacement[G_dof-1][0])
                else:
                    cur_disp.append(0.0)

            nodal_depth = []
            if i_pmodel == 0:
                for i_node, node in enumerate(p_model.model_nodes):
                    cur_depth = self.roof_bay_model.initial_impounded_depth['Primary'][i_pmodel][i_node] - cur_disp[i_node]
                    nodal_depth.append(cur_depth)
                        
            impounded_depth_p[i_pmodel] = nodal_depth

        impounded_depth = {
            'Primary':impounded_depth_p,
            'Secondary':impounded_depth_s,
        }           

        return impounded_depth

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

    def perform_analysis(self):
        '''
        Performs the iterative analysis of the PondPy object.

        Parameters
        ----------
        None

        Returns
        -------
        output : dict
            dictionary of output variables
            Keys
            ----
            Iterations --> iterations : int
                number of iterations run
            Time --> time_elapsed : float
                amount of time the analysis took to run in seconds
            Weight --> impounded_weight : list
                list of impounded weight for each iteration
        '''
        iteration = 0
        impounded_weight = []
        out_str = 'Iteration\t|\tWater Weight (k)\t|\tDifference\n'
        start = time.time()
        while True:
            rain_load = self.roof_bay_model._get_secondary_rl(self.impounded_depth)
            self.roof_bay_model.analyze_roof_bay(rain_load=rain_load)
            cur_impounded_weight = self._calculate_impounded_weight(self.impounded_depth)
            impounded_weight.append(cur_impounded_weight)

            if iteration > 0:
                diff = (impounded_weight[iteration] - impounded_weight[iteration-1])/impounded_weight[iteration-1]
                out_str += f'{iteration}\t\t|\t{round(cur_impounded_weight,2)}\t\t\t|\t{round(diff,5)}\n'
            else:
                diff = 1
                out_str += f'{iteration}\t\t|\t{round(cur_impounded_weight,2)}\t\t\t|\t----\n'

            if diff <= self.stop_criterion or iteration >= self.max_iter:
                end = time.time()
                time_elapsed = end - start
                out_str += f'Analysis finished in {round(time_elapsed, 2)} s.'
                if self.show_results:
                    print(out_str)

                output = {
                    'Weight':impounded_weight,
                    'Iterations':iteration,
                    'Time':time_elapsed,
                }

                return output
            
            self.impounded_depth = self._calculate_next_impounded_depth()
            iteration += 1

# Define sizes for primary and secondary members
w16x26 = SteelBeamSize('W16X26', aisc.W_shapes.W16X26)
k_14k1 = SteelJoistSize('14K1', sji.K_Series.K_14K1)

# Define loading for the roof bay
loading = Loading(20/1000/144, 22/1000/144, include_sw=True)

# Define the primary and secondary framing
framing_p = [PrimaryMember(20*12, w16x26, [[0,(1,1,0)],[20*12,(1,1,0)]], ploads=[], dloads=[]) for _ in range(2)]
framing_s = [SecondaryMember(20*12, k_14k1, [[0,(1,1,0)],[20*12,(1,1,0)]], ploads=[], dloads=[]) for _ in range(5)]
primary_framing = PrimaryFraming(framing_p)
secondary_framing = SecondaryFraming(framing_s)

model = PondPyModel(primary_framing, secondary_framing, loading)
x = model.perform_analysis()

pdb.set_trace()

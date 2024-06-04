from scipy import integrate
import time

from pondpy import (
    AnalysisError,
    Loading,
    PrimaryFraming,
    ReportBuilder,
    RoofBay,
    RoofBayModel,
    SecondaryFraming,
)

class PondPyModel:
    '''
    A class to represent a pondpy analysis object.

    ...

    Attributes
    ----------
    analysis_complete : bool
        bool indicating whether the analysis has been performed
    impounded_depth : dict
        dictionary containing impounded water depth at model nodes for both primary and secondary members
    iter_results : dict
        dictionary holding iterative analysis results
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
    generate_report():
        Generates a report for the analyzed PondPyModel object.
    perform_analysis():
        Performs the iterative analysis of the PondPyModel object.
    '''
    def __init__(self, primary_framing, secondary_framing, loading, mirrored_left=False, mirrored_right=False, stop_criterion=0.001, max_iter=50, show_results=True):
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
        if not isinstance(loading, Loading):
            raise TypeError('loaidng must be a valid Loading object')
        if not isinstance(max_iter, int) or max_iter <= 0:
            raise TypeError('max_iter must be a positive integer')
        if not isinstance(mirrored_left, bool):
            raise TypeError('mirrored_left must be either True or False')
        if not isinstance(mirrored_right, bool):
            raise TypeError('mirrored_right must be either True or False')
        if not isinstance(primary_framing, PrimaryFraming):
            raise TypeError('primary_framing must be a valid PrimaryFraming object')
        if not isinstance(secondary_framing, SecondaryFraming):
            raise TypeError('secondary_framing must be a valid SecondaryFraming object')
        if not isinstance(show_results, bool):
            raise TypeError('show_results must be either True or False')
        if not isinstance(stop_criterion, float) or stop_criterion <= 0:
            raise TypeError('stop_criterion must be a positive float')

        self.analysis_complete = False
        self.iter_results = {}
        self.loading = loading
        self.max_iter = max_iter
        self.mirrored_left = mirrored_left
        self.mirrored_right = mirrored_right
        self.primary_framing = primary_framing
        self.secondary_framing = secondary_framing
        self.show_results = show_results
        self.stop_criterion = stop_criterion

        self._create_roof_bay_model()
        self.impounded_depth = self.roof_bay_model._initial_impounded_water_depth()

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
        '''impounded_depth_p = {}
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
                        
            impounded_depth_p[i_pmodel] = nodal_depth'''

        impounded_depth = {
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

    def generate_report(self, output_folder, filename='pondpy_results', filetype='html', company='', proj_num='', proj_name='', desc=''):
        '''
        Generates a report for the analyzed PondPyModel object.

        Parameters
        ----------
        company : str, optional
            string representing the company name
        desc : str, optional
            string representing the calculation description
        filename : str, optional
            string represengting the output filename
        filetype : str, optional
            string representing the desired output file type
        output_folder : str
            string representing the location to which the report should be saved
        proj_name : str, optional
            string representing the project name
        proj_num : str, optional
            string representing the project number

        Returns
        -------
        None
        '''
        if not self.analysis_complete:
            raise AnalysisError('Analysis must be performed before a report can be generated.')
        
        report_builder = ReportBuilder(
            output_folder=output_folder,
            filename=filename,
            filetype=filetype,
        )

        context = {
            'company':company,
            'desc':desc,
            'project_info':proj_num+'-'+proj_name,
            'favicon_path':report_builder.favicon_path,
            'generated_at':report_builder.generated_at,
            'logo_path':report_builder.logo_path,
            'version_no':report_builder.version_no,
            'dead_load':round(self.loading.dead_load*144*1000, 1),
            'initial_rain_depth':round(self.loading.dead_load*144*1000/5.2, 2),
            'model': self,
            'num_iter':self.iter_results['Iterations'],
            'num_p':len(self.roof_bay_model.primary_models),
            'num_s':len(self.roof_bay_model.secondary_models),
            'rain_load':round(self.loading.rain_load*144*1000, 1),
            'w_water':round(self.iter_results['Weight'][-1], 2),
        }

        report_builder.save_report(context=context)

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

                self.analysis_complete = True
                self.iter_results = output

                return output
            
            self.impounded_depth = self._calculate_next_impounded_depth()
            iteration += 1

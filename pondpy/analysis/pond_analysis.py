from pondpy import (
    AnalysisError,
    Beam,
    BeamModel,
    DistLoad,
    PointLoad,
)

CONV_D_TO_Q = 62.4/(12**3)/1000 # Constant to convert water depth in inches to rain load in k/in^2

class Loading:
    '''
    A class to represent the loading criteria for a roof bay.

    ...

    Attributes
    ----------
    dead_load : float
        magnitude of the dead load on the roof in k/in^2
    rain_load : float
        magnitude of the rain load on the roof in k/in^2
    include_sw : bool
        indicates whether to conside member self-weight in the analysis
    '''
    def __init__(self, dead_load, rain_load, include_sw = True):
        '''
        Constructs all the necessary attributes for the loading object.

        Parameters
        ----------
        dead_load : float
            magnitude of the dead load on the roof in k/in^2
        rain_load : float
            magnitude of the rain load on the roof in k/in^2
        include_sw : bool, optional
            indicates whether to conside member self-weight in the analysis
        '''
        if not isinstance(dead_load, (int, float)):
            raise TypeError('dead_load must be either int or float')
        if not isinstance(rain_load, (int, float)):
            raise TypeError('rain_load must be either int or float')
        if not isinstance(include_sw, bool):
            raise TypeError('include_sw must be either True or False')
        
        self.dead_load = dead_load # Units: k/in^2
        self.rain_load = rain_load # Units: k/in^2
        self.include_sw = include_sw

class PrimaryMember(Beam):
    '''
    A class representing a primary member in the roof bay.

    Attributes
    ----------
    dloads : list
        list of dist load objects
    length : float
        length of the beam
    size : steel beam size object
        steel beam size object for the beam
    supports : list
        list of tuples indicating location and type of beam supports
    ploads : list
        list of point load objects
    '''
    pass

class PrimaryFraming:
    '''
    A class representing the primary members in the framing system in the roof bay.

    ...

    Attributes
    ----------
    primary_members : list
        list of all primary members in the framing system
    '''
    def __init__(self, primary_members):
        '''
        Constructs all the necessary attributes for the primary framing object.

        Parameters
        ----------
        primary_members : list
            list of all primary members in the primary framing system
        '''
        if not isinstance(primary_members, list) or not all(isinstance(item, (PrimaryMember)) for item in primary_members):
            raise TypeError('primary_members must be a list of valid PrimaryMember objects')
        
        self.primary_members = primary_members

    def __str__(self):
        '''
        Prints the size of each primary framing member in the framing system.
        '''
        return f'Primary framing members: {[member.size.name for member in self.primary_members]}'

class RoofBay:
    '''
    A model representing the roof bay to be analyzed.

    ...

    Attributes
    ----------
    loading : loading
        loading object representing the loading criteria for the roof bay
    mirrored_left : bool
        indicates whether the roof bay is mirrored on the left
    mirrored_right : bool
        indicates whether the roof bay is mirrored on the right
    primary_framing : primary framing
        primary framing object for the roof bay
    primary_sw : dict
        dictionary containing distload objects for each primary member self-weight
    secondary_dl : dict
        dictionary containing distload objects for each secondary member dead load, including self-weight
    secondary_framing : secondary framing
        secondary framing object for the roof bay
    secondary_spacing : float
        spacing between secondary members along the length of the primary members
    secondary_tribw : list
        list containing tributary width for each secondary framing member
    '''
    def __init__(self, primary_framing, secondary_framing, loading, mirrored_left=False, mirrored_right=False):
        '''
        Constructs all the necessary attributes for the roof bay object.

        Parameters
        ----------
        loading : loading
            loading object representing the loading criteria for the roof bay
        mirrored_left : bool, optional
            indicates whether the roof bay is mirrored on the left
        mirrored_right : bool, optional
            indicates whether the roof bay is mirrored on the right
        primary_framing : primary framing
            primary framing object for the roof bay
        secondary_framing : secondary framing
            secondary framing object for the roof bay
        '''
        if not isinstance(loading, Loading):
            raise TypeError('loading must be a valid Loading object')
        if not isinstance(primary_framing, PrimaryFraming):
            raise TypeError('primary_framing must be a valid PrimaryFraming object')
        if not isinstance(secondary_framing, SecondaryFraming):
            raise TypeError('secondary_framing must be a valid SecondaryFraming object')
        if not isinstance(mirrored_left, bool):
            raise TypeError('mirrored_left must be either True or False')
        if not isinstance(mirrored_right, bool):
            raise TypeError('mirrored_right must be either True or False')

        self.primary_framing = primary_framing
        self.secondary_framing = secondary_framing
        self.loading = loading
        self.mirrored_left = mirrored_left
        self.mirrored_right = mirrored_right

        self._get_secondary_spacing()
        self._get_secondary_dl()
        self._get_primary_sw()

    def _get_primary_sw(self):
        '''
        Calculates the self-weight (if enabled) of each primary member.

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        primary_sw = {}

        for idx, member in enumerate(self.primary_framing.primary_members):
            x_i_sw = 0
            x_j_sw = member.length

            # Calculate self-weight, if enabled
            if self.loading.include_sw:
                sw = member.size.properties.weight/1000/12 # Convert lb/ft to kip/in
            else:
                sw = 0
            
            # Place load into dictionary
            if idx not in primary_sw.keys():
                primary_sw[idx] = []

            primary_sw[idx].append(DistLoad(location=(x_i_sw, x_j_sw), magnitude=((0, 0), (-sw, -sw), (0, 0))))

        self.primary_sw = primary_sw   

    def _get_secondary_dl(self):
        '''
        Calculates the dead load (including the member self-weight, if enabled) acting on each secondary framing member.

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        # Initialize dictionary to hold load values
        secondary_dl = {}

        # Calculate tributary width for each member
        trib_w = [self.secondary_spacing for _ in range(len(self.secondary_framing.secondary_members))]

        # Reduce tributary width for end members if roof bay is not mirrored on each side
        if not self.mirrored_left:
            trib_w[0] = trib_w[0]/2
        if not self.mirrored_right:
            trib_w[-1] = trib_w[-1]/2
        
        q_dl = self.loading.dead_load
        x_i_dl = 0
        
        for idx, member in enumerate(self.secondary_framing.secondary_members):
            # Calculate distributed dead load for each member
            w_dl = q_dl*trib_w[idx] # Units: k/in
            x_j_dl = member.length

            if idx not in secondary_dl.keys():
                secondary_dl[idx] = []

            # Calculate self-weight, if enabled
            if self.loading.include_sw:
                sw = member.size.properties.weight/1000/12 # Convert lb/ft to kip/in
            else:
                sw = 0

            # Place load into dictionary
            secondary_dl[idx].append(DistLoad(location=(x_i_dl, x_j_dl), magnitude=((0, 0), (-(w_dl+sw), -(w_dl+sw)), (0, 0))))

        self.secondary_dl = secondary_dl
        self.secondary_tribw = trib_w

    def _get_secondary_spacing(self):
        '''
        Calculates the secondary member spacing, assuming all members are evenly spaced.

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        primary_length = self.primary_framing.primary_members[0].length
        n_secondary = len(self.secondary_framing.secondary_members)

        secondary_spacing = primary_length/(n_secondary-1)

        self.secondary_spacing = secondary_spacing       

class RoofBayModel:
    '''
    A class representing the roof bay model object.

    ...

    Attributes
    ----------
    analysis_complete : bool
        bool indicating whether the analysis has been successfully performed
    analysis_ready : bool
        bool indicating whether the analysis has been initialized and is ready to be performed
    initial_impounded_depth : dict
        dictionary containing initial impounded water depth in inches for each primary and secondary member
    max_node_spacing : int or float
        maximum node spacing along length of beam model objects in inches
    primary_models : list
        list of beam model objects for the primary framing members
    roof_bay : roof bay
        roof bay object
    secondary_models : list
        list of beam model objects for the secondary framing members

    Methods
    -------
    analyze_roof_bay(rain_load):
        Analyzes the roof bay for the dead load and the input rain loads.
    generate_plots():
        Generates the deflected shape, shear force diagram, and bending moment diagram plots for each primary and secondary member.
    initialize_analysis():
        Prepares the model for analysis. To be called at instantiation and when the user specifies.
    '''

    def __init__(self, roof_bay, max_node_spacing = 6):
        '''
        Constructs all the necessary attributes for the roof bay object.

        Parameters
        ----------
        max_node_spacing : int or float, optional
            maximum node spacing along length of beam model objects in inches
        roof_bay : roof bay
            roof bay object
        '''
        if not isinstance(roof_bay, RoofBay):
            raise TypeError('roof_bay must be a valid RoofBay object')
        if not isinstance(max_node_spacing, (int, float)):
            raise TypeError('max_node_spacing must be int or float')

        self.analysis_complete = False
        self.analysis_ready = False
        self.roof_bay = roof_bay
        self.max_node_spacing = max_node_spacing

        self.initialize_analysis()

    def _apply_primary_loads(self):
        '''
        Applies the support reactions from each SecondaryMember object in the RoofBayModel object
        to the PrimaryMember objects. SecondaryMember analysis must be performed before calling 
        this method.
        '''
        s_spacing = self.roof_bay.secondary_spacing
        for i_pmodel, p_model in enumerate(self.primary_models):
            ploads = []
            for i_smodel, s_model in enumerate(self.secondary_models):
                sup_reactions = [s_model.support_reactions[node] for node in s_model.support_nodes]
                x_load = s_spacing*i_smodel

                reaction = tuple(-1*sup_reactions[i_pmodel])
                cur_pload = [PointLoad(x_load, reaction)]
                ploads.extend(cur_pload)

                p_model.add_beam_pload(ploads, add_type='replace')
            
    def _apply_secondary_loads(self, rain_load):
        '''
        Applies the dead and rain loading to each SecondaryMember object in the RoofBayModel object.

        Parameters
        ----------
        rain_load : list
            list of dist load objects representing the rain load on the roof bay
        '''
        for i_smodel, s_model in enumerate(self.secondary_models):
            dloads = []
            # Retrieve the dead load from secondary_dl dictionary
            s_dl = [self.roof_bay.secondary_dl[i_smodel][0]]
            dloads.extend(s_dl)

            # Retrieve the rain loads from input rain_load list
            s_rl = rain_load[i_smodel]
            dloads.extend(s_rl)

            s_model.add_beam_dload(dloads, add_type='replace')
        
    def _create_primary_models(self):
        '''
        Creates BeamModels for each primary member in the roof bay, adds the primary member self-weight (if enabled)
        to the PrimaryMember object's dloads attribute, and initializes the BeamModels for analysis.

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        primary_models = []
        for idx, p_mem in enumerate(self.roof_bay.primary_framing.primary_members):
            cur_model = BeamModel(p_mem, max_node_spacing=self.max_node_spacing, ini_analysis=True)

            # Retrieve self-weight from primary_sw dictionary
            p_sw = self.roof_bay.primary_sw[idx]
            # Add self-weight to the model
            cur_model.add_beam_dload(p_sw)

            primary_models.append(cur_model)

        self.primary_models = primary_models

    def _create_secondary_models(self):
        '''
        Creates BeamModels for each secondary member in the roof bay, adds the secondary member dead load to the
        SecondaryMember object's dloads attribute, and initializes the BeamModels for analysis.

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        secondary_models = []
        for idx, s_mem in enumerate(self.roof_bay.secondary_framing.secondary_members):
            cur_model = BeamModel(s_mem, max_node_spacing=self.max_node_spacing, ini_analysis=True)

            # Retrieve dead load from secondary_dl dictionary
            s_dl = self.roof_bay.secondary_dl[idx]
            # Add the dead load to the model
            cur_model.add_beam_dload(s_dl)

            secondary_models.append(cur_model)

        self.secondary_models = secondary_models

    def _get_secondary_rl(self, impounded_depth):
        '''
        Calculates the rain load at each node along the length of each secondary member based on the impounded
        water depth at each node and the trib width for each member.

        Parameters
        ----------
        impounded_depth : dict
            dictionary containing impounded water depth in inches for each primary and secondary member

        Returns
        -------
        None
        '''
        trib_w = self.roof_bay.secondary_tribw

        secondary_rl = {}
        for i_member, member in enumerate(self.secondary_models):
            member_rl = []
            cur_tribw = trib_w[i_member] # inches
            # Calculate distributed rain load for each member
            for i_node, node in enumerate(member.model_nodes[:-1]):
                if i_node < len(member.model_nodes):
                    x_i_rl = node # inches
                    x_j_rl = member.model_nodes[i_node+1] # inches

                    depth_i = impounded_depth['Secondary'][i_member][i_node] # inches
                    depth_j = impounded_depth['Secondary'][i_member][i_node+1] # inches

                    q_rl_i = depth_i*CONV_D_TO_Q # k/in^2
                    q_rl_j = depth_j*CONV_D_TO_Q # k/in^2

                    w_rl_i = q_rl_i*cur_tribw # k/in
                    w_rl_j = q_rl_j*cur_tribw # k/in

                    cur_rl = DistLoad(location=(x_i_rl, x_j_rl), magnitude=((0, 0), (-w_rl_i, -w_rl_j), (0, 0)))

                member_rl.append(cur_rl)

            if i_member not in secondary_rl.keys():
                secondary_rl[i_member] = []

            secondary_rl[i_member].extend(member_rl)

        return secondary_rl

    def _initial_impounded_water_depth(self):
        '''
        Calculates the initial impounded water depth at each node for each primary and secondary member.

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        # Load and calculate required parameters
        q_rl = self.roof_bay.loading.rain_load # Units: k/in^2
        d_impounded_i = q_rl/CONV_D_TO_Q # Depth of impounded water at end i in inches
        roof_slope = self.roof_bay.secondary_framing.slope/12 # Roof slope in in/in
        bay_length = self.roof_bay.secondary_framing.secondary_members[0].length # Length of roof bay in inches
        if roof_slope == 0:
            impounded_length = bay_length
        else:
            impounded_length = d_impounded_i/roof_slope # Length of impounded water along secondary framing in inches
        

        # First deal with the primary members
        impounded_depth_p = {}
        for i_pmodel, p_model in enumerate(self.primary_models):
            if i_pmodel == 0:
                impounded_depth_p[i_pmodel] = [d_impounded_i for _ in range(len(p_model.model_nodes))]
            else:
                if impounded_length <= bay_length:
                    impounded_depth_p[i_pmodel] = [0.0 for _ in range(len(p_model.model_nodes))]
                elif impounded_length > bay_length:
                    impounded_depth_p[1] = [d_impounded_i-roof_slope*bay_length for _ in range(len(p_model.model_nodes))]

        # Next deal with the secondary members
        impounded_depth_s = {}
        for idx, s_model in enumerate(self.secondary_models):
            cur_nodes = s_model.model_nodes
            nodal_depth = []
            for node in cur_nodes:
                if node <= impounded_length:
                    cur_depth = d_impounded_i - roof_slope*node
                elif node > impounded_length:
                    cur_depth = 0.0

                nodal_depth.append(cur_depth)
            
            impounded_depth_s[idx] = nodal_depth

        return {
            'Primary':impounded_depth_p,
            'Secondary':impounded_depth_s,
        }

    def analyze_roof_bay(self, rain_load):
        '''
        Analyzes the roof bay for the dead load and the input rain loads.

        Parameters
        ----------
        rain_load : list
            list of dist load objects representing the rain load on the roof bay

        Returns
        -------
        None
        '''
        # Handle the secondary member analysis first
        # Apply the secondary loads
        self._apply_secondary_loads(rain_load=rain_load)

        # Perform the secondary member analysis
        for s_model in self.secondary_models:
            s_model.perform_analysis()

        # Next handle the primary member analysis
        # Apply the secondary member reactions as point loads to the primary members
        self._apply_primary_loads()

        # Perform the primary member analysis
        for p_model in self.primary_models:
            p_model.perform_analysis()

        self.analysis_complete = True

    def generate_plots(self):
        '''
        Generates the deflected shape, shear force diagram, and bending moment
        diagram plots for each primary and secondary member.

        Parameters
        ----------
        None

        Returns
        -------
        plots : dict
            dictionary of dictionaries of lists containing the deflected shape,
            shear force diagram, and bending moment diagram plots for each
            primary and secondary member
        '''
        if not self.analysis_complete:
            raise AnalysisError('Analysis must be performed prior to generating plots.')
        
        plots = {
            'bmd':{
                'Primary': [],
                'Secondary': [],
            },
            'sfd':{
                'Primary': [],
                'Secondary': [],
            },
            'defl':{
                'Primary': [],
                'Secondary': [],
            },
        }

        # First loop over the primary models
        for p_model in self.primary_models:
            cur_bmd, _ = p_model.plot_bmd(with_design=True)
            cur_sfd, _ = p_model.plot_sfd(with_design=True)
            cur_defl, _ = p_model.plot_deflected_shape()

            plots['bmd']['Primary'].append(cur_bmd)
            plots['sfd']['Primary'].append(cur_sfd)
            plots['defl']['Primary'].append(cur_defl)

        # Next loop over the secondary models
        for s_model in self.secondary_models:
            cur_bmd, _ = s_model.plot_bmd(with_design=True)
            cur_sfd, _ = s_model.plot_sfd(with_design=True)
            cur_defl, _ = s_model.plot_deflected_shape()

            plots['bmd']['Secondary'].append(cur_bmd)
            plots['sfd']['Secondary'].append(cur_sfd)
            plots['defl']['Secondary'].append(cur_defl)

        # Return the plots dict
        return plots

    def initialize_analysis(self):
        '''
        Prepares the model for analysis. To be called at instantiation and 
        when the user specifies.

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        self._create_primary_models()
        self._create_secondary_models()
        self.initial_impounded_depth = self._initial_impounded_water_depth()
        self.initial_secondary_rl = self._get_secondary_rl(impounded_depth=self.initial_impounded_depth)
        self.analysis_ready = True

class SecondaryMember(Beam):
    '''
    A class representing a secondary member in the roof bay.

    Attributes
    ----------
    dloads : list
        list of dist load objects
    length : float
        length of the beam
    size : steel beam size object
        steel beam size object for the beam
    supports : list
        list of tuples indicating location and type of beam supports
    ploads : list
        list of point load objects
    '''
    pass

class SecondaryFraming:
    '''
    A class representing the secondary members in the framing system in the roof bay.

    ...

    Attributes
    ----------
    secondary_members : list
        list of all primary members in the framing system
    slope : float
        slope of the roof bay in in/ft
    '''
    def __init__(self, secondary_members, slope=0.25):
        '''
        Constructs all the necessary attributes for the secondary framing object.

        Parameters
        ----------
        secondary_members : list
            list of all primary members in the framing system
        slope : int or float, optional
            slope of the roof bay in in/ft
        '''
        if not isinstance(secondary_members, list) or not all(isinstance(item, SecondaryMember) for item in secondary_members):
            raise TypeError('secondary_members must be a list of valid SecondaryFraming objects')
        if not isinstance(slope, (int, float)):
            raise TypeError('slope must be int or float')

        self.secondary_members = secondary_members
        self.slope = slope

    def __str__(self):
        '''
        Prints the size of each primary framing member in the framing system.
        '''
        return f'Secondary framing members: {[member.size.name for member in self.secondary_members]}'
    
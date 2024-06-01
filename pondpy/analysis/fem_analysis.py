import joistpy
import math
import matplotlib.pyplot as plt
import numpy as np
import steelpy

beam_section_types = ['AISC']
joist_section_types = ['SJI']

class SteelBeamSize:
    '''
    A class representing a steel beam size.

    ...

    Attributes
    ----------
    e_mod : int or float
        elastic modulus of steel in ksi
    name : str
        name of the steel beam size
    properties : steelpy object
        steelpy object containing properties for the specified steel beam size
    section_type : str
        string indicating the section type of the steel shape
    '''
    def __init__(self, name, properties, e_mod=29000, section_type='AISC'):
        '''
        Constructs all the necessary attributes for the steel beam size object.

        Parameters
        ----------
        e_mod : int or float, optional
            elastic modulus of steel in ksi
        name : str
            name of the steel beam size
        properties : steelpy object
            steelpy object containing properties for the specified steel beam size
        section_type : str, optional
            string indicating the section type of the steel shape
        '''
        if not isinstance(name, str):
            raise TypeError('name must be a string.')
        if not isinstance(properties, steelpy.steelpy.Section):
            raise TypeError('properties must be a valid steelpy Section object.')
        if not isinstance(e_mod, (int, float)):
            raise TypeError('e_mod must be int or float.')
        if not isinstance(section_type, str) or section_type not in beam_section_types:
            raise TypeError(f'section_type must be a string. Options are: AISC.')
        
        self.name = name
        self.properties = properties
        self.e_mod = e_mod
        self.section_type = section_type

    def __str__(self):
        '''
        Prints the name of the steel beam size.
        '''
        return f'{self.name}'
    
class SteelJoistSize:
    '''
    A class that represents a steel joist size.

    ...

    Attributes
    ----------
    e_mod : int or float
        elastic modulus of steel in ksi
    name : str
        name of the steel joist size
    properties : joistpy object
        joistpy object containing properties for the specified steel joist size
    section_type : str
        string indicating the section type of the steel shape
    '''
    def __init__(self, name, properties, e_mod=29000, section_type='SJI'):
        '''
        Constructs all the necessary attributes for the steel beam size object.

        Parameters
        ----------
        e_mod : int or float, optional
            elastic modulus of steel in ksi
        name : str
            name of the steel joist size
        properties : joistpy object
            joistpy object containing properties for the specified steel joist size
        section_type : str, optional
            string indicating the section type of the steel shape
        '''
        if not isinstance(name, str):
            raise TypeError('name must be a string.')
        if not isinstance(properties, joistpy.joistpy.Designation):
            raise TypeError('properties must be a valid joistpy Designation object.')
        if not isinstance(e_mod, (int, float)):
            raise TypeError('e_mod must be int or float.')
        if not isinstance(section_type, str) or section_type not in joist_section_types:
            raise TypeError(f'section_type must be a string. Options are: SJI.')
        
        self.name = name
        self.properties = properties
        self.e_mod = e_mod
        self.section_type = section_type

    def __str__(self):
        '''
        Prints the name of the steel joist size.
        '''
        return f'{self.name}'

class Beam:
    '''
    A class that represents an idealized beam.

    ...

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
    def __init__(self, length, size, supports, ploads=[], dloads=[]):
        '''
        Constructs all the necessary attributes for the beam object.

        Parameters
        ----------
        dloads : list, optional
            list of dist load objects
        length : float
            length of the beam
        size : steel beam size object
            steel beam size object for the beam
        supports : list
            list of tuples indicating location and type of beam supports
        ploads : list, optional
            list of point load objects
        '''
        if not isinstance(length, (int, float)):
            raise TypeError('length must be int of float.')
        if not isinstance(size, (SteelBeamSize, SteelJoistSize)):
            raise TypeError('size must be a valid SteelBeamSize or SteelJoistSize object.')
        if not isinstance(ploads, list):
            raise TypeError('ploads must be a list of DistLoad objects or empty list.')
        if not isinstance(dloads, list):
            raise TypeError('dloads must be a list of PointLoad objects or empty list.')
        if not isinstance(supports, list):
            raise TypeError('supports must be a list of tuples of tuples indicating location and type of support.')
        
        if size.section_type == 'SJI' and size.properties.get_wl360(span=length/12) == 0.0:
            raise ValueError(f'Joist span exceeds allowable span for {size.name}.')
        
        self.length = length
        self.size = size
        self.ploads = ploads
        self.dloads = dloads
        self.supports = supports

        self.e_mod = size.e_mod
        if size.section_type == 'SJI':
            self.mom_inertia = size.properties.get_mom_inertia(span=length/12)
            self.area = (size.properties.weight/490)*144
        elif size.section_type == 'AISC':
            self.mom_inertia = size.properties.Ix
            self.area = size.properties.area

class BeamModel:
    '''
    A class representing the analytical model of an idealized beam

    ...

    Parameters
    ----------
    beam : beam object
        beam object to be analyzed
    dof_num : list
        list of lists representing the degrees of freedom for each node in the model
    elem_dload : list
        list of lists representing the distributed load acting on each element in the model
    elem_loads : list
        list of lists representing the fixed end forces in each direction at each end of each element
    elem_nodes : list
        list of lists representing the node number at each end of each element in the model
    element_forces : numpy array
        numpy array representing the forces at each end of each element
        * analysis must be performed to access this attribute
    fef_load_vector : numpy array
        numpy array represengting the fixed end forces calculated from the dist loads at each node in the model
    global_displacement : numpy array
        numpy array representing the global displacement at each global degree of freedom
    global_stiffness_matrix : numpy array
        numpy array representing the global stiffness matrix for the model
    ini_analysis : bool
        indicates whether or not to initialize analysis upon instantiation
    local_stiffness_matrices : list
        list of numpy arrays representing the local stiffness matrix for each element in the model
    max_node_spacing : float
        maximum node spacing along the length of the beam model
    model_nodes : list
        list of locations of the nodes along the length of the beam model
    n_dof : int
        number of degrees of freedom in the model
    nodal_load_vector : numpy array
        numpy array containing the applied nodal loads at each node in the model
    node_elem_fef : list
        list of lists representing the fixed end forces at each node in the model
    node_pload : list
        list of lists representing the point loads at each node in the model
    node_support : list
        list of lists representing the support type at each node in the model
    points_of_interest : list
        list representing points of interest along the length of the beam for use in creating nodes
    support_nodes : list
        list containing the node number of all support nodes in the model
    support_reactions : numpy array
        numpy array representing the support reaction at each node in the model
        * analysis must be performed to access this attribute

    Methods
    -------
    add_beam_dload(dload, add_type='add')
        Adds a distributed load to the Beam object referenced by the BeamModel object.
    add_beam_pload(pload, add_type='add')
        Adds a point load to the Beam object referenced by the BeamModel object.
    initialize_analysis():
        Prepares the model for analysis. To be called at instantiation and when the user specifies.
    perform_analysis():
        Computes the displacement vector, element force matrix, and support reaction vector.
    plot_bmd():
        Plots the bending moment diagram of the analyzed beam.
    plot_deflected_shape():
        Plots the deflected shape of the analyzed beam.
    plot_sfd():
        Plots the shear force diagram of the analyzed beam.
    '''
    def __init__(self, beam, max_node_spacing=6, ini_analysis=True):
        '''
        Constructs all the necessary attributes for the beam model object.

        Parameters
        ----------
        beam : beam object
            beam object to be analyzed
        ini_analysis : bool, optional
            indicates whether or not to initialize analysis upon instantiation
        max_node_spacing : float, optional
            maximum node spacing along the length of the beam model
        '''
        self.beam = beam
        self.max_node_spacing = max_node_spacing

        if ini_analysis:
            self.initialize_analysis()
            self.element_forces = np.zeros((len(self.elem_nodes), 6))
            self.support_reactions = np.zeros((len(self.model_nodes), 3))

    def _assemble_global_stiffness(self):
        '''
        Assembles the global stiffness matrix for the model.

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        # Initialize numpy matrix with n_dof x n_dof dimensions
        local_stiffness_matrices = []
        S = np.zeros((self.n_dof, self.n_dof))

        # Loop over all model elements
        for i_elem in range(len(self.elem_nodes)):
            # Get the local element stiffness matrix, K
            node_i = self.elem_nodes[i_elem][0]
            node_j = self.elem_nodes[i_elem][1]
            L = self.model_nodes[node_i] - self.model_nodes[node_j]
            E = self.beam.e_mod
            A = self.beam.area
            I = self.beam.mom_inertia

            K = np.zeros((6, 6))
            K[0][0] = (E*A)/L
            K[0][3] = -K[1][1]
            K[1][1] = (12*E*I)/(L**3)
            K[1][2] = (6*E*I)/(L**2)
            K[1][4] = -K[1][1]
            K[1][5] = K[1][2]
            K[2][2] = (4*E*I)/(L)
            K[2][4] = -K[1][2]
            K[2][5] = 0.5*K[2][2]
            K[3][3] = K[0][0]
            K[4][4] = K[1][1]
            K[4][5] = -K[1][2]
            K[5][5] = K[2][2]

            for i_row in range(6):
                for i_col in range(i_row+1, 6):
                    K[i_col][i_row] = K[i_row][i_col]

            local_stiffness_matrices.append(K)

            l_dof1 = -1
            #Fill in the upper triangle terms of [K] into [S]
            for i_node1 in range(2):
                # Get end node number for element #i_elem
                node_num1 = self.elem_nodes[i_elem][i_node1]
                for i_dof1 in range(3):
                    l_dof2 = l_dof1
                    l_dof1 += 1
                    G_dof1 = self.dof_num[node_num1][i_dof1]
                    for i_node2 in range(i_node1, 2):
                        node_num2 = self.elem_nodes[i_elem][i_node2]
                        B_dof2 = 0
                        if i_node2 == i_node1:
                            B_dof2 = i_dof1
                        for i_dof2 in range(B_dof2, 3):
                            l_dof2 += 1
                            G_dof2 = self.dof_num[node_num2][i_dof2]
                            if G_dof1 != 0 and G_dof2 != 0:
                                S[G_dof1-1][G_dof2-1] += K[l_dof1][l_dof2]

            # Fill in symmetric terms
            for i_row in range(self.n_dof):
                for i_col in range(i_row+1, self.n_dof):
                    S[i_col][i_row] = S[i_row][i_col]

        self.global_stiffness = S
        self.local_stiffness_matrices = local_stiffness_matrices

    def _create_model_nodes_and_elems(self):
        '''
        Defines the model nodes based on the points of interest
        and maximum node spacing defined by the user.

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        model_segments = []
        for idx, poi in enumerate(self.points_of_interest[:-1]):
            segment = (self.points_of_interest[idx], self.points_of_interest[idx+1])

            model_segments.append(segment)

        nodes = []
        for pair in model_segments:
            # Determine number of sub-segments
            n_sub = math.ceil((pair[1]-pair[0])/self.max_node_spacing)
            # Subdivide segments and add the nodes to the model_nodes list
            nodes.extend([((pair[1]-pair[0])/n_sub)*i+pair[0] for i in range(n_sub+1)])

        # Remove duplicate nodes
        model_nodes = []
        for node in nodes:
            if node not in model_nodes:
                model_nodes.append(node)

        # Store end nodes for each element
        elem_nodes = []
        for idx, node in enumerate(model_nodes[:-1]):
            elem_nodes.append([idx, idx+1])

        self.model_nodes = model_nodes
        self.elem_nodes = elem_nodes

    def _fill_global_dof(self):
        '''
        Fills global dof array with the appropriate global dof number
        and determine the total number of dof in the model.

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        # Initialize list with n_nodes rows and 3 columns in each row
        dof_num = [[0, 0, 0] for _ in range(len(self.model_nodes))]

        # Initialize the dof counter
        dof_count = 0

        # Loop over all nodes
        for i_node in range(len(self.model_nodes)):
            # Loop over each dof
            for i_dof in range(3):
                # Increase total dof number for each new dof
                if self.node_support[i_node][i_dof] == 0:
                    # This node is not restrained and is a dof
                    dof_count += 1
                    dof_num[i_node][i_dof] = dof_count
                else:
                    # This node is restrained
                    dof_num[i_node][i_dof] = 0

        self.dof_num = dof_num
        self.n_dof = dof_count

    def _get_load_vector(self):
        '''
        Assembles the global load vector, including fixed end forces
        from distributed loads on elements.

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        # Initialize an empty numpy array with n_dof x 1 dimensions for both the
        # applied concentrated loads and the fixed end forces
        P = np.zeros((self.n_dof, 1))
        Pf = np.zeros((self.n_dof, 1))

        # Loop over all nodes
        for i_node in range(len(self.model_nodes)):
            # Loop over each dof
            for i_dof in range(3):
                if self.dof_num[i_node][i_dof] != 0:
                    P[self.dof_num[i_node][i_dof]-1] += self.node_pload[i_node][i_dof]
                    Pf[self.dof_num[i_node][i_dof]-1] += self.node_elem_fef[i_node][i_dof]

        self.nodal_load_vector = P
        self.fef_load_vector = Pf

    def _get_node_elem_fef(self):
        '''
        Calculates the fixed end forces due to distributed loads on
        model elements.

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        elem_loads = [[0, 0, 0, 0, 0, 0] for _ in range(len(self.elem_nodes))]
        node_elem_fef = [[0, 0 ,0] for _ in range(len(self.model_nodes))]
        # Loop over all elements
        for i_elem, elem in enumerate(self.elem_nodes):
            # Calculate fixed end forces for y-distributed loads
            w1 = self.elem_dload[i_elem][1][0]
            w2 = self.elem_dload[i_elem][1][1]
            L = self.model_nodes[elem[1]] - self.model_nodes[elem[0]]
            if w1 != 0 and w2 != 0:
                # Calculate fixed end forces if w1 >= w2
                if abs(w1) > abs(w2):
                    v_react_i = (w2*L)/2 + (7*(w1-w2)*L)/20
                    v_react_j = (w2*L)/2 + (3*(w1-w2)*L)/20
                    m_react_i = (w2*L**2)/12 + ((w1-w2)*L**2)/20
                    m_react_j = -(w2*L**2)/12 - ((w1-w2)*L**2)/30
                # Calculate fixed end forces if w1 <= w2
                elif abs(w2) >= abs(w1):
                    v_react_i = (w1*L)/2 + (3*(w2-w1)*L)/20
                    v_react_j = (w1*L)/2 + (7*(w2-w1)*L)/20
                    m_react_i = (w1*L**2)/12 + ((w2-w1)*L**2)/30
                    m_react_j = -(w1*L**2)/12 - ((w2-w1)*L**2)/20
                # Place the fixed end forces in the proper location
                node_elem_fef[elem[0]][1] += v_react_i
                node_elem_fef[elem[0]][2] += m_react_i
                node_elem_fef[elem[1]][1] += v_react_j
                node_elem_fef[elem[1]][2] += m_react_j

                elem_loads[i_elem][1] += v_react_i
                elem_loads[i_elem][2] += m_react_i
                elem_loads[i_elem][4] += v_react_j
                elem_loads[i_elem][5] += m_react_j

        self.node_elem_fef = node_elem_fef
        self.elem_loads = elem_loads

    def _get_points_of_interest(self):
        '''
        Defines points of interest along the length of the beam model,
        including beam start and end points, points of load application, and
        support points.

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        points_of_interest = []

        # Add end points
        points_of_interest.extend([0, self.beam.length])

        # Add support points
        for support in self.beam.supports:
            if support[0] not in points_of_interest:
                points_of_interest.append(support[0])

        # Add locations of point loads
        for load in self.beam.ploads:
            if load.location not in points_of_interest:
                points_of_interest.append(load.location)

        # Add starting and ending locations of distributed loads
        for load in self.beam.dloads:
            for point in load.location:
                if point not in points_of_interest:
                    points_of_interest.append(point)

        points_of_interest.sort()

        self.points_of_interest = points_of_interest

    def _set_dload_elems(self):
        '''
        Determines which model elements have been defined by the user
        as having applied distributed loads.

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        elem_dload    = [[[0, 0], [0,0], [0,0]] for _ in range(len(self.elem_nodes))]
        for idx, elem in enumerate(self.elem_nodes):
            for dload in self.beam.dloads:
                m = []
                b = []
                for dir in dload.magnitude:
                    m.append((dir[1]-dir[0])/(dload.location[1]-dload.location[0]))
                    b.append(dir[0])
                if (dload.location[0] <= self.model_nodes[elem[0]] and
                        dload.location[1] >= self.model_nodes[elem[1]]):
                    for idx2, _ in enumerate(elem_dload[idx]):
                        elem_dload[idx][idx2][0] += m[idx2]*(self.model_nodes[elem[0]]-dload.location[0])+b[idx2]
                        elem_dload[idx][idx2][1] += m[idx2]*(self.model_nodes[elem[1]]-dload.location[0])+b[idx2]

        self.elem_dload = elem_dload

    def _set_pload_nodes(self):
        '''
        Determines which model nodes have been defined by the
        user as having applied point loads.

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        node_pload = [[0, 0, 0] for _ in range(len(self.model_nodes))]
        for idx, node in enumerate(self.model_nodes):
            for pload in self.beam.ploads:
                if pload.location == node:
                    for idx2, _ in enumerate(node_pload[idx]):
                        node_pload[idx][idx2] += pload.magnitude[idx2]

        self.node_pload = node_pload

    def _set_support_nodes(self):
        '''
        Determines which model nodes have been defined by the
        user as supports.
        '''
        node_support = [(0, 0, 0) for _ in range(len(self.model_nodes))]
        support_nodes = []
        for i_node, node in enumerate(self.model_nodes):
            for support in self.beam.supports:
                if support[0] == node:
                    node_support[i_node] = support[1]
                    support_nodes.append(i_node)

        self.node_support = node_support
        self.support_nodes = support_nodes

    def add_beam_dload(self, dload, add_type='add'):
        '''
        Adds a distributed load to the Beam object referenced by the BeamModel object.

        Parameters
        ----------
        add_type : str, optional
            indicates whether to add the dload to the existing loads or replace the existing loads
        dload : list
            list of dist load objects representing the distributed load(s) to be added to the beam referenced by the beam model

        Returns
        -------
        None
        '''
        # Add the distributed load
        if add_type == 'replace':
            self.beam.dloads = dload
        elif add_type == 'add':
            self.beam.dloads.extend(dload)

        # Re-initialize the analysis
        self.initialize_analysis()

    def add_beam_pload(self, pload, add_type='add'):
        '''
        Adds a point load to the Beam object referenced by the BeamModel object.

        Parameters
        ----------
        add_type : str, optional
            indicates whether to add the pload to the existing loads or replace the existing loads
        pload : list
            list of point load objects representing the point load(s) to be added to the beam referenced by the beam model

        Returns
        -------
        None
        '''
        # Add the point load
        if add_type == 'replace':
            self.beam.ploads = pload
        elif add_type == 'add':
            self.beam.ploads.extend(pload)

        # Re-initialize the analysis
        self.initialize_analysis()

    def initialize_analysis(self):
        '''
        Prepares the model for analysis. To be called at instantiation and when the user specifies.

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        self._get_points_of_interest()
        self._create_model_nodes_and_elems()
        self._set_support_nodes()
        self._set_pload_nodes()
        self._set_dload_elems()
        self._get_node_elem_fef()
        self._fill_global_dof()
        self._assemble_global_stiffness()
        self._get_load_vector()

    def perform_analysis(self):
        '''
        Computes the displacement vector, element force matrix, and support reaction vector.

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        # Calculate the global displacement vector
        load_vector = self.nodal_load_vector - self.fef_load_vector
        self.global_displacement = np.matmul(
                np.linalg.inv(self.global_stiffness), load_vector
                )

        # Calculate element forces
        elemxyM = np.zeros((len(self.elem_nodes), 6))

        # Loop over all elements
        for i_elem in range(len(self.elem_nodes)):
            local_delta = np.zeros((6, 1))
            local_Pf = np.zeros((6, 1))

            # Get local element stiffness matrix
            K = self.local_stiffness_matrices[i_elem]

            l_dof = -1
            # Extract local data first
            for i_node in range(2):
                # Get end node number for element # i_elem
                node_num = self.elem_nodes[i_elem][i_node]
                for i_dof in range(3):
                    l_dof += 1
                    # Extract local element loads
                    local_Pf[l_dof] = self.elem_loads[i_elem][l_dof]

                    # Extract local deformations
                    G_dof = self.dof_num[node_num][i_dof]
                    if G_dof != 0:
                        local_delta[l_dof] = self.global_displacement[G_dof-1]

            # Calculate element forces
            local_element_forces = np.matmul(K, local_delta) + local_Pf

            # Store element forces
            elemxyM[i_elem] = local_element_forces.transpose()

        # Calculate support reactions
        support_reactions = np.zeros((len(self.model_nodes), 3))

        # Loop over all elements
        for i_elem in range(len(self.elem_nodes)):
            l_dof = -1

            # Loop over each node in the element
            for i_node in range(2):
                node_num = self.elem_nodes[i_elem][i_node]
                # Loop over each dof
                for i_dof in range(3):
                    l_dof += 1
                    if self.dof_num[node_num][i_dof] == 0:
                        support_reactions[node_num][i_dof] += elemxyM[i_elem][l_dof]

        self.element_forces = elemxyM
        self.support_reactions = support_reactions

    def plot_bmd(self):
        '''
        Plots the bending moment diagram of the analyzed beam.

        Parameters
        ----------
        None

        Returns
        -------
        plt : pyplot object
            pyplot object representing the bending moment diagram for the analyzed model
        '''
        left_moment = []
        right_moment = []
        for elem_f in self.element_forces:
            left_moment.append(elem_f[2]/12)
            right_moment.append(elem_f[5]/12)
        
        mom_count1 = 0
        mom_count2 = 0

        bmd_val = np.zeros((2*len(self.model_nodes)))
        for i_bmd in range(2*len(self.model_nodes)):
            if i_bmd < 2*len(self.model_nodes)-2 and (i_bmd+1) % 2 != 0:
                bmd_val[i_bmd] = -left_moment[mom_count1]
                mom_count1 += 1
            elif i_bmd < 2*len(self.model_nodes)-2 and (i_bmd+1) % 2 == 0:
                bmd_val[i_bmd] = bmd_val[i_bmd-1]
                mom_count2 += 1
            elif i_bmd == 2*len(self.model_nodes)-2:
                bmd_val[i_bmd] = right_moment[len(self.elem_nodes)-1]
            elif i_bmd == 2*len(self.model_nodes)-1:
                bmd_val[i_bmd] = bmd_val[i_bmd-1]

        lval_bmd = np.zeros(2*(len(self.model_nodes)))
        lval_bmd_count = 0
        for i_lval_bmd in range(len(self.model_nodes)):
            lval_bmd[i_lval_bmd+lval_bmd_count] = self.model_nodes[i_lval_bmd]/12
            lval_bmd[i_lval_bmd+lval_bmd_count+1] = self.model_nodes[i_lval_bmd]/12
            lval_bmd_count += 1
        
        plt.figure()
        plt.plot(lval_bmd.tolist(), bmd_val.tolist(),'b-')

        plt.xlabel('Length (ft)')
        plt.ylabel(f'Bending Moment (k-ft)')

        plt.grid()

        return plt

    def plot_deflected_shape(self, scale=1):
        '''
        Plots the deflected shape of the analyzed beam.

        Parameters
        ----------
        scale : int, optional
            scale to be applied to the deflected shape

        Returns
        -------
        plt : pyplot object
            pyplot object representing the deflected shape of the analyzed beam
        '''
        y_disp = []
        for i_node in range(len(self.model_nodes)):
            G_dof = self.dof_num[i_node][1]
            if G_dof != 0:
                y_disp.append(self.global_displacement[G_dof-1][0]*scale)
            else:
                y_disp.append(0.0)
        
        plt.figure()
        plt.plot([x/12 for x in self.model_nodes], y_disp, 'b-')

        plt.xlabel('Length (ft)')
        plt.ylabel(f'Deflection (in) - Scale={scale}:1')

        plt.grid()

        return plt

    def plot_sfd(self):
        '''
        Plots the shear force diagram of the analyzed beam.

        Parameters
        ----------
        None

        Returns
        -------
        plt : pyplot object
            pyplot object representing the shear force diagram for the analyzed model
        '''
        left_shear = []
        right_shear = []
        for elem_f in self.element_forces:
            left_shear.append(elem_f[1])
            right_shear.append(elem_f[4])

        shear_count1 = 0
        shear_count2 = 0

        sfd_val = np.zeros(2*len(self.model_nodes))
        for i_sfd in range(1, len(self.model_nodes)):
            if i_sfd < 2*len(self.model_nodes)-1:
                #print(shear_count1, shear_count2)
                sfd_val[i_sfd+shear_count2] = -left_shear[shear_count1]
                sfd_val[i_sfd+shear_count2+1] = right_shear[shear_count1]
                shear_count1 += 1
                shear_count2 += 1
            elif i_sfd == 2*len(self.model_nodes)-1:
                sfd_val[i_sfd] = 0

        lval_sfd = np.zeros(2*(len(self.model_nodes)))
        lval_sfd_count = 0
        for i_lval_sfd in range(len(self.model_nodes)):
            lval_sfd[i_lval_sfd+lval_sfd_count] = self.model_nodes[i_lval_sfd]/12
            lval_sfd[i_lval_sfd+lval_sfd_count+1] = self.model_nodes[i_lval_sfd]/12
            lval_sfd_count += 1

        plt.figure()
        plt.plot(lval_sfd.tolist(), sfd_val.tolist(), 'b-')

        plt.xlabel('Length (ft)')
        plt.ylabel(f'Shear Force (k)')

        plt.grid()

        return plt

class DistLoad:
    '''
    A class representing a distributed load.

    Attributes
    ----------
    location : tuple
        tuple representing the start and end locations of the distributed load along the beam
    magntidue : tuple
        tuple of tuples representing the magnitude of the distributed load at its start and end locations
    '''
    def __init__(self, location, magnitude):
        '''
        Constructs all the necessary attributes for the dist load object.

        Parameters
        ----------
        location : tuple
            tuple representing the start and end locations of the distributed load along the beam
        magntidue : tuple
            tuple of tuples representing the magnitude of the distributed load at its start and end locations
        '''
        if not self._valid_dload_location(location):
            raise TypeError('location must be a tuple of length 2 containing int or float.')
        if not self._valid_dload_magnitude(magnitude):
            raise TypeError('magnitude must be a tuple of 3 tuples each with length 2 containing int or float.')
        
        self.location = location
        self.magnitude = magnitude
        
    def _valid_dload_location(self, location):
        '''
        Checks that the location parameter passed to the __init__ method is valid.
        
        Parameters
        __________
        location : tuple
            tuple representing the start and end locations of the distributed load along the beam
            
        Returns
        -------
        bool : bool
            bool indicating whether the location is valid input
        '''
        if not isinstance(location, tuple):
            return False
        elif len(location) != 2:
            return False
        elif not all(isinstance(item, (int, float)) for item in location):
            return False
        else:
            return True
    
    def _valid_dload_magnitude(self, magnitude):
        '''
        Checks that the magnitude parameter passed to the __init__ method is valid.
        
        Parameters
        __________
        magntidue : tuple
            tuple of tuples representing the magnitude of the distributed load at its start and end locations
            
        Returns
        -------
        bool : bool
            bool indicating whether the magnitude is valid input
        '''
        if not isinstance(magnitude, tuple):
            return False
        elif len(magnitude) != 3:
            return False
        elif not all(isinstance(item, tuple) for item in magnitude):
            return False
        else:
            for item in magnitude:
                if len(item) != 2:
                    return False
                for mag in item:
                    if not isinstance(mag, (int, float)):
                        return False
            return True

class PointLoad:
    '''
    A class representing a concentrated load.

    Attributes
    ----------
    location : tuple
        tuple representing the locations of the concentrated load along the beam
    magntidue : tuple
        tuple representing the magnitude of the concentrated load
    '''
    def __init__(self, location, magnitude):
        '''
        Constructs all the necessary attributes for the point load object.

        Parameters
            ----------
        location : tuple
            tuple representing the locations of the concentrated load along the beam
        magntidue : tuple
            tuple representing the magnitude of the concentrated load
        '''
    def __init__(self, location, magnitude):
        self.location = location
        self.magnitude = magnitude

import math
import numpy as np

class SteelBeamSize:
  def __init__(self, name, properties, e_mod=29000, section_type='AISC'):
    self.name = name
    self.properties = properties
    self.e_mod = e_mod
    self.section_type = section_type

  def __str__(self):
    return f'{self.name}'
  
class SteelJoistSize:
  def __init__(self, name, properties, e_mod=29000, section_type='SJI'):
    self.name = name
    self.properties = properties
    self.e_mod = e_mod
    self.section_type = section_type

  def __str__(self):
    return f'{self.name}'

class Beam:
  def __init__(self, length, size, supports, ploads=[], dloads=[]):
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

class PointLoad:
  def __init__(self, location, magnitude):
    self.location = location
    self.magnitude = magnitude

class DistLoad:
  def __init__(self, location, magnitude):
    self.location = location
    self.magnitude = magnitude

class BeamModel:
  def __init__(self, beam, max_node_spacing=0.5*12, ini_analysis=True):
    self.beam = beam
    self.max_node_spacing = max_node_spacing

    if ini_analysis:
      self.initialize_analysis()

  def get_points_of_interest(self):
    '''
    Defines points of interest along the length of the beam model,
    including beam start and end points, points of load application, and
    support points.
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

  def create_model_nodes_and_elems(self):
    '''
    Defines the model nodes based on the points of interest
    and maximum node spacing defined by the user.
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

  def set_support_nodes(self):
    '''
    Determines which model nodes have been defined by the
    user as supports.
    '''
    node_support = [(0, 0, 0) for _ in range(len(self.model_nodes))]
    for idx, node in enumerate(self.model_nodes):
      for support in self.beam.supports:
        if support[0] == node:
          node_support[idx] = support[1]

    self.node_support = node_support

  def set_pload_nodes(self):
    '''
    Determines which model nodes have been defined by the
    user as having applied point loads.
    '''
    node_pload = [[0, 0, 0] for _ in range(len(self.model_nodes))]
    for idx, node in enumerate(self.model_nodes):
      for pload in self.beam.ploads:
        if pload.location == node:
          for idx2, _ in enumerate(node_pload[idx]):
            node_pload[idx][idx2] += pload.magnitude[idx2]

    self.node_pload = node_pload

  def set_dload_elems(self):
    '''
    Determines which model elements have been defined by the user
    as having applied distributed loads.
    '''
    elem_dload  = [[[0, 0], [0,0], [0,0]] for _ in range(len(self.elem_nodes))]
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
            elem_dload[idx][idx2][0] = m[idx2]*self.model_nodes[elem[0]]+b[idx2]
            elem_dload[idx][idx2][1] = m[idx2]*self.model_nodes[elem[1]]+b[idx2]

    self.elem_dload = elem_dload

  def get_node_elem_fef(self):
    '''
    Calculates the fixed end forces due to distributed loads on
    model elements.
    '''
    node_elem_fef = [[0, 0 ,0] for _ in range(len(self.model_nodes))]
    # Loop over all elements
    for idx, elem in enumerate(self.elem_nodes):
      # Calculate fixed end forces for y-distributed loads
      w1 = self.elem_dload[idx][1][0]
      w2 = self.elem_dload[idx][1][1]
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
        node_elem_fef[elem[0]][1] += -v_react_i
        node_elem_fef[elem[0]][2] += -m_react_i
        node_elem_fef[elem[1]][1] += -v_react_j
        node_elem_fef[elem[1]][2] += -m_react_j

    self.node_elem_fef = node_elem_fef

  def fill_global_dof(self):
    '''
    Fills global dof array with the appropriate global dof number
    and determine the total number of dof in the model.
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

  def assemble_global_stiffness(self):
    '''
    Assembles the global stiffness matrix for the model.
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

  def get_load_vector(self):
    '''
    Assembles the global load vector, including fixed end forces
    from distributed loads on elements.
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

  def initialize_analysis(self):
    '''
    Prepares the model for analysis. To be called at instantiation and 
    when the user specifies.
    '''
    self.get_points_of_interest()
    self.create_model_nodes_and_elems()
    self.set_support_nodes()
    self.set_pload_nodes()
    self.set_dload_elems()
    self.get_node_elem_fef()
    self.fill_global_dof()
    self.assemble_global_stiffness()
    self.get_load_vector()

  def perform_analysis(self):
    '''
    Computes the displacement vector, element force matrix, and
    support reaction vector.
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
          local_Pf[l_dof] = self.node_elem_fef[node_num][i_dof]

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

  def add_beam_dload(self, dload, add_type='add'):
    '''
    Adds a distributed load to the Beam object referenced by the BeamModel object.
    '''
    # Add the distributed load
    if add_type == 'replace':
      self.beam.dloads = dload
    elif add_type == 'add':
      self.beam.dloads.append(dload)

    # Re-initialize the analysis
    self.initialize_analysis()

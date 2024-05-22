from fem_analysis import (
    Beam,
    BeamModel,
    DistLoad,
)

class Loading:
    def __init__(self, dead_load, rain_load, include_sw = True):
        self.dead_load = dead_load # Units: k/in^2
        self.rain_load = rain_load # Units: k/in^2
        self.include_sw = include_sw

class PrimaryMember(Beam):
    pass

class SecondaryMember(Beam):
    pass

class PrimaryFraming:
    def __init__(self, primary_members):
        self.primary_members = primary_members

    def __str__(self):
        return f'Primary framing members: {[member.size.name for member in self.primary_members]}'

class SecondaryFraming:
    def __init__(self, secondary_members, slope=0.25):
        self.secondary_members = secondary_members
        self.slope = slope

    def __str__(self):
        return f'Secondary framing members: {[member.size.name for member in self.secondary_members]}'

class RoofBay:
    def __init__(self, primary_framing, secondary_framing, loading, mirrored_left=False, mirrored_right=False):
        self.primary_framing = primary_framing
        self.secondary_framing = secondary_framing
        self.loading = loading
        self.mirrored_left = mirrored_left
        self.mirrored_right = mirrored_right

    def get_secondary_spacing(self):
        '''
        Method to get the secondary member spacing, assuming all members are evenly spaced.
        '''
        primary_length = self.primary_framing.primary_members[0].length
        n_secondary = len(self.secondary_framing.secondary_members)

        secondary_spacing = primary_length/(n_secondary-1)

        return secondary_spacing

    def get_secondary_dl(self):
        '''
        Method to get the dead load (including the member self-weight, if enabled) acting on each secondary framing member.
        '''
        # Initialize dictionary to hold load values
        secondary_dl = {}

        # Calculate tributary width for each member
        trib_w = [self.get_secondary_spacing() for _ in range(len(self.secondary_framing.secondary_members))]

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

        return secondary_dl


import pandas as pd

from .analysis import (
    Beam,
    BeamModel,
    DistLoad,
    SteelBeamSize,
    SteelJoistSize,
)

class Loading:
    def __init__(self, dead_load, rain_load):
        self.dead_load = dead_load # Units: k/in^2
        self.rain_load = rain_load # Units: k/in^2

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
        primary_length = self.primary_framing.primary_members[0].length
        n_secondary = len(self.secondary_framing.secondary_members)

        secondary_spacing = primary_length/n_secondary

        return secondary_spacing

    def get_initial_secondary_loading(self):
        secondary_loading = {}
        # First deal with the dead load
        trib_w = self.get_secondary_spacing()
        q_dl = self.loading.dead_load
        w_dl = q_dl*trib_w # Units: k/in
        x_i_dl = 0
        for idx, member in self.secondary_framing.secondary_members:
            x_j_dl = member.length

            if idx not in secondary_loading.keys():
                secondary_loading[idx] = []

            secondary_loading[idx].append(DistLoad(location=(x_i_dl, x_j_dl), magnitude=((0, 0), (-w_dl, -w_dl), (0, 0))))

        # Next deal with the rain load
        conv = 62.4/(12**3)/1000
        q_rl = self.loading.rain_load
        rain_depth_i = q_rl/conv
        rain_length = rain_depth_i/(self.secondary_framing.slope/12)
        w_i_rl = rain_depth_i*conv
        x_i_rl = 0
        for idx, member in self.secondary_framing.secondary_members:
            if rain_length > member.length:
                rain_depth_j = rain_depth_i - (self.secondary_framing.slope/12)*member.length
                x_j_rl = member.length
            elif rain_length <= member.length:
                rain_depth_j = 0
                x_j_rl = rain_length
            w_j_rl = rain_depth_j*conv

            if idx not in secondary_loading.keys():
                secondary_loading[idx] = []

            secondary_loading[idx].append(DistLoad(location=(x_i_rl, x_j_rl), magnitude=((0, 0), (-w_i_rl, -w_j_rl), (0, 0))))


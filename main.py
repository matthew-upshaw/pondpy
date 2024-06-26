'''
This module contains an example of how to set
up and run an analysis of a simple roof bay.
'''
import os

from joistpy import sji
from steelpy import aisc


output_folder = os.path.join(os.path.dirname(__file__), 'example_reports')
output_filename = 'pondpy_results'
output_filetype = 'html'

def run_analysis(model):
    model.perform_analysis()
    model.generate_report(
        output_folder=output_folder,
        filename=output_filename,
        filetype=output_filetype,
        company='Example Company',
        proj_num='12345',
        proj_name='Example Project',
        desc='A sample calculation',
    )

from pondpy import (
    SteelBeamSize,
    SteelJoistSize,
    PrimaryMember,
    PrimaryFraming,
    SecondaryMember,
    SecondaryFraming,
    Loading,
    PondPyModel,
)

w12x16 = SteelBeamSize('W12X16', aisc.W_shapes.W12X16)
w16x26 = SteelBeamSize('W16X26', aisc.W_shapes.W16X26)
k_14k1 = SteelJoistSize('14K1', sji.K_Series.K_14K1)

p_length = 19.65*12 # length of primary members in inches
s_length = 20*12 # length of secondary members in inches

# Support types are designated by tuples representing (Tx, Ty, Rz).
# A 0 indicates the degree of freedom is unrestrained while a 1 indicates a 
# restrained degree of freedom.
p_support = [[0, (1, 1, 0)], [p_length, (1, 1, 0)]]
s_support = [[0, (1, 1, 0)], [s_length, (1, 1, 0)]]

p_girder1 = PrimaryMember(p_length, w16x26, p_support)
p_girder2 = PrimaryMember(p_length, w16x26, p_support)
s_beam1 = SecondaryMember(s_length, w12x16, s_support)
s_beam2 = SecondaryMember(s_length, w12x16, s_support)
s_joist1 = SecondaryMember(s_length, k_14k1, s_support)
s_joist2 = SecondaryMember(s_length, k_14k1, s_support)
s_joist3 = SecondaryMember(s_length, k_14k1, s_support) 

p_framing = PrimaryFraming([p_girder1, p_girder2])
s_framing = SecondaryFraming([s_beam1, s_joist1, s_joist2, s_joist3, s_beam2])

q_dl = 20/1000/144 # Surface dead load in ksi
q_rl = 22.4/1000/144 # Surface rain load at secondary drainage inlet in ksi

loading = Loading(q_dl, q_rl)

pondpy_model = PondPyModel(p_framing, s_framing, loading)

if __name__ == '__main__':
    run_analysis(pondpy_model)

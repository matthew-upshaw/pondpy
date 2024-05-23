import pdb

from joistpy import sji
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

# Define the roof bay
roof_bay = RoofBay(primary_framing, secondary_framing, loading)

roof_bay_model = RoofBayModel(roof_bay)
roof_bay_model.analyze_roof_bay(rain_load=roof_bay_model.initial_secondary_rl)
pdb.set_trace()

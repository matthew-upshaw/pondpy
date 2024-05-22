from joistpy import sji
from steelpy import aisc

from fem_analysis import (
    SteelBeamSize,
    SteelJoistSize,
)

from pond_analysis import (
    Loading,
    PrimaryFraming,
    PrimaryMember,
    RoofBay,
    SecondaryFraming,
    SecondaryMember,
)

# Define sizes for primary and secondary members
w16x26 = SteelBeamSize('W16X26', aisc.W_shapes.W16X26)
k_12k1 = SteelJoistSize('12K1', sji.K_Series.K_12K1)

# Define loading for the roof bay
loading = Loading(20/1000/12, 25/1000/12, include_sw=False)

# Define the primary and secondary members
primary_mem = PrimaryMember(20*12, w16x26, [[0,(1,1,1)],[20*12,(1,1,1)]])
secondary_mem = SecondaryMember(20*12, k_12k1, [[0,(1,1,1)],[20*12,(1,1,1)]])

# Define the primary and secondary framing
framing_p = [primary_mem for x in range(2)]
framing_s = [secondary_mem for x in range(5)]
primary_framing = PrimaryFraming(framing_p)
secondary_framing = SecondaryFraming(framing_s)

# Define the roof bay
roof_bay = RoofBay(primary_framing, secondary_framing, loading)

secondary_dl = roof_bay.get_secondary_dl()
print(secondary_dl[0][0].location)

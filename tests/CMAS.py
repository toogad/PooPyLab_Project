# This file is part of PooPyLab.
#
# PooPyLab is a simulation software for biological wastewater treatment
# processes using International Water Association Activated Sludge Models.
#    
#    Copyright (C) Kai Zhang
#
#    PooPyLab is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    PooPyLab is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with PooPyLab.  If not, see <http://www.gnu.org/licenses/>.
#
# -----------------------------------------------------------------------------
#    Definition of a Complete-Mix Activated Sludge (CMAS) Process Flow Diagram.
#
#
#    Process Flow Diagram:
#
#    Inlet --p1-> reactor(ra) --p2-> final.clar --p3-> outlet
#                 ^                       |
#                 |                       p4
#                 |                       |
#                 |                       |
#                 |                       V
#                 +<--RAS-----splt*<------+
#                              |
#                              +----------p5---------> waste (WAS)
#
#
#       splt* is an SRT Controlling Splitter
#
#    Author: Kai Zhang
#
# Change Log: 
#   2019-07-24 KZ: init
#

from unit_procs.streams import influent, effluent, WAS, splitter, pipe
from unit_procs.bio import asm_reactor
from unit_procs.physchem import final_clarifier
from utils.pfd import check, show


inlet = influent()
p1 = pipe()

ra = asm_reactor()
p2 = pipe()

fc = final_clarifier()
p3 = pipe()  # to outlet
p4 = pipe()  # to splt

outlet = effluent()

splt = splitter()
p5 = pipe()  # to waste
RAS = pipe()  # to ra

waste = WAS()

wwtp = [inlet,
        p1, p2, p3, p4, p5,
        ra, fc, outlet,
        RAS, waste, splt]

#SRT = 10  # day

def construct():
    # make an CMAS plant
    inlet.set_downstream_main(p1)
    p1.set_downstream_main(ra)
    ra.set_downstream_main(p2)
    p2.set_downstream_main(fc)
    fc.set_downstream_main(p3)
    fc.set_downstream_side(p4)
    p3.set_downstream_main(outlet)
    p4.set_downstream_main(splt)
    splt.set_downstream_main(RAS)
    splt.set_downstream_side(p5)
    splt.set_as_SRT_controller(True)
    RAS.set_downstream_main(ra)
    p5.set_downstream_main(waste)
    inlet.set_mainstream_flow(10)  # mgd
    splt.set_sidestream_flow(0.01)

    print("CMAS PFD constructed.")

    return wwtp
 

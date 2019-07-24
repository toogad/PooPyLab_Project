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
#    Definition of a Modified Luzak Ettinger (MLE) Process Flow Diagram.
#
#    Author: Kai Zhang
#
# Change Log: 
#   2019-07-24 KZ: init
#

from unit_procs.streams import influent, effluent, WAS, splitter, pipe
from unit_procs.bio import asm_reactor
from unit_procs.physchem import final_clarifier
from utils.pfd import check_pfd, show_pfd
import pdb


inlet = influent()
p1 = pipe()

ra = asm_reactor()
p2 = pipe()

rb = asm_reactor()
p3 = pipe()

fc = final_clarifier()
p4 = pipe()  # to outlet
p5 = pipe()  # to splt

outlet = effluent()

splt = splitter()
p6 = pipe()  # to waste
RAS = pipe()  # to ra

waste = WAS()

wwtp = [inlet,
        p1, p2, p3, p4, p5, p6,
        ra, rb, fc, outlet,
        RAS, waste, splt]

def construct():
    # make an MLE plant
    inlet.set_downstream_main(p1)
    p1.set_downstream_main(ra)
    ra.set_downstream_main(p2)
    p2.set_downstream_main(rb)
    rb.set_downstream_main(p3)
    p3.set_downstream_main(fc)
    fc.set_downstream_main(p4)
    fc.set_downstream_side(p5)
    p4.set_downstream_main(outlet)
    p5.set_downstream_main(splt)
    splt.set_downstream_main(RAS)
    splt.set_downstream_side(p6)
    splt.set_as_SRT_controller(True)
    RAS.set_downstream_main(ra)
    p6.set_downstream_main(waste)
    inlet.set_mainstream_flow(0.1)  # mgd
    splt.set_sidestream_flow(0.01)

    print("MLE PFD constructed.")

    return wwtp


def destroy():
    # disconnection is done by removing upstream dischargers of a unit
    p1.remove_upstream(inlet)
    p3.remove_upstream(p1)  # on purpose
    p3.remove_upstream(rb)
    splt.remove_upstream(p5)
    p6.remove_upstream(splt)
    ra.remove_upstream(RAS)
    outlet.remove_upstream(p4)
    print("MLE PFD destoryed")
    return None
 

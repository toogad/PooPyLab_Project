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
#    Definition of a Pre/Post Anoxic DN Process Flow Diagram.
#
#
#    Process Flow Diagram:
#
# inlet--p1->rPAX--p2->rPOX--p3-->splt1--p4->rAXP--p5->rOXP--p6->fc--p7->outlet
#            ^ ^                   |                             |
#            | |                   |                             p8
#            | |                   v                             |
#            | +-----IR(p11)-------+                             |
#            |                                                   V
#            +<-------RAS(p9)----splt2*<-------------------------+
#                                 |
#                                 +------p10--> waste(WAS)
#
#
#       splt*: SRT Controlling Splitter
#       rPAX : reactor_Pre_Anoxic
#       rPOX : reactor_Pre_Oxic
#       rAXP : reactor_Post_Anoxic
#       rOXP : reactor_Post_Oxic
#
#    Author: Kai Zhang
#
# Change Log:
# 20220228 KZ: corrected name in PFD
# 20201129 KZ: re-run after package structure update
# 20191029 KZ: init
#

from PooPyLab.unit_procs.streams import splitter, pipe, WAS
from PooPyLab.unit_procs.streams import influent, effluent
from PooPyLab.unit_procs.bio import asm_reactor
from PooPyLab.unit_procs.physchem import final_clarifier
#from PooPyLab.utils.pfd import check, show


inlet = influent()

p1 = pipe()
p2 = pipe()
p3 = pipe()
p4 = pipe()
p5 = pipe()
p6 = pipe()
p7 = pipe()
p8 = pipe()
# return activated sludge
RAS = pipe()  # aka p9
RAS.__name__ = 'RAS'
p10 = pipe()
# internal recirculation
IR = pipe()  # aka p11
IR.__name__ = 'IR'

rPAX = asm_reactor()
rPOX = asm_reactor()
rAXP = asm_reactor()
rOXP = asm_reactor()

fc = final_clarifier()

outlet = effluent()

splt1 = splitter()
splt2 = splitter()

waste = WAS()


wwtp = [inlet,
        p1, p2, p3, p4, p5, p6, p7, p8,
        RAS, p10, IR,
        rPAX, rPOX, rAXP, rOXP, fc, 
        outlet, waste, 
        splt1, splt2]

SRT = 15  # day

def construct():
    # make an 4-stage plant
    inlet.set_downstream_main(p1)
    p1.set_downstream_main(rPAX)
    rPAX.set_downstream_main(p2)
    p2.set_downstream_main(rPOX)
    rPOX.set_downstream_main(p3)
    p3.set_downstream_main(splt1)
    splt1.set_downstream_main(p4)
    splt1.set_downstream_side(IR)
    p4.set_downstream_main(rAXP)
    IR.set_downstream_main(rPAX)
    rAXP.set_downstream_main(p5)
    p5.set_downstream_main(rOXP)
    rOXP.set_downstream_main(p6)
    p6.set_downstream_main(fc)
    fc.set_downstream_main(p7)
    fc.set_downstream_side(p8)
    p7.set_downstream_main(outlet)
    p8.set_downstream_main(splt2)
    splt2.set_downstream_main(RAS)
    splt2.set_downstream_side(p10)
    RAS.set_downstream_main(rPAX)
    p10.set_downstream_main(waste)

    splt2.set_as_SRT_controller(True)

    inlet.set_mainstream_flow(37800)

    splt1.set_sidestream_flow(3.0*37800)  #IR
    splt2.set_mainstream_flow(0.5*37800)  #RAS
    
    rPAX.set_model_condition(10, 0.0)
    rPOX.set_model_condition(10, 2.0)
    rAXP.set_model_condition(10, 0.0)
    rOXP.set_model_condition(10, 1.0)

    rPAX.set_active_vol(3000)
    rPOX.set_active_vol(9500)
    rAXP.set_active_vol(1000)
    rOXP.set_active_vol(500)

    print("Pre- & Post-Anoxic Denitrification PFD constructed.")

    return wwtp

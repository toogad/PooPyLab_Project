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
#    Definition of a Modified Ludzack-Ettinger (MLE) Process Flow Diagram.
#
#
#    Process Flow Diagram:
#
#    inlet--p1->react(AX)--p2->react(OX)--p3-->splt1--p4->fc--p5->outlet
#               ^  ^                            |         |
#               |  |                            |         p6
#               |  |                            |         |
#               |  +-----IR(p9)---------------- V         |
#               |                                         V
#               +<-------RAS(p7)----splt2*<---------------+
#                                        |
#                                        +------p8---> waste(WAS)
#
#
#       splt* is an SRT Controlling Splitter
#
#    Author: Kai Zhang
#
# Change Log:
# 20201129 KZ: re-run after package structure update
# 20191022 KZ: init
#

from PooPyLab.unit_procs.streams import influent, effluent, WAS, splitter, pipe
from PooPyLab.unit_procs.bio import asm_reactor
from PooPyLab.unit_procs.physchem import final_clarifier


inlet = influent()

p1 = pipe()
p2 = pipe()
p3 = pipe()
p4 = pipe()
p5 = pipe()
p6 = pipe()
# return activated sludge
RAS = pipe()  # aka p7
p8 = pipe()
# internal recirculation
IR = pipe()  # aka p9

AX = asm_reactor()
OX = asm_reactor()

fc = final_clarifier()

outlet = effluent()

splt1 = splitter()
splt2 = splitter()

waste = WAS()


wwtp = [inlet,
        p1, p2, p3, p4, p5, p6, RAS, p8, IR,
        AX, OX, fc, outlet,
        waste, splt1, splt2]

SRT = 15  # day

def construct():
    # make an MLE plant
    inlet.set_downstream_main(p1)
    p1.set_downstream_main(AX)
    AX.set_downstream_main(p2)
    p2.set_downstream_main(OX)
    OX.set_downstream_main(p3)
    p3.set_downstream_main(splt1)
    splt1.set_downstream_main(p4)
    splt1.set_downstream_side(IR)

    IR.set_downstream_main(AX)  # NOxN recirc.

    p4.set_downstream_main(fc)

    fc.set_downstream_main(p5)
    fc.set_downstream_side(p6)

    p5.set_downstream_main(outlet)

    p6.set_downstream_main(splt2)

    splt2.set_as_SRT_controller(True)
    splt2.set_downstream_main(RAS)
    splt2.set_downstream_side(p8)

    RAS.set_downstream_main(AX)
    p8.set_downstream_main(waste)

    inlet.set_mainstream_flow(37800)

    splt1.set_sidestream_flow(3.0*37800)  #IR
    splt2.set_mainstream_flow(0.5*37800)  #RAS
    
    AX.set_model_condition(10, 0.0)
    OX.set_model_condition(10, 2.0)

    AX.set_active_vol(4000)
    OX.set_active_vol(10000)

    print("MLE PFD constructed.")

    return wwtp
 

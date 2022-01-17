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
#    Definition of a Completely-mixed Stirred Tank Reactor (CSTR) Process Flow.
#
#
#    Process Flow Diagram:
#
#    Inlet --p1-> reactor(ra) --p2-> outlet
#
#
#    Author: Kai Zhang
#
# Change Log: 
# 20201129 KZ: re-run after package structure update
# 20200708 KZ: init
#

from PooPyLab.unit_procs.streams import pipe
from PooPyLab.unit_procs.streams import influent, effluent
from PooPyLab.unit_procs.bio import asm_reactor


inlet = influent()
p1 = pipe()

ra = asm_reactor()
p2 = pipe()

outlet = effluent()

wwtp = [inlet,
        p1, ra, p2,
        outlet]

SRT = 10  # day, in CSTR, this is not a CONTROLLED operation param.

def construct():
    # make an CMAS plant
    inlet.set_downstream_main(p1)
    p1.set_downstream_main(ra)
    ra.set_downstream_main(p2)
    p2.set_downstream_main(outlet)

    inlet.set_mainstream_flow(37800)
    
    ra.set_model_condition(10, 2.0)
    ra.set_active_vol(37800*2)  # CSTR SRT = HRT, let HRT = 2 d

    print("CMAS PFD constructed.")

    return wwtp
 

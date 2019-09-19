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
#
#    Definition of a PFD with an influent, an ASMReactor, and an effluent
#    connected via pipes.
#
#
#    Process Flow Diagram:
#
#    inlet --p1-> reactor --p2-> outlet
#
#
#    Author: Kai Zhang
#
# Change Log: 
# 20190911 KZ: set_model_condition replaced set_ASM_condition
# 20190815 KZ: init
#

from unit_procs.streams import influent, effluent, pipe
from unit_procs.bio import asm_reactor
from utils.pfd import check, show


inlet = influent()
p1 = pipe()
p2 = pipe()
reactor = asm_reactor()
outlet = effluent()

wwtp = [inlet,
        p1, p2,
        reactor,
        outlet]

def construct():
    inlet.set_downstream_main(p1)
    p1.set_downstream_main(reactor)
    reactor.set_downstream_main(p2)
    reactor.set_model_condition(10, 2)
    reactor.set_active_vol(37800*9)
    p2.set_downstream_main(outlet)

    print("PFD constructed.")

    return wwtp
 

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
#    Definition of a simple PFD with an influent, a splitter, a WAS, an
#    effluent and pipes.
#
#
#    Process Flow Diagram:
#
#    Inlet --p1-> splt --p2-> outlet
#                   |
#                   |
#                   |
#                   -----p3-> waste
#
#    Author: Kai Zhang
#
# Change Log: 
#   2019-08-15 KZ: init
#

from unit_procs.streams import influent, effluent, pipe, splitter, WAS


inlet = influent()
p1 = pipe()
p2 = pipe()
p3 = pipe()
splt = splitter()
waste = WAS()
outlet = effluent()


wwtp = [inlet,
        p1, p2, p3,
        splt,
        waste,
        outlet]

def construct():
    inlet.set_downstream_main(p1)
    p1.set_downstream_main(splt)
    splt.set_downstream_main(p2)
    splt.set_downstream_side(p3)
    p2.set_downstream_main(outlet)
    p3.set_downstream_main(waste)

    splt.set_as_SRT_controller(True)

    print("PFD constructed.")

    return wwtp
 

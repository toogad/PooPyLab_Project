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
#    Definition of an influent connected with an effluent via a pipe
#
#
#    Process Flow Diagram:
#
#    Inlet --p1-> outlet
#
#
#    Author: Kai Zhang
#
# Change Log: 
#   2019-08-15 KZ: init
#

from unit_procs.streams import influent, effluent, pipe
from utils.pfd import check, show


inlet = influent()
p1 = pipe()

outlet = effluent()

wwtp = [inlet,
        p1,
        outlet]

def construct():
    inlet.set_downstream_main(p1)
    p1.set_downstream_main(outlet)

    print("PFD constructed.")

    return wwtp
 

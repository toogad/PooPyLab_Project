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
#
#    Definition of global utility functions related to the process flow
#    diagram (PFD).
#
#    Author: Kai Zhang
#
# Change Log: 
#   2019-02-12 KZ: init
#


from unit_procs.streams import influent, effluent, WAS, pipe, splitter
from unit_procs.bio import asm_reactor
from unit_procs.physchem import final_clarifier


def check_connection(pfd=[]):
    loose_end = 0
    for unit in pfd:
        if not unit.has_discharger():
            print(unit.__name__, "'s upstream is not connected")
            loose_end += 1
        if unit.has_sidestream():
            if not unit.side_outlet_connected():
                print(unit.__name__, "'s sidestream is not connected")
                loose_end += 1
        elif not unit.main_outlet_connected():
            print(unit.__name__,"'s main downstream is not connected")
            loose_end +=1 
    if loose_end == 0:
        print("The PFD is ready for simulation")
    else:
        print(loose_end, " connecton(s) to be fixed.")
    return loose_end


def show_pfd(wwtp=[]):
    for unit in wwtp:
        print(unit.__name__, ": receives from:", end=" ")
        if isinstance(unit, influent):
            print("None")
        else:
            upstr = unit.get_upstream()
            for dschgr in upstr:
                print(dschgr.__name__, ",", end=" ")
            print()
        print("         : discharges to:", end=" ")
        if isinstance(unit, effluent) or not unit.main_outlet_connected():
            print("None")
        elif unit.main_outlet_connected():
            print(unit.get_downstream_main().__name__, end="(main)")
        else:
            print("None")
        if unit.has_sidestream():
            print(", and ", end=" ")
            if unit.get_downstream_side() == None:
                print("None", end="")
            else:
                print(unit.get_downstream_side().__name__, end="")
            print("(side)")
        else:
            print()
    return None


def flow_balance(wwtp=[]):
    pass

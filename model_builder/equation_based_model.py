#!/usr/bin/python3

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
# 20201129 KZ: re-run after package structure update
# 20190920 KZ: revised to match other testing results
# 20190724 KZ: init
#

def eqs_sys(Inlet_1_MO_FLOW, Inlet_1_MO_COMP,
            Pipe_1_IN_FLOW, Pipe_1_MO_FLOW, Pipe_1_IN_COMP, Pipe_1_MO_COMP):
    # list of RHS below
    RHS = []

    # Inlet:
    RHS.append(Inlet_1_MO_FLOW - 3780.0)
    RHS.append(Inlet_1_MO_COMP[0] - 0)  # MO_COMP[0] is DO in this prototype
    RHS.append(Inlet_1_MO_COMP[1] - 200)  #MO_COMP[1] is S_S
    RHS.append(Inlet_1_MO_COMP[2] - 0)  # MO_COMP[2] is X_BH

    # p1:
    RHS.append(Pipe_1_IN_FLOW - Inlet_1_MO_FLOW)
    for i in range(len(Inlet_1_MO_COMP)):
        RHS.append(Pipe_1_IN_COMP[i] - Inlet_1_MO_COMP[i])
    for i in range(len(Inlet_1_MO_COMP)):
        RHS.append(Pipe_1_MO_COMP[i] - Pipe_1_IN_COMP[i])
    #TODO: continue to build the model out






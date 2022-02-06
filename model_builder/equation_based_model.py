#!/usr/bin/python3

# This file is part of PooPyLab.
#
# PooPyLab is a simulation software for biological wastewater treatment processes using International Water Association
# Activated Sludge Models.
#
#    Copyright (C) Kai Zhang
#
#    PooPyLab is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
#    License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any
#    later version.
#
#    PooPyLab is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
#    warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
#    details.
#
#    You should have received a copy of the GNU General Public License along with PooPyLab. If not, see
#    <http://www.gnu.org/licenses/>.
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
# 20220203 KZ: use for equation based simulation prototyping
# 20201129 KZ: re-run after package structure update
# 20190920 KZ: revised to match other testing results
# 20190724 KZ: init
#

# Inlet (Influent_1):
#   Known:  IN_FLOW, model components from fractionation estimate,
#           Flow_Source: Inlet = UPS, MainOutlet = UPS, SideOutlet = PRG
#   Find:   MO_FLOW, MO_COMPS

# p1 (Pipe_1):
#   Known:  Flow_Source = UPS
#   Find:   IN_FLOW, MO_FLOW, IN_COMPS, MO_COMPS

# ra (ASMReactor_1):
#   Known:  Kinetic Parameters, Stoichiometrics, Mixed Liquor Temperature, Mixed Liquor DO,
#           Flow_Source = UPS
#   Find:   IN_FLOW, MO_FLOW, IN_COMPS, MO_COMPS

# p2 (Pipe_2):
#   Known:  Flow_Source = 


def eqs_sys(Influent_1_MO_FLOW, Influent_1_MO_COMPS,
            Pipe_1_IN_FLOW, Pipe_1_MO_FLOW, Pipe_1_IN_COMPS, Pipe_1_MO_COMPS,
            ASMReactor_1_IN_FLOW, ASMReactor_1_MO_FLOW, ASMReactor_1_IN_COMPS, ASMReactor_1_MO_COMPS):
    # list of RHS below
    RHS = []

    # number of model components:
    num_comps = len(Influent_1_MO_COMPS)


    # Inlet:
    RHS.append(Influent_1_MO_FLOW - 3780.0)
    RHS.append(Influent_1_MO_COMPS[0] - 0)  # MO_COMPS[0] is DO in this prototype
    RHS.append(Influent_1_MO_COMPS[1] - 200)  #MO_COMPS[1] is S_S
    RHS.append(Influent_1_MO_COMPS[2] - 0)  # MO_COMPS[2] is X_BH


    # p1:
    RHS.append(Pipe_1_IN_FLOW - Influent_1_MO_FLOW)
    RHS.append(Pipe_1_MO_FLOW - Pipe_1_IN_FLOW)
    for i in range(num_comps):
        RHS.append(Pipe_1_IN_COMPS[i] - Influent_1_MO_COMPS[i])
    for i in range(num_comps):
        RHS.append(Pipe_1_MO_COMPS[i] - Pipe_1_IN_COMPS[i])


    # ra:
    RHS.append(ASMReactor_1_IN_FLOW - Influent_1_MO_FLOW - RAS_MO_FLOW)
    RHS.append(ASMReactor_1_MO_FLOW - ASMReactor_1_IN_FLOW)

    for i in range(num_comps):
        RHS.append(ASMReactor_1_IN_COMPS[i]
                    - (Influent_1_MO_COMPS[i] * Influent_1_MO_FLOW + Pipe_1_MO_COMPS[i] * Pipe_1_MO_FLOW)
                        / ASMReactor_1_IN_FLOW)

    ASMReactor_1_MONOD[0] = ASMReactor_1_MO_COMPS[1] / (ASMReactor_1_KS + ASMReactor_1_MO_COMPS[1])

    ASMReactor_1_RATE[0] = ASMReactor_1_MUHAT * ASMReactor_1_MONOD[0] * ASMReactor_1_MO_COMPS[2]

    ASMReactor_1_OVERALLRATE[0] = (ASMReactor_1_YH - 1) / ASMReactor_1_YH * ASMReactor_1_RATE[0]

    ASMReactor_1_OVERALLRATE[1] = -1 / ASMReactor_1_YH * ASMReactor_1_RATE[0]

    ASMReactor_1_OVERALLRATE[2] = ASMReactor_1_RATE[0]

    for i in range(num_comps):
        RHS.append((ASMReactor_1_IN_FLOW * ASMReactor_1_IN_COMPS[i] - ASMReactor_1_MO_FLOW * ASMReactor_1_MO_COMPS[i])
                    + ASMReactor_1_OVERALLRATE[i])


    # p2:
    RHS.append(Pipe_2_IN_FLOW - ASMReactor_1_MO_FLOW)
    RHS.append(Pipe_2_MO_FLOW - Pipe_2_IN_FLOW)
    for i in range(num_comps):
        RHS.append(Pipe_2_IN_COMPS[i] - ASMReactor_1_MO_COMPS[i])
    for i in range(num_comps):
        RHS.append(Pipe_2_MO_COMPS[i] - Pipe_2_IN_COMPS[i])


    # Final_Clar, assuming it is a perfect clarifier for prototype testing
    RHS.append(FinalClarifier_1_IN_FLOW - Pipe_2_MO_FLOW)
    RHS.append(FinalClarifier_1_IN_FLOW - FinalClarifier_1_SO_FLOW - FinalClarifier_1_MO_FLOW)
    RHS.append(FinalClarifier_1_SO_FLOW - Pipe_4_IN_FLOW)

    for i in range(num_comps):
        RHS.append(FinalClarifier_1_IN_COMPS[i] - Pipe_2_MO_COMPS[i])

    RHS.append(FinalClarifier_1_MO_COMPS[0] - 0)  # assume DO is depeleted
    RHS.append(FinalClarifier_1_MO_COMPS[1] - FinalClarifier_1_IN_COMPS[1])
    RHS.append(FinalClarifier_1_MO_COMPS[2] - 0)  # assume perfect solids-liquid separation

    RHS.append(FinalClarifier_1_SO_COMPS[0] - 0)
    RHS.append(FinalClarifier_1_SO_COMPS[1] - FinalClarifier_1_IN_COMPS[1])
    RHS.append(FinalClarifier_1_SO_COMPS[2]
                - (FinalClarifier_1_IN_FLOW * FinalClarifier_1_IN_COMPS[2]
                    - FinalClarifier_1_MO_FLOW * FinalClarifier_1_MO_COMPS[2])
                    / FinalClarifier_1_SO_FLOW)


    # p3
    RHS.append(Pipe_3_IN_FLOW - Pipe_3_MO_FLOW)
    RHS.append(Pipe_3_MO_FLOW - Effluent_1_IN_FLOW)
    for i in range(num_comps):
        RHS.append(Pipe_3_IN_COMPS[i] - FinalClarifier_1_MO_COMPS[i])
    for i in range(num_comps):
        RHS.append(Pipe_3_MO_COMPS[i] - Pipe_3_IN_COMPS[i])


    # p4
    RHS.append(Pipe_4_IN_FLOW - Splitter_1_IN_FLOW)
    RHS.append(Pipe_4_MO_FLOW - FinalClarifier_1_IN_FLOW)
    for i in range(num_comps):
        RHS.append(Pipe_4_IN_COMPS[i] - FinalClarifier_1_MO_COMPS[i])
    for i in range(num_comps):
        RHS.append(Pipe_4_MO_COMPS[i] - Pipe_4_IN_COMPS[i])

    
    # splt1, SRT Controlling
    RHS.append(Splitter_1_IN_FLOW - Splitter_1_SO_FLOW - Splitter_1_MO_FLOW)
    RHS.append(Splitter_1_MO_FLOW - RAS_IN_FLOW)
    RHS.append(Splitter_1_SO_FLOW - Pipe_5_IN_FLOW)
    
    for i in range(num_comps):
        RHS.append(Splitter_1_IN_COMPS[i] - FinalClarifier_1_SO_COMPS[i])
    for i in range(num_comps):
        RHS.append(Splitter_1_MO_COMPS[i] - FinalClarifier_1_IN_COMPS[i])
    for i in range(num_comps):
        RHS.append(Splitter_1_SO_COMPS[i] - FinalClarifier_1_IN_COMPS[i])

    
    # RAS
    RHS.append(RAS_IN_FLOW - USER_SET_RAS_IN_FLOW)
    RHS.append(RAS_MO_FLOW - RAS_IN_FLOW)
    for i in range(num_comps):
        RHS.append(RAS_IN_COMPS[i] - Splitter_1_MO_COMPS[i])
    for i in range(num_comps):
        RHS.append(RAS_MO_COMPS[i] - RAS_IN_COMPS[i])


    # p5
    RHS.append(Pipe_5_IN_FLOW - Pipe_5_MO_FLOW)
    RHS.append(Pipe_5_MO_FLOW - WAS_1_IN_FLOW)
    for i in range(num_comps):
        RHS.append(Pipe_5_IN_COMPS[i] - Splitter_1_SO_COMPS[i])
    for i in range(num_comps):
        RHS.append(Pipe_5_MO_COMPS[i] - Pipe_5_IN_COMPS[i])


    # WAS
    RHS.append(WAS_1_IN_FLOW 
                - (ASMReactor_1_MO_COMPS[2] * ASMReactor_1_VOLUME / Target_SRT
                    - Effluent_1_IN_COMPS[2] * Effluent_1_IN_FLOW)
                * 1.42 / Pipe_5_MO_COMPS[2])
    for i in range(num_comps):
        RHS.append(WAS_1_IN_COMPS[i] - Pipe_5_MO_COMPS[i])
    
    
    # Effluent
    RHS.append(Effluent_1_IN_FLOW - (Influent_1_MO_FLOW - WAS_1_IN_FLOW))
    for i in range(num_comps):
        RHS.append(Effluent_1_IN_COMPS[i] - Pipe_3_MO_COMPS[i])
    
    return RHS[:]
    #TODO: continue to build the model out






#!/usr/bin/env python

# This is a test program for the PooPyLab biological wastewater treatment
# software package.
# The main objective of this test program is to partition and tear the 
# PFD in order to determine the calculation order.

# The PFD (flow sheet) used in this test is from Chapter 8 of 
# Systematic Methods of Chemical Process Design (1997)
# Lorenz T. Biegler, Ignacio E. Grossmann, Arthur W. Westerberg

import influent, effluent, was, splitter, reactor, clarifier, pipe
from Test_Functions3 import *
#import constants
import os

os.system('cls' if os.name == 'nt' else 'clear')


# MAIN TEST:
WWTP = []
Inf, Pipe, React, Splt, Eff = [], [], [], [], []


for i in range(4):
    Inf.append(influent.influent())
    Inf[i].set_flow(10)#TODO: Units to be noted in ''' ''' if a function asks for params
    Eff.append(effluent.effluent())

for i in range(35):
    Pipe.append(pipe.pipe())
    
for i in range(11):
    Splt.append(splitter.splitter())

for i in range(7):
    React.append(reactor.asm_reactor())

Splt[0].__name__ = 'C'
Splt[1].__name__ = 'F'
Splt[2].__name__ = 'G'
Splt[3].__name__ = 'R'
Splt[4].__name__ = 'S'
Splt[5].__name__ = 'O'
Splt[6].__name__ = 'L'
Splt[7].__name__ = 'M'
Splt[8].__name__ = 'K'
Splt[9].__name__ = 'I'
Splt[10].__name__ = 'N'

Clarifier = clarifier.final_clarifier()
Clarifier.__name__ = "D"

WAS1 = was.WAS()

React[0].__name__ = 'A'
React[1].__name__ = 'B'
React[2].__name__ = 'E'
React[3].__name__ = 'H'
React[4].__name__ = 'Q'
React[5].__name__ = 'J'
React[6].__name__ = 'P'


Inf[0].set_downstream_main(Pipe[0])
Inf[0].set_flow(40)
Pipe[0].set_downstream_main(React[2])
React[2].set_downstream_main(Pipe[1])
Pipe[1].set_downstream_main(React[0])

Inf[1].set_downstream_main(Pipe[30])
Pipe[30].set_downstream_main(React[0])
React[0].set_downstream_main(Pipe[2])
Pipe[2].set_downstream_main(React[1])
React[1].set_downstream_main(Pipe[3])
Pipe[3].set_downstream_main(Splt[0])

Splt[0].set_downstream_main(Pipe[27])
Splt[0].set_downstream_side(Pipe[4])
Splt[0].set_sidestream_flow(1)

Pipe[27].set_downstream_main(Clarifier)
Pipe[4].set_downstream_main(Splt[1])

Splt[1].set_downstream_main(Pipe[5])
Splt[1].set_downstream_side(Pipe[24])
Splt[1].set_sidestream_flow(0.5)

Pipe[24].set_downstream_main(Splt[2])
Pipe[5].set_downstream_main(React[3])

Splt[2].set_downstream_main(Pipe[26])
Splt[2].set_downstream_side(Pipe[25])
Splt[2].set_sidestream_flow(0.1)

Pipe[26].set_downstream_main(Splt[0])
Pipe[25].set_downstream_main(Eff[3])

Clarifier.set_downstream_main(Pipe[29])
Clarifier.set_downstream_side(Pipe[28])
Clarifier.set_sidestream_flow(0.2)

Pipe[29].set_downstream_main(React[2])
Pipe[28].set_downstream_main(React[3])

React[3].set_downstream_main(Pipe[6])

Pipe[6].set_downstream_main(Splt[9])

Splt[9].set_downstream_main(Pipe[23])
Splt[9].set_downstream_side(Pipe[7])
Splt[9].set_sidestream_flow(0.02)

Pipe[23].set_downstream_main(React[4])
Pipe[7].set_downstream_main(React[5])

React[5].set_downstream_main(Pipe[8])
React[4].set_downstream_main(Pipe[13])

Pipe[13].set_downstream_main(Splt[3])

Splt[3].set_downstream_main(Pipe[14])
Splt[3].set_downstream_side(Pipe[15])
Splt[3].set_sidestream_flow(0.4)

Pipe[14].set_downstream_main(React[5])
Pipe[15].set_downstream_main(Eff[2])

Pipe[8].set_downstream_main(Splt[8])

Splt[8].set_downstream_main(Pipe[9])
Splt[8].set_downstream_side(Pipe[19])
Splt[8].set_sidestream_flow(0.35)

Pipe[19].set_downstream_main(Eff[1])

Pipe[9].set_downstream_main(Splt[6])

Splt[6].set_downstream_main(Pipe[31])
Splt[6].set_downstream_side(Pipe[10])
Splt[6].set_sidestream_flow(0.05)

Pipe[31].set_downstream_main(Splt[7])
Pipe[10].set_downstream_main(Splt[5])

Splt[7].set_downstream_main(Pipe[22])
Splt[7].set_downstream_side(Pipe[32])
Splt[7].set_sidestream_flow(0.002)

Pipe[22].set_downstream_main(Splt[4])
Pipe[32].set_downstream_main(Splt[10])

Splt[10].set_downstream_main(Pipe[33])
Splt[10].set_downstream_side(Pipe[34])
Splt[10].set_sidestream_flow(0.0001)
Pipe[33].set_downstream_main(Eff[0])
Pipe[34].set_downstream_main(Splt[6])

Splt[4].set_downstream_main(Pipe[12])
Splt[4].set_downstream_side(Pipe[16])
Splt[4].set_sidestream_flow(0.03)
Splt[4].set_as_SRT_controller(True)

Pipe[16].set_downstream_main(WAS1)
Pipe[12].set_downstream_main(React[4])

Splt[5].set_downstream_main(Pipe[17])
Splt[5].set_downstream_side(Pipe[11])
Splt[5].set_sidestream_flow(0.1)
Pipe[11].set_downstream_main(Splt[4])
Pipe[17].set_downstream_main(React[6])

React[6].set_downstream_main(Pipe[18])
Pipe[18].set_downstream_main(Splt[8])

Inf[2].set_downstream_main(Pipe[20])
Inf[2].set_flow(10)
Pipe[20].set_downstream_main(Splt[5])

Inf[3].set_downstream_main(Pipe[21])
Inf[3].set_flow(20)
Pipe[21].set_downstream_main(React[6])

WWTP = Inf + Pipe + React + Splt + Eff
WWTP.append(WAS1)
WWTP.append(Clarifier)

response = input("continue?")

print("Begin Connection Test...")

CheckPlantConnection(WWTP)
CheckUpstream(WWTP)
CheckDownstream(WWTP)

Groups = FindGroups(WWTP)

for sub in Groups:
    print("[ ", end=' ')
    for unit in sub:
        print(unit.__name__,";", end=' ')
    print("]")

ElementalCircuits = []
import pdb
pdb.set_trace()
FindLoops(Groups, ElementalCircuits)
print(len(ElementalCircuits))
for subgroup in ElementalCircuits:
    print(len(subgroup))
    print("[ ", end=' ')
    for t in subgroup:
        print(t.__name__, "; ", end=' ')
    print("]")

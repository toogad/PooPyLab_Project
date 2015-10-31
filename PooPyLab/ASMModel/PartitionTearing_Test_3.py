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
    Inf.append(influent.Influent())
    Inf[i].SetFlow(10)#TODO: Units to be noted in ''' ''' if a function asks for params
    Eff.append(effluent.Effluent())

for i in range(35):
    Pipe.append(pipe.Pipe())
    
for i in range(11):
    Splt.append(splitter.Splitter())

for i in range(7):
    React.append(reactor.ASMReactor())

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

Clarifier = clarifier.Final_Clarifier()
Clarifier.__name__ = "D"

WAS1 = was.WAS()

React[0].__name__ = 'A'
React[1].__name__ = 'B'
React[2].__name__ = 'E'
React[3].__name__ = 'H'
React[4].__name__ = 'Q'
React[5].__name__ = 'J'
React[6].__name__ = 'P'


Inf[0].SetDownstreamMainUnit(Pipe[0])
Inf[0].SetFlow(40)
Pipe[0].SetDownstreamMainUnit(React[2])
React[2].SetDownstreamMainUnit(Pipe[1])
Pipe[1].SetDownstreamMainUnit(React[0])

Inf[1].SetDownstreamMainUnit(Pipe[30])
Pipe[30].SetDownstreamMainUnit(React[0])
React[0].SetDownstreamMainUnit(Pipe[2])
Pipe[2].SetDownstreamMainUnit(React[1])
React[1].SetDownstreamMainUnit(Pipe[3])
Pipe[3].SetDownstreamMainUnit(Splt[0])

Splt[0].SetDownstreamMainUnit(Pipe[27])
Splt[0].SetDownstreamSideUnit(Pipe[4])
Splt[0].SetSidestreamFlow(1)

Pipe[27].SetDownstreamMainUnit(Clarifier)
Pipe[4].SetDownstreamMainUnit(Splt[1])

Splt[1].SetDownstreamMainUnit(Pipe[5])
Splt[1].SetDownstreamSideUnit(Pipe[24])
Splt[1].SetSidestreamFlow(0.5)

Pipe[24].SetDownstreamMainUnit(Splt[2])
Pipe[5].SetDownstreamMainUnit(React[3])

Splt[2].SetDownstreamMainUnit(Pipe[26])
Splt[2].SetDownstreamSideUnit(Pipe[25])
Splt[2].SetSidestreamFlow(0.1)

Pipe[26].SetDownstreamMainUnit(Splt[0])
Pipe[25].SetDownstreamMainUnit(Eff[3])

Clarifier.SetDownstreamMainUnit(Pipe[29])
Clarifier.SetDownstreamSideUnit(Pipe[28])
Clarifier.SetSidestreamFlow(0.2)

Pipe[29].SetDownstreamMainUnit(React[2])
Pipe[28].SetDownstreamMainUnit(React[3])

React[3].SetDownstreamMainUnit(Pipe[6])

Pipe[6].SetDownstreamMainUnit(Splt[9])

Splt[9].SetDownstreamMainUnit(Pipe[23])
Splt[9].SetDownstreamSideUnit(Pipe[7])
Splt[9].SetSidestreamFlow(0.02)

Pipe[23].SetDownstreamMainUnit(React[4])
Pipe[7].SetDownstreamMainUnit(React[5])

React[5].SetDownstreamMainUnit(Pipe[8])
React[4].SetDownstreamMainUnit(Pipe[13])

Pipe[13].SetDownstreamMainUnit(Splt[3])

Splt[3].SetDownstreamMainUnit(Pipe[14])
Splt[3].SetDownstreamSideUnit(Pipe[15])
Splt[3].SetSidestreamFlow(0.4)

Pipe[14].SetDownstreamMainUnit(React[5])
Pipe[15].SetDownstreamMainUnit(Eff[2])

Pipe[8].SetDownstreamMainUnit(Splt[8])

Splt[8].SetDownstreamMainUnit(Pipe[9])
Splt[8].SetDownstreamSideUnit(Pipe[19])
Splt[8].SetSidestreamFlow(0.35)

Pipe[19].SetDownstreamMainUnit(Eff[1])

Pipe[9].SetDownstreamMainUnit(Splt[6])

Splt[6].SetDownstreamMainUnit(Pipe[31])
Splt[6].SetDownstreamSideUnit(Pipe[10])
Splt[6].SetSidestreamFlow(0.05)

Pipe[31].SetDownstreamMainUnit(Splt[7])
Pipe[10].SetDownstreamMainUnit(Splt[5])

Splt[7].SetDownstreamMainUnit(Pipe[22])
Splt[7].SetDownstreamSideUnit(Pipe[32])
Splt[7].SetSidestreamFlow(0.002)

Pipe[22].SetDownstreamMainUnit(Splt[4])
Pipe[32].SetDownstreamMainUnit(Splt[10])

Splt[10].SetDownstreamMainUnit(Pipe[33])
Splt[10].SetDownstreamSideUnit(Pipe[34])
Splt[10].SetSidestreamFlow(0.0001)
Pipe[33].SetDownstreamMainUnit(Eff[0])
Pipe[34].SetDownstreamMainUnit(Splt[6])

Splt[4].SetDownstreamMainUnit(Pipe[12])
Splt[4].SetDownstreamSideUnit(Pipe[16])
Splt[4].SetSidestreamFlow(0.03)
Splt[4].SetAsSRTController(True)

Pipe[16].SetDownstreamMainUnit(WAS1)
Pipe[12].SetDownstreamMainUnit(React[4])

Splt[5].SetDownstreamMainUnit(Pipe[17])
Splt[5].SetDownstreamSideUnit(Pipe[11])
Splt[5].SetSidestreamFlow(0.1)
Pipe[11].SetDownstreamMainUnit(Splt[4])
Pipe[17].SetDownstreamMainUnit(React[6])

React[6].SetDownstreamMainUnit(Pipe[18])
Pipe[18].SetDownstreamMainUnit(Splt[8])

Inf[2].SetDownstreamMainUnit(Pipe[20])
Inf[2].SetFlow(10)
Pipe[20].SetDownstreamMainUnit(Splt[5])

Inf[3].SetDownstreamMainUnit(Pipe[21])
Inf[3].SetFlow(20)
Pipe[21].SetDownstreamMainUnit(React[6])

WWTP = Inf + Pipe + React + Splt + Eff
WWTP.append(WAS1)
WWTP.append(Clarifier)

response = raw_input("continue?")

print "Begin Connection Test..."

CheckPlantConnection(WWTP)
CheckUpstream(WWTP)
CheckDownstream(WWTP)

Groups = FindGroups(WWTP)

for sub in Groups:
    print "[ ",
    for unit in sub:
        print unit.__name__,";",
    print "]"

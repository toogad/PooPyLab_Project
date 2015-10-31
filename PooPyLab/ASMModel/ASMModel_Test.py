#!/usr/bin/env python

# This is a test program for the PooPyLab biological wastewater treatment
# software package.
# The main objective of this test program is to connect units and find out
# if they can communicate with each other appropriately. The main 
# indicators will be the flow balance among all units.
#   Last Update:
#   June 24, 2015 KZ: rewrote a lines influenced by the updated Splitter
#       and Pipe classes

import influent, effluent, was, splitter, reactor, clarifier, pipe
from Test_Functions3 import *
#import constants
import os

os.system('cls' if os.name == 'nt' else 'clear')

WWTP = []

Inf = influent.Influent()

Pipe1 = pipe.Pipe()
Pipe2 = pipe.Pipe()
Pipe3 = pipe.Pipe()
Pipe4 = pipe.Pipe()
Pipe5 = pipe.Pipe()
Pipe6 = pipe.Pipe()

Reactor1 = reactor.ASMReactor()

Clar1 = clarifier.Final_Clarifier()

Splt1 = splitter.Splitter()

Eff = effluent.Effluent()

WAS1 = was.WAS()



Inf.SetFlow(10)#TODO: Units to be noted in ''' ''' if a function asks for params

#------------Connection Test------------
def ConnectWWTPUnits():

    WWTP.append(Inf)

    Inf.SetDownstreamMainUnit(Pipe1)
    WWTP.append(Pipe1)

    Pipe1.SetDownstreamMainUnit(Reactor1)
    WWTP.append(Reactor1)

    Reactor1.SetDownstreamMainUnit(Pipe2)
    WWTP.append(Pipe2)

    Pipe2.SetDownstreamMainUnit(Clar1)
    WWTP.append(Clar1)

    Clar1.SetDownstreamMainUnit(Pipe3)
    WWTP.append(Pipe3)

    Pipe3.SetDownstreamMainUnit(Eff)
    WWTP.append(Eff)

    #Clar1.SetupSidestream(Pipe4, 5)
    Clar1.SetDownstreamSideUnit(Pipe4)
    Clar1.SetSidestreamFlow(5)
    WWTP.append(Pipe4)

    Pipe4.SetDownstreamMainUnit(Splt1)
    WWTP.append(Splt1)

    Splt1.SetDownstreamMainUnit(Pipe5)
    WWTP.append(Pipe5)

    Pipe5.SetDownstreamMainUnit(Reactor1)

    #Splt1.SetupSidestream(Pipe6, 1)
    Splt1.SetDownstreamSideUnit(Pipe6)
    Splt1.SetSidestreamFlow(1)
    WWTP.append(Pipe6)

    Splt1.SetAsSRTController(True)

    Pipe6.SetDownstreamMainUnit(WAS1)
    WWTP.append(WAS1)
#End of ConnectWWTPUnits()


response = raw_input("continue?")

print "Begin Connection Test..."

ConnectWWTPUnits()
CheckPlantConnection(WWTP)
CheckUpstream(WWTP)
CheckDownstream(WWTP)
print "End Connection Test"
# Connection Test Summary: SO FAR SO GOOD!!
response = raw_input("continue?")

#------------Disconnection Test---------
# PooPyLab is NOT Microsoft Visio. If the user is to re-direct the connected pipe to another 
# object, he/she would need to remove that pipe first, and then redraw a new pipe to the 
# desired object.
print "Begin Disconnection Test..."

Reactor1.RemoveUpstreamUnit(Pipe1)
Pipe5.RemoveUpstreamUnit(Splt1)
WAS1.RemoveUpstreamUnit(Pipe6)
Splt1.RemoveUpstreamUnit(Pipe4)
Pipe6.RemoveUpstreamUnit(Splt1) 
Clar1.RemoveUpstreamUnit(Pipe2)
Pipe2.RemoveUpstreamUnit(Reactor1)
Eff.RemoveUpstreamUnit(Pipe3)
Pipe3.RemoveUpstreamUnit(Clar1)

CheckPlantConnection(WWTP)

CheckUpstream(WWTP)
print
CheckDownstream(WWTP)
response = raw_input("continue?")

print "Reconnecting..."
WWTP = []
ConnectWWTPUnits()
CheckPlantConnection(WWTP)
CheckUpstream(WWTP)
CheckDownstream(WWTP)

print "End Disconnection Test."
response = raw_input("continue?")
print len(WWTP) 
#The connection test, disconnection test, and reconnection of the WWTP show that the 
# PooPyLab classes were capable of communicate to one another in terms of upstream
# and downstream relations.

print "=====Begin Receive and Discharge Tests==========="



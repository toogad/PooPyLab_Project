
# This is a test program for the PooPyLab biological wastewater treatment
# software package.
# The main objective of this test program is to connect units and find out
# if they can communicate with each other appropriately. The main 
# indicators will be the flow balance among all units.

import influent, effluent, was, splitter, reactor, clarifier, pipe
#import constants

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

Inf.SetFlow(10)#Units to be noted in ''' ''' if a function asks for params

#------------Connection Test------------
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

Clar1.SetupSideStream(Pipe4, 5)
WWTP.append(Pipe4)

Pipe4.SetDownstreamMainUnit(Splt1)
WWTP.append(Splt1)

Splt1.SetDownstreamMainUnit(Pipe5)
WWTP.append(Pipe5)

Pipe5.SetDownstreamMainUnit(Reactor1)

Splt1.SetupSideStream(Pipe6, 1)
WWTP.append(Pipe6)

Splt1.SetAsSRTController(True)

Pipe6.SetDownstreamMainUnit(WAS1)
WWTP.append(WAS1)


print "Checking units' upstream processes..."
for unit in WWTP:
    upstr = []
    print unit.__name__, "'s upstream has ",
    if unit.GetUpstreamUnits():
        upstr = unit.GetUpstreamUnits().keys()
    else:
        print None
    for element in upstr:
        print element.__name__, "; ",
    print

print
print "Checking units' downstream processes..."
for unit in WWTP:
    print unit.__name__, "'s Main downstream has ", 
    if unit.GetDownstreamMainUnit():
        print unit.GetDownstreamMainUnit().__name__
    else:
        print None
    if unit.HasSidestream():
        print unit.__name__, "'s Side downstream has ", unit.GetDownstreamSideUnit().__name__

print
# Connection Test Summary: SO FAR SO GOOD!!

#------------Disconnection Test---------







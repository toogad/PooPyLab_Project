
# This is a test program for the PooPyLab biological wastewater treatment
# software package.
# The main objective of this test program is to connect units and find out
# if they can communicate with each other appropriately. The main 
# indicators will be the flow balance among all units.

import influent, effluent, was, splitter, reactor, clarifier, pipe
#import constants

def CheckPlantConnection(WWTP = []):
    LooseEnd = 0
    for unit in WWTP:
        if not unit.UpstreamConnected():
            print unit.__name__,"'s upstream is not connected"
            LooseEnd += 1
        if unit.HasSidestream():
            if not unit.SideOutletConnected():
                print unit.__name__ ,"'s sidestream is not connected"
                LooseEnd += 1
        elif not unit.MainOutletConnected():
            print unit.__name__,"'s main downstream is not connected"
            LooseEnd += 1 
    if not LooseEnd:
        print "WWTP is ready for simulation"
    else:
        print LooseEnd, " connecton(s) to be fixed."
# End of CheckPlantConnection()


def CheckUpstream(WWTP = []):
    ''' Check the upstream connection of units in WWTP'''
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
# End of CheckUpstream()

def CheckDownstream(WWTP = []):
    ''' Check the downstream connection of units in WWTP'''
    print "Checking units' downstream processes..."
    for unit in WWTP:
        print unit.__name__, "'s Main downstream has ", 
        if unit.GetDownstreamMainUnit():
            print unit.GetDownstreamMainUnit().__name__
        else:
            print None
        if unit.HasSidestream():
            print unit.__name__, "'s Side downstream has ", 
            if unit.GetDownstreamSideUnit():
                print unit.GetDownstreamSideUnit().__name__
            else:
                print None
    print
# End of CheckDownstream()

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
    print "Begin Connection Test..."

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

    Clar1.SetupSidestream(Pipe4, 5)
    WWTP.append(Pipe4)

    Pipe4.SetDownstreamMainUnit(Splt1)
    WWTP.append(Splt1)

    Splt1.SetDownstreamMainUnit(Pipe5)
    WWTP.append(Pipe5)

    Pipe5.SetDownstreamMainUnit(Reactor1)

    Splt1.SetupSidestream(Pipe6, 1)
    WWTP.append(Pipe6)

    Splt1.SetAsSRTController(True)

    Pipe6.SetDownstreamMainUnit(WAS1)
    WWTP.append(WAS1)
#End of ConnectWWTPUnits()



ConnectWWTPUnits()
CheckPlantConnection(WWTP)
CheckUpstream(WWTP)
CheckDownstream(WWTP)
print "End Connection Test"
# Connection Test Summary: SO FAR SO GOOD!!

#------------Disconnection Test---------
# PooPyLab is NOT Microsoft Visio. If the user is to re-direct the connected pipe to another 
# object, he/she would need to remove that pipe first, and then redraw a new pipe to the 
# desired object.
print "Begin Disconnection Test..."

Reactor1.RemoveUpstreamUnit(Pipe1)
Pipe5.RemoveUpstreamUnit(Splt1)
WAS1.RemoveUpstreamUnit(Pipe6)
Splt1.RemoveUpstreamUnit(Pipe4)
Pipe6.RemoveUpstreamUnit(Splt1.Sidestream) # TODO: HOW ARE WE GOING TO HANDLE THIS WHEN WORKING WITH GUI???
Clar1.RemoveUpstreamUnit(Pipe2)
Pipe2.RemoveUpstreamUnit(Reactor1)
Eff.RemoveUpstreamUnit(Pipe3)
Pipe3.RemoveUpstreamUnit(Clar1)

CheckPlantConnection(WWTP)

CheckUpstream(WWTP)
print
CheckDownstream(WWTP)
print "End Disconnection Test."

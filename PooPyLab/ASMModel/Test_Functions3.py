
# This is part of the test program for the PooPyLab biological wastewater 
# treatment software package.
#
# This file contains the functions used in the test programs
# Last update:
#   2015-6-26, KZ: elimiated duplicates by revising FindSCC()
#   2015-6-24, KZ: added note about the Splitter update
#   2015-4-14, Kai Zhang

'''
def print_elem(container):
    print "[",
    for element in container:
        print element.__name__, " ",
    print "]"
'''

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
            for element in upstr:
                print element.__name__, "; ",
            print
        else:
            print None
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


# The purpose of partitioning a PFD is to find the groups 
# of units which must be solved together, with as fewest
# number of units as possible.
# The algorithm was developed by Sargent and Westerberg
# (1964):
#   It traces from one unit to the next through the unit
#   output streams, forming a "string" of units.
#   This tracing continues until:
#       a) A unit in the string re-appears; or
#       b) A unit or group of units with no more output
#           is encountered.
#
#   1. Select a unit/group
#   2. Trace outputs downstream until
#       2a. a unit or a group on the path reappears 
#           --> Go to Step 3;
#       2b. a unit or a group reached with no external
#           outputs --> Go to Step 4.
#   3. Label all units into a group. --> Go to Step 2.
#   4. Delete the unit or group. Record it in a list.
#       --> Go to Step 2
#   5. Calculation Sequence is from the bottom to top
#       of list.
#
#   Later I abandoned the SW1964 algorithm above because
#   it is complicated in implementation and not the best
#   in terms of speed. Instead, the graph algorithm for
#   finding Strongly Connected Components (SCC) 
#   was adopted.
#
#   Preliminary results showed that the SCC algorithm
#   produced results that included the loops identified
#   by the S&W algoritm. However, there was an unwanted
#   SCC included in the result. I am thinking it might
#   has to do with how the Splitter was implemented.
#
#   As of June 24,2015, the Splitter class was updated
#   so that there is no Branch class in the sidestream.
#   The main- and sidestream are now implemented in the
#   same way.
#
#   June 26, 2015, duplicates were eliminated from the
#   results. No matter how the WWTP list was constructed,
#   the SCC algorithm always finds a unique answer for
#   the same process flow diagram (i.e. flowsheet).
#
#   The functions needed are _GetFinishTime(), _SCC_(),
#   _FindSCC_(), and FindGroups()


def _GetFinishTime_(PFD, Start, FinishTime):
    if Start == None or Start.IsVisited(): #order around "or" is important
        return
    Start.SetAsVisited(True)
    if Start.HasSidestream():
        _GetFinishTime_(PFD, Start.GetDownstreamSideUnit(), FinishTime)
    _GetFinishTime_(PFD, Start.GetDownstreamMainUnit(), FinishTime)
    FinishTime.append(Start)
    return 
            
def _SCC_(Start, SCC):
    if Start == None or Start.IsVisited(): #the order around "or" is important
        return SCC
    Start.SetAsVisited(True)
    UpstreamUnits = Start.GetUpstreamUnits()
    if UpstreamUnits != None:
        for key in UpstreamUnits:    
            if not (key.IsVisited()):
                SCC.append(key)
                _SCC_(key, SCC)
        return SCC

def _FindSCC_(FinishTime):
    FinishTime.reverse()
    Found = []
    for elem in FinishTime:
        SCC = [elem]
        if elem.IsVisited():
            SCC.pop(SCC.index(elem))
        else:
            temp = _SCC_(elem, SCC)
            if temp and len(temp)>1:
                Found.append(temp)
    return Found

def FindGroups(WWTP):
    '''Wrapper function for _GetFinishTime_(), _SCC_(), and _FindSCC_()'''
    FinishTime = []
    for unit in WWTP:
        if not (unit.IsVisited()):
            _GetFinishTime_(WWTP, unit, FinishTime)
    #for t in range(len(FinishTime)):
    #    print t, ": ", FinishTime[t].__name__
    for unit in WWTP:
        unit.SetAsVisited(False)
    return _FindSCC_(FinishTime)

#==========================UNDER DEVELOPMENT=============================

def _FindLoop_(SCC=[], Start, Done=set(), Loop):
    if len(Done) == len(SCC) or (Start in Done):
        return Loop
    

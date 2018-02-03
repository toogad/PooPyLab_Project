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
        print(element.__name__, " ",)
    print("]")
'''

def CheckPlantConnection(WWTP = []):
    LooseEnd = 0
    for unit in WWTP:
        if not unit.upstream_connected():
            print(unit.__name__, "'s upstream is not connected")
            LooseEnd += 1
        if unit.has_sidestream():
            if not unit.side_outlet_connected():
                print(unit.__name__, "'s sidestream is not connected")
                LooseEnd += 1
        elif not unit.main_outlet_connected():
            print(unit.__name__,"'s main downstream is not connected")
            LooseEnd +=1 
    if not LooseEnd:
        print("WWTP is ready for simulation")
    else:
        print(LooseEnd, " connecton(s) to be fixed.")
# End of CheckPlantConnection()


def CheckUpstream(WWTP = []):
    ''' Check the upstream connection of units in WWTP'''
    print("Checking units' upstream processes...")
    for unit in WWTP:
        upstr = []
        print(unit.__name__, "'s upstream has ",)
        if unit.get_upstream_units():
            upstr = unit.get_upstream_units().keys()
            for element in upstr:
                print(element.__name__, "; ",)
            print()
        else:
            print(None)
# End of CheckUpstream()

def CheckDownstream(WWTP = []):
    ''' Check the downstream connection of units in WWTP'''
    print("Checking units' downstream processes...")
    for unit in WWTP:
        print(unit.__name__, "'s Main downstream has ", )
        if unit.get_downstream_main_unit():
            print(unit.get_downstream_main_unit().__name__)
        else:
            print(None)
        if unit.has_sidestream():
            print(unit.__name__, "'s Side downstream has ", )
            if unit.get_downstream_side_unit():
                print(unit.get_downstream_side_unit().__name__)
            else:
                print(None)
    print()
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
#   have to do with how the Splitter was implemented.
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
    if Start == None or Start.is_visited(): #order around "or" is important
        return
    Start.set_as_visited(True)
    if Start.has_sidestream():
        _GetFinishTime_(PFD, Start.get_downstream_side_unit(), FinishTime)
    _GetFinishTime_(PFD, Start.get_downstream_main_unit(), FinishTime)
    FinishTime.append(Start)
    return 
            
def _SCC_(Start, SCC):
    if Start == None or Start.is_visited(): #the order around "or" is important
        return SCC
    Start.set_as_visited(True)
    UpstreamUnits = Start.get_upstream_units()
    if UpstreamUnits != None:
        for key in UpstreamUnits:    
            if not (key.is_visited()):
                SCC.append(key)
                _SCC_(key, SCC)
        return SCC

def _FindSCC_(FinishTime):
    FinishTime.reverse()
    Found = []
    for elem in FinishTime:
        SCC = [elem]
        if elem.is_visited():
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
        if not (unit.is_visited()):
            _GetFinishTime_(WWTP, unit, FinishTime)
    #for t in range(len(FinishTime)):
    #    print t, ": ", FinishTime[t].__name__
    for unit in WWTP:
        unit.set_as_visited(False)
    return _FindSCC_(FinishTime)

#==========================UNDER DEVELOPMENT=============================

def _Unblock_(Obj, Blocked, PreFix):
    # Obj: Object to be unblocked; equivalent to variable u in Johnson 1975 [SIAM]
    # Blocked: list of objects that are currently blocked
    # PreFix: dict of path leading to a particular object; equivalent to var. B() in Johnson 1975 [SIAM]
    #print 'Unblocking: ', Obj.__name__,
    if Obj in Blocked:
        Blocked.pop(Blocked.index(Obj))
    while PreFix.has_key(Obj):
        unit = PreFix[Obj].pop(0)
        if unit in Blocked:
            _Unblock_(unit, Blocked, PreFix)

def _Circuit_(Obj, SCC, Start, Blocked, StepStack, PreFix, Unblock_Ready, FoundCircuits):
    # Obj: see remark in _Unblock_() function
    # SCC: list of Strongly Connected Components found previously
    # Start: current starting point; equivalent to variable s in Johnson 1975 [SIAM]
    # Blocked: see remark in _Unblock_() function
    # StepStack: stack that stores the objects that have encountered so far with Start being the 1st obj
    # PreFix: see remark in _Unblock_() function
    # Unblock_Ready: boolean flag; equivalent to boolean flag f in Johnson 1975 [SIAM]
    # FoundCircuits: list of elemental circuits found within the SCC
    Unblock_Ready = False
    StepStack.append(Obj)
    Blocked.append(Obj)
    
##    print(Current Blocked[]', )
##    for item in Blocked:
##        print item.__name__,
##    print()
##    prin('Current StepStack[]: ',)
##    for item in StepStack:
##        print(item.__name__,)
##    print()

    next = [] # next was not in Johnson 1975 algorithm. It was specific for PooPyLab objects.
    if Obj.has_sidestream():
        next = [Obj.get_downstream_side_unit()]
    next.append(Obj.get_downstream_main_unit())
    for k in next:
        if k in SCC:
            if k == Start:
                StepStackCopy = StepStack[:]
                StepStackCopy.sort()
                FoundCircuits.append(StepStackCopy[:])
#                for subgroup in FoundCircuits:
#                    print([ ",)
#                    for item in subgroup:
#                        print item.__name__, "; ",
#                    print( ]")
                Unblock_Ready = True
            elif not (k in Blocked):
                if _Circuit_(k, SCC, Start, Blocked, StepStack, PreFix, Unblock_Ready, FoundCircuits):
                    Unblock_Ready = True
            if Unblock_Ready:
                _Unblock_(Obj, Blocked, PreFix)
                print()
            else:
                for k in next:
                    if k in SCC:
                        if PreFix.has_key(Obj) and not (k in PreFix[Obj]):
                            PreFix[Obj].append(k)
    StepStack.pop()
    return Unblock_Ready
    
def FindLoops(Groups, FoundCircuits):
    for SCC in Groups:
        Blocked = [] 
        StepStack = []
        PreFix = {}
        Unblock_Ready = False
        for Obj in SCC:
#            print(Current Start: ', Obj.__name__)
            _Circuit_(Obj, SCC, Obj, Blocked, StepStack, PreFix, Unblock_Ready, FoundCircuits)
#            print("FoundCircuits []: ", len(FoundCircuits))
#        user_key = raw_input('Paused...')

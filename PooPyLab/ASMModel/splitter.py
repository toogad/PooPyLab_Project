# This file is part of PooPyLab.
#
# PooPyLab is a simulation software for biological wastewater treatment
# processes using International Water Association Activated Sludge Models.
#    
#    Copyright (C) 2014  Kai Zhang
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
#
#This file provides the definition of Splitter.
#
#Update Log:
#   June 24, 2015 KZ: Updated SetDownstreamSideUnit() to differential main/side
#   June 23, 2015 KZ: Rewrote sidestream to eliminate Branch class
#   June 18, 2015 KZ: Removed _PreFix and _Group status and 
#                       Set(Get)PreFixStatus(), Set(Get)GroupStatus;
#                       Renamed _Done to _Visited and SetAs(Is)Done() to
#                       SetAs(Is)Visited()
#   March 20, 2015 KZ: Added _PreFix, _Group, _Done status and 
#                       Set(Get)PreFixStatus(), Set(Get)GroupStatus, 
#                       SetAs(Is)Done().
#   November 18, 2014 KZ: renamed "SideStream" into "Sidestream";
#                           Added _SidestreamConnected and SideOutletConnected()
#   Sep 26, 2014 KZ: fixed pipe.Pipe.__init__
#   April 27, 2014 KZ: Change the sidestream class from Influent() to Sidestream()
#   April 18, 2014 KZ: Rewrite definition based on the new class system structure
#   December 25, 2013 KZ: commented out the BlendComponent() function in ReceiveFrom()
#   December 07, 2013
#

import pipe 


class Splitter(pipe.Pipe):
    __id = 0

    def __init__(self):
        pipe.Pipe.__init__(self)
        self.__class__.__id += 1
        self.__name__ = "Splitter_" + str(self.__id)

        #self._Sidestream = None
        #self.Sidestream.SetFlow(0.0)

        #the main outlet is defined in pipe.Pipe as self._MainOutlet
        # therefore add the _SideOutlet only here.
        self._SideOutlet = None
        
        self._MainOutletFlow = 0.0
        self._SideOutletFlow = 0.0
        
        self._SideOutletConnected = False

        # _Visited is True/False on whether the loop finding process has finished
        #   analyzing the unit
        self._Visited = False
       
        self._SRTController = False
        print self.__name__, "initialized successfully."
    
    def IsSRTController(self):
        ''' Mark the Splitter whether it controls the plant's Solids Retention Time.
            Default value: False
        '''
        return self._SRTController

    def SetAsSRTController(self, setting = False):
        ''' Take user-input to set whether the current Splitter control plant's SRT'''
        self._SRTController = setting
        #TODO: HOW DOES THIS IMPACT WAS FLOW BASED ON USER SPECIFIED SRT?

    def SetSidestreamFlow(self, Flow):
        self._SideOutletFlow = Flow
        #TODO: Need to be able to dynamically update the sidestream flow
    
    def TotalizeFlow(self):
        ''' totalize the flow for the Splitter unit,
        '''
        self._TotalFlow = self._MainOutletFlow = 0.0
        for unit in self._Inlet:
            self._TotalFlow += self._Inlet[unit]
        #TODO: Need to pay close attention to the flow balance below during runtime
        #self.Sidestream.TotalizeFlow()
        #self._SideOutletFlow = self.Sidestream.GetOutletFlow()
        self._MainOutletFlow = self._TotalFlow - self._SideOutletFlow
        self._FlowTotalized = True


    def SetDownstreamSideUnit(self, SingleReceiver):
        ''' Set the sidestream unit that will receive effluent from the current unit'''
        if self._SideOutlet != SingleReceiver:
            self._SideOutlet = SingleReceiver
            self._SideOutletConnected = True
            if SingleReceiver != None:
                SingleReceiver.AddUpstreamUnit(self, "Side")#TODO: OKAY??
                
    def GetDownstreamSideUnit(self):
        return self._SideOutlet

    def Discharge(self):
        ''' Pass the total flow and blended components to the next unit.
            Both mainstream and sidestream units shall receive their flows and component
            concentratons.
        '''
        self.UpdateCombinedInput()
        if self._MainOutlet != None and self._Sidestream != None:
            self.GetDownstreamMainUnit().UpdateCombinedInput()
            self.GetDownstreamSideUnit().UpdateCombinedInput() 
        else:
            print "ERROR: ", self.__name__, " downstream unit setup not complete"

    def HasSidestream(self):
        ''' Check if the current unit has a sidestream discharge.
            Default = False, i.e. no sidestream
            Return type: boolean
        '''
        return True 
    
    def SideOutletConnected(self):
        return self._SideOutletConnected

    def SetAsVisited(self, Status = False):
        self._Visited = Status

    def IsVisited(self):
        return self._Visited
 
    #def GetWAS(self, WWTP, TargetSRT): 
    #    '''Get the mass of DRY solids to be wasted (WAS) in KiloGram'''
    #    #WWTP is a list that stores all the process units
    #    TotalSolids = 0.0 #as TSS in KiloGram
    #    if self._SRTController:
    #        for unit in WWTP:
    #            if isinstance(unit, .ASMReactor):
    #                TotalSolids += unit.GetTSS() * unit.GetActiveVolume() / 1000.0
    #    if TargetSRT > 0:
    #        return TotalSolids / TargetSRT
    #    else:
    #        print "Error in Target SRT (equal to or less than 0 day; GetWAS() returns 0."
    #        return 0;


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
# This file provides the definition of Splitter.
#
# Update Log:
# Jul 30, 2017 KZ: pythonic style
# Mar 21, 2017 KZ: Migrated to Python3
# Jun 24, 2015 KZ: Updated SetDownstreamSideUnit() to differential main/side
# Jun 23, 2015 KZ: Rewrote sidestream to eliminate Branch class
# Jun 18, 2015 KZ: Removed _PreFix and _Group status and 
#                     Set(Get)PreFixStatus(), Set(Get)GroupStatus;
#                     Renamed _Done to _Visited and SetAs(Is)Done() to
#                     SetAs(Is)Visited()
# Mar 20, 2015 KZ: Added _PreFix, _Group, _Done status and 
#                     Set(Get)PreFixStatus(), Set(Get)GroupStatus, 
#                     SetAs(Is)Done().
# Nov 18, 2014 KZ: renamed "SideStream" into "Sidestream";
#                         Added _SidestreamConnected and SideOutletConnected()
# Sep 26, 2014 KZ: fixed pipe.Pipe.__init__
# Apr 27, 2014 KZ: Change the sidestream class from Influent() to Sidestream()
# Apr 18, 2014 KZ: Rewrite definition based on the new class system structure
# Dec 25, 2013 KZ: commented out the BlendComponent() function in ReceiveFrom()
# Dec 07, 2013
#

import pipe 


class splitter(pipe.pipe):
    __id = 0

    def __init__(self):
        pipe.pipe.__init__(self)
        self.__class__.__id += 1
        self.__name__ = "Splitter_" + str(self.__id)

        # the main outlet is defined in pipe.pipe as _main_outlet
        # therefore add the _side_outlet only here.
        self._side_outlet= None
        
        self._main_outlet_flow = 0.0
        self._side_outlet_flow = 0.0
        
        self._side_outlet_connected = False

        # boolean on whether the loop finding process has finished
        #   analyzing the unit
        self._visited = False
       
        self._SRT_controller = False
        print(self.__name__, "initialized successfully.")
    
    def is_SRT_controller(self):
        ''' Mark the splitter whether it controls the plant's Solids Retention
            Time.
            Default value: False
        '''
        return self._SRT_controller

    def set_as_SRT_controller(self, setting=False):
        ''' Take user-input to set whether the current Splitter control 
            plant's SRT
        '''
        self._SRT_controller = setting
        #TODO: HOW DOES THIS IMPACT WAS FLOW BASED ON USER SPECIFIED SRT?

    def set_sidestream_flow(self, flow):
        self._side_outlet_flow = flow
        #TODO: Need to be able to dynamically update the sidestream flow
    
    def totalize_flow(self):
        ''' totalize the flow for the Splitter unit '''
        self._total_flow = self._main_outlet_flow = 0.0
        for unit in self._inlet:
            self._total_flow += self._inlet[unit]
        #TODO: Need to pay attention to the flow balance below during runtime
        self._main_outlet_flow = self._total_flow - self._side_outlet_flow
        self._flow_totalized = True


    def set_downstream_side_unit(self, rcvr):
        ''' Set the sidestream unit that will receive effluent from the
            current unit
        '''
        if self._side_outlet != rcvr:
            self._side_outlet = rcvr
            self._side_outlet_connected = True
            if rcvr != None:
                rcvr.add_upstream_unit(self, "Side")  #TODO: OKAY??
                
    def get_downstream_side_unit(self):
        return self._side_outlet

    def discharge(self):
        ''' Pass the total flow and blended components to the next unit.
            Both mainstream and sidestream units shall receive their flows 
            and component concentratons.
        '''
        self.update_combined_input()
        if self._main_outlet != None and self.set_sidestream_flow != None:
            self.get_downstream_main_unit().update_combined_input()
            self.get_downstream_main_unit().update_combined_input() 
        else:
            print("ERROR: ", self.__name__, "downstream unit setup incomplete")

    def has_sidestream(self):
        return True 
    
    def _side_outlet_connected(self):
        return self._side_outlet_connected

    def set_as_visited(self, status=False):
        self._visited = status

    def is_visited(self):
        return self._visited
 
    #def GetWAS(self, WWTP, TargetSRT): 
    #    '''Get the mass of DRY solids to be wasted (WAS) in KiloGram'''
    #    #WWTP is a list that stores all the process units
    #    TotalSolids = 0.0 #as TSS in KiloGram
    #    if self._SRTController:
    #        for unit in WWTP:
    #            if isinstance(unit, ASMReactor):
    #                TotalSolids += unit.GetTSS() \
    #                               * unit.GetActiveVolume() / 1000.0
    #    if TargetSRT > 0:
    #        return TotalSolids / TargetSRT
    #    else:
    #        print("Error in Target SRT <=  0 day; GetWAS() returns 0.")
    #        return 0;


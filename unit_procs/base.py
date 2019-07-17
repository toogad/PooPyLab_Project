#   This file is part of PooPyLab.
#
#    PooPyLab is a simulation software for biological wastewater treatment
#    processes using the International Water Association Activated Sludge
#    Models.
#   
#    Copyright (C) Kai Zhang
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
# --------------------------------------------------------------------
#   Definition of the base class for WWTP components.
#
#   Update Log:
#   Jul 16, 2019 KZ: added get_type()
#   Jun 19, 2019 KZ: improved branch flow balance
#   Jun 18, 2019 KZ: added funcs to assist branch flow balance
#   Jun 10, 2019 KZ: further revised to splitter-like base
#   Jun 04, 2019 KZ: change the base to splitter-like.
#   May 22, 2019 KZ: added options for branch in get_xxxx() functions
#   Jan 12, 2019 KZ: resumed and cleaned up
#   Feb 03, 2018 KZ: reviewed
#   Jul 21, 2017 KZ: made it more pythonic
#   Mar 21, 2017 KZ: Migrated to Python3
#   Jun 16, 2015 KZ: Removed Set(Get)PreFix(), Set(Get)Group();
#                       Renamed SetAs(Is)Done() to SetAs(Is)Visited()
#   Mar 20, 2015 KZ: Added Set(Get)PreFix(), Set(Get)Group(), 
#                       SetAs(Is)Done() for tracking status in loop finding
#   Nov 20, 2014 KZ: Added UpstreamConnected() and MainOutletConnected() 
#   Jun 29, 2014 KZ: Replace Interpret() with GetXXXX() functions
#   Jun 28, 2014 KZ: Added GetTSS(), getTotalCOD(), and getSoluableCOD()
#   Mar 15, 2014 KZ: Moved AddUpstreamUnit(), RemoveUpstreamUnit(), and 
#                       SetDownstreamMainUnit() to Pipe()
#   Mar 06, 2014 KZ: Re-wrote the common interface and change Base into an 
#                       abstract class
#   Dec 25, 2013 KZ: commented out the BlendComponent() function in 
#                       ReceiveFrom()
#   Dec 17, 2013 KZ: added _PrevComp[0:12] to store state variables from 
#                       previous iteration
#   Dec 07, 2013 Kai Zhang (KZ)



from abc import ABCMeta, abstractmethod

class poopy_lab_obj(object):
    '''
    Defines the common interfaces for all PooPyLab objects.
    '''

    __metaclass__ = ABCMeta

    @abstractmethod
    def _branch_flow_helper(self):
        '''
        helper function to calculate 1 of the 3 branches' flow based on the
        other 2.
        return True if flow balace is done, False otherwise
        '''
        pass

    @abstractmethod
    def get_type(self):
        '''
        Return the type (Influent, Effluent, Pipe, Splitter, etc) of the
        current object.
        '''
        pass

    @abstractmethod
    def has_sidestream(self):
        ''' 
        Check if the current unit has a sidestream discharge.
        Default = True, i.e. splitter always has a sidestream
        '''
        pass


    @abstractmethod
    def add_upstream(self, discharger, branch):
        '''
        Add the discharger's branch to self._inlet
        '''
        pass


    @abstractmethod
    def has_discharger(self):
        '''
        Return True if upstream is connected, False if not
        '''
        pass


    @abstractmethod
    def get_upstream(self):
        ''' 
        Get the dict that stores all the upstream units that feed into
        the current one
        Return Type: {poopy_lab_obj:flow_into_self}
        '''
        pass


    @abstractmethod
    def totalize_inflow(self):
        pass


    @abstractmethod
    def blend_inlet_comps(self):
        pass


    @abstractmethod
    def update_combined_input(self):
        '''
        Wrapper that combines the flows and loads into current unit
        '''
        pass


    @abstractmethod
    def remove_upstream(self, discharger):
        '''
        Remove an existing discharger from self._inlet
        '''
        pass


    @abstractmethod
    def set_downstream_main(self, receiver):
        pass


    @abstractmethod
    def main_outlet_connected(self):
        pass


    @abstractmethod
    def get_downstream_main(self):
        pass


    @abstractmethod
    def set_mainstream_flow_by_upstream(self, flag):
        pass


    @abstractmethod
    def set_mainstream_flow(self, flow):
        pass


    @abstractmethod
    def get_main_outflow(self):
        '''
        Return the mainstream outlet flow
        Return value type: float
        '''
        pass


    @abstractmethod
    def get_main_outlet_concs(self):
        '''
        Return the effluent model components of the mainstream outlet
        Return type: list
        '''
        pass


    @abstractmethod
    def set_downstream_side(self, receiver):
        pass


    @abstractmethod
    def side_outlet_connected(self):
        '''
        Return True if the downstream main outlet is connected,
        False if not.
        '''
        pass


    @abstractmethod
    def get_downstream_side(self):
        pass


    @abstractmethod
    def set_sidestream_flow(self, flow):
        pass


    @abstractmethod
    def sidestream_flow_defined(self):
        pass


    @abstractmethod
    def get_side_outflow(self):
        '''
        Return the sidestream outlet flow
        '''
        pass


    @abstractmethod
    def get_side_outlet_concs(self):
        pass


    @abstractmethod
    def set_flow(self, discharger, flow):
        '''
        specify the flow from the discharger
        '''
        pass


    @abstractmethod
    def _discharge_main_outlet(self):
        pass


    @abstractmethod
    def _discharge_side_outlet(self):
        pass


    @abstractmethod
    def discharge(self):
        '''
        Pass the total flow and blended components to the next units.
        '''
        pass


    @abstractmethod
    def get_TSS(self, branch="Main_Out"):
        pass


    @abstractmethod
    def get_VSS(self, branch="Main_Out"):
        pass


    @abstractmethod
    def get_COD(self, branch="Main_Out"):
        pass


    @abstractmethod
    def get_sCOD(self, branch="Main_Out"):
        pass


    @abstractmethod
    def get_pCOD(self, branch="Main_Out"):
        pass


    @abstractmethod
    def get_TN(self, branch="Main_Out"):
        pass


    @abstractmethod
    def get_orgN(self, branch="Main_Out"):
        pass


    @abstractmethod
    def get_inorgN(self, branch="Main_Out"):
        pass


    @abstractmethod
    def get_pN(self, branch="Main_Out"):
        pass


    @abstractmethod
    def get_sN(self, branch="Main_Out"):
        pass


    @abstractmethod
    def set_as_visited(self, Status):
        ''' Set the unit as True when done visiting it in the loop finding
            process. Status = False by default.
        '''
        pass


    @abstractmethod
    def is_visited(self):
        ''' Return True if the unit is labelled as visited, False otherwise '''
        pass

